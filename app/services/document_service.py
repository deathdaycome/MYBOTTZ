"""
Сервис для работы с документами и шаблонами
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import jinja2
import pdfkit
import uuid
import os
from decimal import Decimal

from ..database.models import Project, AdminUser
from ..database.crm_models import Client, Deal, Document, DocumentTemplate
# from ..database.crm_models import Invoice, PaymentSchedule  # TODO: Создать эти модели
from ..config.logging import get_logger

logger = get_logger(__name__)


class DocumentService:
    """Сервис для работы с документами"""
    
    def __init__(self, db: Session):
        self.db = db
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('app/templates/documents'),
            autoescape=True
        )
        self.upload_path = os.getenv("UPLOAD_PATH", "./uploads/documents")
        os.makedirs(self.upload_path, exist_ok=True)
    
    # === Шаблоны документов ===
    
    def create_template(self, template_data: Dict[str, Any], created_by: int) -> DocumentTemplate:
        """Создать новый шаблон документа"""
        template = DocumentTemplate(
            name=template_data['name'],
            type=template_data['type'],
            content=template_data['content'],
            variables=template_data.get('variables', {}),
            settings=template_data.get('settings', {}),
            is_active=template_data.get('is_active', True),
            created_by=created_by
        )
        
        self.db.add(template)
        self.db.commit()
        
        logger.info(f"Created document template: {template.name}")
        return template
    
    def get_template(self, template_id: int) -> Optional[DocumentTemplate]:
        """Получить шаблон по ID"""
        return self.db.query(DocumentTemplate).filter(
            DocumentTemplate.id == template_id,
            DocumentTemplate.is_active == True
        ).first()
    
    def get_templates_by_type(self, doc_type: str) -> List[DocumentTemplate]:
        """Получить активные шаблоны по типу"""
        return self.db.query(DocumentTemplate).filter(
            DocumentTemplate.type == doc_type,
            DocumentTemplate.is_active == True
        ).order_by(DocumentTemplate.name).all()
    
    def update_template(self, template_id: int, updates: Dict[str, Any]) -> Optional[DocumentTemplate]:
        """Обновить шаблон"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_at = datetime.utcnow()
        self.db.commit()
        
        return template
    
    def deactivate_template(self, template_id: int) -> bool:
        """Деактивировать шаблон"""
        template = self.get_template(template_id)
        if template:
            template.is_active = False
            template.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    # === Генерация документов ===
    
    def generate_document(self, template_id: int, entity_type: str, 
                         entity_id: int, created_by: int) -> Optional[Document]:
        """Генерация документа на основе шаблона"""
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template {template_id} not found")
            return None
        
        # Получаем данные для подстановки
        context = self._get_entity_context(entity_type, entity_id)
        if not context:
            logger.error(f"Entity {entity_type}:{entity_id} not found")
            return None
        
        # Добавляем системные переменные
        context.update({
            'current_date': datetime.now().strftime('%d.%m.%Y'),
            'current_datetime': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'document_number': self._generate_document_number(template.type)
        })
        
        # Рендерим контент
        try:
            jinja_template = jinja2.Template(template.content)
            rendered_content = jinja_template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return None
        
        # Создаем документ
        document = Document(
            template_id=template_id,
            type=template.type,
            number=context['document_number'],
            title=f"{template.name} - {context.get('client_name', '')}",
            content=rendered_content,
            entity_type=entity_type,
            entity_id=entity_id,
            status='draft',
            created_by=created_by
        )
        
        # Генерируем файлы
        file_paths = self._generate_files(document, template.settings)
        if file_paths:
            document.file_path = file_paths.get('pdf')
            document.settings = {'file_paths': file_paths}
        
        self.db.add(document)
        self.db.commit()
        
        logger.info(f"Generated document: {document.title}")
        return document
    
    def _get_entity_context(self, entity_type: str, entity_id: int) -> Optional[Dict[str, Any]]:
        """Получить контекст для сущности"""
        context = {}
        
        if entity_type == 'client':
            client = self.db.query(Client).filter(Client.id == entity_id).first()
            if not client:
                return None
            
            context.update({
                'client_name': client.name,
                'client_inn': client.inn,
                'client_kpp': client.kpp,
                'client_ogrn': client.ogrn,
                'client_legal_address': client.legal_address,
                'client_actual_address': client.actual_address,
                'client_phone': client.phone,
                'client_email': client.email,
                'client_bank_name': client.bank_name,
                'client_bank_bik': client.bank_bik,
                'client_bank_account': client.bank_account,
                'client_corr_account': client.correspondent_account,
                'client_director': client.director_name,
                'client_accountant': client.accountant_name
            })
            
        elif entity_type == 'deal':
            deal = self.db.query(Deal).filter(Deal.id == entity_id).first()
            if not deal:
                return None
            
            context.update({
                'deal_title': deal.title,
                'deal_amount': deal.amount,
                'deal_discount': deal.discount or 0,
                'deal_final_amount': deal.amount - (deal.discount or 0),
                'deal_prepayment': deal.prepayment_amount,
                'deal_prepayment_percent': deal.prepayment_percent,
                'deal_description': deal.description,
                'deal_requirements': deal.requirements,
                'deal_start_date': deal.start_date.strftime('%d.%m.%Y') if deal.start_date else '',
                'deal_end_date': deal.end_date.strftime('%d.%m.%Y') if deal.end_date else ''
            })
            
            # Добавляем данные клиента
            if deal.client:
                client_context = self._get_entity_context('client', deal.client_id)
                if client_context:
                    context.update(client_context)
                    
        elif entity_type == 'project':
            project = self.db.query(Project).filter(Project.id == entity_id).first()
            if not project:
                return None
            
            context.update({
                'project_title': project.title,
                'project_description': project.description,
                'project_cost': project.estimated_cost,
                'project_prepayment': project.prepayment_amount,
                'project_client_paid': project.client_paid_total,
                'project_remaining': (project.estimated_cost or 0) - (project.client_paid_total or 0),
                'project_start_date': project.start_date.strftime('%d.%m.%Y') if project.start_date else '',
                'project_end_date': project.planned_end_date.strftime('%d.%m.%Y') if project.planned_end_date else '',
                'project_status': project.status
            })
            
            # Добавляем данные клиента из сделки
            if project.deal_id:
                deal = self.db.query(Deal).filter(Deal.id == project.deal_id).first()
                if deal and deal.client:
                    client_context = self._get_entity_context('client', deal.client_id)
                    if client_context:
                        context.update(client_context)
        
        # Добавляем данные нашей компании
        context.update(self._get_company_context())
        
        return context
    
    def _get_company_context(self) -> Dict[str, Any]:
        """Получить контекст нашей компании"""
        return {
            'company_name': 'ООО "BotDev"',
            'company_inn': '7708123456',
            'company_kpp': '770801001',
            'company_ogrn': '1197746123456',
            'company_legal_address': '127055, г. Москва, ул. Новослободская, д. 23',
            'company_actual_address': '127055, г. Москва, ул. Новослободская, д. 23',
            'company_phone': '+7 (495) 123-45-67',
            'company_email': 'info@botdev.ru',
            'company_website': 'https://botdev.ru',
            'company_bank_name': 'ПАО "Сбербанк"',
            'company_bank_bik': '044525225',
            'company_bank_account': '40702810123450000000',
            'company_corr_account': '30101810400000000225',
            'company_director': 'Иванов Иван Иванович',
            'company_accountant': 'Петрова Мария Сергеевна'
        }
    
    def _generate_document_number(self, doc_type: str) -> str:
        """Генерация номера документа"""
        prefix_map = {
            'contract': 'Д',
            'invoice': 'С',
            'act': 'А',
            'offer': 'КП',
            'other': 'ДОК'
        }
        
        prefix = prefix_map.get(doc_type, 'ДОК')
        date_part = datetime.now().strftime('%Y%m%d')
        
        # Получаем последний номер за сегодня
        last_doc = self.db.query(Document).filter(
            Document.type == doc_type,
            Document.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
        ).order_by(Document.id.desc()).first()
        
        if last_doc and last_doc.number:
            try:
                last_number = int(last_doc.number.split('-')[-1])
                next_number = last_number + 1
            except:
                next_number = 1
        else:
            next_number = 1
        
        return f"{prefix}-{date_part}-{next_number:03d}"
    
    def _generate_files(self, document: Document, settings: Dict) -> Dict[str, str]:
        """Генерация файлов документа"""
        files = {}
        
        # Генерируем HTML файл
        html_filename = f"{document.number}_{uuid.uuid4().hex[:8]}.html"
        html_path = os.path.join(self.upload_path, html_filename)
        
        # Оборачиваем контент в HTML структуру
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{document.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f5f5f5; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .footer {{ margin-top: 40px; border-top: 1px solid #ddd; padding-top: 20px; }}
                .signature-block {{ margin-top: 60px; }}
                .signature-line {{ display: inline-block; width: 200px; border-bottom: 1px solid #333; }}
            </style>
        </head>
        <body>
            {document.content}
        </body>
        </html>
        """
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        files['html'] = html_path
        
        # Генерируем PDF если нужно
        if settings.get('generate_pdf', True):
            pdf_filename = f"{document.number}_{uuid.uuid4().hex[:8]}.pdf"
            pdf_path = os.path.join(self.upload_path, pdf_filename)
            
            try:
                pdfkit.from_string(html_content, pdf_path, options={
                    'page-size': 'A4',
                    'margin-top': '20mm',
                    'margin-right': '20mm',
                    'margin-bottom': '20mm',
                    'margin-left': '20mm',
                    'encoding': "UTF-8",
                    'no-outline': None
                })
                files['pdf'] = pdf_path
            except Exception as e:
                logger.error(f"Error generating PDF: {e}")
        
        return files
    
    # === Управление документами ===
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """Получить документ по ID"""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_documents(self, filters: Dict[str, Any]) -> List[Document]:
        """Получить список документов с фильтрами"""
        query = self.db.query(Document)
        
        if filters.get('type'):
            query = query.filter(Document.type == filters['type'])
        
        if filters.get('status'):
            query = query.filter(Document.status == filters['status'])
        
        if filters.get('entity_type'):
            query = query.filter(Document.entity_type == filters['entity_type'])
        
        if filters.get('entity_id'):
            query = query.filter(Document.entity_id == filters['entity_id'])
        
        if filters.get('created_by'):
            query = query.filter(Document.created_by == filters['created_by'])
        
        if filters.get('date_from'):
            query = query.filter(Document.created_at >= filters['date_from'])
        
        if filters.get('date_to'):
            query = query.filter(Document.created_at <= filters['date_to'])
        
        if filters.get('search'):
            search = f"%{filters['search']}%"
            query = query.filter(or_(
                Document.title.ilike(search),
                Document.number.ilike(search)
            ))
        
        return query.order_by(Document.created_at.desc()).all()
    
    def update_document_status(self, document_id: int, status: str, 
                              signed_at: datetime = None) -> Optional[Document]:
        """Обновить статус документа"""
        document = self.get_document(document_id)
        if not document:
            return None
        
        document.status = status
        if status == 'signed' and signed_at:
            document.signed_at = signed_at
        
        document.updated_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Document {document_id} status updated to {status}")
        return document
    
    def send_document(self, document_id: int, recipient_email: str, 
                     message: str = None) -> bool:
        """Отправить документ по email"""
        document = self.get_document(document_id)
        if not document:
            return False
        
        # TODO: Интеграция с email сервисом
        # Пока просто обновляем статус
        document.sent_at = datetime.utcnow()
        document.status = 'sent'
        
        if not document.settings:
            document.settings = {}
        
        document.settings['sent_to'] = recipient_email
        document.settings['sent_message'] = message
        
        self.db.commit()
        
        logger.info(f"Document {document_id} sent to {recipient_email}")
        return True
    
    def duplicate_document(self, document_id: int, created_by: int) -> Optional[Document]:
        """Создать копию документа"""
        original = self.get_document(document_id)
        if not original:
            return None
        
        new_doc = Document(
            template_id=original.template_id,
            type=original.type,
            number=self._generate_document_number(original.type),
            title=f"{original.title} (копия)",
            content=original.content,
            entity_type=original.entity_type,
            entity_id=original.entity_id,
            status='draft',
            created_by=created_by,
            settings=original.settings
        )
        
        self.db.add(new_doc)
        self.db.commit()
        
        return new_doc
    
    # === Массовая генерация ===
    
    def batch_generate_documents(self, template_id: int, entity_type: str,
                                entity_ids: List[int], created_by: int) -> List[Document]:
        """Массовая генерация документов"""
        documents = []
        
        for entity_id in entity_ids:
            doc = self.generate_document(template_id, entity_type, entity_id, created_by)
            if doc:
                documents.append(doc)
        
        logger.info(f"Batch generated {len(documents)} documents")
        return documents
    
    # === Предустановленные шаблоны ===
    
    def create_default_templates(self, created_by: int):
        """Создать стандартные шаблоны документов"""
        templates = [
            {
                'name': 'Договор на разработку Telegram бота',
                'type': 'contract',
                'content': self._get_telegram_bot_contract_template(),
                'variables': {
                    'required': ['client_name', 'deal_amount', 'bot_name', 'bot_description'],
                    'optional': ['deal_prepayment', 'deal_end_date', 'support_period']
                }
            },
            {
                'name': 'Договор на разработку Telegram Mini App',
                'type': 'contract',
                'content': self._get_telegram_miniapp_contract_template(),
                'variables': {
                    'required': ['client_name', 'deal_amount', 'app_name', 'app_description'],
                    'optional': ['deal_prepayment', 'deal_end_date', 'hosting_period']
                }
            },
            {
                'name': 'Договор на создание автоматизации',
                'type': 'contract', 
                'content': self._get_automation_contract_template(),
                'variables': {
                    'required': ['client_name', 'deal_amount', 'automation_description'],
                    'optional': ['deal_prepayment', 'deal_end_date', 'integration_list']
                }
            },
            {
                'name': 'Договор на разработку мобильного приложения',
                'type': 'contract',
                'content': self._get_mobile_app_contract_template(), 
                'variables': {
                    'required': ['client_name', 'deal_amount', 'app_name', 'platforms'],
                    'optional': ['deal_prepayment', 'deal_end_date', 'store_publishing']
                }
            },
            {
                'name': 'Счет на оплату',
                'type': 'invoice',
                'content': self._get_default_invoice_template(),
                'variables': {
                    'required': ['client_name', 'deal_amount'],
                    'optional': ['client_inn', 'client_kpp']
                }
            },
            {
                'name': 'Акт выполненных работ',
                'type': 'act',
                'content': self._get_default_act_template(),
                'variables': {
                    'required': ['client_name', 'project_title', 'project_cost'],
                    'optional': ['project_description']
                }
            },
            {
                'name': 'Коммерческое предложение на Telegram бота',
                'type': 'offer',
                'content': self._get_telegram_bot_offer_template(),
                'variables': {
                    'required': ['client_name', 'bot_name', 'deal_amount'],
                    'optional': ['bot_features', 'deal_requirements']
                }
            }
        ]
        
        for template_data in templates:
            existing = self.db.query(DocumentTemplate).filter(
                DocumentTemplate.name == template_data['name']
            ).first()
            
            if not existing:
                self.create_template(template_data, created_by)
    
    def _get_default_contract_template(self) -> str:
        """Шаблон договора"""
        return """
<div class="header">
    <h1>ДОГОВОР № {{ document_number }}</h1>
    <p>на разработку программного обеспечения</p>
    <p>г. Москва &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ current_date }}</p>
</div>

<p>{{ company_name }}, именуемое в дальнейшем «Исполнитель», в лице {{ company_director }}, действующего на основании Устава, с одной стороны, и {{ client_name }}, именуемое в дальнейшем «Заказчик», в лице {{ client_director }}, действующего на основании Устава, с другой стороны, заключили настоящий договор о нижеследующем:</p>

<h2>1. ПРЕДМЕТ ДОГОВОРА</h2>
<p>1.1. Исполнитель обязуется выполнить работы по разработке программного обеспечения «{{ deal_title }}» (далее – «Программное обеспечение»), а Заказчик обязуется принять и оплатить выполненные работы.</p>
<p>1.2. Описание работ: {{ deal_description }}</p>

<h2>2. СТОИМОСТЬ РАБОТ И ПОРЯДОК РАСЧЕТОВ</h2>
<p>2.1. Стоимость работ по настоящему договору составляет {{ deal_final_amount }} рублей, НДС не облагается.</p>
{% if deal_prepayment %}
<p>2.2. Заказчик производит предоплату в размере {{ deal_prepayment }} рублей в течение 3 (трех) банковских дней с момента подписания договора.</p>
<p>2.3. Окончательный расчет производится в течение 5 (пяти) банковских дней после подписания акта выполненных работ.</p>
{% else %}
<p>2.2. Оплата производится в течение 5 (пяти) банковских дней после подписания акта выполненных работ.</p>
{% endif %}

<h2>3. СРОКИ ВЫПОЛНЕНИЯ РАБОТ</h2>
<p>3.1. Срок выполнения работ: {% if deal_end_date %}до {{ deal_end_date }}{% else %}30 рабочих дней с момента получения предоплаты{% endif %}.</p>

<h2>4. ПРАВА И ОБЯЗАННОСТИ СТОРОН</h2>
<p>4.1. Исполнитель обязуется:</p>
<ul>
    <li>выполнить работы в соответствии с требованиями Заказчика;</li>
    <li>передать Заказчику исходные коды и документацию;</li>
    <li>обеспечить техническую поддержку в течение 3 месяцев.</li>
</ul>

<p>4.2. Заказчик обязуется:</p>
<ul>
    <li>предоставить необходимую информацию для выполнения работ;</li>
    <li>своевременно производить оплату;</li>
    <li>принять выполненные работы.</li>
</ul>

<h2>5. РЕКВИЗИТЫ СТОРОН</h2>
<table>
    <tr>
        <th>Исполнитель</th>
        <th>Заказчик</th>
    </tr>
    <tr>
        <td>
            {{ company_name }}<br>
            ИНН: {{ company_inn }}<br>
            КПП: {{ company_kpp }}<br>
            ОГРН: {{ company_ogrn }}<br>
            Адрес: {{ company_legal_address }}<br>
            Банк: {{ company_bank_name }}<br>
            БИК: {{ company_bank_bik }}<br>
            Р/с: {{ company_bank_account }}<br>
            К/с: {{ company_corr_account }}
        </td>
        <td>
            {{ client_name }}<br>
            ИНН: {{ client_inn }}<br>
            КПП: {{ client_kpp }}<br>
            ОГРН: {{ client_ogrn }}<br>
            Адрес: {{ client_legal_address }}<br>
            Банк: {{ client_bank_name }}<br>
            БИК: {{ client_bank_bik }}<br>
            Р/с: {{ client_bank_account }}<br>
            К/с: {{ client_corr_account }}
        </td>
    </tr>
</table>

<div class="signature-block">
    <table style="width: 100%; border: none;">
        <tr>
            <td style="width: 50%; border: none;">
                <p><strong>Исполнитель:</strong></p>
                <p>_______________ / {{ company_director }} /</p>
                <p>М.П.</p>
            </td>
            <td style="width: 50%; border: none;">
                <p><strong>Заказчик:</strong></p>
                <p>_______________ / {{ client_director }} /</p>
                <p>М.П.</p>
            </td>
        </tr>
    </table>
</div>
"""
    
    def _get_default_invoice_template(self) -> str:
        """Шаблон счета"""
        return """
<div style="border: 2px solid #000; padding: 10px; margin-bottom: 20px;">
    <table style="width: 100%; border: none;">
        <tr>
            <td style="border: none;">{{ company_bank_name }}</td>
            <td style="border: none; text-align: right;">БИК {{ company_bank_bik }}</td>
        </tr>
        <tr>
            <td colspan="2" style="border: none;">Банк получателя</td>
        </tr>
    </table>
    <table style="width: 100%; border: none; margin-top: 10px;">
        <tr>
            <td style="border: none;">ИНН {{ company_inn }}</td>
            <td style="border: none;">КПП {{ company_kpp }}</td>
            <td style="border: none; text-align: right;">Сч. № {{ company_bank_account }}</td>
        </tr>
        <tr>
            <td colspan="2" style="border: none;">{{ company_name }}</td>
            <td style="border: none;"></td>
        </tr>
        <tr>
            <td colspan="2" style="border: none;">Получатель</td>
            <td style="border: none;"></td>
        </tr>
    </table>
</div>

<h1 style="text-align: center;">Счет на оплату № {{ document_number }} от {{ current_date }}</h1>

<table style="border: none; width: 100%;">
    <tr>
        <td style="border: none;"><strong>Поставщик:</strong></td>
        <td style="border: none;">{{ company_name }}, ИНН {{ company_inn }}, {{ company_legal_address }}, тел.: {{ company_phone }}</td>
    </tr>
    <tr>
        <td style="border: none;"><strong>Покупатель:</strong></td>
        <td style="border: none;">{{ client_name }}{% if client_inn %}, ИНН {{ client_inn }}{% endif %}{% if client_legal_address %}, {{ client_legal_address }}{% endif %}</td>
    </tr>
</table>

<h2>Детализация:</h2>
<table>
    <thead>
        <tr>
            <th>№</th>
            <th>Наименование работ/услуг</th>
            <th>Кол-во</th>
            <th>Ед.</th>
            <th>Цена</th>
            <th>Сумма</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>{{ deal_title }}</td>
            <td>1</td>
            <td>усл.</td>
            <td>{{ deal_amount }}</td>
            <td>{{ deal_amount }}</td>
        </tr>
    </tbody>
</table>

<p><strong>Итого:</strong> {{ deal_amount }} руб.</p>
<p><strong>НДС:</strong> Без НДС</p>
<p><strong>Всего к оплате:</strong> {{ deal_amount }} руб.</p>

<p>Всего наименований 1, на сумму {{ deal_amount }} руб.</p>

<div class="signature-block">
    <p>Руководитель _________________ {{ company_director }}</p>
    <p>Главный бухгалтер _________________ {{ company_accountant }}</p>
</div>
"""
    
    def _get_default_act_template(self) -> str:
        """Шаблон акта выполненных работ"""
        return """
<div class="header">
    <h1>АКТ № {{ document_number }}</h1>
    <p>сдачи-приемки выполненных работ</p>
    <p>г. Москва &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ current_date }}</p>
</div>

<p>{{ company_name }}, именуемое в дальнейшем «Исполнитель», в лице {{ company_director }}, действующего на основании Устава, с одной стороны, и {{ client_name }}, именуемое в дальнейшем «Заказчик», в лице {{ client_director }}, действующего на основании Устава, с другой стороны, составили настоящий акт о нижеследующем:</p>

<p>1. Исполнитель выполнил, а Заказчик принял следующие работы:</p>

<table>
    <thead>
        <tr>
            <th>№</th>
            <th>Наименование работ</th>
            <th>Сумма, руб.</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>{{ project_title }}{% if project_description %}<br><small>{{ project_description }}</small>{% endif %}</td>
            <td>{{ project_cost }}</td>
        </tr>
    </tbody>
    <tfoot>
        <tr>
            <td colspan="2"><strong>Итого:</strong></td>
            <td><strong>{{ project_cost }}</strong></td>
        </tr>
    </tfoot>
</table>

<p>2. Вышеперечисленные работы выполнены полностью и в срок.</p>
<p>3. Заказчик претензий к качеству и объему выполненных работ не имеет.</p>
<p>4. Настоящий акт составлен в двух экземплярах, по одному для каждой из сторон.</p>

<div class="signature-block">
    <table style="width: 100%; border: none;">
        <tr>
            <td style="width: 50%; border: none;">
                <p><strong>Исполнитель:</strong></p>
                <p>{{ company_name }}</p>
                <p>{{ company_director }}</p>
                <p>_______________ /_______________/</p>
                <p>М.П.</p>
            </td>
            <td style="width: 50%; border: none;">
                <p><strong>Заказчик:</strong></p>
                <p>{{ client_name }}</p>
                <p>{{ client_director }}</p>
                <p>_______________ /_______________/</p>
                <p>М.П.</p>
            </td>
        </tr>
    </table>
</div>
"""
    
    def _get_default_offer_template(self) -> str:
        """Шаблон коммерческого предложения"""
        return """
<div style="text-align: center; margin-bottom: 40px;">
    <img src="https://botdev.ru/logo.png" style="height: 60px;">
    <h1>КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ</h1>
    <p>№ {{ document_number }} от {{ current_date }}</p>
</div>

<p><strong>Кому:</strong> {{ client_name }}</p>
<p><strong>От:</strong> {{ company_name }}</p>

<h2>Уважаемые партнеры!</h2>

<p>Компания {{ company_name }} рада предложить вам услуги по разработке: <strong>{{ deal_title }}</strong></p>

{% if deal_description %}
<h3>Описание проекта:</h3>
<p>{{ deal_description }}</p>
{% endif %}

{% if deal_requirements %}
<h3>Функциональные возможности:</h3>
<p>{{ deal_requirements }}</p>
{% endif %}

<h3>Стоимость и сроки:</h3>
<table>
    <tr>
        <td><strong>Стоимость разработки:</strong></td>
        <td>{{ deal_amount }} руб.</td>
    </tr>
    {% if deal_discount %}
    <tr>
        <td><strong>Скидка:</strong></td>
        <td>{{ deal_discount }} руб.</td>
    </tr>
    <tr>
        <td><strong>Итого:</strong></td>
        <td>{{ deal_final_amount }} руб.</td>
    </tr>
    {% endif %}
    <tr>
        <td><strong>Срок выполнения:</strong></td>
        <td>{% if deal_end_date %}до {{ deal_end_date }}{% else %}30 рабочих дней{% endif %}</td>
    </tr>
    {% if deal_prepayment %}
    <tr>
        <td><strong>Предоплата:</strong></td>
        <td>{{ deal_prepayment_percent }}% ({{ deal_prepayment }} руб.)</td>
    </tr>
    {% endif %}
</table>

<h3>Что вы получаете:</h3>
<ul>
    <li>Полностью готовое к использованию решение</li>
    <li>Исходные коды и документацию</li>
    <li>3 месяца бесплатной технической поддержки</li>
    <li>Обучение вашего персонала</li>
    <li>Гарантию на исправление ошибок в течение года</li>
</ul>

<h3>Почему стоит выбрать нас:</h3>
<ul>
    <li>Более 5 лет опыта в разработке ботов и автоматизации</li>
    <li>Команда сертифицированных специалистов</li>
    <li>Прозрачная схема работы и отчетности</li>
    <li>Гибкий подход к требованиям заказчика</li>
    <li>Соблюдение сроков и бюджета</li>
</ul>

<h3>Порядок работы:</h3>
<ol>
    <li>Заключение договора и получение предоплаты</li>
    <li>Детальный анализ требований</li>
    <li>Разработка и тестирование</li>
    <li>Демонстрация результата</li>
    <li>Внедрение и обучение</li>
    <li>Техническая поддержка</li>
</ol>

<p><strong>Данное предложение действительно в течение 14 дней.</strong></p>

<div style="margin-top: 40px; padding: 20px; background: #f5f5f5; border-radius: 10px;">
    <h3>Контакты для связи:</h3>
    <p>Телефон: {{ company_phone }}</p>
    <p>Email: {{ company_email }}</p>
    <p>Сайт: {{ company_website }}</p>
</div>

<p style="margin-top: 40px;">С уважением,<br>
{{ company_director }}<br>
Генеральный директор {{ company_name }}</p>
"""

    def _get_telegram_bot_contract_template(self) -> str:
        """Шаблон договора на разработку Telegram бота"""
        return """
<div class="header">
    <h1>ДОГОВОР № {{ document_number }}</h1>
    <p>на разработку Telegram бота</p>
    <p>г. Москва &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ current_date }}</p>
