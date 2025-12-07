from fastapi import APIRouter, Request, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import shutil
import os
import uuid

from ...database.database import get_db
from ...database.models import ProjectChat, ProjectChatMessage, Project, AdminUser
from ..middleware.auth import get_current_admin_user

router = APIRouter()
templates = Jinja2Templates(directory="app/admin/templates")

# Страница списка чатов
@router.get("/chats", response_class=HTMLResponse)
async def chats_page(
    request: Request,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Страница списка чатов"""
    return templates.TemplateResponse("chats_modern.html", {
        "request": request,
        "current_user": current_user
    })


# Страница детального чата
@router.get("/chats/{chat_id}", response_class=HTMLResponse)
async def chat_detail_page(
    chat_id: int,
    request: Request,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Страница детального просмотра чата"""
    chat = db.query(ProjectChat).filter(ProjectChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Загружаем проект
    project = db.query(Project).filter(Project.id == chat.project_id).first()

    return templates.TemplateResponse("chat_detail.html", {
        "request": request,
        "current_user": current_user,
        "chat": chat
    })


# API: Получить список всех чатов
@router.get("/api/chats")
async def get_chats(
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """API: Получить чаты проектов (с фильтрацией для исполнителей)"""
    print(f"🔍 Запрос чатов от админ-пользователя: id={current_user.get('id')}, username={current_user.get('username')}, role={current_user.get('role')}")

    # Получаем чаты с учетом роли пользователя
    query = db.query(ProjectChat).join(Project)

    # Если пользователь - исполнитель, показываем только его проекты
    if current_user.get("role") == "executor":
        print(f"👷 Пользователь - исполнитель, фильтруем по assigned_executor_id={current_user.get('id')}")
        query = query.filter(Project.assigned_executor_id == current_user.get("id"))

        # Проверим, сколько проектов назначено на этого исполнителя
        executor_projects = db.query(Project).filter(Project.assigned_executor_id == current_user.get("id")).all()
        print(f"📊 Найдено проектов для исполнителя: {len(executor_projects)}")
        for p in executor_projects[:5]:
            print(f"  - Проект ID:{p.id}, Название:{p.title}")

    chats = query.all()
    print(f"✅ Возвращаем чатов: {len(chats)}")

    result = []
    for chat in chats:
        project = db.query(Project).filter(Project.id == chat.project_id).first()

        # Получаем имя клиента
        client_name = None
        if project.user:
            if project.user.first_name:
                client_name = project.user.first_name
                if project.user.last_name:
                    client_name += f' {project.user.last_name}'
            elif project.user.username:
                client_name = f'@{project.user.username}'

        # Получаем последнее сообщение
        last_message = db.query(ProjectChatMessage).filter(
            ProjectChatMessage.chat_id == chat.id
        ).order_by(ProjectChatMessage.created_at.desc()).first()

        result.append({
            'id': chat.id,
            'project': {
                'id': project.id,
                'title': project.title,
                'client_name': client_name,
                'status': project.status
            },
            'last_message': {
                'sender_type': last_message.sender_type,
                'message_text': last_message.message_text,
                'created_at': last_message.created_at.isoformat()
            } if last_message else None,
            'last_message_at': chat.last_message_at.isoformat() if chat.last_message_at else None,
            'unread_by_executor': chat.unread_by_executor,
            'unread_by_client': chat.unread_by_client,
            'is_pinned_by_owner': chat.is_pinned_by_owner if hasattr(chat, 'is_pinned_by_owner') else False,
            'is_hidden_by_owner': chat.is_hidden_by_owner if hasattr(chat, 'is_hidden_by_owner') else False,
            'created_at': chat.created_at.isoformat()
        })

    return result


# API: Получить сообщения чата
@router.get("/api/chats/{chat_id}/messages")
async def get_chat_messages(
    chat_id: int,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """API: Получить сообщения чата"""
    chat = db.query(ProjectChat).filter(ProjectChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Получаем все сообщения
    messages = db.query(ProjectChatMessage).filter(
        ProjectChatMessage.chat_id == chat_id
    ).order_by(ProjectChatMessage.created_at.asc()).all()

    # Помечаем сообщения от клиента как прочитанные исполнителем
    for msg in messages:
        if not msg.is_read_by_executor and msg.sender_type == 'client':
            msg.is_read_by_executor = True
            msg.read_at = datetime.utcnow()

    chat.unread_by_executor = 0
    db.commit()

    return {
        'messages': [
            {
                'id': msg.id,
                'sender_type': msg.sender_type,
                'message_text': msg.message_text,
                'attachments': msg.attachments or [],
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read_by_executor if msg.sender_type == 'client' else msg.is_read_by_client
            }
            for msg in messages
        ]
    }


# API: Отправить сообщение в чат
@router.post("/api/chats/{chat_id}/messages")
async def send_chat_message(
    chat_id: int,
    message_text: Optional[str] = Form(None),
    attachments: Optional[List[UploadFile]] = File(None),
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """API: Отправить сообщение в чат от исполнителя"""
    chat = db.query(ProjectChat).filter(ProjectChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Обрабатываем вложения
    attachment_files = []
    if attachments:
        upload_dir = "uploads/chat_attachments"
        os.makedirs(upload_dir, exist_ok=True)

        for file in attachments:
            if file.filename:
                # Генерируем уникальное имя файла
                file_ext = os.path.splitext(file.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(upload_dir, unique_filename)

                # Сохраняем файл
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                attachment_files.append({
                    'filename': file.filename,
                    'url': f'/{file_path}',
                    'size': os.path.getsize(file_path)
                })

    # Создаем сообщение
    message = ProjectChatMessage(
        chat_id=chat_id,
        sender_type='executor',
        message_text=message_text,
        attachments=attachment_files if attachment_files else None,
        created_at=datetime.utcnow(),
        is_read_by_executor=True,
        is_read_by_client=False
    )

    db.add(message)

    # Обновляем чат
    chat.last_message_at = datetime.utcnow()
    chat.unread_by_client += 1

    db.commit()
    db.refresh(message)

    # Отправляем уведомление клиенту в Telegram
    project = db.query(Project).filter(Project.id == chat.project_id).first()
    if project and project.user and project.user.telegram_id:
        from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
        from ...config.settings import settings
        from datetime import datetime
        import asyncio

        # Получаем имя исполнителя
        executor_name = 'Исполнитель'
        if current_user.get('first_name'):
            executor_name = current_user['first_name']
            if current_user.get('last_name'):
                executor_name += f" {current_user['last_name']}"
        elif current_user.get('username'):
            executor_name = current_user['username']

        print(f"🔔 [NOTIFICATION DEBUG] Отправляем уведомление клиенту {project.user.telegram_id}, от исполнителя {executor_name}")

        # Отправляем уведомление асинхронно
        async def send_notification():
            try:
                bot = Bot(settings.BOT_TOKEN)
                preview_text = message_text[:150] + "..." if message_text and len(message_text) > 150 else (message_text or "📎 Вложение")

                notification_message = f"""
💬 <b>Новое сообщение в проекте</b>

📋 <b>Проект:</b> {project.title}
👤 <b>От:</b> {executor_name} (Исполнитель)

💬 <b>Сообщение:</b>
{preview_text}

🕐 <b>Время:</b> {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}
                """

                # Для клиента используем WebAppInfo чтобы открыть мини-приложение
                miniapp_url = f"{settings.MINIAPP_URL}#/chat/{chat_id}"
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton("💬 Ответить", web_app=WebAppInfo(url=miniapp_url))
                ]])

                await bot.send_message(
                    chat_id=project.user.telegram_id,
                    text=notification_message,
                    parse_mode='HTML',
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
                print(f"✅ [NOTIFICATION DEBUG] Уведомление клиенту успешно отправлено!")
            except Exception as e:
                print(f"❌ [NOTIFICATION DEBUG] Ошибка отправки уведомления клиенту: {e}")

        asyncio.create_task(send_notification())

    return {
        'id': message.id,
        'sender_type': message.sender_type,
        'message_text': message.message_text,
        'attachments': message.attachments or [],
        'created_at': message.created_at.isoformat()
    }


# API: Закрепить/открепить чат
@router.post("/api/chats/{chat_id}/pin")
async def toggle_pin_chat(
    chat_id: int,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """API: Закрепить или открепить чат (только для owner/admin)"""
    # Проверяем права доступа (только owner и admin могут закреплять чаты)
    if current_user.get("role") not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owner and admin can pin chats")

    chat = db.query(ProjectChat).filter(ProjectChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Переключаем состояние закрепления
    current_pinned = chat.is_pinned_by_owner if hasattr(chat, 'is_pinned_by_owner') else False
    chat.is_pinned_by_owner = not current_pinned

    db.commit()

    return {
        'id': chat.id,
        'is_pinned_by_owner': chat.is_pinned_by_owner,
        'message': 'Чат закреплен' if chat.is_pinned_by_owner else 'Чат откреплен'
    }


# API: Скрыть/показать чат
@router.post("/api/chats/{chat_id}/hide")
async def toggle_hide_chat(
    chat_id: int,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """API: Скрыть или показать чат (только для owner/admin)"""
    # Проверяем права доступа (только owner и admin могут скрывать чаты)
    if current_user.get("role") not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only owner and admin can hide chats")

    chat = db.query(ProjectChat).filter(ProjectChat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Переключаем состояние скрытия
    current_hidden = chat.is_hidden_by_owner if hasattr(chat, 'is_hidden_by_owner') else False
    chat.is_hidden_by_owner = not current_hidden

    db.commit()

    return {
        'id': chat.id,
        'is_hidden_by_owner': chat.is_hidden_by_owner,
        'message': 'Чат скрыт' if chat.is_hidden_by_owner else 'Чат возвращен'
    }
