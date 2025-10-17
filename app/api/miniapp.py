from fastapi import APIRouter, Depends, Header, HTTPException, Form, File, UploadFile
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
from ..database.models import User, Project, ProjectRevision, RevisionMessage, RevisionMessageFile, RevisionFile
from ..config.settings import get_settings

router = APIRouter(prefix="/api/miniapp", tags=["miniapp"])
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

    projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).order_by(Project.created_at.desc()).all()

    print(f"📊 Найдено проектов: {len(projects)}")
    if projects:
        for p in projects[:3]:
            print(f"  - ID: {p.id}, Название: {p.title}")

    return [project.to_dict() for project in projects]


@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить детали проекта"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
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
    projects = db.query(Project).filter(
        Project.user_id == current_user.id
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
    # Получаем все проекты пользователя
    user_projects = db.query(Project).filter(
        Project.user_id == current_user.id
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
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
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
        ProjectRevision.id == revision_id,
        ProjectRevision.created_by_id == current_user.id
    ).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

    # Получаем проект для названия
    project = db.query(Project).filter(Project.id == revision.project_id).first()

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
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
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
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
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
    # Проверяем доступ к правке
    revision = db.query(ProjectRevision).filter(
        ProjectRevision.id == revision_id,
        ProjectRevision.created_by_id == current_user.id
    ).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

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
    # Проверяем доступ к правке
    revision = db.query(ProjectRevision).filter(
        ProjectRevision.id == revision_id,
        ProjectRevision.created_by_id == current_user.id
    ).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")

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
