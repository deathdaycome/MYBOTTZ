"""
Voice Assistant API V2 - Advanced AI Sales Coach with Context Management
Новая система: Контекстный менеджер + Трехуровневые подсказки + Определение этапов
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

# ====================================
# Enums для этапов и типов
# ====================================

class ConversationStage(str, Enum):
    """Этапы разговора"""
    GREETING = "greeting"  # Знакомство
    DISCOVERY = "discovery"  # Сбор требований
    PRESENTATION = "presentation"  # Презентация решения
    PRICING = "pricing"  # Обсуждение цены
    OBJECTION = "objection"  # Работа с возражениями
    CLOSING = "closing"  # Закрытие сделки


class ClientType(str, Enum):
    """Типы клиентов"""
    UNKNOWN = "unknown"  # Неизвестный
    NEWBIE = "newbie"  # Новичок (не знает что нужно)
    TECHNICAL = "technical"  # Технарь (знает технологии)
    BUSINESS = "business"  # Бизнесмен (только про деньги)
    TOXIC = "toxic"  # Токсик (придирается)


# ====================================
# Контекстный менеджер
# ====================================

@dataclass
class CallContext:
    """Контекст звонка - умная память разговора"""

    # Краткая сводка разговора (до 400 символов)
    summary: str = ""

    # Требования клиента (список до 10 пунктов)
    requirements: List[str] = None

    # Текущий этап разговора
    stage: ConversationStage = ConversationStage.GREETING

    # Тип клиента
    client_type: ClientType = ClientType.UNKNOWN

    # Сигналы о бюджете
    budget_signals: List[str] = None

    # Красные флаги
    red_flags: List[str] = None

    # Время начала звонка
    start_time: str = ""

    # Счетчики
    message_count: int = 0
    questions_count: int = 0

    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.budget_signals is None:
            self.budget_signals = []
        if self.red_flags is None:
            self.red_flags = []
        if not self.start_time:
            self.start_time = datetime.now().isoformat()

    def update_summary(self, new_info: str):
        """Обновить краткую сводку"""
        if len(self.summary) + len(new_info) < 400:
            self.summary += " " + new_info
        else:
            # Оставляем только последние 400 символов
            self.summary = (self.summary + " " + new_info)[-400:]

    def add_requirement(self, req: str):
        """Добавить требование"""
        if len(self.requirements) < 10 and req not in self.requirements:
            self.requirements.append(req)

    def add_budget_signal(self, signal: str):
        """Добавить сигнал о бюджете"""
        if signal not in self.budget_signals:
            self.budget_signals.append(signal)

    def add_red_flag(self, flag: str):
        """Добавить красный флаг"""
        if flag not in self.red_flags:
            self.red_flags.append(flag)

    def to_dict(self) -> dict:
        """Конвертировать в словарь"""
        return {
            "summary": self.summary,
            "requirements": self.requirements,
            "stage": self.stage.value,
            "client_type": self.client_type.value,
            "budget_signals": self.budget_signals,
            "red_flags": self.red_flags,
            "message_count": self.message_count,
            "questions_count": self.questions_count,
        }


# ====================================
# Connection Manager with Context
# ====================================

class ConnectionManager:
    """Manages WebSocket connections with call context"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.call_contexts: Dict[str, CallContext] = {}
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}

    async def connect(self, connection_id: str, websocket: WebSocket):
        """Connect a new client"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.call_contexts[connection_id] = CallContext()
        self.conversation_history[connection_id] = []
        logger.info(f"WebSocket connected with context: {connection_id}")

    def disconnect(self, connection_id: str):
        """Disconnect a client"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.call_contexts:
            del self.call_contexts[connection_id]
        if connection_id in self.conversation_history:
            del self.conversation_history[connection_id]
        logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_message(self, connection_id: str, message: dict):
        """Send a message to a specific client"""
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_json(message)

    def get_context(self, connection_id: str) -> Optional[CallContext]:
        """Get call context"""
        return self.call_contexts.get(connection_id)

    def get_history(self, connection_id: str) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history.get(connection_id, [])

    def add_message(self, connection_id: str, message: Dict[str, Any]):
        """Add message to history"""
        if connection_id in self.conversation_history:
            self.conversation_history[connection_id].append(message)
            # Обновляем счетчик в контексте
            context = self.get_context(connection_id)
            if context:
                context.message_count += 1