</div>

<p>{{ company_name }}, именуемое в дальнейшем «Исполнитель», в лице {{ company_director }}, действующего на основании Устава, с одной стороны, и {{ client_name }}, именуемое в дальнейшем «Заказчик», в лице {{ client_director }}, действующего на основании Устава, с другой стороны, заключили настоящий договор о нижеследующем:</p>

<h2>1. ПРЕДМЕТ ДОГОВОРА</h2>
<p>1.1. Исполнитель обязуется выполнить работы по созданию Telegram бота «{{ bot_name }}» (далее – «Бот»), а Заказчик обязуется принять и оплатить выполненные работы.</p>
<p>1.2. Описание функционала бота: {{ bot_description }}</p>
<p>1.3. Бот должен обеспечивать взаимодействие с пользователями через платформу Telegram и выполнять следующие задачи:</p>
<ul>
<li>Автоматизация общения с клиентами</li>
<li>Обработка заявок и запросов</li>
<li>Интеграция с внешними сервисами при необходимости</li>
</ul>

<h2>2. СТОИМОСТЬ РАБОТ И ПОРЯДОК РАСЧЕТОВ</h2>
<p>2.1. Стоимость работ по настоящему договору составляет {{ deal_amount }} рублей, НДС не облагается.</p>
{% if deal_prepayment %}
<p>2.2. Заказчик производит предоплату в размере {{ deal_prepayment }} рублей в течение 3 (трех) банковских дней с момента подписания договора.</p>
<p>2.3. Окончательный расчет производится в течение 5 (пяти) банковских дней после подписания акта выполненных работ.</p>
{% else %}
<p>2.2. Оплата производится в течение 5 (пяти) банковских дней после подписания акта выполненных работ.</p>
{% endif %}

