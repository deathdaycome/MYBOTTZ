"""
AI Sales Assistant Service - Умный помощник продажника для Авито
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..services.openai_service import get_openai_client
from ..config.settings import settings

logger = logging.getLogger(__name__)

class AISalesService:
    """Сервис AI-продажника для Авито мессенджера"""
    
    def __init__(self):
        self.openai_client = get_openai_client()
        
        # База знаний продуктов
        self.products_knowledge = {
            "telegram_bots": {
                "name": "Telegram боты",
                "description": "Автоматизация бизнес-процессов через чат-ботов",
                "features": ["Прием заказов", "Техподдержка", "CRM интеграция", "Уведомления"],
                "price_range": "от 15,000 до 150,000 руб",
                "timeline": "2-6 недель"
            },
            "telegram_miniapps": {
                "name": "Telegram Mini Apps",
                "description": "Полноценные веб-приложения внутри Telegram",
                "features": ["Каталог товаров", "Интернет-магазин", "Бронирование", "Игры"],
                "price_range": "от 50,000 до 500,000 руб",
                "timeline": "4-12 недель"
            },
            "full_applications": {
                "name": "Полноценные приложения",
                "description": "Комплексные системы автоматизации бизнеса",
                "features": ["CRM системы", "Админ-панели", "API интеграции", "Аналитика"],
                "price_range": "от 100,000 до 1,000,000 руб",
                "timeline": "8-24 недели"
            }
        }
        
        # Шаблоны для разных сфер бизнеса
        self.industry_templates = {
            "ювелирка": {
                "pain_points": ["Сложно вести учет изделий", "Много заказов теряется", "Клиенты забывают про заказы"],
                "solutions": ["Каталог украшений в Telegram", "Автоматические уведомления", "CRM для ювелиров"],
                "examples": "каталог украшений с фото, система заказов, уведомления о готовности"
            },
            "красота": {
                "pain_points": ["Записи путаются", "Клиенты не приходят", "Сложно управлять расписанием"],
                "solutions": ["Система записи через бот", "Напоминания клиентам", "Управление расписанием"],
                "examples": "бот для записи к мастеру, система напоминаний, каталог услуг"
            },
            "ресторан": {
                "pain_points": ["Заказы теряются", "Сложная доставка", "Много звонков"],
                "solutions": ["Бот для заказов", "Система доставки", "Автоматизация кухни"],
                "examples": "меню в боте, заказ доставки, уведомления повару"
            },
            "недвижимость": {
                "pain_points": ["Много объектов", "Клиенты теряются", "Сложно показывать квартиры"],
                "solutions": ["Каталог недвижимости", "CRM для риелторов", "Виртуальные туры"],
                "examples": "поиск квартир в боте, запись на просмотр, калькулятор ипотеки"
            },
            "автомобили": {
                "pain_points": ["Много вопросов по машинам", "Клиенты долго выбирают", "Сложно вести учет"],
                "solutions": ["Каталог авто в боте", "Консультант по подбору", "CRM автосалона"],
                "examples": "подбор авто по критериям, калькулятор кредита, история машины"
            }
        }
    
    def analyze_industry(self, industry_input: str) -> Dict[str, Any]:
        """Анализирует сферу клиента и возвращает релевантную информацию"""
        industry_lower = industry_input.lower().strip()
        
        # Поиск по ключевым словам
        matched_industry = None
        for key, data in self.industry_templates.items():
            if key in industry_lower or any(word in industry_lower for word in key.split()):
                matched_industry = key
                break
        
        # Дополнительные проверки
        if not matched_industry:
            keywords_mapping = {
                "украшения": "ювелирка",
                "золото": "ювелирка", 
                "серебро": "ювелирка",
                "кольца": "ювелирка",
                "салон": "красота",
                "маникюр": "красота",
                "массаж": "красота",
                "кафе": "ресторан",
                "доставка": "ресторан",
                "еда": "ресторан",
                "квартира": "недвижимость",
                "дом": "недвижимость",
                "риелтор": "недвижимость",
                "машина": "автомобили",
                "авто": "автомобили",
                "автосалон": "автомобили"
            }
            
            for keyword, industry in keywords_mapping.items():
                if keyword in industry_lower:
                    matched_industry = industry
                    break
        
        if matched_industry:
            return {
                "industry": matched_industry,
                "data": self.industry_templates[matched_industry],
                "confidence": "high"
            }
        else:
            # Общий подход для неопознанных сфер
            return {
                "industry": "общий_бизнес",
                "data": {
                    "pain_points": ["Много рутинных процессов", "Клиенты теряются", "Сложно управлять"],
                    "solutions": ["Автоматизация через бота", "CRM система", "Уведомления клиентам"],
                    "examples": "автоматизация заказов, система уведомлений, CRM для бизнеса"
                },
                "confidence": "low"
            }

    def generate_startup_offer(self, industry: str, client_context: str = "") -> str:
        """Генерирует стартовый оффер для клиента"""
        
        industry_info = self.analyze_industry(industry)
        industry_data = industry_info["data"]
        
        system_prompt = f"""Ты - Николаев Иван, эксперт по разработке Telegram ботов и мини-приложений.
        
        ТВОЯ ЗАДАЧА: Создать мощный стартовый оффер для клиента из сферы "{industry}".
        
        ТВОИ ПРОДУКТЫ:
        - Telegram боты (автоматизация, заказы, поддержка) - от 15,000₽
        - Telegram Mini Apps (каталоги, магазины, сервисы) - от 50,000₽  
        - Полноценные приложения (CRM, админ-панели) - от 100,000₽
        
        БОЛИ КЛИЕНТА В ЭТОЙ СФЕРЕ:
        {', '.join(industry_data['pain_points'])}
        
        ТВОИ РЕШЕНИЯ:
        {', '.join(industry_data['solutions'])}
        
        ПРИМЕРЫ ДЛЯ ЭТОЙ СФЕРЫ:
        {industry_data['examples']}
        
        ТРЕБОВАНИЯ:
        1. Максимум 1000 символов
        2. Сразу зацепи болью клиента
        3. Покажи конкретную выгоду
        4. Приведи релевантный пример
        5. Предложи встречу/звонок
        6. Пиши от лица Ивана, тон - экспертный но дружелюбный
        
        КОНТЕКСТ КЛИЕНТА: {client_context}"""

        user_prompt = f"""Создай убойный стартовый оффер для клиента из сферы "{industry}". 
        
        Структура:
        1. Обращение + боль (2-3 предложения)
        2. Конкретное решение с примером (3-4 предложения) 
        3. Выгода в цифрах (1-2 предложения)
        4. Призыв к действию (1 предложение)
        
        Максимум 1000 символов, без воды!"""

        try:
            response = self.openai_client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            offer = response.choices[0].message.content.strip()
            
            logger.info(f"Generated startup offer for industry: {industry}")
            return offer
            
        except Exception as e:
            logger.error(f"Error generating startup offer: {e}")
            return self._get_fallback_offer(industry)

    def generate_sales_response(self, conversation_context: List[Dict], client_message: str, industry: str = "") -> Dict[str, Any]:
        """Генерирует предложения ответов на сообщение клиента"""
        
        # Анализируем контекст беседы
        context_summary = self._analyze_conversation_context(conversation_context)
        
        system_prompt = f"""Ты - Николаев Иван, топовый продажник Telegram решений.
        
        ТВОЯ МИССИЯ: Предложить 2-3 варианта ответа на сообщение клиента.
        
        ТВОИ ПРОДУКТЫ:
        - Telegram боты - автоматизация бизнеса (от 15,000₽)
        - Mini Apps - полноценные приложения в Telegram (от 50,000₽)
        - Веб-приложения - CRM, админки, интеграции (от 100,000₽)
        
        КОНТЕКСТ БЕСЕДЫ: {context_summary}
        СФЕРА КЛИЕНТА: {industry}
        
        ПРИНЦИПЫ ПРОДАЖ:
        1. Всегда слушай клиента и отвечай по существу
        2. Переводи разговор к болям и потребностям  
        3. Предлагай конкретные решения с примерами
        4. Используй социальные доказательства
        5. Создавай urgency когда уместно
        6. Будь экспертом, но человечным
        
        СООБЩЕНИЕ КЛИЕНТА: "{client_message}"
        
        Сгенерируй 3 варианта ответа:
        - Вариант 1: Прямой и деловой (для серьезных клиентов)
        - Вариант 2: Консультативный (выявление потребностей)  
        - Вариант 3: Кейсовый (с примером успешного проекта)
        
        Каждый ответ до 300 символов."""

        try:
            response = self.openai_client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Клиент написал: {client_message}"}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Парсим ответ на варианты
            variants = self._parse_response_variants(ai_response)
            
            return {
                "success": True,
                "variants": variants,
                "context_analysis": context_summary,
                "recommended_variant": 1  # По умолчанию рекомендуем первый
            }
            
        except Exception as e:
            logger.error(f"Error generating sales response: {e}")
            return {
                "success": True,  # Возвращаем success=True для fallback ответов
                "variants": self._get_fallback_responses(client_message),
                "context_analysis": context_summary,
                "recommended_variant": 1
            }

    def _analyze_conversation_context(self, conversation: List[Dict]) -> str:
        """Анализирует контекст беседы"""
        if not conversation:
            return "Начало беседы"
        
        # Берем последние 5 сообщений для контекста
        recent_messages = conversation[-5:]
        
        context_parts = []
        for msg in recent_messages:
            sender = "Клиент" if msg.get("is_client") else "Продажник"
            text = msg.get("text", "")[:100]  # Обрезаем длинные сообщения
            context_parts.append(f"{sender}: {text}")
        
        return " | ".join(context_parts)

    def _parse_response_variants(self, ai_response: str) -> List[Dict[str, str]]:
        """Парсит ответ AI на варианты"""
        variants = []
        
        # Ищем пронумерованные варианты
        lines = ai_response.split('\n')
        current_variant = {"title": "", "text": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Новый вариант
            if any(marker in line for marker in ["Вариант 1:", "Вариант 2:", "Вариант 3:"]):
                if current_variant["text"]:
                    variants.append(current_variant.copy())
                
                current_variant = {
                    "title": line.replace("Вариант", "").replace(":", "").strip(),
                    "text": ""
                }
            else:
                # Добавляем к текущему варианту
                if current_variant["title"]:
                    current_variant["text"] += line + " "
        
        # Добавляем последний вариант
        if current_variant["text"]:
            variants.append(current_variant)
        
        # Если парсинг не удался, создаем один вариант
        if not variants:
            variants = [{
                "title": "Предложенный ответ",
                "text": ai_response[:300]
            }]
            
        return variants

    def _get_fallback_offer(self, industry: str) -> str:
        """Резервный оффер при ошибке AI"""
        return f"""Привет! Иван Николаев, разрабатываю Telegram решения для бизнеса.
        