manager = ConnectionManager()


# ====================================
# AI Analysis with Context
# ====================================

async def analyze_with_context(
    text: str,
    speaker: str,
    context: CallContext,
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Анализ речи с контекстом - определяет этап, тип клиента, обновляет контекст
    """
    try:
        # Определяем этап разговора
        stage = detect_conversation_stage(text, history, context)
        context.stage = stage

        # Определяем тип клиента (только из речи клиента)
        if speaker == 'client':
            client_type = detect_client_type(text, history)
            if client_type != ClientType.UNKNOWN:
                context.client_type = client_type

            # Ищем требования
            requirements = extract_requirements(text)
            for req in requirements:
                context.add_requirement(req)

            # Ищем сигналы о бюджете
            budget_signals = extract_budget_signals(text)
            for signal in budget_signals:
                context.add_budget_signal(signal)

            # Ищем красные флаги
            red_flags = detect_red_flags(text)
            for flag in red_flags:
                context.add_red_flag(flag)

        # Обновляем краткую сводку
        context.update_summary(f"{speaker[:1].upper()}: {text[:50]}")

        return {
            "stage": stage.value,
            "client_type": context.client_type.value,
            "context_updated": True,
        }

    except Exception as e:
        logger.error(f"Error analyzing with context: {e}", exc_info=True)
        return {"error": str(e)}


def detect_conversation_stage(
    text: str,
    history: List[Dict[str, Any]],
    context: CallContext
) -> ConversationStage:
    """Определить этап разговора"""
    text_lower = text.lower()

    # Приветствие (первые 2 сообщения)
    if context.message_count < 3:
        return ConversationStage.GREETING

    # Возражения (ключевые слова)
    objection_words = ['дорого', 'долго', 'не уверен', 'подумаю', 'не знаю', 'сомневаюсь']
    if any(word in text_lower for word in objection_words):
        return ConversationStage.OBJECTION

    # Обсуждение цены
    pricing_words = ['цена', 'стоимость', 'сколько стоит', 'бюджет', 'прайс', 'оплата']
    if any(word in text_lower for word in pricing_words):
        return ConversationStage.PRICING

    # Закрытие (готов к сделке)
    closing_words = ['когда начнем', 'договор', 'старт', 'приступим', 'согласен', 'подходит']
    if any(word in text_lower for word in closing_words):
        return ConversationStage.CLOSING

    # Презентация (есть требования, обсуждаем решение)
    if len(context.requirements) > 0:
        presentation_words = ['как это работает', 'покажите', 'пример', 'функционал']
        if any(word in text_lower for word in presentation_words):
            return ConversationStage.PRESENTATION

    # Discovery (сбор требований) - по умолчанию
    return ConversationStage.DISCOVERY


def detect_client_type(text: str, history: List[Dict[str, Any]]) -> ClientType:
    """Определить тип клиента"""
    text_lower = text.lower()

    # Технарь
    tech_words = ['api', 'база данных', 'интеграция', 'backend', 'frontend', 'docker', 'postgres']
    if any(word in text_lower for word in tech_words):
        return ClientType.TECHNICAL

    # Бизнесмен
    business_words = ['roi', 'окупаемость', 'выгода', 'прибыль', 'эффективность', 'конверсия']
    if any(word in text_lower for word in business_words):
        return ClientType.BUSINESS

    # Токсик
    toxic_words = ['не понравилось', 'плохо', 'некачественно', 'не работает', 'обман', 'развод']
    if any(word in text_lower for word in toxic_words):
        return ClientType.TOXIC

    # Новичок (много базовых вопросов)
    newbie_words = ['что это', 'как это', 'не понимаю', 'объясните', 'не знаю']
    if any(word in text_lower for word in newbie_words):
        return ClientType.NEWBIE

    return ClientType.UNKNOWN


def extract_requirements(text: str) -> List[str]:
    """Извлечь требования из текста"""
    requirements = []
    text_lower = text.lower()

    # Общие требования
    if 'запись' in text_lower or 'бронирование' in text_lower:
        requirements.append("Система записи/бронирования")
    if 'оплата' in text_lower or 'платеж' in text_lower:
        requirements.append("Прием платежей")
    if 'уведомления' in text_lower or 'напоминания' in text_lower:
        requirements.append("Уведомления и напоминания")
    if 'crm' in text_lower or 'амо' in text_lower or 'bitrix' in text_lower:
        requirements.append("Интеграция с CRM")
    if 'мобильное приложение' in text_lower or 'приложение' in text_lower:
        requirements.append("Мобильное приложение")
    if 'сайт' in text_lower or 'веб' in text_lower:
        requirements.append("Веб-интерфейс")

    return requirements


def extract_budget_signals(text: str) -> List[str]:
    """Извлечь сигналы о бюджете"""
    signals = []
    text_lower = text.lower()

    if 'до 50' in text_lower or 'до 100' in text_lower:
        signals.append(f"Бюджет упомянут: {text[:100]}")
    if 'дорого' in text_lower:
        signals.append("Сигнал: считает дорого")
    if 'недорого' in text_lower or 'бюджетно' in text_lower:
        signals.append("Сигнал: ищет недорого")

    return signals


def detect_red_flags(text: str) -> List[str]:
    """Определить красные флаги"""
    flags = []
    text_lower = text.lower()

    if 'сделать за' in text_lower and ('день' in text_lower or 'неделю' in text_lower):
        flags.append("Нереальные сроки")
    if 'бесплатно' in text_lower or 'даром' in text_lower:
        flags.append("Хочет бесплатно")
    if 'сам сделаю' in text_lower or 'сами сделаем' in text_lower:
        flags.append("Может уйти делать сам")

    return flags


# ====================================
# AI Response Generation - 3 Levels
# ====================================

async def generate_three_level_suggestion(
    client_text: str,
    context: CallContext,
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Генерация трехуровневой подсказки:
    1. Что сказать сейчас (reply_now)
    2. План на 2-3 минуты (next_steps)
    3. Объяснение для новичка (explanation)
    """

    try:
        # Используем OpenRouter API
        import httpx

        openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if not openrouter_api_key:
            # Fallback на моковые данные
            return generate_fallback_suggestion(client_text, context)

        openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        default_model = os.getenv('DEFAULT_MODEL', 'openai/gpt-4o-mini')

        # Новый промпт для трехуровневых подсказок
        system_prompt = f"""
Ты - AI Sales Coach (старший тимлид по продажам). Твоя задача - в реальном времени подсказывать продавцу ЧТО сказать и КАК вести разговор.

📊 ТЕКУЩИЙ КОНТЕКСТ ЗВОНКА:
• Этап: {context.stage.value}
• Тип клиента: {context.client_type.value}
• Требования: {', '.join(context.requirements) if context.requirements else 'Еще не выяснены'}
• Бюджетные сигналы: {', '.join(context.budget_signals) if context.budget_signals else 'Нет'}
• Красные флаги: {', '.join(context.red_flags) if context.red_flags else 'Нет'}

📋 КОМПАНИЯ:
• Telegram-боты, чат-боты, веб-приложения
• Цены: Простой 40-60к, Средний 70-120к, Сложный 150-300к
• Сроки: Простой 1-2 нед, Средний 3-4 нед, Сложный 1.5-3 мес

🎯 ТВОЯ ЗАДАЧА:
Дай ТРИ блока подсказок в строгом JSON формате:

{{
  "reply_now": "Короткая фраза (1-2 предложения) что сказать клиенту ПРЯМО СЕЙЧАС",
  "next_steps": [
    "Пункт 1 - что узнать/сделать в ближайшие 2-3 минуты",
    "Пункт 2",
    "Пункт 3"
  ],
  "explanation": "Простое объяснение для новичка (1-2 предложения): почему это важно и как это поможет закрыть сделку",
  "stage_update": "{context.stage.value}"
}}

ПРАВИЛА:
• reply_now - КОРОТКАЯ фраза, что сказать сейчас (макс 2 предложения)
• next_steps - СПИСОК из 3 конкретных действий
• explanation - ПРОСТОЕ объяснение для новичка
• Веди к сбору ПОЛНОГО ТЗ и выяснению бюджета
• На этапе pricing - называй конкретные цифры
• На этапе objection - работай с возражениями
• На этапе closing - закрывай сделку

ЭТАПЫ:
• greeting - Знакомство, выясняем базовую суть
• discovery - Собираем требования (SPIN questions)
• presentation - Показываем решение
• pricing - Обсуждаем цену
• objection - Работаем с возражениями
• closing - Закрываем сделку

ОТВЕЧАЙ ТОЛЬКО ВАЛИДНЫМ JSON!
"""

        # Собираем контекст разговора (последние 5 сообщений)
        messages = [{"role": "system", "content": system_prompt}]

        for msg in history[-5:]:
            speaker_label = "Клиент" if msg['speaker'] == 'client' else "Менеджер"
            messages.append({
                "role": "user",
                "content": f"{speaker_label}: {msg['text']}"
            })

        # Текущее сообщение клиента
        messages.append({
            "role": "user",
            "content": f"Клиент: {client_text}\n\nДай трехуровневую подсказку в JSON формате."
        })

        # Вызов API
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "HTTP-Referer": "https://nikolaevcodev.ru",
                    "X-Title": "CRM AI Voice Assistant V2",
                },
                json={
                    "model": default_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"}  # Требуем JSON
                }
            )

            if response.status_code != 200:
                logger.error(f"OpenRouter error: {response.status_code}")
                return generate_fallback_suggestion(client_text, context)

            data = response.json()
            ai_response = data['choices'][0]['message']['content']

            # Парсим JSON
            try:
                result = json.loads(ai_response)

                # Валидация
                if not all(key in result for key in ['reply_now', 'next_steps', 'explanation']):
                    raise ValueError("Missing required keys in AI response")

                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI JSON: {e}\nResponse: {ai_response}")
                return generate_fallback_suggestion(client_text, context)

    except Exception as e:
        logger.error(f"Error generating AI suggestion: {e}", exc_info=True)
        return generate_fallback_suggestion(client_text, context)