<h2>3. СРОКИ ВЫПОЛНЕНИЯ РАБОТ</h2>
<p>3.1. Срок разработки бота: {% if deal_end_date %}до {{ deal_end_date }}{% else %}14 рабочих дней с момента получения предоплаты{% endif %}.</p>

<h2>4. ТЕХНИЧЕСКАЯ ПОДДЕРЖКА</h2>
<p>4.1. Исполнитель предоставляет техническую поддержку бота {% if support_period %}в течение {{ support_period }}{% else %}в течение 30 дней{% endif %} с момента сдачи работ.</p>
<p>4.2. Поддержка включает: устранение критических ошибок, консультации по работе бота.</p>

<h2>5. ПРАВА И ОБЯЗАННОСТИ СТОРОН</h2>
<p>5.1. Исполнитель обязуется:</p>
<ul>
<li>Разработать Telegram бота в соответствии с техническим заданием</li>
<li>Обеспечить стабильную работу бота на серверах Telegram</li>
<li>Предоставить исходный код и документацию</li>
<li>Провести обучение Заказчика по работе с ботом</li>
</ul>

<p>5.2. Заказчик обязуется:</p>
<ul>
<li>Своевременно производить оплату в соответствии с договором</li>
<li>Предоставить всю необходимую информацию для разработки</li>
<li>Создать и предоставить Telegram Bot Token</li>
</ul>

