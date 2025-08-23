"""
Роутер для интеграции с Авито мессенджером
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, Depends, Request, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import json
import asyncio
from datetime import datetime
import logging
import os

from ...database.database import get_db_context, get_db
from ...services.notification_service import NotificationService
from ...services.avito_polling_service import polling_service
from ...database.crm_models import Client, ClientStatus, ClientType, AvitoClientStatus
from ...database.models import AdminUser
from ...services.avito_service import get_avito_service, init_avito_service, AvitoService
from ...services.openai_service import generate_conversation_summary
from ..navigation import get_navigation_items
from ...config.settings import settings
# Импортируем функции аутентификации из middleware.auth
from ..middleware.auth import authenticate, get_current_admin_user
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/avito", tags=["avito"])
templates = Jinja2Templates(directory="app/admin/templates")

def get_current_user(username: str):
    """Получение текущего пользователя по имени"""
    if username == settings.ADMIN_USERNAME:
        return {"username": username, "role": "owner", "id": 1}
    else:
        with get_db_context() as db:
            admin_user = db.query(AdminUser).filter(AdminUser.username == username).first()
            if admin_user:
                return {
                    "username": admin_user.username,
                    "role": admin_user.role,
                    "id": admin_user.id,
                    "first_name": admin_user.first_name,
                    "last_name": admin_user.last_name,
                    "email": admin_user.email
                }
    return None

# Инициализация сервиса Авито
AVITO_CLIENT_ID = os.getenv("AVITO_CLIENT_ID")
AVITO_CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET")
AVITO_USER_ID = os.getenv("AVITO_USER_ID")

# WebSocket connections storage
websocket_connections = {}

# Инициализация сервиса сразу при импорте, если есть User ID
logger.info(f"Avito environment check: CLIENT_ID={AVITO_CLIENT_ID[:10] + '...' if AVITO_CLIENT_ID else 'None'}, CLIENT_SECRET={'***' if AVITO_CLIENT_SECRET else 'None'}, USER_ID={AVITO_USER_ID}")

if AVITO_USER_ID and AVITO_CLIENT_ID and AVITO_CLIENT_SECRET:
    try:
        user_id = int(AVITO_USER_ID)
        init_avito_service(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, user_id)
        logger.info(f"Avito service initialized with User ID: {user_id}")
    except Exception as e:
        logger.error(f"Failed to initialize Avito service on import: {e}")
else:
    logger.warning("Avito service not initialized: missing environment variables (CLIENT_ID, CLIENT_SECRET, or USER_ID)")

@router.on_event("startup")
async def startup_event():
    """Инициализация сервиса при старте (fallback)"""
    # Пробуем инициализировать еще раз при старте, если не было инициализировано
    try:
        service = get_avito_service()
        logger.info("Avito service already initialized")
    except:
        if AVITO_USER_ID:
            try:
                user_id = int(AVITO_USER_ID)
                init_avito_service(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, user_id)
                logger.info(f"Avito service initialized in startup event with User ID: {user_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Avito service in startup: {e}")

@router.get("/", response_class=HTMLResponse)
async def avito_messenger(
    request: Request,
    username: str = Depends(authenticate)
):
    """Страница мессенджера Авито"""
    current_user = get_current_user(username)
    return templates.TemplateResponse("avito_messenger.html", {
        "request": request,
        "user": current_user,
        "navigation": get_navigation_items("/avito", user_role=current_user.get('role') if current_user else None),
        "title": "Авито Мессенджер"
    })

@router.get("/debug")
async def debug_status(username: str = Depends(authenticate)):
    """Диагностический эндпоинт для проверки состояния Avito сервиса"""
    debug_info = {
        "environment": {
            "AVITO_CLIENT_ID": AVITO_CLIENT_ID[:10] + "..." if AVITO_CLIENT_ID else None,
            "AVITO_CLIENT_SECRET": "***" if AVITO_CLIENT_SECRET else None,
            "AVITO_USER_ID": AVITO_USER_ID
        },
        "service_status": "not_initialized"
    }
    
    try:
        service = get_avito_service()
        debug_info["service_status"] = "initialized"
        debug_info["service_user_id"] = service.user_id
        
        # Пробуем получить токен
        try:
            token = await service._get_access_token()
            debug_info["token_status"] = f"ok ({token[:10]}...)"
        except Exception as e:
            debug_info["token_status"] = f"error: {str(e)}"
            
    except Exception as e:
        debug_info["service_status"] = f"error: {str(e)}"
    
    return JSONResponse(debug_info)

@router.post("/configure")
async def configure_avito(
    request: Request,
    username: str = Depends(authenticate)
):
    """Конфигурация подключения к Авито"""
    current_user = get_current_user(username)
    if current_user and current_user.get('role') not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    data = await request.json()
    user_id = data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    try:
        # Переинициализация сервиса с новым user_id
        init_avito_service(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, int(user_id))
        
        # Сохранение user_id в переменные окружения или БД
        os.environ["AVITO_USER_ID"] = str(user_id)
        
        return JSONResponse({"status": "success", "message": "Avito configured successfully"})
    except Exception as e:
        logger.error(f"Failed to configure Avito: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chats")
async def get_chats(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    username: str = Depends(authenticate)
):
    """Получение списка чатов"""
    try:
        service = get_avito_service()
        logger.info(f"Getting chats with params: unread_only={unread_only}, limit={limit}, offset={offset}")
        
        chats = await service.get_chats(unread_only=unread_only, limit=limit, offset=offset)
        
        # Преобразуем в словари для JSON
        chats_data = [chat.to_dict() for chat in chats]
        
        logger.info(f"Returning {len(chats_data)} chats to frontend")
        return JSONResponse({"chats": chats_data, "total": len(chats_data)})
    except Exception as e:
        logger.error(f"Failed to get chats: {e}", exc_info=True)
        if "not initialized" in str(e):
            # Возвращаем более информативное сообщение об ошибке
            return JSONResponse(
                status_code=400,
                content={
                    "error": "not_configured", 
                    "message": "Avito service is not initialized. Call init_avito_service first.",
                    "details": "Требуется авторизация через OAuth. Перейдите в настройки Avito."
                }
            )
        # Если ошибка 403 - проблема с доступом
        if "403" in str(e) or "permission denied" in str(e):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "access_denied",
                    "message": "Access denied to Avito API. Invalid User ID or insufficient permissions.",
                    "details": f"User ID: {service.user_id if service else 'Not set'}"
                }
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chats/{chat_id}")
async def get_chat_info(
    chat_id: str,
    username: str = Depends(authenticate)
):
    """Получение информации о чате"""
    try:
        service = get_avito_service()
        chat = await service.get_chat_info(chat_id)
        
        return JSONResponse(chat.to_dict())
    except Exception as e:
        logger.error(f"Failed to get chat info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chats/{chat_id}/messages")
async def get_messages(
    chat_id: str,
    limit: int = 100,
    offset: int = 0,
    username: str = Depends(authenticate)
):
    """Получение сообщений чата"""
    try:
        service = get_avito_service()
        logger.info(f"Getting messages for chat {chat_id} with params: limit={limit}, offset={offset}")
        
        messages = await service.get_chat_messages(chat_id, limit=limit, offset=offset)
        
        # Отмечаем чат как прочитанный
        try:
            await service.mark_chat_as_read(chat_id)
        except Exception as read_error:
            logger.warning(f"Failed to mark chat as read: {read_error}")
        
        # Преобразуем в словари для JSON
        messages_data = [msg.to_dict() for msg in messages]
        
        logger.info(f"Returning {len(messages_data)} messages for chat {chat_id}")
        return JSONResponse({"messages": messages_data, "total": len(messages_data)})
        
    except Exception as e:
        logger.error(f"Failed to get messages for chat {chat_id}: {e}", exc_info=True)
        
        # Проверяем тип ошибки для более детального ответа
        if "not initialized" in str(e):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "not_configured", 
                    "message": "Avito service is not initialized",
                    "details": "Требуется авторизация через OAuth. Перейдите в настройки Avito."
                }
            )
        elif "403" in str(e) or "permission denied" in str(e):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "access_denied",
                    "message": "Access denied to Avito API",
                    "details": f"Chat ID: {chat_id}"
                }
            )
        elif "404" in str(e) or "not found" in str(e):
            return JSONResponse(
                status_code=404,
                content={
                    "error": "chat_not_found",
                    "message": "Chat not found or no longer accessible",
                    "details": f"Chat ID: {chat_id}"
                }
            )
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats/{chat_id}/messages")
async def send_message(
    chat_id: str,
    request: Request,
    username: str = Depends(authenticate)
):
    """Отправка сообщения"""
    try:
        data = await request.json()
        text = data.get("text")
        
        if not text:
            raise HTTPException(status_code=400, detail="Message text is required")
        
        service = get_avito_service()
        message = await service.send_message(chat_id, text)
        
        # Отправляем через WebSocket всем подключенным клиентам
        await broadcast_message(chat_id, message.to_dict())
        
        return JSONResponse(message.to_dict())
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats/{chat_id}/messages/{message_id}/delete")
async def delete_message(
    chat_id: str,
    message_id: str,
    username: str = Depends(authenticate)
):
    """Удаление сообщения"""
    try:
        service = get_avito_service()
        result = await service.delete_message(chat_id, message_id)
        
        return JSONResponse({"status": "success", "deleted": result})
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats/{chat_id}/images")
async def upload_and_send_image(
    chat_id: str,
    file: UploadFile = File(...),
    username: str = Depends(authenticate)
):
    """Загрузка и отправка изображения"""
    try:
        # Проверка типа файла
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Чтение файла
        image_data = await file.read()
        
        service = get_avito_service()
        
        # Загрузка изображения
        image_id = await service.upload_image(image_data)
        
        # Отправка изображения в чат
        message = await service.send_image(chat_id, image_id)
        
        # Отправляем через WebSocket
        await broadcast_message(chat_id, message.to_dict())
        
        return JSONResponse(message.to_dict())
    except Exception as e:
        logger.error(f"Failed to upload and send image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats/{chat_id}/read")
async def mark_as_read(
    chat_id: str,
    username: str = Depends(authenticate)
):
    """Отметить чат как прочитанный"""
    try:
        service = get_avito_service()
        result = await service.mark_chat_as_read(chat_id)
        
        return JSONResponse({"status": "success", "marked_as_read": result})
    except Exception as e:
        logger.error(f"Failed to mark chat as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chats/{chat_id}/ai-suggest")
async def generate_ai_response(
    chat_id: str,
    username: str = Depends(authenticate)
):
    """Генерация AI ответа для чата"""
    try:
        service = get_avito_service()
        
        # Получаем сообщения чата для анализа контекста
        messages = await service.get_chat_messages(chat_id, limit=20)
        
        # Получаем информацию о чате
        chat = await service.get_chat_info(chat_id)
        
        # Подготавливаем контекст для AI
        context_messages = []
        for msg in messages[-10:]:  # Берём последние 10 сообщений
            if msg.type.value == "text" and msg.content.get("text"):
                sender = "Клиент" if msg.direction == "in" else "Менеджер"
                context_messages.append(f"{sender}: {msg.content['text']}")
        
        # Информация о товаре/услуге
        item_context = ""
        if chat.context and chat.context.get("type") == "item":
            item = chat.context.get("value", {})
            item_context = f"Товар/Услуга: {item.get('title', 'Не указано')}"
            if item.get('price'):
                item_context += f" (Цена: {item['price']} руб.)"
        
        # Генерируем ответ с помощью AI
        from ...services.openai_service import generate_customer_response
        
        conversation_context = "\n".join(context_messages)
        
        ai_response = await generate_customer_response(
            conversation_context, 
            item_context,
            chat.users
        )
        
        return JSONResponse({
            "suggestion": ai_response.get("response", "Извините, не могу сгенерировать ответ в данный момент."),
            "reasoning": ai_response.get("reasoning", ""),
            "confidence": ai_response.get("confidence", 0.5)
        })
        
    except Exception as e:
        logger.error(f"Failed to generate AI response for chat {chat_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "ai_generation_failed",
                "message": "Не удалось сгенерировать AI ответ",
                "details": str(e)
            }
        )

@router.post("/chats/{chat_id}/create-client")
async def create_client_from_chat(
    chat_id: str,
    request: Request,
    username: str = Depends(authenticate)
):
    """Создание клиента из чата Авито с AI-сводкой"""
    try:
        current_user = get_current_user(username)
        with get_db_context() as db:
            service = get_avito_service()
            
            # Получаем информацию о чате
            chat = await service.get_chat_info(chat_id)
            
            # Получаем сообщения для анализа
            messages = await service.get_chat_messages(chat_id, limit=50)
            
            # Находим информацию о собеседнике
            other_user = None
            for user in chat.users:
                if user.get("id") != service.user_id:
                    other_user = user
                    break
            
            if not other_user:
                raise HTTPException(status_code=400, detail="Cannot find chat participant")
            
            # Проверяем, не существует ли уже клиент
            existing_client = db.query(Client).filter(
                Client.source == f"avito_{other_user.get('id')}"
            ).first()
            
            if existing_client:
                return JSONResponse({
                    "status": "exists",
                    "client_id": existing_client.id,
                    "message": "Client already exists"
                })
            
            # Подготавливаем историю сообщений для AI
            conversation_text = ""
            for msg in reversed(messages):  # От старых к новым
                if msg.type.value == "text":
                    sender = "Клиент" if msg.direction == "in" else "Мы"
                    text = msg.content.get("text", "")
                    conversation_text += f"{sender}: {text}\n"
            
            # Генерируем AI-сводку диалога
            summary = ""
            preferences = {}
            
            if conversation_text:
                try:
                    summary = await generate_conversation_summary(conversation_text)
                    
                    # Извлекаем ключевую информацию из сводки
                    if "интерес" in summary.lower():
                        preferences["interests"] = summary
                    if "бюджет" in summary.lower():
                        preferences["budget_mentioned"] = True
                except Exception as e:
                    logger.error(f"Failed to generate AI summary: {e}")
                    summary = "Автоматическая сводка недоступна"
            
            # Получаем информацию об объявлении, если есть
            item_info = ""
            if chat.context and chat.context.get("type") == "item":
                item = chat.context.get("value", {})
                item_info = f"Объявление: {item.get('title', 'Без названия')}"
                if item.get('price'):
                    item_info += f" (Цена: {item['price']} руб.)"
            
            # Создаем нового клиента
            new_client = Client(
                name=other_user.get("name", "Клиент из Авито"),
                type=ClientType.INDIVIDUAL,
                status=ClientStatus.NEW,
                phone=other_user.get("phone"),
                source=f"avito_{other_user.get('id')}",
                description=f"{item_info}\n\nСводка диалога:\n{summary}",
                preferences=preferences,
                communication_history=[{
                    "date": datetime.now().isoformat(),
                    "channel": "avito",
                    "summary": summary,
                    "chat_id": chat_id
                }],
                created_by_id=current_user.get('id', 1) if current_user else 1,
                manager_id=current_user.get('id', 1) if current_user else 1
            )
            
            db.add(new_client)
            db.commit()
            db.refresh(new_client)
            
            return JSONResponse({
                "status": "success",
                "client_id": new_client.id,
                "client_name": new_client.name,
                "summary": summary
            })
            
    except Exception as e:
        logger.error(f"Failed to create client from chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: str
):
    """WebSocket для real-time обновлений чата"""
    await websocket.accept()
    
    # Сохраняем соединение
    if chat_id not in websocket_connections:
        websocket_connections[chat_id] = []
    websocket_connections[chat_id].append(websocket)
    
    try:
        while True:
            # Ждем сообщений от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Обработка различных типов сообщений
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        # Удаляем соединение при отключении
        if chat_id in websocket_connections:
            websocket_connections[chat_id].remove(websocket)
            if not websocket_connections[chat_id]:
                del websocket_connections[chat_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if chat_id in websocket_connections and websocket in websocket_connections[chat_id]:
            websocket_connections[chat_id].remove(websocket)

async def broadcast_message(chat_id: str, message: Dict):
    """Отправка сообщения всем подключенным WebSocket клиентам"""
    if chat_id in websocket_connections:
        disconnected = []
        for ws in websocket_connections[chat_id]:
            try:
                await ws.send_json({
                    "type": "new_message",
                    "message": message
                })
            except:
                disconnected.append(ws)
        
        # Удаляем отключенные соединения
        for ws in disconnected:
            websocket_connections[chat_id].remove(ws)

@router.post("/webhook")
async def avito_webhook(request: Request):
    """Обработка webhook уведомлений от Авито"""
    try:
        data = await request.json()
        
        # Логируем входящее уведомление
        logger.info(f"Received Avito webhook: {data}")
        
        # Обработка нового сообщения
        if data.get("type") == "message":
            chat_id = data.get("chat_id")
            message = data.get("message")
            
            # Отправляем через WebSocket
            if chat_id:
                await broadcast_message(chat_id, message)
            
            # Отправляем Telegram уведомление о новом сообщении
            if chat_id and message:
                try:
                    # Получаем информацию о чате
                    avito_service = AvitoService()
                    chats = await avito_service.get_chats(limit=50)
                    
                    # Находим нужный чат
                    target_chat = None
                    for chat in chats:
                        if chat.id == chat_id:
                            target_chat = chat
                            break
                    
                    if target_chat:
                        # Определяем имя клиента
                        current_user_id = 216012096
                        client_name = "Неизвестный клиент"
                        for user in target_chat.users:
                            if user.get("id") != current_user_id:
                                client_name = user.get("name", "Неизвестный клиент")
                                break
                        
                        # Получаем текст сообщения
                        message_text = ""
                        if isinstance(message, dict):
                            content = message.get("content", {})
                            if isinstance(content, dict):
                                message_text = content.get("text", "")
                            elif isinstance(content, str):
                                message_text = content
                        
                        # Пропускаем уведомления о собственных сообщениях
                        author_id = message.get("author_id")
                        if author_id != current_user_id and message_text:
                            # Отправляем уведомление в Telegram
                            from ...services.notification_service import notify_avito_message
                            await notify_avito_message(chat_id, client_name, message_text)
                            logger.info(f"Telegram notification sent for chat {chat_id}")
                            
                            # TODO: Здесь можно добавить автоматические ответы на сервере
                            # если нужно обрабатывать их даже когда интерфейс не открыт
                    
                except Exception as notify_error:
                    logger.error(f"Error sending Telegram notification: {notify_error}")
        
        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.post("/chats/{chat_id}/create-client")
async def create_client_from_chat(
    chat_id: str,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Создание полноценного клиента из Avito чата с AI анализом"""
    try:
        # Получаем сообщения чата
        avito_service = AvitoService()
        messages = await avito_service.get_chat_messages(chat_id)
        
        if not messages:
            raise HTTPException(status_code=404, detail="Сообщения не найдены")
        
        # Подготавливаем контекст для AI
        conversation_text = []
        current_user_id = 216012096  # ID текущего пользователя
        
        for message in messages:
            author_name = message.get("author", {}).get("name", "Неизвестный")
            content = message.get("content", {}).get("text", "")
            
            if content:
                if message.get("author", {}).get("id") == current_user_id:
                    conversation_text.append(f"Менеджер: {content}")
                else:
                    conversation_text.append(f"Клиент: {content}")
        
        conversation_context = "\n".join(conversation_text[-20:])  # Последние 20 сообщений
        
        # AI анализ для извлечения данных клиента
        from ...services.openai_service import OpenAIService
        ai_service = OpenAIService()
        
        analysis_prompt = f"""
Проанализируй диалог между менеджером IT-компании и клиентом. Извлеки следующую информацию о клиенте:

ДИАЛОГ:
{conversation_context}

Ответь в JSON формате:
{{
    "name": "имя клиента (если указано)",
    "phone": "номер телефона (если указан, в формате +7XXXXXXXXXX)",
    "telegram": "telegram username (если указан, без @)",
    "email": "email адрес (если указан)",
    "requirements": "краткое описание требований/пожеланий клиента (что хочет заказать)"
}}

ВАЖНО: Если информация не найдена, оставь поле пустым (""). Телефон нормализуй к формату +7XXXXXXXXXX.
"""
        
        try:
            ai_response = await ai_service.generate_response_with_model(
                analysis_prompt, 
                model="openai/gpt-4o-mini"
            )
            
            # Парсим JSON ответ от AI
            import json
            import re
            
            # Извлекаем JSON из ответа AI
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
            else:
                # Если JSON не найден, возвращаем пустую структуру
                analysis_data = {
                    "name": "",
                    "phone": "",
                    "telegram": "",
                    "email": "",
                    "requirements": ""
                }
                
        except Exception as ai_error:
            logger.error(f"AI analysis error: {ai_error}")
            # Возвращаем пустую структуру при ошибке AI
            analysis_data = {
                "name": "",
                "phone": "",
                "telegram": "",
                "email": "",
                "requirements": ""
            }
        
        # Создаём клиента в базе данных
        client_name = analysis_data.get("name") or "Клиент Avito"
        
        # Проверяем, не существует ли уже клиент с таким chat_id
        existing_client = db.query(Client).filter(Client.avito_chat_id == chat_id).first()
        
        if existing_client:
            # Обновляем существующего клиента
            client = existing_client
            client.name = client_name
            if analysis_data.get("phone"):
                client.phone = analysis_data["phone"]
            if analysis_data.get("email"):
                client.email = analysis_data["email"]
            if analysis_data.get("telegram"):
                client.telegram = analysis_data["telegram"]
        else:
            # Создаём нового клиента
            client = Client(
                name=client_name,
                phone=analysis_data.get("phone"),
                email=analysis_data.get("email"), 
                telegram=analysis_data.get("telegram"),
                source="Avito",
                type=ClientType.INDIVIDUAL,
                status=ClientStatus.NEW,
                avito_chat_id=chat_id,
                avito_status=AvitoClientStatus.WARM_CONTACT,
                avito_notes=f"Требования: {analysis_data.get('requirements', 'Не указаны')}",
                description=analysis_data.get("requirements", "")
            )
            db.add(client)
        
        # Сохраняем историю диалога в клиенте
        dialog_history = []
        for message in messages[-10:]:  # Последние 10 сообщений
            dialog_history.append({
                "timestamp": message.get("created", ""),
                "author_id": message.get("author", {}).get("id"),
                "author_name": message.get("author", {}).get("name", ""),
                "text": message.get("content", {}).get("text", ""),
                "is_client": message.get("author", {}).get("id") != 216012096
            })
        
        client.avito_dialog_history = dialog_history
        client.communication_history = dialog_history  # Дублируем в общую историю
        
        db.commit()
        
        logger.info(f"Client created/updated from chat {chat_id}: {client.id}")
        
        return JSONResponse({
            "status": "success",
            "message": "Клиент успешно создан/обновлен",
            "client_id": client.id,
            "client_data": {
                "name": client.name,
                "phone": client.phone,
                "email": client.email,
                "telegram": client.telegram,
                "avito_status": client.avito_status.value if client.avito_status else None,
                "requirements": analysis_data.get("requirements", "")
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating client from chat {chat_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания клиента: {str(e)}")

@router.post("/polling/start")
async def start_polling(current_user: AdminUser = Depends(get_current_admin_user)):
    """Запуск мониторинга новых сообщений"""
    try:
        if not polling_service.polling_active:
            # Запускаем polling в фоне
            import asyncio
            asyncio.create_task(polling_service.start_polling())
            
        return JSONResponse({"status": "success", "message": "Мониторинг запущен"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.post("/polling/stop")
async def stop_polling(current_user: AdminUser = Depends(get_current_admin_user)):
    """Остановка мониторинга"""
    try:
        polling_service.stop_polling()
        return JSONResponse({"status": "success", "message": "Мониторинг остановлен"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.post("/auto-response/toggle")
async def toggle_auto_response(
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Переключение автоответов"""
    try:
        data = await request.json()
        enabled = data.get('enabled', False)
        
        polling_service.set_auto_response(enabled)
        
        # Если включаем автоответы, убеждаемся что polling запущен
        if enabled and not polling_service.polling_active:
            import asyncio
            asyncio.create_task(polling_service.start_polling())
        
        return JSONResponse({
            "status": "success", 
            "message": f"Автоответы {'включены' if enabled else 'выключены'}",
            "enabled": enabled
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.get("/polling/status")
async def get_polling_status(current_user: AdminUser = Depends(get_current_admin_user)):
    """Статус мониторинга и автоответов"""
    return JSONResponse({
        "polling_active": polling_service.polling_active,
        "auto_response_enabled": polling_service.auto_response_enabled
    })

@router.post("/chats/{chat_id}/status")
async def update_client_avito_status(
    chat_id: str,
    request: Request,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Обновление статуса клиента в Avito"""
    try:
        data = await request.json()
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        if not new_status or new_status not in [s.value for s in AvitoClientStatus]:
            return JSONResponse({"status": "error", "message": "Неверный статус"}, status_code=400)
        
        # Находим клиента по chat_id
        client = db.query(Client).filter(Client.avito_chat_id == chat_id).first()
        
        if not client:
            return JSONResponse({"status": "error", "message": "Клиент не найден"}, status_code=404)
        
        # Обновляем статус
        client.avito_status = AvitoClientStatus(new_status)
        if notes:
            current_notes = client.avito_notes or ""
            client.avito_notes = f"{current_notes}\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
        
        db.commit()
        
        return JSONResponse({
            "status": "success",
            "message": f"Статус клиента обновлен на {new_status}"
        })
        
    except Exception as e:
        logger.error(f"Error updating client status: {e}")
        db.rollback()
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.get("/chats/{chat_id}/export")
async def export_chat_dialog(
    chat_id: str,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Экспорт переписки в текстовый файл"""
    try:
        avito_service = AvitoService()
        messages = await avito_service.get_chat_messages(chat_id)
        
        if not messages:
            return JSONResponse({"status": "error", "message": "Сообщения не найдены"}, status_code=404)
        
        # Формируем текстовый файл
        export_text = f"Экспорт переписки Avito\nЧат ID: {chat_id}\nДата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        export_text += "="*50 + "\n\n"
        
        current_user_id = 216012096
        
        for message in messages:
            timestamp = message.get("created", "")
            author = message.get("author", {})
            author_name = author.get("name", "Неизвестный")
            author_id = author.get("id")
            content = message.get("content", {}).get("text", "")
            
            if content:
                role = "МЕНЕДЖЕР" if author_id == current_user_id else "КЛИЕНТ"
                export_text += f"[{timestamp}] {role} ({author_name}):\n{content}\n\n"
        
        # Возвращаем файл
        from fastapi.responses import Response
        
        filename = f"avito_chat_{chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        return Response(
            content=export_text.encode('utf-8'),
            media_type='text/plain; charset=utf-8',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting chat: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


# WebSocket connections для real-time обновлений
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket подключен. Всего подключений: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket отключен. Всего подключений: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения WebSocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """Отправка сообщения всем подключенным клиентам"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Ошибка отправки broadcast сообщения: {e}")
                disconnected.append(connection)
        
        # Удаляем неактивные соединения
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time обновлений чатов"""
    await manager.connect(websocket)
    try:
        while True:
            # Ждем сообщения от клиента (ping для поддержания соединения)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Ошибка WebSocket: {e}")
        manager.disconnect(websocket)


@router.post("/webhook")
async def avito_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint для получения webhook уведомлений от Avito
    Обновляет чаты в реальном времени
    """
    try:
        # Получаем данные webhook
        webhook_data = await request.json()
        logger.info(f"Получен webhook от Avito: {json.dumps(webhook_data, indent=2, ensure_ascii=False)}")
        
        # Добавляем обработку в фон
        background_tasks.add_task(process_webhook_data, webhook_data)
        
        # Возвращаем успешный ответ быстро (в пределах 2 секунд как требует Avito)
        return {"ok": True, "status": "received"}
        
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        # Все равно возвращаем 200, чтобы Avito не отключил webhook
        return {"ok": False, "error": str(e)}


async def process_webhook_data(webhook_data: dict):
    """Обработка данных webhook в фоне"""
    try:
        # Определяем тип события
        if "message" in webhook_data:
            await handle_new_message_webhook(webhook_data)
        elif "chat" in webhook_data:
            await handle_chat_update_webhook(webhook_data)
        else:
            logger.info(f"Неизвестный тип webhook события: {webhook_data}")
            
    except Exception as e:
        logger.error(f"Ошибка обработки webhook данных: {e}")


async def handle_new_message_webhook(webhook_data: dict):
    """Обработка нового сообщения из webhook"""
    try:
        message_data = webhook_data.get("message", {})
        chat_id = message_data.get("chat_id")
        author_id = message_data.get("author_id")
        
        if not chat_id:
            return
            
        logger.info(f"Новое сообщение в чате {chat_id} от {author_id}")
        
        # Проверяем что сообщение от клиента (не от нас)
        current_user_id = int(settings.AVITO_USER_ID)
        if author_id == current_user_id:
            logger.info("Сообщение от нас самих, игнорируем")
            return
        
        # Отправляем уведомление в Telegram (если настроено)
        notification_service = NotificationService()
        if notification_service:
            try:
                message_text = message_data.get("content", {}).get("text", "Новое сообщение")
                if len(message_text) > 100:
                    message_text = message_text[:100] + "..."
                
                notification_text = f"""
🔔 <b>Новое сообщение Avito</b>

💬 <b>Текст:</b> {message_text}
🔗 <a href="https://{settings.DOMAIN}/admin/avito/">Открыть чат</a>
                """
                
                await notification_service.send_admin_notification(notification_text.strip())
                logger.info("Уведомление отправлено в Telegram")
                
            except Exception as e:
                logger.error(f"Ошибка отправки Telegram уведомления: {e}")
        
        # Отправляем обновление через WebSocket
        await manager.broadcast({
            "type": "new_message",
            "chat_id": chat_id,
            "message": message_data,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"WebSocket уведомление отправлено для чата {chat_id}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки нового сообщения webhook: {e}")


async def handle_chat_update_webhook(webhook_data: dict):
    """Обработка обновления чата из webhook"""
    try:
        chat_data = webhook_data.get("chat", {})
        chat_id = chat_data.get("id")
        
        if not chat_id:
            return
            
        logger.info(f"Обновление чата {chat_id}")
        
        # Отправляем обновление через WebSocket
        await manager.broadcast({
            "type": "chat_update", 
            "chat_id": chat_id,
            "chat": chat_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Ошибка обработки обновления чата webhook: {e}")


@router.get("/webhook/status")
async def webhook_status():
    """Проверка статуса webhook endpoint"""
    return {
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "websocket_connections": len(manager.active_connections),
        "message": "Avito webhook endpoint is working"
    }