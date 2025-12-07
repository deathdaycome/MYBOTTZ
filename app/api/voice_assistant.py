"""
Voice Assistant API - WebSocket endpoint for real-time AI suggestions during sales calls
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import JSONResponse

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

# ====================================
# WebSocket Connection Manager
# ====================================

class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, connection_id: str, websocket: WebSocket):
        """Connect a new client"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")

    def disconnect(self, connection_id: str):
        """Disconnect a client"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_message(self, connection_id: str, message: dict):
        """Send a message to a specific client"""
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# ====================================
# AI Analysis Functions
# ====================================

async def analyze_speech(text: str, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze speech text to detect questions and generate AI suggestions

    Args:
        text: The speech text to analyze
        conversation_history: Previous conversation messages

    Returns:
        Analysis result with question detection and AI suggestion
    """
    try:
        # Simple question detection (can be enhanced with ML)
        is_question = detect_question(text)

        if is_question:
            # Generate AI suggestion
            suggestion = await generate_ai_suggestion(text, conversation_history)

            return {
                'is_question': True,
                'question': text,
                'category': categorize_question(text),
                'suggested_answer': suggestion,
                'confidence': 0.85,  # Mock confidence score
            }
        else:
            return {
                'is_question': False,
                'text': text,
            }

    except Exception as e:
        logger.error(f"Error analyzing speech: {e}", exc_info=True)
        return {
            'is_question': False,
            'text': text,
            'error': str(e),
        }


def detect_question(text: str) -> bool:
    """
    Detect if the text is a question

    Enhanced detection that looks for question patterns anywhere in the text:
    - Ends with '?'
    - Contains question words (кто, что, где, когда, почему, как, сколько, etc.)
    - Always returns True for any client speech to provide AI assistance
    """
    text_lower = text.lower().strip()

    # Always return True to provide AI suggestions for any client speech
    # This ensures the AI assistant is proactive and helpful
    return True

    # Original logic below (kept for reference but not executed):
    # Check for question mark
    if text_lower.endswith('?'):
        return True

    # Check for question words anywhere in the text
    question_words = [
        'кто', 'что', 'где', 'когда', 'почему', 'зачем', 'как', 'сколько',
        'какой', 'какая', 'какие', 'чей', 'чья', 'чьё', 'чьи',
        'можно ли', 'есть ли', 'будет ли', 'можете ли', 'можете',
        'скажите', 'подскажите', 'расскажите', 'объясните', 'стоит', 'цена',
        'сколько стоит', 'во сколько', 'хочу', 'нужно', 'надо', 'интересует',
    ]

    for word in question_words:
        if word in text_lower:  # Changed from startswith to 'in'
            return True

    return False


def categorize_question(text: str) -> str:
    """
    Categorize the question into predefined categories
    """
    text_lower = text.lower()

    # Pricing related
    if any(word in text_lower for word in ['цена', 'стоимость', 'сколько стоит', 'прайс', 'оплата']):
        return 'pricing'

    # Technical questions
    if any(word in text_lower for word in ['технология', 'техническ', 'функционал', 'возможности', 'фича']):
        return 'technical'

    # Timeline questions
    if any(word in text_lower for word in ['срок', 'когда', 'как долго', 'время', 'дедлайн']):
        return 'timeline'

    # Process questions
    if any(word in text_lower for word in ['процесс', 'как происходит', 'этап', 'шаг']):
        return 'process'

    # Support questions
    if any(word in text_lower for word in ['поддержка', 'помощь', 'проблема', 'ошибка', 'не работает']):
        return 'support'

    return 'general'