<h2>6. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ</h2>
<p>6.1. Все споры разрешаются путем переговоров, а при невозможности достижения согласия - в суде по месту нахождения Исполнителя.</p>
<p>6.2. Договор вступает в силу с момента подписания и действует до полного исполнения обязательств сторонами.</p>
<p>6.3. Настоящий договор составлен в двух экземплярах, имеющих одинаковую юридическую силу, по одному для каждой из сторон.</p>

<div style="margin-top: 40px; display: flex; justify-content: space-between;">
    <div style="width: 45%;">
        <h3>ИСПОЛНИТЕЛЬ:</h3>
        <p>{{ company_name }}</p>
        <p>ИНН: {{ company_inn }}</p>
        <p>Адрес: {{ company_address }}</p>
        <p>Тел.: {{ company_phone }}</p>
        <div style="margin-top: 40px;">________________ {{ company_director }}</div>
        <p style="margin-top: 5px;">М.П.</p>
    </div>
    <div style="width: 45%;">
        <h3>ЗАКАЗЧИК:</h3>
        <p>{{ client_name }}</p>
        <p>ИНН: {{ client_inn }}</p>
        <p>Адрес: {{ client_address }}</p>
        <p>Тел.: {{ client_phone }}</p>
        <div style="margin-top: 40px;">________________ {{ client_director }}</div>
        <p style="margin-top: 5px;">М.П.</p>
    </div>
