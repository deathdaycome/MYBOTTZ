"""
Сервис для интеграции разделов CRM между собой
Лид → Сделка → Клиент → Проект → Финансы
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from ..database.models import Project, FinanceTransaction, FinanceCategory
    from ..database.crm_models import Lead, Client, Deal, LeadStatus, DealStatus, ClientStatus
except ImportError as e:
    # Логируем ошибку, но не падаем
    import logging
    logging.error(f"IntegrationService: Ошибка импорта моделей: {e}")
from ..config.logging import get_logger

logger = get_logger(__name__)

class IntegrationService:
    def __init__(self, db: Session):
        self.db = db

    def convert_lead_to_deal(
        self,
        lead_id: int,
        deal_data: Dict[str, Any],
        current_user_id: int
    ) -> Dict[str, Any]:
        """
        Конвертирует лид в сделку
        """
        try:
            # Получаем лид
            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return {"success": False, "error": "Лид не найден"}
            
            # Проверяем, что лид можно конвертировать
            if lead.status != LeadStatus.WON:
                # Обновляем статус лида на "выиграно"
                lead.status = LeadStatus.WON
                lead.converted_at = datetime.utcnow()
            
            # Создаем или получаем клиента
            client = None
            if lead.client_id:
                client = self.db.query(Client).filter(Client.id == lead.client_id).first()
            else:
                # Создаем нового клиента из данных лида
                client = Client(
                    name=lead.contact_name or lead.company_name or "Клиент",
                    type="company" if lead.company_name else "individual",
                    phone=lead.contact_phone,
                    email=lead.contact_email,
                    telegram=lead.contact_telegram,
                    company_name=lead.company_name,
                    website=lead.company_website,
                    address=lead.company_address,
                    source=lead.source,
                    status=ClientStatus.NEW,
                    created_at=datetime.utcnow()
                )
                self.db.add(client)
                self.db.flush()
                
                # Обновляем лид с привязкой к клиенту
                lead.client_id = client.id
            
            # Создаем сделку
            deal = Deal(
                title=deal_data.get("title", lead.title),
                client_id=client.id,
                amount=deal_data.get("amount", lead.budget),
                currency="RUB",
                status=DealStatus.NEW,
                probability=deal_data.get("probability", lead.probability or 50),
                description=deal_data.get("description", lead.description),
                expected_close_date=deal_data.get("expected_close_date", lead.expected_close_date),
                source_lead_id=lead.id,
                created_by_id=current_user_id,
                created_at=datetime.utcnow()
            )
            
            self.db.add(deal)
            self.db.flush()
            
            # Обновляем лид
            lead.converted_to_deal_id = deal.id
            
            self.db.commit()
            
            logger.info(f"Лид {lead_id} успешно конвертирован в сделку {deal.id}")
            
            return {
                "success": True,
                "data": {
                    "deal_id": deal.id,
                    "client_id": client.id,
                    "lead_id": lead.id
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка конвертации лида в сделку: {e}")
            return {"success": False, "error": str(e)}

    def convert_deal_to_project(
        self,
        deal_id: int,
        project_data: Dict[str, Any],
        current_user_id: int
    ) -> Dict[str, Any]:
        """
        Конвертирует сделку в проект
        """
        try:
            # Получаем сделку
            deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
            if not deal:
                return {"success": False, "error": "Сделка не найдена"}
            
            # Проверяем статус сделки
            if deal.status not in [DealStatus.CONTRACT_SIGNED, DealStatus.PREPAYMENT]:
                return {"success": False, "error": "Сделка должна иметь статус 'договор подписан' или 'предоплата'"}
            
            # Получаем клиента
            client = self.db.query(Client).filter(Client.id == deal.client_id).first()
            if not client:
                return {"success": False, "error": "Клиент не найден"}
            
            # Создаем проект
            project = Project(
                title=project_data.get("title", deal.title),
                description=project_data.get("description", deal.description),
                technical_specification=project_data.get("technical_specification", ""),
                status=project_data.get("status", "new"),
                complexity=project_data.get("complexity", "medium"),
                estimated_cost=deal.amount,
                final_cost=deal.amount,
                estimated_hours=project_data.get("estimated_hours"),
                deadline=project_data.get("deadline", deal.expected_close_date),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                source_deal_id=deal.id
            )
            
            # Привязываем к пользователю (если есть telegram_id у клиента)
            if hasattr(client, 'telegram_id') and client.telegram_id:
                from ..database.models import User
                user = self.db.query(User).filter(User.telegram_id == client.telegram_id).first()
                if user:
                    project.user_id = user.id
            
            # Назначаем исполнителя
            if project_data.get("assigned_executor_id"):
                project.assigned_executor_id = project_data["assigned_executor_id"]
            
            self.db.add(project)
            self.db.flush()
            
            # Обновляем сделку
            deal.converted_to_project_id = project.id
            deal.status = DealStatus.IN_WORK
            
            # Активируем клиента
            if client.status == ClientStatus.NEW:
                client.status = ClientStatus.ACTIVE
            
            self.db.commit()
            
            logger.info(f"Сделка {deal_id} успешно конвертирована в проект {project.id}")
            
            return {
                "success": True,
                "data": {
                    "project_id": project.id,
                    "deal_id": deal.id,
                    "client_id": client.id
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка конвертации сделки в проект: {e}")
            return {"success": False, "error": str(e)}

    def create_project_income_transaction(
        self,
        project_id: int,
        amount: float,
        description: str,
        current_user_id: int,
        account: str = "card",
        payment_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Создает финансовую транзакцию дохода от проекта
        """
        try:
            # Получаем проект
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return {"success": False, "error": "Проект не найден"}
            
            # Ищем категорию "Доходы от проектов" или создаем её
            income_category = self.db.query(FinanceCategory).filter(
                FinanceCategory.name == "Доходы от проектов",
                FinanceCategory.type == "income"
            ).first()
            
            if not income_category:
                income_category = FinanceCategory(
                    name="Доходы от проектов",
                    type="income",
                    description="Доходы от выполненных проектов",
                    color="#4caf50",
                    icon="fas fa-project-diagram",
                    created_by_id=current_user_id,
                    created_at=datetime.utcnow()
                )
                self.db.add(income_category)
                self.db.flush()
            
            # Создаем транзакцию
            transaction = FinanceTransaction(
                amount=amount,
                type="income",
                description=f"{description} (Проект: {project.title})",
                date=payment_date or datetime.utcnow(),
                category_id=income_category.id,
                project_id=project_id,
                account=account,
                created_by_id=current_user_id,
                created_at=datetime.utcnow()
            )
            
            self.db.add(transaction)
            
            # Обновляем проект (добавляем к оплаченной сумме)
            if not hasattr(project, 'paid_amount'):
                project.paid_amount = 0
            project.paid_amount = (project.paid_amount or 0) + amount
            project.updated_at = datetime.utcnow()
            
            # Если проект полностью оплачен, обновляем статус
            if project.paid_amount >= project.final_cost:
                project.status = "completed"
            
            self.db.commit()
            
            logger.info(f"Создана транзакция дохода {amount}₽ для проекта {project_id}")
            
            return {
                "success": True,
                "data": {
                    "transaction_id": transaction.id,
                    "project_id": project_id,
                    "amount": amount
                }
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка создания транзакции дохода: {e}")
            return {"success": False, "error": str(e)}

    def get_integration_chain(self, entity_type: str, entity_id: int) -> Dict[str, Any]:
        """
        Получает цепочку интеграции для сущности
        Лид → Сделка → Проект → Транзакции
        """
        try:
            result = {
                "success": True,
                "data": {
                    "lead": None,
                    "deal": None,
                    "client": None,
                    "project": None,
                    "transactions": []
                }
            }
            
            if entity_type == "lead":
                lead = self.db.query(Lead).filter(Lead.id == entity_id).first()
                if lead:
                    result["data"]["lead"] = self._serialize_lead(lead)
                    
                    # Связанная сделка
                    if lead.converted_to_deal_id:
                        deal = self.db.query(Deal).filter(Deal.id == lead.converted_to_deal_id).first()
                        if deal:
                            result["data"]["deal"] = self._serialize_deal(deal)
                            
                            # Связанный проект
                            if hasattr(deal, 'converted_to_project_id') and deal.converted_to_project_id:
                                project = self.db.query(Project).filter(Project.id == deal.converted_to_project_id).first()
                                if project:
                                    result["data"]["project"] = self._serialize_project(project)
                                    
                                    # Связанные транзакции
                                    transactions = self.db.query(FinanceTransaction).filter(
                                        FinanceTransaction.project_id == project.id
                                    ).all()
                                    result["data"]["transactions"] = [self._serialize_transaction(t) for t in transactions]
                    
                    # Клиент
                    if lead.client_id:
                        client = self.db.query(Client).filter(Client.id == lead.client_id).first()
                        if client:
                            result["data"]["client"] = self._serialize_client(client)
            
            elif entity_type == "deal":
                deal = self.db.query(Deal).filter(Deal.id == entity_id).first()
                if deal:
                    result["data"]["deal"] = self._serialize_deal(deal)
                    
                    # Связанный лид
                    if deal.source_lead_id:
                        lead = self.db.query(Lead).filter(Lead.id == deal.source_lead_id).first()
                        if lead:
                            result["data"]["lead"] = self._serialize_lead(lead)
                    
                    # Клиент
                    client = self.db.query(Client).filter(Client.id == deal.client_id).first()
                    if client:
                        result["data"]["client"] = self._serialize_client(client)
            
            elif entity_type == "project":
                project = self.db.query(Project).filter(Project.id == entity_id).first()
                if project:
                    result["data"]["project"] = self._serialize_project(project)
                    
                    # Связанные транзакции
                    transactions = self.db.query(FinanceTransaction).filter(
                        FinanceTransaction.project_id == project.id
                    ).all()
                    result["data"]["transactions"] = [self._serialize_transaction(t) for t in transactions]
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка получения цепочки интеграции: {e}")
            return {"success": False, "error": str(e)}

    def _serialize_lead(self, lead: Lead) -> Dict[str, Any]:
        """Сериализация лида"""
        return {
            "id": lead.id,
            "title": lead.title,
            "status": lead.status.value,
            "source": lead.source,
            "source_type": lead.source_type,
            "company_name": lead.company_name,
            "contact_name": lead.contact_name,
            "contact_phone": lead.contact_phone,
            "contact_email": lead.contact_email,
            "budget": lead.budget,
            "probability": lead.probability,
            "created_at": lead.created_at.isoformat() if lead.created_at else None
        }

    def _serialize_deal(self, deal: Deal) -> Dict[str, Any]:
        """Сериализация сделки"""
        return {
            "id": deal.id,
            "title": deal.title,
            "status": deal.status.value,
            "amount": deal.amount,
            "probability": deal.probability,
            "created_at": deal.created_at.isoformat() if deal.created_at else None
        }

    def _serialize_client(self, client: Client) -> Dict[str, Any]:
        """Сериализация клиента"""
        return {
            "id": client.id,
            "name": client.name,
            "type": client.type.value,
            "status": client.status.value,
            "phone": client.phone,
            "email": client.email,
            "company_name": client.company_name,
            "created_at": client.created_at.isoformat() if client.created_at else None
        }

    def _serialize_project(self, project: Project) -> Dict[str, Any]:
        """Сериализация проекта"""
        return {
            "id": project.id,
            "title": project.title,
            "status": project.status,
            "estimated_cost": project.estimated_cost,
            "final_cost": project.final_cost,
            "paid_amount": getattr(project, 'paid_amount', 0),
            "created_at": project.created_at.isoformat() if project.created_at else None
        }

    def _serialize_transaction(self, transaction: FinanceTransaction) -> Dict[str, Any]:
        """Сериализация транзакции"""
        return {
            "id": transaction.id,
            "amount": transaction.amount,
            "type": transaction.type,
            "description": transaction.description,
            "account": transaction.account,
            "date": transaction.date.isoformat() if transaction.date else None,
            "category": transaction.category.name if transaction.category else None
        }