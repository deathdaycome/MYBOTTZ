"""
Роутер для интеграции с Авито мессенджером
"""

from fastapi import APIRouter, Depends, Request, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
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

from ...database.database import get_db_context
from ...database.crm_models import Client, ClientStatus, ClientType
from ...database.models import AdminUser
from ...services.avito_service import get_avito_service, init_avito_service, AvitoService
from ...services.openai_service import generate_conversation_summary
from ..navigation import get_navigation_items
from ...config.settings import settings
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/avito", tags=["avito"])
templates = Jinja2Templates(directory="app/admin/templates")

# Локальная аутентификация для избежания циклического импорта
security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Аутентификация пользователя"""
    correct_username = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        # Проверяем других пользователей в БД
        with get_db_context() as db:
            admin_user = db.query(AdminUser).filter(AdminUser.username == credentials.username).first()
            if admin_user and admin_user.check_password(credentials.password) and admin_user.is_active:
                return credentials.username
        
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"}
        )
    
    return credentials.username

def get_current_user(username: str):
    """Получение текущего пользователя"""
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
AVITO_CLIENT_ID = os.getenv("AVITO_CLIENT_ID", "fakHmzyCUJTM56AEQv8i")
AVITO_CLIENT_SECRET = os.getenv("AVITO_CLIENT_SECRET", "tMJVVuzTkNUP3Dh2c08V_f7OZG1xNKUrPLzl9xJd")
AVITO_USER_ID = os.getenv("AVITO_USER_ID")

# WebSocket connections storage
websocket_connections = {}

@router.on_event("startup")
async def startup_event():
    """Инициализация сервиса при старте"""
    if AVITO_USER_ID:
        try:
            init_avito_service(AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, int(AVITO_USER_ID))
            logger.info("Avito service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Avito service: {e}")

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

@router.post("/configure")
async def configure_avito(
    request: Request,
    username: str = Depends(authenticate)
):
    """Конфигурация подключения к Авито"""
    current_user = get_current_user(username)
    if current_user.get('role') not in ["owner", "admin"]:
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
        chats = await service.get_chats(unread_only=unread_only, limit=limit, offset=offset)
        
        # Преобразуем в словари для JSON
        chats_data = [chat.to_dict() for chat in chats]
        
        return JSONResponse({"chats": chats_data, "total": len(chats_data)})
    except Exception as e:
        logger.error(f"Failed to get chats: {e}")
        if "not initialized" in str(e):
            raise HTTPException(status_code=400, detail="Avito service not configured. Please set User ID.")
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
        messages = await service.get_chat_messages(chat_id, limit=limit, offset=offset)
        
        # Отмечаем чат как прочитанный
        await service.mark_chat_as_read(chat_id)
        
        # Преобразуем в словари для JSON
        messages_data = [msg.to_dict() for msg in messages]
        
        return JSONResponse({"messages": messages_data, "total": len(messages_data)})
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
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

@router.post("/chats/{chat_id}/create-client")
async def create_client_from_chat(
    chat_id: str,
    request: Request,
    username: str = Depends(authenticate)
):
    """Создание клиента из чата Авито с AI-сводкой"""
    try:
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
                created_by_id=get_current_user(username).get('id', 1),
                manager_id=get_current_user(username).get('id', 1)
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
        
        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)