from fastapi import APIRouter, Depends, Header, HTTPException, Form, File, UploadFile, Request
from sqlalchemy.orm import Session
from typing import Optional, List
import hmac
import hashlib
import urllib.parse
from datetime import datetime, timedelta
import os
import uuid
import shutil

from ..database.database import get_db, get_or_create_user, create_project
from ..database.models import User, Project, ProjectRevision, RevisionMessage, RevisionMessageFile, RevisionFile, ProjectChat, ProjectChatMessage, AdminUser
from ..config.settings import get_settings

router = APIRouter(prefix="/api", tags=["miniapp"])
settings = get_settings()


def verify_telegram_web_app_data(init_data: str) -> dict:
    """
    Проверяет подлинность данных от Telegram WebApp
    """
    try:
        # Парсим init_data
        parsed_data = dict(urllib.parse.parse_qsl(init_data))

        # Извлекаем хеш
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            raise HTTPException(status_code=401, detail="No hash provided")

        # Сортируем параметры и создаем data-check-string
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)

        # Создаем secret_key
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()

        # Вычисляем хеш
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Сравниваем хеши
        if calculated_hash != received_hash:
            raise HTTPException(status_code=401, detail="Invalid hash")

        return parsed_data

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Verification failed: {str(e)}")


async def get_current_user(
    x_telegram_init_data: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Получает текущего пользователя из Telegram init data
    """
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="No Telegram data provided")

    # Проверяем подлинность данных
    parsed_data = verify_telegram_web_app_data(x_telegram_init_data)

    # Извлекаем данные пользователя
    import json
    user_data = json.loads(parsed_data.get('user', '{}'))

    if not user_data:
        raise HTTPException(status_code=401, detail="No user data")

    # Получаем или создаем пользователя
    user = get_or_create_user(
        db=db,
        telegram_id=user_data['id'],
        username=user_data.get('username'),
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name')
    )

    return user


# === ПРОЕКТЫ ===

@router.get("/projects")
async def get_user_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все проекты пользователя"""
    print(f"🔍 Mini App: Запрос проектов от пользователя: id={current_user.id}, telegram_id={current_user.telegram_id}, username={current_user.username}")

    # Фильтруем проекты по user_id ИЛИ по client_telegram_id
    from sqlalchemy import or_, and_
    projects = db.query(Project).filter(
        or_(
            Project.user_id == current_user.id,
            and_(
                Project.client_telegram_id.isnot(None),
                Project.client_telegram_id == str(current_user.telegram_id)
            )
        ),
        Project.is_archived == False  # Не показываем архивные проекты
    ).order_by(Project.created_at.desc()).all()

    print(f"📊 Найдено проектов: {len(projects)}")
    if projects:
        for p in projects[:3]:
            print(f"  - ID: {p.id}, Название: {p.title}, user_id: {p.user_id}, client_telegram_id: {p.client_telegram_id}")

    return [project.to_dict() for project in projects]


@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить детали проекта"""
    from sqlalchemy import or_
    project = db.query(Project).filter(
        Project.id == project_id,
        or_(
            Project.user_id == current_user.id,
            Project.client_telegram_id == str(current_user.telegram_id)
        )
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project.to_dict()


@router.get("/projects/stats")
async def get_projects_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статистику по проектам"""
    from sqlalchemy import or_, and_

    # Получаем проекты где:
    # 1. user_id совпадает (владелец проекта)
    # 2. ИЛИ client_telegram_id совпадает с telegram_id пользователя (клиент проекта)
    projects = db.query(Project).filter(
        or_(
            Project.user_id == current_user.id,
            and_(
                Project.client_telegram_id.isnot(None),
                Project.client_telegram_id == str(current_user.telegram_id)
            )
        ),
        Project.is_archived == False  # Не показываем архивные проекты
    ).all()

    stats = {
        'total': len(projects),
        'in_progress': sum(1 for p in projects if p.status in ['in_progress', 'testing']),
        'completed': sum(1 for p in projects if p.status == 'completed'),
        'total_cost': sum(p.final_cost or p.estimated_cost or 0 for p in projects)
    }

    return stats


@router.get("/revisions/stats")
async def get_all_revisions_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить общую статистику по всем правкам пользователя"""
    # Получаем все проекты пользователя (по user_id ИЛИ по client_telegram_id)
    from sqlalchemy import or_
    user_projects = db.query(Project).filter(
        or_(
            Project.user_id == current_user.id,
            Project.client_telegram_id == str(current_user.telegram_id)
        )
    ).all()

    project_ids = [p.id for p in user_projects]

    # Получаем все правки по всем проектам пользователя
    revisions = db.query(ProjectRevision).filter(
        ProjectRevision.project_id.in_(project_ids)
    ).all() if project_ids else []

    # Считаем открытые правки (не completed и не rejected)
    open_revisions = sum(1 for r in revisions if r.status not in ['completed', 'rejected', 'approved'])

    stats = {
        'total': len(revisions),
        'open': open_revisions,
        'pending': sum(1 for r in revisions if r.status == 'pending'),
        'in_progress': sum(1 for r in revisions if r.status == 'in_progress'),
        'completed': sum(1 for r in revisions if r.status in ['completed', 'approved']),
        'needs_rework': sum(1 for r in revisions if r.status == 'needs_rework'),
    }

    return stats


@router.post("/projects/quick")
async def create_quick_project(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать проект через быстрый запрос"""

    # Определяем стоимость на основе бюджета
    budget = data.get('budget', '')
    estimated_cost = 0.0
    if "До 50" in budget:
        estimated_cost = 50000.0
    elif "50-100" in budget or "50 000 - 100 000" in budget:
        estimated_cost = 75000.0
    elif "100-200" in budget or "100 000 - 200 000" in budget:
        estimated_cost = 150000.0
    elif "200-500" in budget or "200 000 - 500 000" in budget:
        estimated_cost = 350000.0
    elif "Более 500" in budget:
        estimated_cost = 500000.0

    # Определяем плановую дату завершения на основе deadline
    deadline_str = data.get('deadline', '')
    days_to_add = 30  # По умолчанию - месяц

    if "быстрее" in deadline_str.lower():
        days_to_add = 7
    elif "месяца" in deadline_str.lower():
        days_to_add = 30
    elif "1-3" in deadline_str:
        days_to_add = 60
    elif "3-6" in deadline_str:
        days_to_add = 120
    elif "6" in deadline_str:
        days_to_add = 180

    planned_end_date = datetime.utcnow() + timedelta(days=days_to_add)

    # Создаем проект
    project_data = {
        'title': data['title'],
        'description': data['description'],
        'project_type': data['project_type'],
        'status': 'new',
        'estimated_cost': estimated_cost,
        'complexity': 'medium',
        'planned_end_date': planned_end_date,
        'structured_tz': {
            'quick_request': True,
            'budget': budget,
            'deadline': deadline_str,
        }
    }

    project = create_project(db, current_user.id, project_data)
    db.commit()

    return project.to_dict()


# === ПРАВКИ ===

@router.get("/projects/{project_id}/revisions")
async def get_project_revisions(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все правки проекта"""
    # Проверяем, что проект принадлежит пользователю
    from sqlalchemy import or_
    project = db.query(Project).filter(
        Project.id == project_id,
        or_(
            Project.user_id == current_user.id,
            Project.client_telegram_id == str(current_user.telegram_id)
        )
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    revisions = db.query(ProjectRevision).filter(
        ProjectRevision.project_id == project_id
    ).order_by(ProjectRevision.created_at.desc()).all()

    return {
        'revisions': [
            {
                'id': r.id,
                'project_id': r.project_id,
                'revision_number': r.revision_number,
                'title': r.title,
                'description': r.description,
                'status': r.status,
                'priority': r.priority,
                'progress': r.progress if r.progress is not None else 0,
                'time_spent_seconds': r.time_spent_seconds if r.time_spent_seconds is not None else 0,
                'estimated_time': r.estimated_time,
                'actual_time': r.actual_time,
                'created_by_id': r.created_by_id,
                'assigned_to_id': r.assigned_to_id,
                'assigned_to_username': r.assigned_to.username if r.assigned_to else None,
                'project_title': project.title,
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None,
                'completed_at': r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in revisions
        ]
    }


@router.get("/revisions/{revision_id}")
async def get_revision(
    revision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить детали правки"""
    revision = db.query(ProjectRevision).filter(
        ProjectRevision.id == revision_id
    ).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

    # Получаем проект и проверяем доступ
    from sqlalchemy import or_
    project = db.query(Project).filter(
        Project.id == revision.project_id,
        or_(
            Project.user_id == current_user.id,
            Project.client_telegram_id == str(current_user.telegram_id)
        )
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        'revision': {
            'id': revision.id,
            'project_id': revision.project_id,
            'project_title': project.title if project else None,
            'revision_number': revision.revision_number,
            'title': revision.title,
            'description': revision.description,
            'status': revision.status,
            'priority': revision.priority,
            'progress': revision.progress if revision.progress is not None else 0,
            'time_spent_seconds': revision.time_spent_seconds if revision.time_spent_seconds is not None else 0,
            'estimated_time': revision.estimated_time,
            'actual_time': revision.actual_time,
            'created_by_id': revision.created_by_id,
            'assigned_to_id': revision.assigned_to_id,
            'assigned_to_username': revision.assigned_to.username if revision.assigned_to else None,
            'created_at': revision.created_at.isoformat() if revision.created_at else None,
            'updated_at': revision.updated_at.isoformat() if revision.updated_at else None,
            'completed_at': revision.completed_at.isoformat() if revision.completed_at else None,
        }
    }


@router.post("/revisions")
async def create_revision(
    project_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form('normal'),
    files: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новую правку с файлами"""
    # Проверяем, что проект принадлежит пользователю
    from sqlalchemy import or_
    project = db.query(Project).filter(
        Project.id == project_id,
        or_(
            Project.user_id == current_user.id,
            Project.client_telegram_id == str(current_user.telegram_id)
        )
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Получаем номер следующей правки
    max_revision_number = db.query(ProjectRevision.revision_number).filter(
        ProjectRevision.project_id == project_id
    ).order_by(ProjectRevision.revision_number.desc()).first()

    next_revision_number = (max_revision_number[0] if max_revision_number else 0) + 1

    # Создаем правку
    revision = ProjectRevision(
        project_id=project_id,
        revision_number=next_revision_number,
        title=title,
        description=description,
        priority=priority,
        status='pending',
        created_by_id=current_user.id
    )

    db.add(revision)
    db.flush()  # Получаем ID правки для сохранения файлов

    # Сохраняем файлы
    saved_files = []
    if files:
        upload_dir = f"uploads/revisions/{revision.id}"
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            if file.filename:
                # Генерируем уникальное имя
                file_ext = os.path.splitext(file.filename)[1]
                unique_name = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(upload_dir, unique_name)

                # Сохраняем файл
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                # Определяем тип файла
                file_type = 'image' if file.content_type and file.content_type.startswith('image/') else \
                           'video' if file.content_type and file.content_type.startswith('video/') else 'document'

                # Создаем запись в БД
                revision_file = RevisionFile(
                    revision_id=revision.id,
                    filename=unique_name,
                    original_filename=file.filename,
                    file_type=file_type,
                    file_size=os.path.getsize(file_path),
                    file_path=file_path,
                    uploaded_by_type='client',
                    uploaded_by_user_id=current_user.id
                )
                db.add(revision_file)
                saved_files.append(revision_file)

    db.commit()
    db.refresh(revision)

    return {
        'id': revision.id,
        'project_id': revision.project_id,
        'revision_number': revision.revision_number,
        'title': revision.title,
        'description': revision.description,
        'status': revision.status,
        'priority': revision.priority,
        'created_at': revision.created_at.isoformat() if revision.created_at else None,
        'files': [
            {
                'id': f.id,
                'filename': f.filename,
                'original_filename': f.original_filename,
                'file_type': f.file_type,
                'file_size': f.file_size,
                'file_url': f'/{f.file_path}',
            }
            for f in saved_files
        ]
    }


@router.get("/projects/{project_id}/revisions/stats")
async def get_revision_stats(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статистику по правкам проекта"""
    # Проверяем, что проект принадлежит пользователю
    from sqlalchemy import or_
    project = db.query(Project).filter(
        Project.id == project_id,
        or_(
            Project.user_id == current_user.id,
            Project.client_telegram_id == str(current_user.telegram_id)
        )
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    revisions = db.query(ProjectRevision).filter(
        ProjectRevision.project_id == project_id
    ).all()

    stats = {
        'total': len(revisions),
        'pending': sum(1 for r in revisions if r.status == 'pending'),
        'in_progress': sum(1 for r in revisions if r.status == 'in_progress'),
        'completed': sum(1 for r in revisions if r.status == 'completed'),
        'rejected': sum(1 for r in revisions if r.status == 'rejected'),
    }

    return {'stats': stats}


@router.get("/revisions/{revision_id}/messages")
async def get_revision_messages(
    revision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить сообщения правки (чат)"""
    # Проверяем доступ к правке через проект
    revision = db.query(ProjectRevision).filter(
        ProjectRevision.id == revision_id
    ).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

    # Проверяем доступ к проекту
    from sqlalchemy import or_
    project = db.query(Project).filter(
        Project.id == revision.project_id,
        or_(
            Project.user_id == current_user.id,
            Project.client_telegram_id == str(current_user.telegram_id)
        )
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = db.query(RevisionMessage).filter(
        RevisionMessage.revision_id == revision_id
    ).order_by(RevisionMessage.created_at.asc()).all()

    return {
        'messages': [
            {
                'id': m.id,
                'revision_id': m.revision_id,
                'sender_type': m.sender_type,
                'sender_user_id': m.sender_user_id,
                'message': m.message,
                'is_internal': m.is_internal,
                'created_at': m.created_at.isoformat() if m.created_at else None,
                'files': [
                    {
                        'id': f.id,
                        'filename': f.filename,
                        'original_filename': f.original_filename,
                        'file_type': f.file_type,
                        'file_size': f.file_size,
                        'file_path': f.file_path,
                        'file_url': f'/{f.file_path}',
                    }
                    for f in m.files
                ] if hasattr(m, 'files') and m.files else []
            }
            for m in messages
        ]
    }


@router.post("/revisions/{revision_id}/messages")
async def send_revision_message(
    revision_id: int,
    message: str = Form(...),
    files: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправить сообщение в чат правки с файлами"""
    # Проверяем доступ к правке через проект
    revision = db.query(ProjectRevision).filter(
        ProjectRevision.id == revision_id
    ).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

    # Проверяем доступ к проекту
    from sqlalchemy import or_
    project = db.query(Project).filter(
        Project.id == revision.project_id,
        or_(
            Project.user_id == current_user.id,
            Project.client_telegram_id == str(current_user.telegram_id)
        )
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="Access denied")

    # Создаем сообщение
    new_message = RevisionMessage(
        revision_id=revision_id,
        sender_type='client',
        sender_user_id=current_user.id,
        message=message,
        is_internal=False
    )

    db.add(new_message)
    db.flush()  # Получаем ID сообщения

    # Сохраняем файлы
    saved_files = []
    if files:
        upload_dir = f"uploads/revisions/messages"
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            if file.filename:
                # Генерируем уникальное имя
                file_ext = os.path.splitext(file.filename)[1]
                unique_name = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(upload_dir, unique_name)

                # Сохраняем файл
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

                # Определяем тип файла
                file_type = 'image' if file.content_type and file.content_type.startswith('image/') else \
                           'video' if file.content_type and file.content_type.startswith('video/') else 'other'

                # Создаем запись в БД
                message_file = RevisionMessageFile(
                    message_id=new_message.id,
                    filename=unique_name,
                    original_filename=file.filename,
                    file_type=file_type,
                    file_size=os.path.getsize(file_path),
                    file_path=file_path
                )
                db.add(message_file)
                saved_files.append(message_file)

    db.commit()
    db.refresh(new_message)

    # Отправляем уведомления
    try:
        from ..config.settings import get_settings
        from telegram import Bot

        settings = get_settings()
        bot = Bot(settings.BOT_TOKEN)

        # Определяем, кого уведомлять
        # Если сообщение от клиента - уведомляем исполнителя и админов
        # Если сообщение от сотрудника/админа - уведомляем клиента

        notify_users = []

        # Получаем telegram_id клиента (владельца проекта)
        client_telegram_id = None
        if project.client_telegram_id:
            client_telegram_id = int(project.client_telegram_id)
        elif project.user and project.user.telegram_id:
            client_telegram_id = project.user.telegram_id

        # Проверяем, кто отправил сообщение
        is_from_client = current_user.telegram_id == client_telegram_id

        if is_from_client:
            # Сообщение от клиента - уведомляем исполнителя и админов
            # Уведомляем исполнителя правки
            if revision.assigned_to and revision.assigned_to.telegram_id:
                notify_users.append({
                    'telegram_id': revision.assigned_to.telegram_id,
                    'name': revision.assigned_to.username
                })

            # Уведомляем админов
            from ..database.models import AdminUser
            admins = db.query(AdminUser).filter(
                AdminUser.role == "owner",
                AdminUser.telegram_id.isnot(None)
            ).all()

            for admin in admins:
                if admin.telegram_id not in [u['telegram_id'] for u in notify_users]:
                    notify_users.append({
                        'telegram_id': admin.telegram_id,
                        'name': admin.username
                    })
        else:
            # Сообщение от сотрудника/админа - уведомляем клиента
            if client_telegram_id:
                notify_users.append({
                    'telegram_id': client_telegram_id,
                    'name': project.user.first_name if project.user else 'Клиент'
                })

        # Формируем сообщение
        sender_name = current_user.first_name if hasattr(current_user, 'first_name') else current_user.username
        notification_text = f"""
💬 <b>Новый комментарий в правке</b>

📋 <b>Проект:</b> {project.title}
✏️ <b>Правка:</b> {revision.title}

👤 <b>От:</b> {sender_name}
💭 <b>Сообщение:</b>
{message[:200]}{'...' if len(message) > 200 else ''}

📱 Откройте мини-приложение для просмотра
"""

        # Отправляем уведомления
        for user in notify_users:
            try:
                await bot.send_message(
                    chat_id=user['telegram_id'],
                    text=notification_text,
                    parse_mode='HTML'
                )
                print(f"✅ Уведомление отправлено {user['name']} (TG: {user['telegram_id']})")
            except Exception as e:
                print(f"❌ Ошибка отправки уведомления {user['name']}: {e}")

    except Exception as e:
        print(f"❌ Ошибка при отправке уведомлений о комментарии в правке: {e}")

    return {
        'message': {
            'id': new_message.id,
            'revision_id': new_message.revision_id,
            'sender_type': new_message.sender_type,
            'sender_user_id': new_message.sender_user_id,
            'message': new_message.message,
            'is_internal': new_message.is_internal,
            'created_at': new_message.created_at.isoformat() if new_message.created_at else None,
            'files': [
                {
                    'id': f.id,
                    'filename': f.filename,
                    'original_filename': f.original_filename,
                    'file_type': f.file_type,
                    'file_size': f.file_size,
                    'file_path': f.file_path,
                    'file_url': f'/{f.file_path}',
                }
                for f in saved_files
            ]
        }
    }


@router.patch("/revisions/{revision_id}/progress")
async def update_revision_progress(
    revision_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить прогресс правки (только для админов/исполнителей)"""
    revision = db.query(ProjectRevision).filter(
        ProjectRevision.id == revision_id
    ).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

    # Обновляем прогресс
    if hasattr(revision, 'progress'):
        revision.progress = data['progress']

    db.commit()
    db.refresh(revision)

    return {
        'revision': {
            'id': revision.id,
            'progress': getattr(revision, 'progress', 0),
        }
    }


@router.patch("/revisions/{revision_id}/status")
async def update_revision_status(
    revision_id: int,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить статус правки (только для админов/исполнителей)"""
    revision = db.query(ProjectRevision).filter(
        ProjectRevision.id == revision_id
    ).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

    # Обновляем статус
    revision.status = data['status']

    if data['status'] == 'completed':
        revision.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(revision)

    return {
        'revision': {
            'id': revision.id,
            'status': revision.status,
            'completed_at': revision.completed_at.isoformat() if revision.completed_at else None,
        }
    }


# ============================================
# ДОКУМЕНТЫ (Documents)
# ============================================

@router.get("/documents")
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список документов клиента"""

    # Получаем все проекты пользователя
    user_projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).all()

    project_ids = [p.id for p in user_projects]

    if not project_ids:
        return {'documents': []}

    # Получаем документы для этих проектов
    query = """
        SELECT
            id, type, name, number, project_id, file_path, file_size, file_type,
            status, date, signed_at, description, created_at
        FROM documents
        WHERE project_id IN ({})
        ORDER BY created_at DESC
    """.format(','.join('?' * len(project_ids)))

    cursor = db.execute(query, project_ids)
    documents = cursor.fetchall()

    return {
        'documents': [
            {
                'id': doc[0],
                'type': doc[1],
                'name': doc[2],
                'number': doc[3],
                'project_id': doc[4],
                'file_path': doc[5],
                'file_url': f'/{doc[5]}' if doc[5] else None,
                'file_size': doc[6],
                'file_type': doc[7],
                'status': doc[8],
                'date': doc[9],
                'signed_at': doc[10],
                'description': doc[11],
                'created_at': doc[12],
            }
            for doc in documents
        ]
    }


@router.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о конкретном документе"""

    # Проверяем доступ: документ должен принадлежать проекту пользователя
    query = """
        SELECT d.*, p.name as project_name
        FROM documents d
        JOIN projects p ON d.project_id = p.id
        WHERE d.id = ? AND p.user_id = ?
    """

    cursor = db.execute(query, (document_id, current_user.id))
    doc = cursor.fetchone()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        'document': {
            'id': doc[0],
            'type': doc[1],
            'name': doc[2],
            'number': doc[3],
            'project_id': doc[5],
            'project_name': doc[-1],
            'file_path': doc[6],
            'file_url': f'/{doc[6]}' if doc[6] else None,
            'file_size': doc[7],
            'file_type': doc[8],
            'status': doc[12],
            'date': doc[13],
            'signed_at': doc[15],
            'description': doc[16],
        }
    }


# ============================================
# ФИНАНСЫ / ПЛАТЕЖИ (Finance / Payments)
# ============================================

@router.get("/finance/summary")
async def get_finance_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить сводку по финансам клиента"""

    # Получаем все проекты пользователя
    user_projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).all()

    project_ids = [p.id for p in user_projects]

    if not project_ids:
        return {
            'total_amount': 0,
            'paid_amount': 0,
            'balance': 0,
            'projects_count': 0
        }

    # Получаем сводку по сделкам
    query = """
        SELECT
            COUNT(*) as projects_count,
            COALESCE(SUM(amount), 0) as total_amount,
            COALESCE(SUM(paid_amount), 0) as paid_amount
        FROM deals
        WHERE project_id IN ({})
    """.format(','.join('?' * len(project_ids)))

    cursor = db.execute(query, project_ids)
    summary = cursor.fetchone()

    total_amount = summary[1] if summary else 0
    paid_amount = summary[2] if summary else 0
    balance = total_amount - paid_amount

    return {
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'balance': balance,
        'projects_count': summary[0] if summary else 0
    }


@router.get("/finance/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список транзакций клиента"""

    # Получаем проекты пользователя
    user_projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).all()

    project_ids = [p.id for p in user_projects]

    if not project_ids:
        return {'transactions': []}

    # Получаем транзакции
    query = """
        SELECT
            t.id, t.transaction_type, t.project_id, t.amount, t.currency,
            t.description, t.payment_method, t.status, t.transaction_date,
            p.name as project_name
        FROM transactions t
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.project_id IN ({})
        ORDER BY t.transaction_date DESC
    """.format(','.join('?' * len(project_ids)))

    cursor = db.execute(query, project_ids)
    transactions = cursor.fetchall()

    return {
        'transactions': [
            {
                'id': tr[0],
                'type': tr[1],
                'project_id': tr[2],
                'project_name': tr[9],
                'amount': tr[3],
                'currency': tr[4],
                'description': tr[5],
                'payment_method': tr[6],
                'status': tr[7],
                'date': tr[8],
            }
            for tr in transactions
        ]
    }


@router.get("/finance/deals")
async def get_deals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список сделок клиента"""

    # Получаем client_id пользователя
    query_client = """
        SELECT id FROM clients WHERE telegram_id = ?
    """
    cursor = db.execute(query_client, (current_user.telegram_id,))
    client = cursor.fetchone()

    if not client:
        return {'deals': []}

    client_id = client[0]

    # Получаем сделки
    query = """
        SELECT
            d.id, d.title, d.status, d.description, d.amount, d.paid_amount,
            d.start_date, d.end_date, d.prepayment_percent, d.prepayment_amount,
            p.name as project_name, p.id as project_id
        FROM deals d
        LEFT JOIN projects p ON d.project_id = p.id
        WHERE d.client_id = ?
        ORDER BY d.start_date DESC
    """

    cursor = db.execute(query, (client_id,))
    deals = cursor.fetchall()

    return {
        'deals': [
            {
                'id': deal[0],
                'title': deal[1],
                'status': deal[2],
                'description': deal[3],
                'amount': deal[4],
                'paid_amount': deal[5],
                'balance': (deal[4] or 0) - (deal[5] or 0),
                'start_date': deal[6],
                'end_date': deal[7],
                'prepayment_percent': deal[8],
                'prepayment_amount': deal[9],
                'project_name': deal[10],
                'project_id': deal[11],
            }
            for deal in deals
        ]
    }


# ============================================
# УВЕДОМЛЕНИЯ (Notifications)
# ============================================

@router.get("/notifications")
async def get_notifications(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список уведомлений для клиента"""

    # Получаем уведомления из notification_log
    query = """
        SELECT
            id, notification_type, title, message, status,
            sent_at, entity_type, entity_id
        FROM notification_log
        WHERE telegram_user_id = ?
        ORDER BY sent_at DESC
        LIMIT ?
    """

    cursor = db.execute(query, (str(current_user.telegram_id), limit))
    notifications = cursor.fetchall()

    return {
        'notifications': [
            {
                'id': notif[0],
                'type': notif[1],
                'title': notif[2],
                'message': notif[3],
                'status': notif[4],
                'sent_at': notif[5],
                'entity_type': notif[6],
                'entity_id': notif[7],
            }
            for notif in notifications
        ]
    }


@router.get("/notifications/unread-count")
async def get_unread_notifications_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить количество непрочитанных уведомлений"""

    # Для простоты считаем непрочитанными уведомления за последние 7 дней
    query = """
        SELECT COUNT(*)
        FROM notification_log
        WHERE telegram_user_id = ?
        AND sent_at >= datetime('now', '-7 days')
    """

    cursor = db.execute(query, (str(current_user.telegram_id),))
    count = cursor.fetchone()[0]

    return {
        'unread_count': count
    }


# ===== ЧАТЫ ПРОЕКТОВ =====

@router.get("/chats")
async def get_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить все чаты проектов клиента"""
    try:
        print(f"🔍 Запрос чатов от пользователя: id={current_user.id}, telegram_id={current_user.telegram_id}")

        # Находим все проекты клиента (используем тот же фильтр что и для /api/projects)
        from sqlalchemy import or_, and_
        projects = db.query(Project).filter(
            or_(
                Project.user_id == current_user.id,
                and_(
                    Project.client_telegram_id.isnot(None),
                    Project.client_telegram_id == str(current_user.telegram_id)
                )
            )
        ).all()

        print(f"📊 Найдено проектов: {len(projects)}")

        chats = []
        for project in projects:
            # Находим или создаем чат для проекта
            chat = db.query(ProjectChat).filter(ProjectChat.project_id == project.id).first()

            if not chat:
                # Автоматически создаем чат
                chat = ProjectChat(
                    project_id=project.id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(chat)
                db.flush()
                print(f"✅ Создан новый чат для проекта {project.id}")

            # Получаем последнее сообщение
            last_message = db.query(ProjectChatMessage).filter(
                ProjectChatMessage.chat_id == chat.id
            ).order_by(ProjectChatMessage.created_at.desc()).first()

            # Получаем исполнителя проекта
            executor = None
            if project.assigned_executor_id:
                executor = db.query(AdminUser).filter(AdminUser.id == project.assigned_executor_id).first()

            chats.append({
                'id': chat.id,
                'project': {
                    'id': project.id,
                    'title': project.title,
                    'status': project.status,
                    'executor': {
                        'id': executor.id,
                        'name': executor.username or executor.first_name
                    } if executor else None
                },
                'last_message': {
                    'sender_type': last_message.sender_type,
                    'message_text': last_message.message_text,
                    'created_at': last_message.created_at.isoformat()
                } if last_message else None,
                'last_message_at': chat.last_message_at.isoformat() if chat.last_message_at else None,
                'unread_by_client': chat.unread_by_client,
                'created_at': chat.created_at.isoformat()
            })

        db.commit()
        print(f"✅ Возвращено чатов: {len(chats)}")
        return chats

    except Exception as e:
        print(f"❌ Ошибка в get_chats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chats/{chat_id}/messages")
async def get_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить сообщения чата"""
    try:
        print(f"📨 get_chat_messages: chat_id={chat_id}, user_id={current_user.id}, telegram_id={current_user.telegram_id}")

        # Проверяем доступ к чату
        chat = db.query(ProjectChat).filter(ProjectChat.id == chat_id).first()
        if not chat:
            print(f"❌ Чат {chat_id} не найден")
            raise HTTPException(status_code=404, detail="Chat not found")

        print(f"✅ Чат найден: project_id={chat.project_id}")

        project = db.query(Project).filter(Project.id == chat.project_id).first()
        print(f"✅ Проект: {project.title}, user_id={project.user_id}, client_telegram_id={project.client_telegram_id}")

        from sqlalchemy import or_
        # Проверяем что пользователь имеет доступ к проекту (владелец или клиент)
        if not (project.user_id == current_user.id or project.client_telegram_id == str(current_user.telegram_id)):
            print(f"❌ Доступ запрещен: project.user_id={project.user_id}, current_user.id={current_user.id}, project.client_telegram_id={project.client_telegram_id}, current_user.telegram_id={current_user.telegram_id}")
            raise HTTPException(status_code=403, detail="Access denied")

        # Получаем сообщения
        messages = db.query(ProjectChatMessage).filter(
            ProjectChatMessage.chat_id == chat_id
        ).order_by(ProjectChatMessage.created_at.asc()).all()

        print(f"📝 Найдено сообщений: {len(messages)}")

        # Получаем имя клиента
        client_name = 'Клиент'
        if project.user:
            if project.user.first_name:
                client_name = project.user.first_name
                if project.user.last_name:
                    client_name += f' {project.user.last_name}'
            elif project.user.username:
                client_name = f'@{project.user.username}'

        # Помечаем сообщения как прочитанные клиентом
        for msg in messages:
            if not msg.is_read_by_client and msg.sender_type != 'client':
                msg.is_read_by_client = True
                msg.read_at = datetime.utcnow()

        chat.unread_by_client = 0
        db.commit()

        return {
            'project_title': project.title,
            'client_name': client_name,
            'messages': [
                {
                    'id': msg.id,
                    'sender_type': msg.sender_type,
                    'sender_name': client_name if msg.sender_type == 'client' else 'Исполнитель',
                    'message_text': msg.message_text,
                    'attachments': msg.attachments or [],
                    'created_at': msg.created_at.isoformat(),
                    'is_read': msg.is_read_by_client if msg.sender_type == 'executor' else msg.is_read_by_executor
                }
                for msg in messages
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка в get_chat_messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chats/{chat_id}/messages")
async def send_chat_message(
    chat_id: int,
    request: Request,
    message_text: Optional[str] = Form(None),
    attachments: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправить сообщение в чат"""
    try:
        # Детальное логирование в файл
        with open("/tmp/chat_debug.log", "a") as f:
            import json
            f.write(f"\n{'='*80}\n")
            f.write(f"[{datetime.now()}] send_chat_message вызван\n")
            f.write(f"chat_id: {chat_id}\n")
            f.write(f"\nHeaders:\n")
            for key, value in request.headers.items():
                f.write(f"  {key}: {value}\n")
            f.write(f"\nmessage_text: {repr(message_text)}\n")
            f.write(f"message_text type: {type(message_text)}\n")
            f.write(f"attachments: {attachments}\n")
            f.write(f"attachments type: {type(attachments)}\n")
            if attachments:
                f.write(f"attachments length: {len(attachments)}\n")
                for i, att in enumerate(attachments):
                    f.write(f"  attachment[{i}]: filename={att.filename}, content_type={att.content_type}\n")
            f.write(f"user: {current_user.id}, telegram_id={current_user.telegram_id}\n")

        print(f"📨 send_chat_message: chat_id={chat_id}, message_text={message_text}, attachments={attachments}")

        # Проверяем доступ к чату
        chat = db.query(ProjectChat).filter(ProjectChat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        project = db.query(Project).filter(Project.id == chat.project_id).first()

        from sqlalchemy import or_
        # Проверяем что пользователь имеет доступ к проекту
        if not (project.user_id == current_user.id or project.client_telegram_id == str(current_user.telegram_id)):
            raise HTTPException(status_code=403, detail="Access denied")

        # Обрабатываем вложения
        attachment_files = []
        print(f"🔍 Проверка attachments: {attachments}, type: {type(attachments)}")
        if attachments:
            upload_dir = os.path.join(settings.UPLOAD_DIR, "chat_attachments", str(chat_id))
            os.makedirs(upload_dir, exist_ok=True)

            for file in attachments:
                if file.filename:
                    file_ext = os.path.splitext(file.filename)[1]
                    unique_filename = f"{uuid.uuid4()}{file_ext}"
                    file_path = os.path.join(upload_dir, unique_filename)

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
            sender_type='client',
            sender_id=current_user.id,
            message_text=message_text,
            attachments=attachment_files,
            created_at=datetime.utcnow(),
            is_read_by_client=True,
            is_read_by_executor=False
        )

        db.add(message)

        # Обновляем чат
        chat.last_message_at = datetime.utcnow()
        chat.updated_at = datetime.utcnow()
        chat.unread_by_executor += 1

        db.commit()

        # Отправляем уведомление исполнителю в Telegram
        print(f"🔔 [NOTIFICATION DEBUG] Начинаем процесс уведомления для chat_id={chat_id}")
        project = db.query(Project).filter(Project.id == chat.project_id).first()
        print(f"🔔 [NOTIFICATION DEBUG] project найден: {project is not None}, project_id={chat.project_id}")

        if project:
            print(f"🔔 [NOTIFICATION DEBUG] project.assigned_executor_id = {project.assigned_executor_id}")

        if project and project.assigned_executor_id:
            from ..database.models import AdminUser
            from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
            from ..config.settings import settings
            from datetime import datetime
            import asyncio

            # Получаем данные исполнителя
            executor = db.query(AdminUser).filter(AdminUser.id == project.assigned_executor_id).first()
            print(f"🔔 [NOTIFICATION DEBUG] executor найден: {executor is not None}")

            if executor:
                print(f"🔔 [NOTIFICATION DEBUG] executor.telegram_id = {executor.telegram_id}")

            if executor and executor.telegram_id:
                # Получаем имя клиента
                client_name = current_user.first_name or 'Клиент'
                if current_user.last_name:
                    client_name += f" {current_user.last_name}"

                print(f"🔔 [NOTIFICATION DEBUG] Отправляем уведомление исполнителю {executor.telegram_id}, от клиента {client_name}")

                # Отправляем уведомление асинхронно используя временный бот
                async def send_notification():
                    try:
                        bot = Bot(settings.BOT_TOKEN)
                        preview_text = message_text[:150] + "..." if message_text and len(message_text) > 150 else (message_text or "📎 Вложение")

                        notification_message = f"""
💬 <b>Новое сообщение в проекте</b>

📋 <b>Проект:</b> {project.title}
👤 <b>От:</b> {client_name} (Клиент)

💬 <b>Сообщение:</b>
{preview_text}

🕐 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
                        """

                        admin_url = f"http://147.45.215.199:8001/admin/chats/{chat_id}"
                        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Ответить", url=admin_url)]])

                        await bot.send_message(
                            chat_id=executor.telegram_id,
                            text=notification_message,
                            parse_mode='HTML',
                            reply_markup=keyboard,
                            disable_web_page_preview=True
                        )
                        print(f"✅ [NOTIFICATION DEBUG] Уведомление успешно отправлено!")
                    except Exception as e:
                        print(f"❌ [NOTIFICATION DEBUG] Ошибка отправки: {e}")

                asyncio.create_task(send_notification())
            else:
                print(f"🔔 [NOTIFICATION DEBUG] Уведомление НЕ отправлено: executor={executor is not None if executor else None}, telegram_id={executor.telegram_id if executor else None}")
        else:
            print(f"🔔 [NOTIFICATION DEBUG] Уведомление НЕ отправлено: project={project is not None}, assigned_executor_id={project.assigned_executor_id if project else None}")

        return {
            'id': message.id,
            'sender_type': message.sender_type,
            'message_text': message.message_text,
            'attachments': message.attachments or [],
            'created_at': message.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка в send_chat_message: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/chats/{chat_id}/read")
async def mark_chat_as_read(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Пометить все сообщения чата как прочитанные"""
    try:
        # Проверяем доступ к чату
        chat = db.query(ProjectChat).filter(ProjectChat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        project = db.query(Project).filter(Project.id == chat.project_id).first()

        from sqlalchemy import or_
        if not (project.user_id == current_user.id or project.client_telegram_id == str(current_user.telegram_id)):
            raise HTTPException(status_code=403, detail="Access denied")

        # Помечаем все непрочитанные сообщения как прочитанные
        messages = db.query(ProjectChatMessage).filter(
            ProjectChatMessage.chat_id == chat_id,
            ProjectChatMessage.is_read_by_client == False,
            ProjectChatMessage.sender_type == 'executor'
        ).all()

        for msg in messages:
            msg.is_read_by_client = True
            msg.read_at = datetime.utcnow()

        chat.unread_by_client = 0
        db.commit()

        return {'success': True}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка в mark_chat_as_read: {e}")
        raise HTTPException(status_code=500, detail=str(e))