def generate_fallback_suggestion(text: str, context: CallContext) -> Dict[str, Any]:
    """Fallback подсказки если AI не работает"""

    stage = context.stage

    # Простые шаблоны по этапам
    if stage == ConversationStage.GREETING:
        return {
            "reply_now": "Здравствуйте! Расскажите, какая задача у вас стоит?",
            "next_steps": [
                "Выяснить суть задачи",
                "Узнать текущую ситуацию",
                "Спросить про сроки"
            ],
            "explanation": "На этапе знакомства важно быстро понять суть задачи, чтобы перейти к сбору требований.",
            "stage_update": "greeting"
        }

    elif stage == ConversationStage.DISCOVERY:
        return {
            "reply_now": "Понятно. Уточните, какие именно функции вам нужны?",
            "next_steps": [
                "Собрать список функций",
                "Спросить про интеграции",
                "Выяснить бюджет"
            ],
            "explanation": "Собираем полное ТЗ. Чем больше деталей узнаем, тем точнее назовем цену.",
            "stage_update": "discovery"
        }

    elif stage == ConversationStage.PRICING:
        return {
            "reply_now": "По вашим требованиям стоимость составит 80-120 тысяч рублей.",
            "next_steps": [
                "Объяснить из чего складывается цена",
                "Показать примеры работ",
                "Предложить рассрочку или этапы"
            ],
            "explanation": "Называем конкретную вилку цен. Это создает доверие и позволяет работать с бюджетом клиента.",
            "stage_update": "pricing"
        }

    else:
        return {
            "reply_now": "Хороший вопрос! Давайте обсудим детали.",
            "next_steps": [
                "Уточнить требования",
                "Обсудить сроки",
                "Назвать примерную стоимость"
            ],
            "explanation": "Ведем разговор к сбору полной информации для точной оценки проекта.",
            "stage_update": stage.value
        }


