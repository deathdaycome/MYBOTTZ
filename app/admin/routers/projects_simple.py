# Упрощенный роутер проектов для отладки
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...database.database import get_db
from ...database.models import Project, User
from ...config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["projects"])

# Статусы проектов
PROJECT_STATUSES = {
    "new": "Новый",
    "review": "На рассмотрении", 
    "accepted": "Принят",
    "in_progress": "В работе",
    "testing": "Тестирование",
    "completed": "Завершен",
    "cancelled": "Отменен",
    "on_hold": "Приостановлен"
}

@router.get("/")
async def get_projects_list(db: Session = Depends(get_db)):
    """Получить список проектов"""
    try:
        projects = db.query(Project).limit(10).all()
        
        projects_data = []
        for project in projects:
            project_dict = project.to_dict()
            projects_data.append(project_dict)
        
        return {
            "success": True,
            "projects": projects_data,
            "total": len(projects_data)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения проектов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения проектов: {str(e)}")

@router.put("/{project_id}/status")
async def update_project_status_simple(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обновить статус проекта (упрощенная версия)"""
    try:
        data = await request.json()
        new_status = data.get("status")
        comment = data.get("comment", "")
        
        logger.info(f"Получен запрос на изменение статуса проекта {project_id} на '{new_status}'")
        
        if not new_status:
            raise HTTPException(status_code=400, detail="Не указан новый статус")
        
        if new_status not in PROJECT_STATUSES:
            raise HTTPException(status_code=400, detail="Неверный статус")
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        old_status = project.status
        project.status = new_status
        project.updated_at = datetime.utcnow()
        
        # Логируем изменение статуса
        if not project.project_metadata:
            project.project_metadata = {}
        
        if "status_history" not in project.project_metadata:
            project.project_metadata["status_history"] = []
        
        project.project_metadata["status_history"].append({
            "from_status": old_status,
            "to_status": new_status,
            "changed_at": datetime.utcnow().isoformat(),
            "comment": comment
        })
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"Статус проекта {project_id} изменен с '{old_status}' на '{new_status}'")
        
        return {
            "success": True,
            "message": f"Статус проекта изменен на '{PROJECT_STATUSES[new_status]}'",
            "project": {
                "id": project.id,
                "status": project.status,
                "status_name": PROJECT_STATUSES[project.status],
                "updated_at": project.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка обновления статуса проекта {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления статуса: {str(e)}")

