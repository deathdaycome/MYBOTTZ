import openai
import httpx
import json
import time
import re
from typing import Dict, Any, Optional, List
from ..config.settings import settings
from ..config.logging import get_logger, log_api_call, log_error

logger = get_logger(__name__)

class OpenAIService:
    """Сервис для работы с OpenAI API через OpenRouter"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL if settings.OPENROUTER_API_KEY else "https://api.openai.com/v1"
        self.default_model = settings.DEFAULT_MODEL
        
        # Настройка клиента
        if settings.OPENROUTER_API_KEY:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    async def generate_response(self, prompt: str, user_id: int = None, system_prompt: str = None) -> str:
        """Базовый метод для генерации ответов от AI"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            response_time = time.time() - start_time
            
            ai_response = response.choices[0].message.content
            
            log_api_call("OpenAI", "generate_response", True, response_time)
            logger.info(f"Ответ AI получен за {response_time:.2f}с для пользователя {user_id}")
            
            return ai_response
            
        except Exception as e:
            log_api_call("OpenAI", "generate_response", False)
            log_error(e, "generate_response")
            logger.error(f"Ошибка при генерации ответа: {e}")
            return None

    async def create_technical_specification(self, user_request: str, additional_context: Dict = None) -> Dict[str, Any]:
        """Создание технического задания на основе пользовательского запроса"""
        
        system_prompt = """
        Ты - эксперт по созданию технических заданий для разработки Telegram-ботов и автоматизации.
        
        ВАЖНО: Создавай МАКСИМАЛЬНО ПОДРОБНЫЕ технические задания в текстовом формате.
        
        Структура ответа:
        📋 НАЗВАНИЕ ПРОЕКТА
        [Краткое название проекта]
        
        📝 ОПИСАНИЕ ПРОЕКТА
        [Подробное описание проекта минимум 3-4 предложения]
        
        🎯 ЦЕЛИ И ЗАДАЧИ
        [Детальные цели и задачи проекта]
        
        👥 ЦЕЛЕВАЯ АУДИТОРИЯ
        [Подробное описание целевой аудитории]
        
        ⚙️ ОСНОВНЫЕ ФУНКЦИИ
        [Подробный список всех функций с описанием]
        
        🔧 ТЕХНИЧЕСКИЙ СТЕК
        [Технологии: Python, aiogram/python-telegram-bot, PostgreSQL, etc.]
        
        🔗 ИНТЕГРАЦИИ
        [Необходимые интеграции с внешними системами]
        
        📊 АДМИН-ПАНЕЛЬ
        [Требования к админ-панели если нужна]
        
        📈 ЭТАПЫ РАЗРАБОТКИ
        [Поэтапный план разработки]
        
        ⚠️ РИСКИ И СЛОЖНОСТИ
        [Возможные сложности и способы их решения]
        
        ⏱️ ВРЕМЕННЫЕ РАМКИ
        [Оценка времени разработки]
        
        💰 ПРИМЕРНАЯ СТОИМОСТЬ
        [Оценка стоимости с обоснованием]
        
        🚀 MVP ФУНКЦИИ
        [Функции для первой версии]
        
        ➕ ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ
        [Функции для будущих версий]
        
        ОБЯЗАТЕЛЬНО:
        1. Детально расписывай каждую функцию бота
        2. Указывай реалистичные сроки и стоимость
        3. Описывай технические сложности
        4. Предлагай конкретный стек технологий
        5. Анализируй что может быть проблемным в разработке
        6. Расписывай пользовательские сценарии
        7. Делай ТЗ максимально информативным
        """
        
        user_prompt = f"""
        Запрос пользователя: {user_request}
        
        Дополнительный контекст: {additional_context or {}}
        
        Создай подробное техническое задание в указанном формате.
        """
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            response_time = time.time() - start_time
            
            # Получаем текстовое ТЗ
            tz_text = response.choices[0].message.content
            logger.info(f"Получено ТЗ от OpenAI длиной {len(tz_text)} символов")
            
            # Парсим текст и создаем структуру данных
            tz_data = self._parse_text_tz_to_dict(tz_text, user_request)
            
            # Рассчитываем стоимость
            cost_estimation = self._calculate_project_cost(tz_data)
            tz_data.update(cost_estimation)
            
            log_api_call("OpenAI", "create_tz", True, response_time)
            logger.info(f"ТЗ создано успешно за {response_time:.2f}с")
            
            return tz_data
            
        except Exception as e:
            log_api_call("OpenAI", "create_tz", False)
            log_error(e, "create_technical_specification")
            
            # В случае ошибки возвращаем подробное fallback ТЗ
            logger.warning("Создаем fallback ТЗ из-за ошибки API")
            return self._create_detailed_fallback_tz(user_request)
    
    async def consultant_response(self, user_query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Получение ответа от AI-консультанта"""
        
        system_prompt = getattr(settings, 'CONSULTANT_SYSTEM_PROMPT', """
        Ты - эксперт по разработке ботов и автоматизации бизнеса.
        Помогай пользователям с техническими вопросами, выбором технологий, архитектурой решений.
        """) + """
        
        Дополнительные инструкции:
        - Отвечай конкретно и по делу
        - Давай практические советы
        - Если нужно, приводи примеры кода или конфигураций
        - Учитывай контекст предыдущих сообщений
        - Будь дружелюбным, но профессиональным
        - Если вопрос не по теме разработки ботов, вежливо перенаправь на специализированные темы
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем историю разговора если есть
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Последние 10 сообщений
        
        messages.append({"role": "user", "content": user_query})
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=getattr(settings, 'CONSULTANT_TEMPERATURE', 0.7),
                max_tokens=getattr(settings, 'CONSULTANT_MAX_TOKENS', 1500)
            )
            
            response_time = time.time() - start_time
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0;
            
            log_api_call("OpenAI", "consultant", True, response_time)
            logger.info(f"Ответ консультанта получен за {response_time:.2f}с, токенов: {tokens_used}")
            
            return {
                "response": ai_response,
                "tokens_used": tokens_used,
                "response_time": response_time
            }
            
        except Exception as e:
            log_api_call("OpenAI", "consultant", False)
            log_error(e, "consultant_response")
            raise
    
    async def improve_technical_specification(self, current_tz: Dict, user_feedback: str) -> Dict[str, Any]:
        """Улучшение существующего ТЗ на основе обратной связи"""
        
        system_prompt = """
        Улучши существующее техническое задание на основе обратной связи пользователя.
        Сохрани структуру JSON, но обнови соответствующие поля.
        """
        
        user_prompt = f"""
        Текущее ТЗ: {json.dumps(current_tz, ensure_ascii=False, indent=2)}
        
        Обратная связь пользователя: {user_feedback}
        
        Обнови ТЗ с учетом пожеланий.
        """
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_time = time.time() - start_time
            
            content = response.choices[0].message.content
            
            try:
                updated_tz = json.loads(content)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    updated_tz = json.loads(json_match.group())
                else:
                    raise ValueError("Не удалось извлечь JSON из ответа")
            
            # Пересчитываем стоимость
            cost_estimation = self._calculate_project_cost(updated_tz)
            updated_tz.update(cost_estimation)
            
            log_api_call("OpenAI", "improve_tz", True, response_time)
            
            return updated_tz
            
        except Exception as e:
            log_api_call("OpenAI", "improve_tz", False)
            log_error(e, "improve_technical_specification")
            raise
    
    async def analyze_uploaded_document(self, document_text: str) -> Dict[str, Any]:
        """Анализ загруженного документа и извлечение требований"""
        
        system_prompt = """
        Проанализируй загруженный документ и извлеки из него техническое задание для разработки бота.
        
        Верни результат в том же JSON формате, что и для создания ТЗ с нуля.
        Если в документе недостаточно информации, укажи это в соответствующих полях.
        """
        
        user_prompt = f"""
        Содержимое документа:
        {document_text}
        
        Извлеки и структурируй техническое задание.
        """
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_time = time.time() - start_time
            
            content = response.choices[0].message.content
            
            try:
                tz_data = json.loads(content)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    tz_data = json.loads(json_match.group())
                else:
                    raise ValueError("Не удалось извлечь JSON из ответа")
            
            cost_estimation = self._calculate_project_cost(tz_data)
            tz_data.update(cost_estimation)
            
            log_api_call("OpenAI", "analyze_document", True, response_time)
            
            return tz_data
            
        except Exception as e:
            log_api_call("OpenAI", "analyze_document", False)
            log_error(e, "analyze_uploaded_document")
            raise
    
    def _calculate_project_cost(self, tz_data: Dict) -> Dict[str, Any]:
        """Реалистичный расчет стоимости проекта на основе ТЗ"""
        
        # Получаем сложность и часы
        complexity = tz_data.get("complexity", "medium")
        
        # Считаем часы более точно
        estimated_hours = 0
        
        # Часы из детальных функций
        for func in tz_data.get("detailed_functions", []):
            estimated_hours += func.get("estimated_hours", 5)
        
        # Часы из разделов бота
        for section in tz_data.get("bot_sections", []):
            estimated_hours += section.get("estimated_hours", 8)
        
        # Часы из интеграций
        for integration in tz_data.get("integrations", []):
            estimated_hours += integration.get("estimated_hours", 3)
        
        # Часы админ панели
        admin_panel = tz_data.get("admin_panel_requirements", {})
        if admin_panel.get("needed", False):
            estimated_hours += admin_panel.get("estimated_hours", 15)
        
        # Если часы не посчитались из структуры, берем из общего поля
        if estimated_hours == 0:
            estimated_hours = tz_data.get("estimated_hours", 40)
        
        # Базовая стоимость (реалистичная)
        base_hourly_rate = 1500  # 1500₽ за час - реалистичная ставка
        base_cost = estimated_hours * base_hourly_rate
        
        # Реалистичные коэффициенты сложности
        complexity_multipliers = {
            'simple': 1.0,      # Простые боты
            'medium': 1.2,      # Средней сложности
            'complex': 1.5,     # Сложные с интеграциями
            'premium': 2.0      # Очень сложные enterprise решения
        }
        complexity_multiplier = complexity_multipliers.get(complexity, 1.2)
        
        # Основная стоимость
        total_cost = base_cost * complexity_multiplier
        
        # Дополнительные расходы
        integrations_count = len(tz_data.get("integrations", []))
        integration_cost = integrations_count * 3000  # 3000₽ за интеграцию
        
        # Минимальная стоимость проекта
        minimum_cost = 15000
        
        # Итоговая стоимость
        final_cost = max(total_cost + integration_cost, minimum_cost)
        
        # Округляем до тысяч
        final_cost = round(final_cost / 1000) * 1000
        
        # Диапазон ±15%
        min_cost = int(final_cost * 0.85)
        max_cost = int(final_cost * 1.15)
        
        return {
            "estimated_cost": int(final_cost),
            "cost_range": f"{min_cost:,}-{max_cost:,}".replace(",", " "),
            "estimated_hours": estimated_hours,
            "hourly_rate": base_hourly_rate,
            "complexity_multiplier": complexity_multiplier,
            "integration_cost": integration_cost,
            "base_cost": int(base_cost),
            "cost_breakdown": {
                "development": int(base_cost * complexity_multiplier),
                "integrations": integration_cost,
                "total": int(final_cost)
            }
        }
    
    def _parse_text_tz_to_dict(self, tz_text: str, user_request: str) -> Dict[str, Any]:
        """Парсинг текстового ТЗ в словарь для дальнейшей обработки"""
        
        # Простой парсинг секций по эмодзи
        sections = {}
        
        # Извлекаем название проекта
        title_match = re.search(r'📋 НАЗВАНИЕ ПРОЕКТА\s*\n([^\n]+)', tz_text)
        title = title_match.group(1).strip() if title_match else f"Проект: {user_request[:50]}..."
        
        # Извлекаем описание
        desc_match = re.search(r'📝 ОПИСАНИЕ ПРОЕКТА\s*\n(.*?)(?=\n[🎯👥⚙️🔧🔗📊📈⚠️⏱️💰🚀➕]|$)', tz_text, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else "Детальное описание проекта будет дополнено при обсуждении."
        
        # Извлекаем цели
        goals_match = re.search(r'🎯 ЦЕЛИ И ЗАДАЧИ\s*\n(.*?)(?=\n[👥⚙️🔧🔗📊📈⚠️⏱️💰🚀➕]|$)', tz_text, re.DOTALL)
        goals = goals_match.group(1).strip() if goals_match else "Цели и задачи будут уточнены."
        
        # Извлекаем функции
        functions_match = re.search(r'⚙️ ОСНОВНЫЕ ФУНКЦИИ\s*\n(.*?)(?=\n[🔧🔗📊📈⚠️⏱️💰🚀➕]|$)', tz_text, re.DOTALL)
        functions_text = functions_match.group(1).strip() if functions_match else ""
        
        # Парсим функции в список
        functions = []
        if functions_text:
            # Ищем строки начинающиеся с - или • или цифр
            function_lines = re.findall(r'(?:^|\n)[-•\d\.]\s*([^\n]+)', functions_text, re.MULTILINE)
            functions = [f.strip() for f in function_lines if f.strip()]
        
        # Если функций нет, добавляем базовые
        if not functions:
            functions = ["Базовая функциональность бота", "Обработка команд пользователя", "Интерфейс взаимодействия"]
        
        # Извлекаем технический стек
        tech_match = re.search(r'🔧 ТЕХНИЧЕСКИЙ СТЕК\s*\n(.*?)(?=\n[🔗📊📈⚠️⏱️💰🚀➕]|$)', tz_text, re.DOTALL)
        tech_text = tech_match.group(1).strip() if tech_match else "Python, aiogram, PostgreSQL"
        
        # Извлекаем интеграции
        integrations_match = re.search(r'🔗 ИНТЕГРАЦИИ\s*\n(.*?)(?=\n[📊📈⚠️⏱️💰🚀➕]|$)', tz_text, re.DOTALL)
        integrations_text = integrations_match.group(1).strip() if integrations_match else ""
        
        # Определяем сложность на основе текста
        complexity = "medium"
        if any(word in tz_text.lower() for word in ["сложн", "premium", "enterprise", "интеграц"]):
            complexity = "complex"
        elif any(word in tz_text.lower() for word in ["простой", "базов", "минимальн"]):
            complexity = "simple"
        
        # Оценка часов на основе количества функций
        estimated_hours = max(len(functions) * 8, 24)  # Минимум 24 часа
        
        return {
            "title": title,
            "description": description,
            "goals": goals,
            "target_audience": "Целевая аудитория определяется исходя из специфики проекта",
            "tz_text": tz_text,  # Сохраняем полный текст ТЗ
            "bot_sections": [
                {
                    "section_name": "Основная функциональность",
                    "description": "Главные функции бота",
                    "functions": functions,
                    "complexity_level": complexity,
                    "estimated_hours": estimated_hours
                }
            ],
            "detailed_functions": [
                {
                    "function_name": func,
                    "description": f"Подробная реализация: {func}",
                    "user_flow": "Пользовательский сценарий будет детализирован",
                    "technical_requirements": "Технические требования по согласованию",
                    "complexity_risks": "Риски будут оценены при детальном планировании",
                    "estimated_hours": 8
                } for func in functions[:3]  # Берем первые 3 функции
            ],
            "technology_stack": {
                "language": "Python",
                "framework": "aiogram / python-telegram-bot",
                "database": "PostgreSQL",
                "additional_tools": ["Redis", "Docker"],
                "external_apis": ["По требованию проекта"]
            },
            "integrations": [
                {
                    "name": "Базовые интеграции",
                    "purpose": "Для обеспечения функциональности",
                    "complexity": "medium",
                    "estimated_hours": 5
                }
            ],
            "admin_panel_requirements": {
                "needed": True,
                "functions": [
                    "Управление пользователями",
                    "Статистика использования",
                    "Настройки бота"
                ],
                "estimated_hours": 15
            },
            "development_stages": [
                {
                    "stage": "Этап 1: Проектирование и настройка",
                    "description": "Детальное планирование архитектуры",
                    "deliverables": ["Техническая документация", "Настройка окружения"],
                    "duration_days": 2,
                    "hours": 10
                },
                {
                    "stage": "Этап 2: Разработка основного функционала",
                    "description": "Реализация ключевых функций",
                    "deliverables": ["Рабочий MVP", "Тестирование"],
                    "duration_days": 5,
                    "hours": estimated_hours
                }
            ],
            "complexity_analysis": {
                "overall_complexity": complexity,
                "complex_features": ["Интеграции с внешними API", "Сложная логика обработки"],
                "simple_features": ["Базовые команды", "Простые ответы"],
                "integration_complexity": "Средняя сложность интеграций"
            },
            "risks_and_challenges": [
                {
                    "risk": "Изменение требований в процессе разработки",
                    "impact": "medium",
                    "mitigation": "Четкое планирование и поэтапная разработка"
                }
            ],
            "estimated_hours": estimated_hours,
            "priority_features": functions[:2] if len(functions) >= 2 else functions,
            "optional_features": functions[2:] if len(functions) > 2 else ["Дополнительные функции по запросу"]
        }

    def _create_detailed_fallback_tz(self, user_request: str) -> Dict[str, Any]:
        """Создание подробного fallback ТЗ при ошибке API"""
        
        # Анализируем запрос пользователя для определения типа проекта
        request_lower = user_request.lower()
        
        # Определяем тип проекта
        if any(word in request_lower for word in ["магазин", "продаж", "товар", "купить", "ecommerce"]):
            project_type = "ecommerce"
        elif any(word in request_lower for word in ["заказ", "доставка", "ресторан", "кафе", "еда"]):
            project_type = "delivery"
        elif any(word in request_lower for word in ["запис", "услуг", "салон", "клиник", "врач"]):
            project_type = "booking"
        elif any(word in request_lower for word in ["обучен", "курс", "урок", "тест"]):
            project_type = "education"
        elif any(word in request_lower for word in ["новости", "контент", "публикац"]):
            project_type = "content"
        else:
            project_type = "general"
        
        # Шаблоны для разных типов проектов
        templates = {
            "ecommerce": {
                "title": "Telegram-бот для интернет-магазина",
                "description": "Автоматизированный бот для продажи товаров через Telegram с интеграцией платежных систем, управлением каталогом и обработкой заказов. Бот обеспечивает полный цикл покупки от просмотра товаров до оплаты и доставки.",
                "functions": [
                    "Каталог товаров с категориями и поиском",
                    "Корзина и оформление заказа",
                    "Интеграция с платежными системами",
                    "Управление статусами заказов",
                    "Система уведомлений о заказах",
                    "Отзывы и рейтинги товаров",
                    "Программа лояльности",
                    "Административная панель для управления товарами"
                ],
                "complexity": "complex",
                "estimated_hours": 80
            },
            "delivery": {
                "title": "Telegram-бот для доставки еды",
                "description": "Система автоматизации заказов еды с интеграцией меню ресторана, расчетом стоимости доставки и отслеживанием статуса заказа. Бот обеспечивает удобное взаимодействие между клиентами и рестораном.",
                "functions": [
                    "Меню с категориями блюд",
                    "Система заказов с корзиной",
                    "Расчет стоимости доставки",
                    "Отслеживание статуса заказа",
                    "Интеграция с картами для адресов",
                    "Система оплаты",
                    "Уведомления курьеров и клиентов",
                    "Админка для управления заказами"
                ],
                "complexity": "complex",
                "estimated_hours": 70
            },
            "booking": {
                "title": "Telegram-бот для записи на услуги",
                "description": "Автоматизированная система записи клиентов на услуги с управлением расписанием, напоминаниями и возможностью отмены или переноса записей. Бот упрощает процесс записи и управления клиентской базой.",
                "functions": [
                    "Просмотр доступных услуг",
                    "Календарь и выбор времени",
                    "Запись на услуги",
                    "Управление записями (отмена, перенос)",
                    "Напоминания о предстоящих записях",
                    "История посещений",
                    "Система отзывов",
                    "Админка для управления расписанием"
                ],
                "complexity": "medium",
                "estimated_hours": 60
            },
            "education": {
                "title": "Telegram-бот для обучения",
                "description": "Образовательный бот с возможностью прохождения курсов, тестирования знаний и отслеживания прогресса. Бот предоставляет интерактивный формат обучения с персонализированным подходом.",
                "functions": [
                    "Каталог курсов и уроков",
                    "Интерактивные уроки",
                    "Система тестирования",
                    "Отслеживание прогресса",
                    "Сертификаты об окончании",
                    "Форум для общения учеников",
                    "Уведомления о новых материалах",
                    "Админка для управления контентом"
                ],
                "complexity": "medium",
                "estimated_hours": 65
            },
            "content": {
                "title": "Telegram-бот для контента и новостей",
                "description": "Автоматизированный бот для публикации и управления контентом с возможностью подписки на различные категории, поиска материалов и интерактивного взаимодействия с аудиторией.",
                "functions": [
                    "Публикация новостей и статей",
                    "Категоризация контента",
                    "Подписка на темы",
                    "Поиск по материалам",
                    "Комментарии и реакции",
                    "Рассылки по расписанию",
                    "Статистика просмотров",
                    "Админка для управления контентом"
                ],
                "complexity": "medium",
                "estimated_hours": 50
            },
            "general": {
                "title": f"Telegram-бот: {user_request[:50]}...",
                "description": "Индивидуальный Telegram-бот, разработанный под конкретные бизнес-задачи. Бот будет включать необходимый функционал для автоматизации процессов и улучшения взаимодействия с клиентами.",
                "functions": [
                    "Базовая навигация и меню",
                    "Обработка пользовательских запросов",
                    "Система уведомлений",
                    "Интеграция с базой данных",
                    "Административная панель",
                    "Аналитика и отчеты",
                    "Настройки и конфигурация",
                    "Техническая поддержка пользователей"
                ],
                "complexity": "medium",
                "estimated_hours": 45
            }
        }
        
        template = templates.get(project_type, templates["general"])
        
        # Создаем подробное ТЗ
        tz_text = f"""📋 НАЗВАНИЕ ПРОЕКТА
{template['title']}

📝 ОПИСАНИЕ ПРОЕКТА
{template['description']}

🎯 ЦЕЛИ И ЗАДАЧИ
• Автоматизация бизнес-процессов через Telegram
• Улучшение клиентского опыта
• Снижение нагрузки на персонал
• Увеличение конверсии и продаж
• Создание дополнительного канала коммуникации

👥 ЦЕЛЕВАЯ АУДИТОРИЯ
Основная аудитория: активные пользователи Telegram в возрасте 18-45 лет
Дополнительная аудитория: клиенты, предпочитающие быстрое и удобное обслуживание

⚙️ ОСНОВНЫЕ ФУНКЦИИ
{chr(10).join(f"• {func}" for func in template['functions'])}

🔧 ТЕХНИЧЕСКИЙ СТЕК
• Python 3.9+
• aiogram 3.x / python-telegram-bot
• PostgreSQL для основной БД
• Redis для кеширования
• Docker для контейнеризации
• FastAPI для админ-панели
• Nginx для проксирования

🔗 ИНТЕГРАЦИИ
• Telegram Bot API
• Платежные системы (ЮKassa, Stripe)
• SMS-сервисы для уведомлений
• Внешние API по требованию
• Системы аналитики

📊 АДМИН-ПАНЕЛЬ
• Управление пользователями и их правами
• Статистика использования бота
• Управление контентом и настройками
• Отчеты и аналитика
• Мониторинг работы системы

📈 ЭТАПЫ РАЗРАБОТКИ
1. Проектирование архитектуры (3 дня)
2. Разработка MVP функций (7 дней)
3. Интеграция с внешними сервисами (5 дней)
4. Создание админ-панели (5 дней)
5. Тестирование и отладка (3 дня)
6. Деплой и настройка (2 дня)

⚠️ РИСКИ И СЛОЖНОСТИ
• Ограничения Telegram Bot API
• Нагрузка при большом количестве пользователей
• Изменения в требованиях платежных систем
• Необходимость соблюдения требований безопасности
• Потребность в масштабировании при росте аудитории

⏱️ ВРЕМЕННЫЕ РАМКИ
Общее время разработки: {template['estimated_hours']} часов
Календарное время: 3-4 недели
Включает: разработку, тестирование, деплой

💰 ПРИМЕРНАЯ СТОИМОСТЬ
Базовая стоимость: {template['estimated_hours'] * 1500:,} рублей
Диапазон: {int(template['estimated_hours'] * 1500 * 0.85):,} - {int(template['estimated_hours'] * 1500 * 1.15):,} рублей
Ставка: 1500₽/час

🚀 MVP ФУНКЦИИ
{chr(10).join(f"• {func}" for func in template['functions'][:4])}

➕ ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ
{chr(10).join(f"• {func}" for func in template['functions'][4:])}
• Мультиязычность
• Интеграция с CRM
• Расширенная аналитика
• Персонализация контента"""
        
        return {
            "title": template['title'],
            "description": template['description'],
            "goals": "Автоматизация бизнес-процессов и улучшение клиентского опыта",
            "target_audience": "Активные пользователи Telegram в возрасте 18-45 лет",
            "tz_text": tz_text,
            "bot_sections": [
                {
                    "section_name": "Основная функциональность",
                    "description": "Ключевые функции бота",
                    "functions": template['functions'],
                    "complexity_level": template['complexity'],
                    "estimated_hours": template['estimated_hours']
                }
            ],
            "detailed_functions": [
                {
                    "function_name": func,
                    "description": f"Подробная реализация: {func}",
                    "user_flow": "Детальный пользовательский сценарий",
                    "technical_requirements": "Технические требования будут уточнены",
                    "complexity_risks": "Риски оценены и учтены в планировании",
                    "estimated_hours": max(8, template['estimated_hours'] // len(template['functions']))
                } for func in template['functions']
            ],
            "technology_stack": {
                "language": "Python",
                "framework": "aiogram 3.x",
                "database": "PostgreSQL",
                "additional_tools": ["Redis", "Docker", "FastAPI"],
                "external_apis": ["Telegram Bot API", "Payment APIs"]
            },
            "integrations": [
                {
                    "name": "Telegram Bot API",
                    "purpose": "Основной интерфейс бота",
                    "complexity": "medium",
                    "estimated_hours": 5
                },
                {
                    "name": "Платежные системы",
                    "purpose": "Обработка платежей",
                    "complexity": "high",
                    "estimated_hours": 10
                }
            ],
            "admin_panel_requirements": {
                "needed": True,
                "functions": [
                    "Управление пользователями",
                    "Статистика и аналитика",
                    "Управление контентом",
                    "Настройки бота"
                ],
                "estimated_hours": 20
            },
            "development_stages": [
                {
                    "stage": "Этап 1: Проектирование",
                    "description": "Детальное планирование архитектуры",
                    "deliverables": ["Техническая документация", "Схема БД"],
                    "duration_days": 3,
                    "hours": 15
                },
                {
                    "stage": "Этап 2: Разработка MVP",
                    "description": "Реализация основных функций",
                    "deliverables": ["Рабочий MVP", "Базовые тесты"],
                    "duration_days": 7,
                    "hours": template['estimated_hours'] // 2
                }
            ],
            "complexity_analysis": {
                "overall_complexity": template['complexity'],
                "complex_features": ["Интеграции с внешними API", "Обработка платежей"],
                "simple_features": ["Базовые команды", "Простые ответы"],
                "integration_complexity": "Средняя сложность интеграций"
            },
            "risks_and_challenges": [
                {
                    "risk": "Ограничения Telegram Bot API",
                    "impact": "medium",
                    "mitigation": "Изучение документации и планирование обходных путей"
                },
                {
                    "risk": "Масштабирование при росте нагрузки",
                    "impact": "high",
                    "mitigation": "Проектирование с учетом масштабирования"
                }
            ],
            "estimated_hours": template['estimated_hours'],
            "priority_features": template['functions'][:4],
            "optional_features": template['functions'][4:] + ["Мультиязычность", "Интеграция с CRM"]
        }

# Создаем глобальный экземпляр сервиса
ai_service = OpenAIService()