</div>
"""

    def _get_telegram_miniapp_contract_template(self) -> str:
        """Шаблон договора на разработку Telegram Mini App"""
        return """
<div class="header">
    <h1>ДОГОВОР № {{ document_number }}</h1>
    <p>на разработку Telegram Mini Application</p>
    <p>г. Москва &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ current_date }}</p>
</div>

<p>{{ company_name }}, именуемое в дальнейшем «Исполнитель», в лице {{ company_director }}, действующего на основании Устава, с одной стороны, и {{ client_name }}, именуемое в дальнейшем «Заказчик», в лице {{ client_director }}, действующего на основании Устава, с другой стороны, заключили настоящий договор о нижеследующем:</p>

<h2>1. ПРЕДМЕТ ДОГОВОРА</h2>
<p>1.1. Исполнитель обязуется выполнить работы по созданию Telegram Mini Application «{{ app_name }}» (далее – «Приложение»), а Заказчик обязуется принять и оплатить выполненные работы.</p>
<p>1.2. Описание приложения: {{ app_description }}</p>
<p>1.3. Приложение должно работать внутри мессенджера Telegram и обеспечивать:</p>
<ul>
<li>Интерактивный пользовательский интерфейс</li>
<li>Интеграцию с Telegram API</li>
<li>Работу с базой данных при необходимости</li>
<li>Адаптивный дизайн для мобильных устройств</li>
</ul>