Вижу, вы в сфере "{industry}". Обычно у таких клиентов проблемы с автоматизацией заказов и общением с клиентами.
        
Могу предложить Telegram бота, который:
✅ Принимает заказы 24/7
✅ Уведомляет клиентов автоматически  
✅ Ведет базу клиентов
✅ Экономит 5-10 часов в неделю
        
Стоимость от 15,000₽, срок 2-3 недели.
        
Можем обсудить детали? Звоните: +7-XXX-XXX-XX-XX"""

    def _get_fallback_responses(self, client_message: str) -> List[Dict[str, str]]:
        """Резервные ответы при ошибке AI"""
        
        # Анализируем сообщение клиента для персонализации
        message_lower = client_message.lower()
        
        if "цена" in message_lower or "стоимость" in message_lower:
            return [
                {
                    "title": "1 Прямой и деловой",
                    "text": "Стоимость зависит от функций. Telegram бот от 15,000₽, Mini App от 50,000₽. Можем обсудить ваш проект?"
                },
                {
                    "title": "2 Консультативный",
                    "text": "Чтобы дать точную оценку, расскажите какие задачи нужно решить? Готов провести бесплатную консультацию."
                },
                {
                    "title": "3 Кейсовый",
                    "text": "Недавно делал бот для ювелирки за 35,000₽ - автоматизировал заказы и уведомления. Экономит 10 часов в неделю."
                }
            ]
        elif "срок" in message_lower or "время" in message_lower:
            return [
                {
                    "title": "1 Прямой и деловой",
                    "text": "Обычно 2-4 недели в зависимости от сложности. Можем начать в ближайшие дни, если проект срочный."
                },
                {
                    "title": "2 Консультативный",
                    "text": "Сроки зависят от количества функций. Расскажите подробнее о проекте - составлю точный план."
                },
                {
                    "title": "3 Кейсовый",
                    "text": "Последний бот сделал за 10 дней - клиент был в восторге от скорости. У вас есть срочность по проекту?"
                }
            ]
        else:
            return [
                {
                    "title": "1 Прямой и деловой",
                    "text": "Понял вашу потребность! Разрабатываю боты для автоматизации бизнеса. Можем обсудить детали вашего проекта?"
                },
                {
                    "title": "2 Консультативный",
                    "text": "Интересная задача! Расскажите подробнее: какие процессы хотите автоматизировать? Сколько клиентов в день?"
                },
                {
                    "title": "3 Кейсовый",
                    "text": "Похожий проект делал для салона красоты - результат отличный! Хотите посмотреть примеры работ?"
                }
            ]

    def get_industry_suggestions(self, partial_input: str = "") -> List[str]:
        """Возвращает подсказки по сферам бизнеса"""
        if not partial_input:
            return list(self.industry_templates.keys())
        
        partial_lower = partial_input.lower()
        suggestions = []
        
        for industry in self.industry_templates.keys():
            if partial_lower in industry or industry.startswith(partial_lower):
                suggestions.append(industry)
                
        return suggestions or ["общий_бизнес", "интернет_магазин", "услуги"]

# Singleton instance
ai_sales_service = AISalesService()

def get_ai_sales_service() -> AISalesService:
    """Получить экземпляр AI Sales Service"""
    return ai_sales_service