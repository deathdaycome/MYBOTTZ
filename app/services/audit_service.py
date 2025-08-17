"""
Сервис для управления аудит-логом
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
import json
import hashlib
from contextlib import contextmanager

from ..database.audit_models import (
    AuditLog, AuditSession, AuditDataChange, AuditAlert,
    AuditReport, AuditStatistics, AuditActionType, 
    AuditEntityType
)
from ..database.models import AdminUser
from ..config.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    """Сервис для работы с аудит-логом"""
    
    def __init__(self, db: Session):
        self.db = db
        self._current_session = None
        self._current_user = None
    
    # === Контекст аудита ===
    
    @contextmanager
    def audit_context(self, user_id: int, session_id: str = None, 
                      ip_address: str = None, user_agent: str = None):
        """Контекстный менеджер для установки контекста аудита"""
        old_user = self._current_user
        old_session = self._current_session
        
        try:
            self._current_user = user_id
            self._current_session = {
                'session_id': session_id,
                'ip_address': ip_address,
                'user_agent': user_agent
            }
            yield self
        finally:
            self._current_user = old_user
            self._current_session = old_session
    
    # === Логирование действий ===
    
    def log_action(self, action_type: AuditActionType, 
                  entity_type: AuditEntityType = None,
                  entity_id: int = None,
                  entity_name: str = None,
                  description: str = None,
                  old_values: Dict = None,
                  new_values: Dict = None,
                  extra_metadata: Dict = None,
                  success: bool = True,
                  error_message: str = None,
                  duration_ms: int = None,
                  user_id: int = None,
                  session_info: Dict = None) -> AuditLog:
        """Записать действие в аудит-лог"""
        
        # Используем переданные параметры или контекст
        user_id = user_id or self._current_user
        session_info = session_info or self._current_session or {}
        
        # Получаем информацию о пользователе
        user_email = None
        user_role = None
        if user_id:
            user = self.db.query(AdminUser).filter(AdminUser.id == user_id).first()
            if user:
                user_email = user.email
                user_role = user.role.value if hasattr(user.role, 'value') else str(user.role)
        
        # Определяем измененные поля
        changed_fields = None
        if old_values and new_values:
            changed_fields = self._get_changed_fields(old_values, new_values)
        
        # Создаем запись
        audit_entry = AuditLog(
            action_type=action_type,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            ip_address=session_info.get('ip_address'),
            user_agent=session_info.get('user_agent'),
            session_id=session_info.get('session_id'),
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            extra_metadata=extra_metadata,
            success='success' if success else 'failure',
            error_message=error_message,
            duration_ms=duration_ms,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_entry)
        
        # Сохраняем детальные изменения для важных полей
        if changed_fields and entity_type:
            self._save_data_changes(audit_entry, old_values, new_values, changed_fields)
        
        # Обновляем статистику сессии
        if session_info.get('session_id'):
            self._update_session_activity(session_info['session_id'])
        
        # Проверяем на подозрительную активность
        if not success or action_type in [AuditActionType.LOGIN_FAILED, 
                                          AuditActionType.PERMISSION_REVOKE]:
            self._check_suspicious_activity(user_id, action_type, session_info)
        
        self.db.commit()
        
        logger.info(f"Audit log: {action_type.value} by user {user_id} on {entity_type.value if entity_type else 'system'}")
        
        return audit_entry
    
    def log_create(self, entity_type: AuditEntityType, entity_id: int, 
                  entity_name: str, data: Dict, **kwargs) -> AuditLog:
        """Логировать создание сущности"""
        description = f"Создан {self._get_entity_name(entity_type)} '{entity_name}'"
        return self.log_action(
            action_type=AuditActionType.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            new_values=data,
            **kwargs
        )
    
    def log_update(self, entity_type: AuditEntityType, entity_id: int,
                  entity_name: str, old_data: Dict, new_data: Dict, **kwargs) -> AuditLog:
        """Логировать обновление сущности"""
        changed_fields = self._get_changed_fields(old_data, new_data)
        description = f"Обновлен {self._get_entity_name(entity_type)} '{entity_name}'. Изменены поля: {', '.join(changed_fields)}"
        
        return self.log_action(
            action_type=AuditActionType.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            old_values=old_data,
            new_values=new_data,
            **kwargs
        )
    
    def log_delete(self, entity_type: AuditEntityType, entity_id: int,
                  entity_name: str, data: Dict = None, **kwargs) -> AuditLog:
        """Логировать удаление сущности"""
        description = f"Удален {self._get_entity_name(entity_type)} '{entity_name}'"
        return self.log_action(
            action_type=AuditActionType.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            old_values=data,
            **kwargs
        )
    
    def log_login(self, user_id: int, success: bool = True, 
                 ip_address: str = None, user_agent: str = None, **kwargs) -> AuditLog:
        """Логировать попытку входа"""
        action_type = AuditActionType.LOGIN if success else AuditActionType.LOGIN_FAILED
        description = "Успешный вход в систему" if success else "Неудачная попытка входа"
        
        return self.log_action(
            action_type=action_type,
            description=description,
            success=success,
            user_id=user_id if success else None,
            session_info={'ip_address': ip_address, 'user_agent': user_agent},
            **kwargs
        )
    
    # === Управление сессиями ===
    
    def create_session(self, user_id: int, session_id: str,
                      ip_address: str = None, user_agent: str = None) -> AuditSession:
        """Создать новую сессию"""
        # Парсим user_agent
        browser, os, device_type = self._parse_user_agent(user_agent)
        
        session = AuditSession(
            session_id=session_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            browser=browser,
            os=os,
            device_type=device_type,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            is_active='active'
        )
        
        self.db.add(session)
        self.db.commit()
        
        # Логируем вход
        self.log_login(user_id, True, ip_address, user_agent)
        
        return session
    
    def end_session(self, session_id: str, reason: str = 'logout'):
        """Завершить сессию"""
        session = self.db.query(AuditSession).filter(
            AuditSession.session_id == session_id
        ).first()
        
        if session:
            session.ended_at = datetime.utcnow()
            session.is_active = 'expired'
            session.termination_reason = reason
            
            # Логируем выход
            self.log_action(
                action_type=AuditActionType.LOGOUT,
                description=f"Завершение сессии: {reason}",
                user_id=session.user_id,
                session_info={'session_id': session_id}
            )
            
            self.db.commit()
    
    def get_active_sessions(self, user_id: int = None) -> List[AuditSession]:
        """Получить активные сессии"""
        query = self.db.query(AuditSession).filter(
            AuditSession.is_active == 'active'
        )
        
        if user_id:
            query = query.filter(AuditSession.user_id == user_id)
        
        return query.all()
    
    # === Поиск и фильтрация ===
    
    def search_logs(self, user_id: int = None, entity_type: AuditEntityType = None,
                   entity_id: int = None, action_type: AuditActionType = None,
                   date_from: datetime = None, date_to: datetime = None,
                   success_only: bool = None, limit: int = 100,
                   offset: int = 0) -> List[AuditLog]:
        """Поиск записей в аудит-логе"""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        
        if date_from:
            query = query.filter(AuditLog.timestamp >= date_from)
        
        if date_to:
            query = query.filter(AuditLog.timestamp <= date_to)
        
        if success_only is not None:
            status = 'success' if success_only else 'failure'
            query = query.filter(AuditLog.success == status)
        
        return query.order_by(desc(AuditLog.timestamp))\
                   .limit(limit).offset(offset).all()
    
    def get_entity_history(self, entity_type: AuditEntityType, 
                          entity_id: int) -> List[AuditLog]:
        """Получить историю изменений сущности"""
        return self.db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        ).order_by(desc(AuditLog.timestamp)).all()
    
    def get_user_activity(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Получить активность пользователя"""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        logs = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= date_from
        ).all()
        
        # Группируем по типам действий
        actions_by_type = {}
        for log in logs:
            action_type = log.action_type.value if log.action_type else 'unknown'
            actions_by_type[action_type] = actions_by_type.get(action_type, 0) + 1
        
        # Группируем по дням
        actions_by_day = {}
        for log in logs:
            day = log.timestamp.date().isoformat()
            actions_by_day[day] = actions_by_day.get(day, 0) + 1
        
        # Последние действия
        recent_actions = logs[:10]
        
        return {
            'total_actions': len(logs),
            'actions_by_type': actions_by_type,
            'actions_by_day': actions_by_day,
            'recent_actions': [log.to_dict() for log in recent_actions],
            'period_days': days
        }
    
    # === Статистика и отчеты ===
    
    def generate_statistics(self, date: datetime = None) -> AuditStatistics:
        """Генерировать статистику за день"""
        if not date:
            date = datetime.utcnow().date()
        
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        # Получаем все логи за день
        logs = self.db.query(AuditLog).filter(
            AuditLog.timestamp >= start_of_day,
            AuditLog.timestamp <= end_of_day
        ).all()
        
        # Считаем статистику
        stats = AuditStatistics(
            date=start_of_day,
            total_actions=len(logs),
            total_users=len(set(log.user_id for log in logs if log.user_id)),
            total_sessions=len(set(log.session_id for log in logs if log.session_id))
        )
        
        # По типам действий
        actions_by_type = {}
        for log in logs:
            action_type = log.action_type.value if log.action_type else 'unknown'
            actions_by_type[action_type] = actions_by_type.get(action_type, 0) + 1
        stats.actions_by_type = actions_by_type
        
        # По сущностям
        actions_by_entity = {}
        for log in logs:
            if log.entity_type:
                entity_type = log.entity_type.value
                actions_by_entity[entity_type] = actions_by_entity.get(entity_type, 0) + 1
        stats.actions_by_entity = actions_by_entity
        
        # Топ пользователей
        user_actions = {}
        for log in logs:
            if log.user_id:
                user_actions[log.user_id] = user_actions.get(log.user_id, 0) + 1
        
        top_users = sorted(user_actions.items(), key=lambda x: x[1], reverse=True)[:10]
        stats.top_users = [{'user_id': uid, 'actions': count} for uid, count in top_users]
        
        # Ошибки
        failed_logs = [log for log in logs if log.success != 'success']
        stats.failed_actions = len(failed_logs)
        
        error_types = {}
        for log in failed_logs:
            error_type = log.action_type.value if log.action_type else 'unknown'
            error_types[error_type] = error_types.get(error_type, 0) + 1
        stats.error_types = error_types
        
        # Производительность
        durations = [log.duration_ms for log in logs if log.duration_ms]
        if durations:
            stats.avg_duration_ms = sum(durations) // len(durations)
            stats.max_duration_ms = max(durations)
        
        # Сохраняем или обновляем
        existing = self.db.query(AuditStatistics).filter(
            AuditStatistics.date == start_of_day
        ).first()
        
        if existing:
            for key, value in stats.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
            existing.calculated_at = datetime.utcnow()
        else:
            self.db.add(stats)
        
        self.db.commit()
        
        return stats
    
    def create_report(self, name: str, report_type: str,
                     date_from: datetime, date_to: datetime,
                     filters: Dict = None, user_id: int = None) -> AuditReport:
        """Создать отчет по аудиту"""
        # Получаем данные
        logs = self.search_logs(
            date_from=date_from,
            date_to=date_to,
            limit=10000
        )
        
        # Применяем дополнительные фильтры
        if filters:
            if filters.get('user_ids'):
                logs = [log for log in logs if log.user_id in filters['user_ids']]
            if filters.get('entity_types'):
                logs = [log for log in logs if log.entity_type and log.entity_type.value in filters['entity_types']]
            if filters.get('action_types'):
                logs = [log for log in logs if log.action_type and log.action_type.value in filters['action_types']]
        
        # Формируем данные отчета
        report_data = {
            'total_records': len(logs),
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'logs': [log.to_dict() for log in logs[:1000]]  # Ограничиваем для JSON
        }
        
        # Формируем сводку
        summary = {
            'total_actions': len(logs),
            'unique_users': len(set(log.user_id for log in logs if log.user_id)),
            'success_rate': len([log for log in logs if log.success == 'success']) / len(logs) * 100 if logs else 0,
            'top_actions': self._get_top_items([log.action_type.value for log in logs if log.action_type], 5),
            'top_entities': self._get_top_items([log.entity_type.value for log in logs if log.entity_type], 5)
        }
        
        # Создаем отчет
        report = AuditReport(
            name=name,
            report_type=report_type,
            date_from=date_from,
            date_to=date_to,
            filters=filters,
            data=report_data,
            summary=summary,
            generated_by=user_id or self._current_user
        )
        
        self.db.add(report)
        self.db.commit()
        
        return report
    
    # === Безопасность ===
    
    def check_security_alerts(self) -> List[AuditAlert]:
        """Проверить наличие угроз безопасности"""
        alerts = []
        
        # Проверяем множественные неудачные попытки входа
        failed_logins = self.db.query(AuditLog).filter(
            AuditLog.action_type == AuditActionType.LOGIN_FAILED,
            AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).all()
        
        # Группируем по IP
        by_ip = {}
        for log in failed_logins:
            ip = log.ip_address or 'unknown'
            by_ip[ip] = by_ip.get(ip, 0) + 1
        
        for ip, count in by_ip.items():
            if count >= 5:
                alert = AuditAlert(
                    alert_type='multiple_failed_logins',
                    severity='high' if count >= 10 else 'medium',
                    title=f"Множественные неудачные попытки входа с IP {ip}",
                    description=f"Обнаружено {count} неудачных попыток входа за последний час",
                    ip_address=ip,
                    details={'failed_attempts': count}
                )
                self.db.add(alert)
                alerts.append(alert)
        
        # Проверяем подозрительные изменения прав
        permission_changes = self.db.query(AuditLog).filter(
            AuditLog.action_type.in_([
                AuditActionType.PERMISSION_GRANT,
                AuditActionType.PERMISSION_REVOKE,
                AuditActionType.ROLE_ASSIGN
            ]),
            AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        if len(permission_changes) > 10:
            alert = AuditAlert(
                alert_type='unusual_permission_activity',
                severity='medium',
                title="Необычная активность изменения прав",
                description=f"Обнаружено {len(permission_changes)} изменений прав за последние 24 часа",
                details={'changes_count': len(permission_changes)}
            )
            self.db.add(alert)
            alerts.append(alert)
        
        if alerts:
            self.db.commit()
        
        return alerts
    
    # === Вспомогательные методы ===
    
    def _get_changed_fields(self, old_values: Dict, new_values: Dict) -> List[str]:
        """Получить список измененных полей"""
        if not old_values or not new_values:
            return []
        
        changed = []
        all_keys = set(old_values.keys()) | set(new_values.keys())
        
        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            # Преобразуем в строки для сравнения
            if old_val != new_val:
                changed.append(key)
        
        return changed
    
    def _save_data_changes(self, audit_log: AuditLog, old_values: Dict,
                          new_values: Dict, changed_fields: List[str]):
        """Сохранить детальные изменения данных"""
        sensitive_fields = ['password', 'token', 'secret', 'api_key']
        
        for field in changed_fields:
            old_val = old_values.get(field) if old_values else None
            new_val = new_values.get(field) if new_values else None
            
            # Маскируем чувствительные данные
            is_sensitive = any(s in field.lower() for s in sensitive_fields)
            if is_sensitive:
                old_val = '***' if old_val else None
                new_val = '***' if new_val else None
            
            change = AuditDataChange(
                audit_log_id=audit_log.id,
                field_name=field,
                field_type=type(new_val).__name__ if new_val else type(old_val).__name__,
                old_value=str(old_val) if old_val is not None else None,
                new_value=str(new_val) if new_val is not None else None,
                is_sensitive='yes' if is_sensitive else 'no'
            )
            
            self.db.add(change)
    
    def _update_session_activity(self, session_id: str):
        """Обновить активность сессии"""
        session = self.db.query(AuditSession).filter(
            AuditSession.session_id == session_id
        ).first()
        
        if session:
            session.last_activity = datetime.utcnow()
            session.actions_count += 1
    
    def _check_suspicious_activity(self, user_id: int, action_type: AuditActionType,
                                  session_info: Dict):
        """Проверить подозрительную активность"""
        # Проверяем количество неудачных попыток
        if action_type == AuditActionType.LOGIN_FAILED:
            recent_failures = self.db.query(AuditLog).filter(
                AuditLog.action_type == AuditActionType.LOGIN_FAILED,
                AuditLog.ip_address == session_info.get('ip_address'),
                AuditLog.timestamp >= datetime.utcnow() - timedelta(minutes=10)
            ).count()
            
            if recent_failures >= 3:
                # Создаем оповещение
                alert = AuditAlert(
                    alert_type='brute_force_attempt',
                    severity='high' if recent_failures >= 5 else 'medium',
                    title=f"Возможная попытка перебора паролей",
                    description=f"{recent_failures} неудачных попыток входа за 10 минут",
                    user_id=user_id,
                    ip_address=session_info.get('ip_address'),
                    details={'attempts': recent_failures}
                )
                self.db.add(alert)
    
    def _parse_user_agent(self, user_agent: str) -> tuple:
        """Парсить User-Agent строку"""
        if not user_agent:
            return None, None, None
        
        browser = None
        os = None
        device_type = 'desktop'
        
        # Простой парсинг (можно заменить на библиотеку user-agents)
        ua_lower = user_agent.lower()
        
        # Определяем браузер
        if 'chrome' in ua_lower:
            browser = 'Chrome'
        elif 'firefox' in ua_lower:
            browser = 'Firefox'
        elif 'safari' in ua_lower:
            browser = 'Safari'
        elif 'edge' in ua_lower:
            browser = 'Edge'
        
        # Определяем ОС
        if 'windows' in ua_lower:
            os = 'Windows'
        elif 'mac' in ua_lower:
            os = 'macOS'
        elif 'linux' in ua_lower:
            os = 'Linux'
        elif 'android' in ua_lower:
            os = 'Android'
        elif 'ios' in ua_lower or 'iphone' in ua_lower:
            os = 'iOS'
        
        # Определяем тип устройства
        if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
            device_type = 'mobile'
        elif 'tablet' in ua_lower or 'ipad' in ua_lower:
            device_type = 'tablet'
        
        return browser, os, device_type
    
    def _get_entity_name(self, entity_type: AuditEntityType) -> str:
        """Получить человекочитаемое название сущности"""
        names = {
            AuditEntityType.USER: 'пользователь',
            AuditEntityType.CLIENT: 'клиент',
            AuditEntityType.LEAD: 'лид',
            AuditEntityType.DEAL: 'сделка',
            AuditEntityType.PROJECT: 'проект',
            AuditEntityType.TASK: 'задача',
            AuditEntityType.DOCUMENT: 'документ',
            AuditEntityType.INVOICE: 'счет',
            AuditEntityType.PAYMENT: 'платеж',
            AuditEntityType.SETTING: 'настройка',
            AuditEntityType.ROLE: 'роль',
            AuditEntityType.PERMISSION: 'разрешение',
            AuditEntityType.AUTOMATION: 'автоматизация',
            AuditEntityType.WORKFLOW: 'рабочий процесс',
            AuditEntityType.REPORT: 'отчет',
            AuditEntityType.FILE: 'файл'
        }
        return names.get(entity_type, 'объект')
    
    def _get_top_items(self, items: List, limit: int = 5) -> List[Dict]:
        """Получить топ элементов по частоте"""
        from collections import Counter
        counter = Counter(items)
        top = counter.most_common(limit)
        return [{'value': value, 'count': count} for value, count in top]
    
    # === Очистка и обслуживание ===
    
    def cleanup_old_logs(self, days: int = 90):
        """Очистить старые логи"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Удаляем старые логи
        deleted = self.db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).delete()
        
        # Удаляем старые сессии
        self.db.query(AuditSession).filter(
            AuditSession.started_at < cutoff_date
        ).delete()
        
        # Удаляем старые оповещения
        self.db.query(AuditAlert).filter(
            AuditAlert.created_at < cutoff_date,
            AuditAlert.is_resolved == 'yes'
        ).delete()
        
        self.db.commit()
        
        logger.info(f"Cleaned up {deleted} old audit logs")
        
        return deleted