<h2>2. СТОИМОСТЬ РАБОТ И ПОРЯДОК РАСЧЕТОВ</h2>
<p>2.1. Стоимость работ по настоящему договору составляет {{ deal_amount }} рублей, НДС не облагается.</p>
{% if deal_prepayment %}
<p>2.2. Заказчик производит предоплату в размере {{ deal_prepayment }} рублей в течение 3 (трех) банковских дней с момента подписания договора.</p>
<p>2.3. Окончательный расчет производится в течение 5 (пяти) банковских дней после подписания акта выполненных работ.</p>
{% else %}
<p>2.2. Оплата производится в течение 5 (пяти) банковских дней после подписания акта выполненных работ.</p>
{% endif %}

<h2>3. СРОКИ ВЫПОЛНЕНИЯ РАБОТ</h2>
<p>3.1. Срок разработки приложения: {% if deal_end_date %}до {{ deal_end_date }}{% else %}21 рабочий день с момента получения предоплаты{% endif %}.</p>

<h2>4. ХОСТИНГ И ПОДДЕРЖКА</h2>
<p>4.1. Исполнитель обеспечивает хостинг приложения {% if hosting_period %}в течение {{ hosting_period }}{% else %}в течение 6 месяцев{% endif %} с момента сдачи работ.</p>
<p>4.2. В стоимость включены: сервер, домен, SSL-сертификат, техническая поддержка.</p>