async def generate_ai_with_openrouter(
    question: str,
    conversation_history: List[Dict[str, Any]],
    category: str
) -> str:
    """
    Generate AI response using OpenRouter API
    """
    import httpx

    openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
    openrouter_base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    default_model = os.getenv('DEFAULT_MODEL', 'openai/gpt-4o-mini')

    # Build system prompt - AI Sales Coach (ментор-продавец)
    system_prompt = """
Ты - AI Sales Coach (ментор-продавец). Твоя задача - ПОДСКАЗЫВАТЬ продавцу, ЧТО говорить клиенту во время звонка.

🎯 ВАЖНО: Ты НЕ отвечаешь клиенту напрямую. Ты подсказываешь продавцу, что ему сказать.

📋 КОНТЕКСТ КОМПАНИИ:
- Специализация: Разработка Telegram-ботов, чат-ботов, веб-приложений
- Средние цены: Простой бот 40-60к, Средний 70-120к, Сложный 150-300к
- Сроки: Простой 1-2 недели, Средний 3-4 недели, Сложный 1.5-3 месяца
- УТП: Быстрый старт, месяц бесплатной поддержки, опыт в нише клиента
- Стек: Python (aiogram, FastAPI), PostgreSQL, Redis, Docker, OpenAI API

🎯 ТВОЯ ЗАДАЧА:
1. Анализируй стадию сделки (Discovery / Presentation / Objection / Closing)
2. Подсказывай продавцу конкретные фразы в формате: "💡 Скажи: '...'"
3. Веди к закрытию сделки используя SPIN, BANT, closing techniques
4. Давай 1-2 варианта ответа (если нужно: мягкий vs агрессивный подход)

📐 SALES FRAMEWORKS:
- SPIN: Situation, Problem, Implication, Need-payoff questions
- BANT: Budget, Authority, Need, Timeline
- Closing: Trial close, Assumptive close, Alternative close

🎨 ФОРМАТ ОТВЕТА:
💡 **Скажи:** "Конкретная фраза для клиента"
🎯 **Цель:** Узнать бюджет / Назвать цену / Закрыть сделку
📊 **Стадия:** Discovery / Presentation / Objection / Closing

ПРИМЕР:
Клиент: "Мне нужен бот для автосервиса"
Твой ответ:
💡 **Скажи:** "Отлично! Расскажите, какие задачи бот должен решать? Запись клиентов, напоминания или что-то ещё?"
🎯 **Цель:** Выявить потребности (SPIN - Situation)
📊 **Стадия:** Discovery

Будь кратким (1-2 фразы для продавца). Веди к сделке агрессивно, но естественно.
"""

    # Build messages
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add recent conversation history for context (last 10 messages for full context)
    for msg in conversation_history[-10:]:
        speaker_label = "👤 Клиент" if msg['speaker'] == 'client' else "💼 Продавец"
        role = "user"  # Весь контекст как user messages для AI Coach
        messages.append({
            "role": role,
            "content": f"{speaker_label}: {msg['text']}"
        })

    # Add current client message
    messages.append({
        "role": "user",
        "content": f"👤 Клиент: {question}"
    })

    # Call OpenRouter API
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{openrouter_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "HTTP-Referer": "https://nikolaevcodev.ru",
                "X-Title": "CRM AI Voice Assistant",
            },
            json={
                "model": default_model,
                "messages": messages,
                "temperature": 0.8,  # Более креативные подсказки
                "max_tokens": 400,  # Больше места для форматированных подсказок
            }
        )

        if response.status_code != 200:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            raise Exception(f"OpenRouter API error: {response.status_code}")

        data = response.json()
        answer = data['choices'][0]['message']['content']

        logger.info(f"OpenRouter AI generated answer for category '{category}': {answer[:100]}...")
        return answer


