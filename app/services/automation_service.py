"""
Сервис для управления автоматизациями и уведомлениями
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import json
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import croniter
import jinja2

from ..database.automation_models import (
    AutomationRule, AutomationExecution, NotificationTemplate,
    Notification, WorkflowTemplate, WorkflowInstance, WorkflowTask,
    NotificationSubscription, AutomationType, TriggerType, 
    NotificationChannel
)
from ..database.crm_models import Client, Lead, Deal, DealStatus, LeadStatus
from ..database.models import Project, AdminUser
from ..config.logging import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class AutomationService:
    """Сервис автоматизаций"""
    
    def __init__(self, db: Session):
        self.db = db
        self.jinja_env = jinja2.Environment()
    
    # === Управление правилами автоматизации ===
    
    def create_rule(self, rule_data: Dict[str, Any], created_by: int) -> AutomationRule:
        """Создать правило автоматизации"""
        rule = AutomationRule(
            name=rule_data['name'],
            description=rule_data.get('description'),
            type=AutomationType(rule_data['type']),
            trigger_type=TriggerType(rule_data['trigger_type']),
            conditions=rule_data.get('conditions', {}),
            schedule=rule_data.get('schedule'),
            actions=rule_data.get('actions', []),
            is_active=rule_data.get('is_active', True),
            priority=rule_data.get('priority', 5),
            max_executions=rule_data.get('max_executions'),
            created_by=created_by
        )
        
        # Если есть расписание, вычисляем следующее время выполнения
        if rule.schedule and rule.trigger_type == TriggerType.TIME_BASED:
            rule.next_execution_at = self._calculate_next_execution(rule.schedule)
        
        self.db.add(rule)
        self.db.commit()
        
        logger.info(f"Created automation rule: {rule.name}")
        return rule
    
    def get_active_rules(self, rule_type: AutomationType = None) -> List[AutomationRule]:
        """Получить активные правила"""
        query = self.db.query(AutomationRule).filter(AutomationRule.is_active == True)
        
        if rule_type:
            query = query.filter(AutomationRule.type == rule_type)
        
        return query.order_by(AutomationRule.priority.desc()).all()
    
    def execute_rule(self, rule_id: int, trigger_data: Dict[str, Any] = None) -> AutomationExecution:
        """Выполнить правило автоматизации"""
        rule = self.db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
        if not rule or not rule.is_active:
            logger.warning(f"Rule {rule_id} not found or inactive")
            return None
        
        # Проверяем лимит выполнений
        if rule.max_executions and rule.execution_count >= rule.max_executions:
            logger.warning(f"Rule {rule_id} reached max executions limit")
            rule.is_active = False
            self.db.commit()
            return None
        
        # Создаем запись о выполнении
        execution = AutomationExecution(
            rule_id=rule_id,
            status='running',
            trigger_data=trigger_data,
            started_at=datetime.utcnow()
        )
        self.db.add(execution)
        self.db.commit()
        
        try:
            # Проверяем условия
            if not self._check_conditions(rule.conditions, trigger_data):
                execution.status = 'skipped'
                execution.result_data = {"message": "Conditions not met"}
            else:
                # Выполняем действия
                results = []
                for action in rule.actions:
                    result = self._execute_action(action, trigger_data)
                    results.append(result)
                
                execution.status = 'completed'
                execution.result_data = {"actions": results}
            
            # Обновляем счетчики
            rule.execution_count += 1
            rule.last_executed_at = datetime.utcnow()
            
            # Вычисляем следующее выполнение для периодических задач
            if rule.trigger_type == TriggerType.TIME_BASED and rule.schedule:
                rule.next_execution_at = self._calculate_next_execution(rule.schedule)
            
        except Exception as e:
            logger.error(f"Error executing rule {rule_id}: {e}")
            execution.status = 'failed'
            execution.error_message = str(e)
        
        finally:
            execution.completed_at = datetime.utcnow()
            execution.duration_ms = int((execution.completed_at - execution.started_at).total_seconds() * 1000)
            self.db.commit()
        
        return execution
    
    def _check_conditions(self, conditions: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Проверить условия срабатывания"""
        if not conditions:
            return True
        
        operator = conditions.get('operator', 'AND')  # AND или OR
        checks = conditions.get('checks', [])
        
        results = []
        for check in checks:
            field = check.get('field')
            op = check.get('operator')
            value = check.get('value')
            
            # Получаем значение из данных
            field_value = data.get(field) if data else None
            
            # Проверяем условие
            result = self._evaluate_condition(field_value, op, value)
            results.append(result)
        
        if operator == 'AND':
            return all(results)
        else:
            return any(results)
    
    def _evaluate_condition(self, field_value: Any, operator: str, compare_value: Any) -> bool:
        """Оценить одно условие"""
        if operator == 'equals':
            return field_value == compare_value
        elif operator == 'not_equals':
            return field_value != compare_value
        elif operator == 'contains':
            return compare_value in str(field_value)
        elif operator == 'greater_than':
            return float(field_value) > float(compare_value)
        elif operator == 'less_than':
            return float(field_value) < float(compare_value)
        elif operator == 'is_empty':
            return not field_value
        elif operator == 'is_not_empty':
            return bool(field_value)
        else:
            return False
    
    def _execute_action(self, action: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнить действие"""
        action_type = action.get('type')
        params = action.get('params', {})
        
        try:
            if action_type == 'send_notification':
                return self._action_send_notification(params, data)
            elif action_type == 'create_task':
                return self._action_create_task(params, data)
            elif action_type == 'update_field':
                return self._action_update_field(params, data)
            elif action_type == 'create_deal':
                return self._action_create_deal(params, data)
            elif action_type == 'change_status':
                return self._action_change_status(params, data)
            elif action_type == 'assign_to_user':
                return self._action_assign_to_user(params, data)
            elif action_type == 'add_tag':
                return self._action_add_tag(params, data)
            elif action_type == 'webhook':
                return self._action_webhook(params, data)
            else:
                return {"success": False, "error": f"Unknown action type: {action_type}"}
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_next_execution(self, schedule: str) -> datetime:
        """Вычислить следующее время выполнения по cron-выражению"""
        try:
            cron = croniter.croniter(schedule, datetime.utcnow())
            return cron.get_next(datetime)
        except Exception as e:
            logger.error(f"Error calculating next execution: {e}")
            return None
    
    # === Действия автоматизации ===
    
    def _action_send_notification(self, params: Dict, data: Dict) -> Dict:
        """Отправить уведомление"""
        template_id = params.get('template_id')
        recipient_id = params.get('recipient_id') or data.get('user_id')
        channel = params.get('channel', 'email')
        
        # Создаем уведомление
        notification = self.create_notification(
            template_id=template_id,
            recipient_id=recipient_id,
            channel=channel,
            data=data
        )
        
        # Отправляем
        self.send_notification(notification.id)
        
        return {"success": True, "notification_id": notification.id}
    
    def _action_create_task(self, params: Dict, data: Dict) -> Dict:
        """Создать задачу"""
        from ..database.models import Task
        
        task = Task(
            title=params.get('title', 'Автоматическая задача'),
            description=params.get('description'),
            assigned_to=params.get('assigned_to'),
            due_date=datetime.utcnow() + timedelta(days=params.get('days_to_complete', 1)),
            priority=params.get('priority', 'normal'),
            created_at=datetime.utcnow()
        )
        
        self.db.add(task)
        self.db.commit()
        
        return {"success": True, "task_id": task.id}
    
    def _action_update_field(self, params: Dict, data: Dict) -> Dict:
        """Обновить поле сущности"""
        entity_type = params.get('entity_type')
        entity_id = data.get(f'{entity_type}_id')
        field_name = params.get('field_name')
        field_value = params.get('field_value')
        
        if entity_type == 'lead':
            entity = self.db.query(Lead).filter(Lead.id == entity_id).first()
        elif entity_type == 'deal':
            entity = self.db.query(Deal).filter(Deal.id == entity_id).first()
        elif entity_type == 'client':
            entity = self.db.query(Client).filter(Client.id == entity_id).first()
        else:
            return {"success": False, "error": f"Unknown entity type: {entity_type}"}
        
        if entity and hasattr(entity, field_name):
            setattr(entity, field_name, field_value)
            self.db.commit()
            return {"success": True, "updated": f"{entity_type}.{field_name}"}
        
        return {"success": False, "error": "Entity or field not found"}
    
    def _action_create_deal(self, params: Dict, data: Dict) -> Dict:
        """Создать сделку"""
        lead_id = data.get('lead_id')
        if not lead_id:
            return {"success": False, "error": "Lead ID not provided"}
        
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"success": False, "error": "Lead not found"}
        
        deal = Deal(
            title=params.get('title') or f"Сделка из лида {lead.title}",
            client_id=lead.client_id,
            lead_id=lead_id,
            amount=params.get('amount') or lead.budget,
            status=DealStatus.NEW,
            responsible_manager_id=lead.responsible_manager_id,
            created_at=datetime.utcnow()
        )
        
        self.db.add(deal)
        
        # Обновляем статус лида
        lead.status = LeadStatus.WON
        lead.converted_to_deal_id = deal.id
        
        self.db.commit()
        
        return {"success": True, "deal_id": deal.id}
    
    def _action_change_status(self, params: Dict, data: Dict) -> Dict:
        """Изменить статус сущности"""
        entity_type = params.get('entity_type')
        entity_id = data.get(f'{entity_type}_id')
        new_status = params.get('new_status')
        
        if entity_type == 'lead':
            entity = self.db.query(Lead).filter(Lead.id == entity_id).first()
            if entity:
                entity.status = LeadStatus(new_status)
        elif entity_type == 'deal':
            entity = self.db.query(Deal).filter(Deal.id == entity_id).first()
            if entity:
                entity.status = DealStatus(new_status)
        elif entity_type == 'project':
            entity = self.db.query(Project).filter(Project.id == entity_id).first()
            if entity:
                entity.status = new_status
        else:
            return {"success": False, "error": f"Unknown entity type: {entity_type}"}
        
        if entity:
            self.db.commit()
            return {"success": True, "updated_status": new_status}
        
        return {"success": False, "error": "Entity not found"}
    
    def _action_assign_to_user(self, params: Dict, data: Dict) -> Dict:
        """Назначить ответственного"""
        entity_type = params.get('entity_type')
        entity_id = data.get(f'{entity_type}_id')
        user_id = params.get('user_id')
        
        if entity_type == 'lead':
            entity = self.db.query(Lead).filter(Lead.id == entity_id).first()
            if entity:
                entity.responsible_manager_id = user_id
        elif entity_type == 'deal':
            entity = self.db.query(Deal).filter(Deal.id == entity_id).first()
            if entity:
                entity.responsible_manager_id = user_id
        else:
            return {"success": False, "error": f"Unknown entity type: {entity_type}"}
        
        if entity:
            self.db.commit()
            return {"success": True, "assigned_to": user_id}
        
        return {"success": False, "error": "Entity not found"}
    
    def _action_add_tag(self, params: Dict, data: Dict) -> Dict:
        """Добавить тег"""
        entity_type = params.get('entity_type')
        entity_id = data.get(f'{entity_type}_id')
        tag = params.get('tag')
        
        # Получаем сущность
        if entity_type == 'client':
            entity = self.db.query(Client).filter(Client.id == entity_id).first()
        elif entity_type == 'lead':
            entity = self.db.query(Lead).filter(Lead.id == entity_id).first()
        else:
            return {"success": False, "error": f"Unknown entity type: {entity_type}"}
        
        if entity:
            # Добавляем тег (предполагаем, что tags - это JSON поле)
            if not entity.tags:
                entity.tags = []
            if tag not in entity.tags:
                entity.tags.append(tag)
            
            self.db.commit()
            return {"success": True, "tag_added": tag}
        
        return {"success": False, "error": "Entity not found"}
    
    def _action_webhook(self, params: Dict, data: Dict) -> Dict:
        """Отправить webhook"""
        import requests
        
        url = params.get('url')
        method = params.get('method', 'POST')
        headers = params.get('headers', {})
        
        # Подготавливаем данные
        payload = {
            **data,
            'timestamp': datetime.utcnow().isoformat(),
            'automation_params': params
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response": response.text[:500]  # Первые 500 символов ответа
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # === Управление уведомлениями ===
    
    def create_notification_template(self, template_data: Dict[str, Any], created_by: int) -> NotificationTemplate:
        """Создать шаблон уведомления"""
        template = NotificationTemplate(
            name=template_data['name'],
            channel=NotificationChannel(template_data['channel']),
            subject=template_data.get('subject'),
            content=template_data['content'],
            variables=template_data.get('variables', []),
            is_active=template_data.get('is_active', True),
            language=template_data.get('language', 'ru'),
            created_by=created_by
        )
        
        self.db.add(template)
        self.db.commit()
        
        return template
    
    def create_notification(self, template_id: int = None, recipient_id: int = None,
                          channel: str = 'email', data: Dict = None) -> Notification:
        """Создать уведомление"""
        notification = Notification(
            template_id=template_id,
            channel=NotificationChannel(channel),
            recipient_id=recipient_id,
            status='pending',
            created_at=datetime.utcnow(),
            data=data
        )
        
        # Если есть шаблон, заполняем содержимое
        if template_id:
            template = self.db.query(NotificationTemplate).filter(
                NotificationTemplate.id == template_id
            ).first()
            
            if template:
                # Рендерим шаблон с данными
                notification.subject = self._render_template(template.subject, data)
                notification.content = self._render_template(template.content, data)
        
        # Получаем контактные данные получателя
        if recipient_id:
            user = self.db.query(AdminUser).filter(AdminUser.id == recipient_id).first()
            if user:
                notification.recipient_type = 'admin'
                notification.recipient_email = user.email
                notification.recipient_phone = user.phone
        
        self.db.add(notification)
        self.db.commit()
        
        return notification
    
    def send_notification(self, notification_id: int) -> bool:
        """Отправить уведомление"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification or notification.status != 'pending':
            return False
        
        try:
            if notification.channel == NotificationChannel.EMAIL:
                success = self._send_email_notification(notification)
            elif notification.channel == NotificationChannel.SMS:
                success = self._send_sms_notification(notification)
            elif notification.channel == NotificationChannel.TELEGRAM:
                success = self._send_telegram_notification(notification)
            elif notification.channel == NotificationChannel.IN_APP:
                success = self._send_in_app_notification(notification)
            else:
                success = False
            
            if success:
                notification.status = 'sent'
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = 'failed'
            
            self.db.commit()
            return success
            
        except Exception as e:
            logger.error(f"Error sending notification {notification_id}: {e}")
            notification.status = 'failed'
            notification.error_message = str(e)
            self.db.commit()
            return False
    
    def _render_template(self, template_str: str, data: Dict) -> str:
        """Рендеринг шаблона с данными"""
        if not template_str:
            return ""
        
        try:
            template = self.jinja_env.from_string(template_str)
            return template.render(**data) if data else template_str
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return template_str
    
    def _send_email_notification(self, notification: Notification) -> bool:
        """Отправить email уведомление"""
        if not notification.recipient_email:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = notification.recipient_email
            msg['Subject'] = notification.subject or "Уведомление"
            
            msg.attach(MIMEText(notification.content, 'html'))
            
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _send_sms_notification(self, notification: Notification) -> bool:
        """Отправить SMS уведомление"""
        # TODO: Интеграция с SMS провайдером
        logger.info(f"SMS notification to {notification.recipient_phone}: {notification.content[:100]}")
        return True
    
    def _send_telegram_notification(self, notification: Notification) -> bool:
        """Отправить Telegram уведомление"""
        if not notification.recipient_telegram_id:
            return False
        
        try:
            from telegram import Bot
            bot = Bot(token=settings.BOT_TOKEN)
            
            # Синхронная отправка
            bot.send_message(
                chat_id=notification.recipient_telegram_id,
                text=notification.content,
                parse_mode='HTML'
            )
            
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False
    
    def _send_in_app_notification(self, notification: Notification) -> bool:
        """Создать внутреннее уведомление"""
        # Просто помечаем как доставленное
        notification.delivered_at = datetime.utcnow()
        return True
    
    # === Управление рабочими процессами ===
    
    def create_workflow_from_template(self, template_id: int, entity_type: str, 
                                     entity_id: int, owner_id: int) -> WorkflowInstance:
        """Создать экземпляр рабочего процесса из шаблона"""
        template = self.db.query(WorkflowTemplate).filter(
            WorkflowTemplate.id == template_id,
            WorkflowTemplate.is_active == True
        ).first()
        
        if not template:
            return None
        
        # Создаем экземпляр процесса
        workflow = WorkflowInstance(
            template_id=template_id,
            entity_type=entity_type,
            entity_id=entity_id,
            owner_id=owner_id,
            current_stage=0,
            status='active',
            started_at=datetime.utcnow()
        )
        
        self.db.add(workflow)
        self.db.flush()
        
        # Создаем задачи для первого этапа
        if template.stages and len(template.stages) > 0:
            self._create_stage_tasks(workflow, template.stages[0], 0)
        
        self.db.commit()
        
        return workflow
    
    def _create_stage_tasks(self, workflow: WorkflowInstance, stage: Dict, stage_index: int):
        """Создать задачи для этапа процесса"""
        tasks = stage.get('tasks', [])
        
        for task_data in tasks:
            task = WorkflowTask(
                workflow_id=workflow.id,
                stage_index=stage_index,
                name=task_data['name'],
                description=task_data.get('description'),
                type=task_data.get('type', 'manual'),
                assigned_to=task_data.get('assigned_to', workflow.owner_id),
                due_date=datetime.utcnow() + timedelta(days=task_data.get('duration_days', 1)),
                status='pending',
                created_at=datetime.utcnow()
            )
            
            self.db.add(task)
            
            # Если задача автоматическая, выполняем сразу
            if task.type == 'automatic':
                self._execute_automatic_task(task)
    
    def _execute_automatic_task(self, task: WorkflowTask):
        """Выполнить автоматическую задачу"""
        task.status = 'in_progress'
        task.started_at = datetime.utcnow()
        
        try:
            # Здесь логика выполнения автоматических задач
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
        except Exception as e:
            logger.error(f"Error executing automatic task {task.id}: {e}")
            task.status = 'failed'
    
    def advance_workflow(self, workflow_id: int) -> bool:
        """Перейти к следующему этапу процесса"""
        workflow = self.db.query(WorkflowInstance).filter(
            WorkflowInstance.id == workflow_id
        ).first()
        
        if not workflow or workflow.status != 'active':
            return False
        
        # Проверяем, все ли задачи текущего этапа выполнены
        current_tasks = self.db.query(WorkflowTask).filter(
            WorkflowTask.workflow_id == workflow_id,
            WorkflowTask.stage_index == workflow.current_stage,
            WorkflowTask.status != 'completed'
        ).count()
        
        if current_tasks > 0:
            return False
        
        # Переходим к следующему этапу
        template = workflow.template
        if template.stages and workflow.current_stage < len(template.stages) - 1:
            workflow.current_stage += 1
            next_stage = template.stages[workflow.current_stage]
            
            # Создаем задачи для нового этапа
            self._create_stage_tasks(workflow, next_stage, workflow.current_stage)
            
            # Обновляем прогресс
            workflow.progress_percent = (workflow.current_stage / len(template.stages)) * 100
        else:
            # Процесс завершен
            workflow.status = 'completed'
            workflow.completed_at = datetime.utcnow()
            workflow.progress_percent = 100
        
        self.db.commit()
        return True
    
    # === Планировщик автоматизаций ===
    
    def run_scheduled_automations(self):
        """Запустить запланированные автоматизации"""
        now = datetime.utcnow()
        
        # Находим правила, готовые к выполнению
        rules = self.db.query(AutomationRule).filter(
            AutomationRule.is_active == True,
            AutomationRule.trigger_type == TriggerType.TIME_BASED,
            AutomationRule.next_execution_at <= now
        ).all()
        
        for rule in rules:
            logger.info(f"Executing scheduled rule: {rule.name}")
            self.execute_rule(rule.id)
    
    def process_event(self, event_type: str, event_data: Dict[str, Any]):
        """Обработать событие для event-based автоматизаций"""
        # Находим правила для данного типа события
        rules = self.db.query(AutomationRule).filter(
            AutomationRule.is_active == True,
            AutomationRule.trigger_type == TriggerType.EVENT_BASED
        ).all()
        
        for rule in rules:
            # Проверяем, подходит ли событие под условия правила
            if rule.conditions.get('event_type') == event_type:
                logger.info(f"Processing event {event_type} with rule: {rule.name}")
                self.execute_rule(rule.id, event_data)