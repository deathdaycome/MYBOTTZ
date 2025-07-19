"""
Сервис управления проектами с учетом ролей доступа
"""

from sqlalchemy.orm import Session, joinedload
from app.database.models import Project, AdminUser, User, ProjectFile
from app.database.database import get_db_connection
from datetime import datetime
from typing import List, Optional, Dict, Any

class ProjectsService:
    """Сервис для управления проектами с разграничением доступа"""
    
    @staticmethod
    def get_projects_for_user(user: AdminUser) -> List[Dict]:
        """Получить проекты в зависимости от роли пользователя"""
        db = next(get_db_connection())
        try:
            if user.is_owner():
                # Владелец видит все проекты
                projects = db.query(Project).options(
                    joinedload(Project.user),
                    joinedload(Project.assigned_executor)
                ).all()
            else:
                # Исполнитель видит только свои назначенные проекты
                projects = db.query(Project).options(
                    joinedload(Project.user),
                    joinedload(Project.assigned_executor)
                ).filter(Project.assigned_executor_id == user.id).all()
            
            result = []
            for project in projects:
                project_dict = project.to_dict()
                
                # Для исполнителя скрываем полную стоимость
                if user.is_executor():
                    project_dict['estimated_cost'] = project.executor_cost or 0
                    project_dict['final_cost'] = project.executor_cost or 0
                
                # Добавляем информацию о пользователе
                if project.user:
                    project_dict['user'] = project.user.to_dict()
                
                result.append(project_dict)
            
            return result
        except Exception as e:
            print(f"Ошибка получения проектов: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_project_by_id(project_id: int, user: AdminUser) -> Optional[Dict]:
        """Получить проект по ID с учетом прав доступа"""
        db = next(get_db_connection())
        try:
            query = db.query(Project).options(
                joinedload(Project.user),
                joinedload(Project.assigned_executor),
                joinedload(Project.files)
            ).filter(Project.id == project_id)
            
            # Если исполнитель - проверяем доступ только к своим проектам
            if user.is_executor():
                query = query.filter(Project.assigned_executor_id == user.id)
            
            project = query.first()
            if not project:
                return None
            
            project_dict = project.to_dict()
            
            # Для исполнителя скрываем полную стоимость
            if user.is_executor():
                project_dict['estimated_cost'] = project.executor_cost or 0
                project_dict['final_cost'] = project.executor_cost or 0
            
            # Добавляем информацию о пользователе
            if project.user:
                project_dict['user'] = project.user.to_dict()
            
            # Добавляем файлы с учетом прав доступа
            project_dict['files'] = ProjectsService.get_project_files(project_id, user)
            
            return project_dict
        except Exception as e:
            print(f"Ошибка получения проекта: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def assign_executor(project_id: int, executor_id: int, executor_cost: float, assigner: AdminUser) -> bool:
        """Назначить исполнителя на проект (только для владельца)"""
        if not assigner.is_owner():
            return False
        
        db = next(get_db_connection())
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            executor = db.query(AdminUser).filter(
                AdminUser.id == executor_id,
                AdminUser.role == 'executor',
                AdminUser.is_active == True
            ).first()
            
            if not project or not executor:
                return False
            
            project.assigned_executor_id = executor_id
            project.executor_cost = executor_cost
            project.assigned_at = datetime.utcnow()
            
            # Добавляем запись в метаданные проекта
            if not project.project_metadata:
                project.project_metadata = {}
            
            if 'assignment_history' not in project.project_metadata:
                project.project_metadata['assignment_history'] = []
            
            project.project_metadata['assignment_history'].append({
                'executor_id': executor_id,
                'executor_username': executor.username,
                'executor_cost': executor_cost,
                'assigned_by': assigner.username,
                'assigned_at': datetime.utcnow().isoformat()
            })
            
            db.commit()
            return True
        except Exception as e:
            print(f"Ошибка назначения исполнителя: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def update_project_status(project_id: int, new_status: str, comment: str, user: AdminUser) -> bool:
        """Обновить статус проекта"""
        db = next(get_db_connection())
        try:
            query = db.query(Project).filter(Project.id == project_id)
            
            # Исполнитель может менять статус только своих проектов
            if user.is_executor():
                query = query.filter(Project.assigned_executor_id == user.id)
            
            project = query.first()
            if not project:
                return False
            
            old_status = project.status
            project.status = new_status
            project.updated_at = datetime.utcnow()
            
            # Добавляем в историю статусов
            if not project.project_metadata:
                project.project_metadata = {}
            
            if 'status_history' not in project.project_metadata:
                project.project_metadata['status_history'] = []
            
            project.project_metadata['status_history'].append({
                'from_status': old_status,
                'to_status': new_status,
                'changed_by': user.username,
                'changed_at': datetime.utcnow().isoformat(),
                'comment': comment
            })
            
            db.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления статуса: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_project_files(project_id: int, user: AdminUser) -> List[Dict]:
        """Получить файлы проекта с учетом прав доступа"""
        db = next(get_db_connection())
        try:
            # Проверяем доступ к проекту
            project_query = db.query(Project).filter(Project.id == project_id)
            if user.is_executor():
                project_query = project_query.filter(Project.assigned_executor_id == user.id)
            
            project = project_query.first()
            if not project:
                return []
            
            # Получаем файлы
            files_query = db.query(ProjectFile).options(
                joinedload(ProjectFile.uploaded_by)
            ).filter(ProjectFile.project_id == project_id)
            
            # Исполнитель видит только свои файлы
            if user.is_executor():
                files_query = files_query.filter(ProjectFile.uploaded_by_id == user.id)
            
            files = files_query.all()
            return [file.to_dict() for file in files]
        except Exception as e:
            print(f"Ошибка получения файлов: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_dashboard_stats(user: AdminUser) -> Dict[str, Any]:
        """Получить статистику для дашборда в зависимости от роли"""
        db = next(get_db_connection())
        try:
            if user.is_owner():
                # Владелец видит общую статистику
                total_projects = db.query(Project).count()
                active_projects = db.query(Project).filter(
                    Project.status.in_(['new', 'review', 'accepted', 'in_progress', 'testing'])
                ).count()
                completed_projects = db.query(Project).filter(Project.status == 'completed').count()
                total_revenue = db.query(Project).with_entities(
                    db.func.sum(Project.estimated_cost)
                ).scalar() or 0
                
                return {
                    'total_projects': total_projects,
                    'active_projects': active_projects,
                    'completed_projects': completed_projects,
                    'total_revenue': total_revenue,
                    'role': 'owner'
                }
            else:
                # Исполнитель видит только свою статистику
                my_projects = db.query(Project).filter(Project.assigned_executor_id == user.id)
                total_projects = my_projects.count()
                active_projects = my_projects.filter(
                    Project.status.in_(['accepted', 'in_progress', 'testing'])
                ).count()
                completed_projects = my_projects.filter(Project.status == 'completed').count()
                my_earnings = my_projects.filter(Project.status == 'completed').with_entities(
                    db.func.sum(Project.executor_cost)
                ).scalar() or 0
                
                return {
                    'total_projects': total_projects,
                    'active_projects': active_projects,
                    'completed_projects': completed_projects,
                    'my_earnings': my_earnings,
                    'role': 'executor'
                }
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {}
        finally:
            db.close()
    
    @staticmethod
    def get_unassigned_projects() -> List[Dict]:
        """Получить неназначенные проекты (только для владельца)"""
        db = next(get_db_connection())
        try:
            projects = db.query(Project).options(
                joinedload(Project.user)
            ).filter(Project.assigned_executor_id.is_(None)).all()
            
            result = []
            for project in projects:
                project_dict = project.to_dict()
                if project.user:
                    project_dict['user'] = project.user.to_dict()
                result.append(project_dict)
            
            return result
        except Exception as e:
            print(f"Ошибка получения неназначенных проектов: {e}")
            return []
        finally:
            db.close()