async def generate_ai_suggestion(question: str, conversation_history: List[Dict[str, Any]]) -> str:
    """
    Generate AI-powered answer suggestion using OpenRouter API
    """
    category = categorize_question(question)

    # Try to use OpenRouter AI, fallback to knowledge base
    try:
        import httpx

        openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_api_key:
            # Use OpenRouter for AI-generated responses
            return await generate_ai_with_openrouter(question, conversation_history, category)
    except Exception as e:
        logger.warning(f"OpenRouter API failed, using fallback: {e}")

    # Fallback: Mock knowledge base
    knowledge_base = {
        'pricing': {
            'base_response': 'Стоимость проекта зависит от его сложности и требований. Базовая ставка составляет 1000 рублей/час. Мы можем предоставить точную оценку после обсуждения всех деталей проекта.',
            'examples': [
                'Для простого бота с базовыми функциями стоимость начинается от 30,000 рублей',
                'Средний проект с интеграциями обходится в 50,000-100,000 рублей',
                'Комплексная система с AI и множеством интеграций - от 150,000 рублей',
            ]
        },
        'timeline': {
            'base_response': 'Сроки разработки зависят от объёма и сложности проекта. Обычно:',
            'examples': [
                'Простой бот - 1-2 недели',
                'Средний проект - 3-4 недели',
                'Сложная система - 1.5-3 месяца',
                'Мы всегда стараемся уложиться в согласованные сроки и держим вас в курсе прогресса'
            ]
        },
        'technical': {
            'base_response': 'Мы используем современный технологический стек:',
            'examples': [
                'Python (aiogram, FastAPI) для разработки ботов',
                'PostgreSQL для надёжного хранения данных',
                'Redis для кэширования и очередей',
                'Docker для контейнеризации',
                'OpenAI API для AI-функций',
                'Интеграции с различными сервисами по API'
            ]
        },
        'process': {
            'base_response': 'Наш процесс разработки включает следующие этапы:',
            'examples': [
                '1. Обсуждение требований и создание технического задания',
                '2. Согласование дизайна и функционала',
                '3. Разработка и тестирование',
                '4. Демонстрация и сбор обратной связи',
                '5. Запуск в продакшн и поддержка'
            ]
        },
        'support': {
            'base_response': 'Мы предоставляем полную техническую поддержку:',
            'examples': [
                'Месяц бесплатной поддержки после запуска',
                'Быстрое реагирование на критические проблемы',
                'Регулярные обновления и улучшения',
                'Документация и обучение вашей команды'
            ]
        },
        'general': {
            'base_response': 'Это отличный вопрос! Позвольте пояснить:',
            'examples': [
                'Мы специализируемся на разработке Telegram-ботов и чат-ботов',
                'Имеем опыт работы с различными отраслями и задачами',
                'Предоставляем полный цикл разработки от идеи до запуска',
                'У нас гибкий подход - мы адаптируемся под ваши потребности'
            ]
        }
    }

    # Get response template for category
    response_data = knowledge_base.get(category, knowledge_base['general'])
    base = response_data['base_response']
    examples = response_data['examples']

    # Construct answer
    if len(examples) > 0:
        answer = base + '\n\n' + '\n'.join([f"• {example}" for example in examples])
    else:
        answer = base

    # In production, this would be:
    # try:
    #     import openai
    #     openai.api_key = os.getenv('OPENAI_API_KEY')
    #
    #     # Build context from conversation history
    #     messages = [
    #         {"role": "system", "content": "Ты - опытный продажник, помогающий отвечать на вопросы клиентов. Давай краткие, точные и убедительные ответы."},
    #     ]
    #
    #     # Add conversation history
    #     for msg in conversation_history[-5:]:  # Last 5 messages for context
    #         messages.append({
    #             "role": "user" if msg['speaker'] == 'client' else "assistant",
    #             "content": msg['text']
    #         })
    #
    #     # Add current question
    #     messages.append({"role": "user", "content": question})
    #
    #     # Call OpenAI
    #     response = openai.ChatCompletion.create(
    #         model="gpt-4o-mini",
    #         messages=messages,
    #         temperature=0.7,
    #         max_tokens=200
    #     )
    #
    #     answer = response.choices[0].message.content
    # except Exception as e:
    #     logger.error(f"OpenAI API error: {e}")
    #     answer = "Извините, возникла проблема с генерацией ответа. Пожалуйста, ответьте на основе своего опыта."

    return answer


# ====================================
# WebSocket Endpoint
# ====================================