# ====================================
# WebSocket Endpoint
# ====================================

@router.websocket("/ws/voice-assistant-v2")
async def voice_assistant_v2_websocket(websocket: WebSocket, auth: Optional[str] = None):
    """
    WebSocket для AI Voice Assistant V2 с контекстным менеджером

    Ожидаемый формат сообщения:
    {
        "type": "speech",
        "text": "...",
        "speaker": "client" | "salesperson",
        "timestamp": "..."
    }

    Формат ответа:
    {
        "type": "suggestion_v2",
        "reply_now": "...",
        "next_steps": [...],
        "explanation": "...",
        "context": {...}
    }
    """

    connection_id = f"conn_{datetime.now().timestamp()}"
    logger.info(f"[V2] WebSocket connection: {connection_id}")

    try:
        await manager.connect(connection_id, websocket)

        # Welcome message
        await websocket.send_json({
            'type': 'connected',
            'message': 'AI Voice Assistant V2 connected',
            'connection_id': connection_id,
        })

        while True:
            data = await websocket.receive_json()
            logger.info(f"[V2] Received: {data.get('type')}")

            message_type = data.get('type')

            if message_type == 'speech':
                text = data.get('text', '').strip()
                speaker = data.get('speaker', 'client')
                timestamp = data.get('timestamp', datetime.now().isoformat())

                if not text:
                    continue

                # Добавляем в историю
                message = {
                    'text': text,
                    'speaker': speaker,
                    'timestamp': timestamp,
                }
                manager.add_message(connection_id, message)

                # Получаем контекст и историю
                context = manager.get_context(connection_id)
                history = manager.get_history(connection_id)

                if not context:
                    continue

                # Анализируем с контекстом
                await analyze_with_context(text, speaker, context, history)

                # Генерируем подсказки только для речи клиента
                if speaker == 'client':
                    logger.info(f"[V2] Generating 3-level suggestion...")

                    suggestion = await generate_three_level_suggestion(
                        text, context, history
                    )

                    # Отправляем подсказку
                    await websocket.send_json({
                        'type': 'suggestion_v2',
                        'reply_now': suggestion.get('reply_now', ''),
                        'next_steps': suggestion.get('next_steps', []),
                        'explanation': suggestion.get('explanation', ''),
                        'context': context.to_dict(),
                        'timestamp': datetime.now().isoformat(),
                    })

                    logger.info(f"[V2] Suggestion sent: {suggestion['reply_now'][:50]}...")

            elif message_type == 'ping':
                await websocket.send_json({'type': 'pong'})

            elif message_type == 'get_context':
                context = manager.get_context(connection_id)
                if context:
                    await websocket.send_json({
                        'type': 'context_data',
                        'context': context.to_dict(),
                    })

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"[V2] Disconnected: {connection_id}")

    except Exception as e:
        logger.error(f"[V2] Error: {e}", exc_info=True)
        manager.disconnect(connection_id)


# ====================================
# Status endpoint
# ====================================

@router.get("/voice-assistant-v2/status")
async def get_v2_status():
    """Get V2 status"""
    return {
        'status': 'operational',
        'version': '2.0',
        'active_connections': len(manager.active_connections),
        'features': [
            'Context Management',
            'Three-Level Suggestions',
            'Stage Detection',
            'Client Type Detection',
        ],
        'timestamp': datetime.now().isoformat(),
    }