<h2>5. ПРАВА И ОБЯЗАННОСТИ СТОРОН</h2>
<p>5.1. Исполнитель обязуется:</p>
<ul>
<li>Разработать Telegram Mini App в соответствии с техническим заданием</li>
<li>Обеспечить корректную работу на всех поддерживаемых устройствах</li>
<li>Предоставить исходный код и документацию</li>
<li>Провести тестирование и отладку</li>
</ul>

<div style="margin-top: 40px; display: flex; justify-content: space-between;">
    <div style="width: 45%;">
        <h3>ИСПОЛНИТЕЛЬ:</h3>
        <p>{{ company_name }}</p>
        <div style="margin-top: 40px;">________________ {{ company_director }}</div>
        <p style="margin-top: 5px;">М.П.</p>
    </div>
    <div style="width: 45%;">
        <h3>ЗАКАЗЧИК:</h3>
        <p>{{ client_name }}</p>
        <div style="margin-top: 40px;">________________ {{ client_director }}</div>
        <p style="margin-top: 5px;">М.П.</p>
    </div>
</div>
"""

    def _get_automation_contract_template(self) -> str:
        """Шаблон договора на создание автоматизации"""
        return """
<div class="header">
    <h1>ДОГОВОР № {{ document_number }}</h1>
    <p>на создание системы автоматизации</p>
    <p>г. Москва &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ current_date }}</p>
</div>

<p>{{ company_name }}, именуемое в дальнейшем «Исполнитель», в лице {{ company_director }}, действующего на основании Устава, с одной стороны, и {{ client_name }}, именуемое в дальнейшем «Заказчик», в лице {{ client_director }}, действующего на основании Устава, с другой стороны, заключили настоящий договор о нижеследующем:</p>

<h2>1. ПРЕДМЕТ ДОГОВОРА</h2>
<p>1.1. Исполнитель обязуется выполнить работы по созданию системы автоматизации бизнес-процессов, а Заказчик обязуется принять и оплатить выполненные работы.</p>
<p>1.2. Описание автоматизации: {{ automation_description }}</p>
{% if integration_list %}
<p>1.3. Интеграции с системами: {{ integration_list }}</p>
{% endif %}

<h2>2. СТОИМОСТЬ РАБОТ И ПОРЯДОК РАСЧЕТОВ</h2>
<p>2.1. Стоимость работ по настоящему договору составляет {{ deal_amount }} рублей, НДС не облагается.</p>
{% if deal_prepayment %}
<p>2.2. Заказчик производит предоплату в размере {{ deal_prepayment }} рублей в течение 3 (трех) банковских дней с момента подписания договора.</p>
<p>2.3. Окончательный расчет производится в течение 5 (пяти) банковских дней после подписания акта выполненных работ.</p>
{% else %}
<p>2.2. Оплата производится в течение 5 (пяти) банковских дней после подписания акта выполненных работ.</p>
{% endif %}