@router.websocket("/ws/voice-assistant")
async def voice_assistant_websocket(websocket: WebSocket, auth: Optional[str] = None):
    """
    WebSocket endpoint for real-time voice assistant

    Expected message format:
    {
        "type": "speech",
        "text": "recognized speech text",
        "timestamp": "ISO timestamp",
        "speaker": "client" | "salesperson"
    }

    Response format:
    {
        "type": "suggestion",
        "question": "client question",
        "answer": "AI-generated suggestion",
        "category": "pricing|technical|timeline|process|support|general",
        "confidence": 0.85
    }
    """
    # Log connection attempt
    logger.info(f"[VOICE] WebSocket connection attempt from {websocket.client}")
    logger.info(f"[VOICE] Auth parameter: {auth[:20] if auth else 'None'}...")

    # Generate unique connection ID
    connection_id = f"conn_{datetime.now().timestamp()}"

    # Conversation history for context
    conversation_history: List[Dict[str, Any]] = []

    try:
        # Accept connection
        logger.info(f"[VOICE] Accepting WebSocket connection {connection_id}")
        await manager.connect(connection_id, websocket)
        logger.info(f"[VOICE] Connection {connection_id} accepted successfully")

        # Send welcome message
        await websocket.send_json({
            'type': 'connected',
            'message': 'AI Voice Assistant connected',
            'connection_id': connection_id,
        })
        logger.info(f"[VOICE] Welcome message sent to {connection_id}")

        while True:
            # Receive message from client
            logger.info(f"[VOICE] Waiting for message from {connection_id}...")
            data = await websocket.receive_json()
            logger.info(f"[VOICE] Received message from {connection_id}: {data}")

            message_type = data.get('type')

            if message_type == 'speech':
                text = data.get('text', '').strip()
                speaker = data.get('speaker', 'client')
                timestamp = data.get('timestamp', datetime.now().isoformat())

                logger.info(f"[VOICE] Speech message: speaker={speaker}, text='{text[:50]}'")

                if not text:
                    logger.warning(f"[VOICE] Empty text received, skipping")
                    continue

                # Add to conversation history
                conversation_history.append({
                    'text': text,
                    'speaker': speaker,
                    'timestamp': timestamp,
                })

                # Only analyze client speech
                if speaker == 'client':
                    logger.info(f"[VOICE] Analyzing client speech: '{text[:50]}'...")
                    # Analyze speech
                    analysis = await analyze_speech(text, conversation_history)
                    logger.info(f"[VOICE] Analysis result: is_question={analysis.get('is_question')}, category={analysis.get('category')}")

                    if analysis.get('is_question'):
                        logger.info(f"[VOICE] Generating AI suggestion...")
                        # Send AI suggestion
                        suggestion_data = {
                            'type': 'suggestion',
                            'question': analysis['question'],
                            'answer': analysis['suggested_answer'],
                            'category': analysis['category'],
                            'confidence': analysis.get('confidence', 0.8),
                            'timestamp': datetime.now().isoformat(),
                        }
                        await websocket.send_json(suggestion_data)
                        logger.info(f"[VOICE] AI suggestion sent: {suggestion_data['answer'][:100]}...")
                        logger.info(f"[VOICE] Question detected: {text[:50]}... -> Category: {analysis['category']}")
                    else:
                        logger.info(f"[VOICE] Not a question, skipping AI suggestion")
                else:
                    logger.info(f"[VOICE] Salesperson speech, not analyzing")

            elif message_type == 'ping':
                # Respond to ping
                await websocket.send_json({'type': 'pong'})
                logger.info(f"[VOICE] Pong sent to {connection_id}")

            elif message_type == 'clear_history':
                # Clear conversation history
                conversation_history = []
                await websocket.send_json({
                    'type': 'history_cleared',
                    'message': 'Conversation history cleared',
                })
                logger.info(f"[VOICE] History cleared for {connection_id}")

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"[VOICE] Client {connection_id} disconnected")

    except Exception as e:
        logger.error(f"[VOICE] WebSocket error for {connection_id}: {e}", exc_info=True)
        manager.disconnect(connection_id)
        try:
            await websocket.send_json({
                'type': 'error',
                'message': f'Server error: {str(e)}',
            })
        except:
            pass


# ====================================
# REST Endpoints (optional, for testing)
# ====================================

@router.get("/voice-assistant/status")
async def get_voice_assistant_status():
    """Get voice assistant service status"""
    return {
        'status': 'operational',
        'active_connections': len(manager.active_connections),
        'timestamp': datetime.now().isoformat(),
    }


@router.post("/voice-assistant/test-analyze")
async def test_analyze(text: str):
    """Test speech analysis (for debugging)"""
    result = await analyze_speech(text, [])
    return JSONResponse(content=result)