<h2>3. СРОКИ ВЫПОЛНЕНИЯ РАБОТ</h2>
<p>3.1. Срок создания автоматизации: {% if deal_end_date %}до {{ deal_end_date }}{% else %}30 рабочих дней с момента получения предоплаты{% endif %}.</p>

<h2>4. ПРАВА И ОБЯЗАННОСТИ СТОРОН</h2>
<p>4.1. Исполнитель обязуется:</p>
<ul>
<li>Создать систему автоматизации согласно техническому заданию</li>
<li>Настроить интеграции с внешними системами</li>
<li>Провести тестирование и отладку</li>
<li>Предоставить документацию и инструкции</li>
<li>Провести обучение сотрудников Заказчика</li>
</ul>

<div style="margin-top: 40px; display: flex; justify-content: space-between;">
    <div style="width: 45%;">
        <h3>ИСПОЛНИТЕЛЬ:</h3>
        <p>{{ company_name }}</p>
        <div style="margin-top: 40px;">________________ {{ company_director }}</div>
        <p style="margin-top: 5px;">М.П.</p>
    </div>
    <div style="width: 45%;">
        <h3>ЗАКАЗЧИК:</h3>
        <p>{{ client_name }}</p>
        <div style="margin-top: 40px;">________________ {{ client_director }}</div>
        <p style="margin-top: 5px;">М.П.</p>
    </div>
</div>
"""

    def _get_mobile_app_contract_template(self) -> str:
        """Шаблон договора на разработку мобильного приложения"""
        return """
<div class="header">
    <h1>ДОГОВОР № {{ document_number }}</h1>
    <p>на разработку мобильного приложения</p>
    <p>г. Москва &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ current_date }}</p>
</div>

<p>{{ company_name }}, именуемое в дальнейшем «Исполнитель», в лице {{ company_director }}, действующего на основании Устава, с одной стороны, и {{ client_name }}, именуемое в дальнейшем «Заказчик», в лице {{ client_director }}, действующего на основании Устава, с другой стороны, заключили настоящий договор о нижеследующем:</p>

<h2>1. ПРЕДМЕТ ДОГОВОРА</h2>
<p>1.1. Исполнитель обязуется выполнить работы по разработке мобильного приложения «{{ app_name }}» для платформ {{ platforms }}, а Заказчик обязуется принять и оплатить выполненные работы.</p>

<h2>2. СТОИМОСТЬ РАБОТ И ПОРЯДОК РАСЧЕТОВ</h2>
<p>2.1. Стоимость работ по настоящему договору составляет {{ deal_amount }} рублей, НДС не облагается.</p>
{% if store_publishing %}
<p>2.2. В стоимость включена публикация в магазинах приложений (App Store, Google Play).</p>
{% endif %}

<div style="margin-top: 40px; display: flex; justify-content: space-between;">
    <div style="width: 45%;">
        <h3>ИСПОЛНИТЕЛЬ:</h3>
        <p>{{ company_name }}</p>
        <div style="margin-top: 40px;">________________ {{ company_director }}</div>
        <p style="margin-top: 5px;">М.П.</p>
    </div>
    <div style="width: 45%;">
        <h3>ЗАКАЗЧИК:</h3>
        <p>{{ client_name }}</p>
        <div style="margin-top: 40px;">________________ {{ client_director }}</div>
        <p style="margin-top: 5px;">М.П.</p>
    </div>
</div>
"""

    def _get_telegram_bot_offer_template(self) -> str:
        """Шаблон коммерческого предложения на Telegram бота"""
        return """
<div style="text-align: center; margin-bottom: 30px;">
    <h1>КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ</h1>
    <h2>Разработка Telegram бота "{{ bot_name }}"</h2>
    <p>Дата: {{ current_date }}</p>
</div>

<p>Уважаемые представители {{ client_name }}!</p>

<p>Предлагаем вам услуги по разработке Telegram бота для автоматизации вашего бизнеса.</p>

<h2>Что вы получите:</h2>
<ul>
<li>🤖 Полностью настроенный Telegram бот</li>
<li>⚡ Автоматизация общения с клиентами</li>
<li>📊 Система сбора заявок и обратной связи</li>
<li>🔧 Интеграция с вашими системами</li>
<li>📱 Адаптивный интерфейс для всех устройств</li>
<li>🛠️ Техническая поддержка и обновления</li>
</ul>

{% if bot_features %}
<h2>Дополнительные функции:</h2>
<p>{{ bot_features }}</p>
{% endif %}

<h2>Стоимость и сроки:</h2>
<p><strong>Стоимость разработки:</strong> {{ deal_amount }} рублей</p>
<p><strong>Сроки выполнения:</strong> 10-14 рабочих дней</p>
<p><strong>Гарантия:</strong> 6 месяцев бесплатной поддержки</p>

<h2>Почему выбирают нас:</h2>
<ul>
<li>✅ Более 100 успешно реализованных проектов</li>
<li>✅ Индивидуальный подход к каждому клиенту</li>
<li>✅ Современные технологии разработки</li>
<li>✅ Прозрачные сроки и стоимость</li>
<li>✅ Поддержка после запуска</li>
</ul>

<p><strong>Данное предложение действительно в течение 14 дней.</strong></p>

<div style="margin-top: 40px; padding: 20px; background: #f5f5f5; border-radius: 10px;">
    <h3>Свяжитесь с нами:</h3>
    <p>📞 Телефон: {{ company_phone }}</p>
    <p>📧 Email: {{ company_email }}</p>
    <p>🌐 Telegram: {{ company_telegram }}</p>
</div>

<p style="margin-top: 40px;">С уважением,<br>
{{ company_director }}<br>
{{ company_name }}</p>
"""