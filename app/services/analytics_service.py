from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import func, and_, or_
from collections import defaultdict, Counter

from ..database.database import get_db_context
from ..database.models import User, Project, ConsultantSession, ConsultantQuery, Message
from ..config.logging import get_logger

logger = get_logger(__name__)

class AnalyticsService:
    """Сервис для аналитики и отчетности"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 минут кэш
    
    def _get_cached_result(self, key: str, func, *args, **kwargs):
        """Получение результата с кэшированием"""
        import time
        
        now = time.time()
        cache_key = f"{key}_{hash(str(args) + str(kwargs))}"
        
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if now - timestamp < self.cache_ttl:
                return result
        
        result = func(*args, **kwargs)
        self.cache[cache_key] = (result, now)
        
        return result
    
    def get_user_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """Статистика пользователей"""
        return self._get_cached_result(
            "user_stats", 
            self._calculate_user_statistics, 
            period_days
        )
    
    def _calculate_user_statistics(self, period_days: int) -> Dict[str, Any]:
        """Расчет статистики пользователей"""
        try:
            with get_db_context() as db:
                # Общая статистика
                total_users = db.query(User).count()
                
                # За период
                period_start = datetime.utcnow() - timedelta(days=period_days)
                new_users = db.query(User).filter(
                    User.registration_date >= period_start
                ).count()
                
                # Активные пользователи (последние 7 дней)
                week_ago = datetime.utcnow() - timedelta(days=7)
                active_users = db.query(User).filter(
                    User.last_activity >= week_ago
                ).count()
                
                # Пользователи с проектами
                users_with_projects = db.query(User).filter(
                    User.projects.any()
                ).count()
                
                # Пользователи с консультациями
                users_with_consultations = db.query(User).filter(
                    User.consultant_sessions.any()
                ).count()
                
                # Статистика по дням регистрации
                daily_registrations = db.query(
                    func.date(User.registration_date).label('date'),
                    func.count(User.id).label('count')
                ).filter(
                    User.registration_date >= period_start
                ).group_by(func.date(User.registration_date)).all()
                
                return {
                    'total_users': total_users,
                    'new_users': new_users,
                    'active_users': active_users,
                    'users_with_projects': users_with_projects,
                    'users_with_consultations': users_with_consultations,
                    'conversion_rate': (users_with_projects / total_users * 100) if total_users > 0 else 0,
                    'activity_rate': (active_users / total_users * 100) if total_users > 0 else 0,
                    'daily_registrations': [
                        {'date': str(reg.date), 'count': reg.count} 
                        for reg in daily_registrations
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка при расчете статистики пользователей: {e}")
            return {}
    
    def get_project_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """Статистика проектов"""
        return self._get_cached_result(
            "project_stats", 
            self._calculate_project_statistics, 
            period_days
        )
    
    def _calculate_project_statistics(self, period_days: int) -> Dict[str, Any]:
        """Расчет статистики проектов"""
        try:
            with get_db_context() as db:
                # Общая статистика
                total_projects = db.query(Project).count()
                
                # За период
                period_start = datetime.utcnow() - timedelta(days=period_days)
                new_projects = db.query(Project).filter(
                    Project.created_at >= period_start
                ).count()
                
                # Статистика по статусам
                status_stats = db.query(
                    Project.status,
                    func.count(Project.id).label('count')
                ).group_by(Project.status).all()
                
                # Статистика по сложности
                complexity_stats = db.query(
                    Project.complexity,
                    func.count(Project.id).label('count')
                ).group_by(Project.complexity).all()
                
                # Статистика по типам проектов
                type_stats = db.query(
                    Project.project_type,
                    func.count(Project.id).label('count')
                ).group_by(Project.project_type).all()
                
                # Финансовая статистика
                total_value = db.query(func.sum(Project.estimated_cost)).scalar() or 0
                completed_value = db.query(func.sum(Project.final_cost)).filter(
                    Project.status == 'completed'
                ).scalar() or 0
                
                avg_project_cost = db.query(func.avg(Project.estimated_cost)).scalar() or 0
                
                # Временная статистика
                avg_development_time = db.query(func.avg(Project.estimated_hours)).scalar() or 0
                
                # Конверсия проектов
                completed_projects = db.query(Project).filter(
                    Project.status == 'completed'
                ).count()
                
                return {
                    'total_projects': total_projects,
                    'new_projects': new_projects,
                    'completed_projects': completed_projects,
                    'completion_rate': (completed_projects / total_projects * 100) if total_projects > 0 else 0,
                    'total_value': total_value,
                    'completed_value': completed_value,
                    'avg_project_cost': avg_project_cost,
                    'avg_development_time': avg_development_time,
                    'status_distribution': {stat.status: stat.count for stat in status_stats},
                    'complexity_distribution': {stat.complexity: stat.count for stat in complexity_stats},
                    'type_distribution': {stat.project_type: stat.count for stat in type_stats}
                }
                
        except Exception as e:
            logger.error(f"Ошибка при расчете статистики проектов: {e}")
            return {}
    
    def get_consultant_statistics(self, period_days: int = 30) -> Dict[str, Any]:
        """Статистика консультанта"""
        return self._get_cached_result(
            "consultant_stats", 
            self._calculate_consultant_statistics, 
            period_days
        )
    
    def _calculate_consultant_statistics(self, period_days: int) -> Dict[str, Any]:
        """Расчет статистики консультанта"""
        try:
            with get_db_context() as db:
                period_start = datetime.utcnow() - timedelta(days=period_days)
                
                # Общая статистика сессий
                total_sessions = db.query(ConsultantSession).count()
                new_sessions = db.query(ConsultantSession).filter(
                    ConsultantSession.created_at >= period_start
                ).count()
                
                # Статистика запросов
                total_queries = db.query(ConsultantQuery).count()
                new_queries = db.query(ConsultantQuery).filter(
                    ConsultantQuery.created_at >= period_start
                ).count()
                
                # Средние показатели
                avg_queries_per_session = db.query(
                    func.avg(
                        db.query(func.count(ConsultantQuery.id))
                        .filter(ConsultantQuery.session_id == ConsultantSession.id)
                        .scalar_subquery()
                    )
                ).scalar() or 0
                
                avg_response_time = db.query(func.avg(ConsultantQuery.response_time)).scalar() or 0
                avg_tokens_used = db.query(func.avg(ConsultantQuery.tokens_used)).scalar() or 0
                
                # Рейтинги
                ratings = db.query(ConsultantQuery.rating).filter(
                    ConsultantQuery.rating.isnot(None)
                ).all()
                
                avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
                rating_distribution = Counter(r.rating for r in ratings)
                
                # Популярные темы
                topic_stats = db.query(
                    ConsultantSession.topic,
                    func.count(ConsultantSession.id).label('count')
                ).group_by(ConsultantSession.topic).all()
                
                # Статистика по дням
                daily_sessions = db.query(
                    func.date(ConsultantSession.created_at).label('date'),
                    func.count(ConsultantSession.id).label('count')
                ).filter(
                    ConsultantSession.created_at >= period_start
                ).group_by(func.date(ConsultantSession.created_at)).all()
                
                return {
                    'total_sessions': total_sessions,
                    'new_sessions': new_sessions,
                    'total_queries': total_queries,
                    'new_queries': new_queries,
                    'avg_queries_per_session': avg_queries_per_session,
                    'avg_response_time': avg_response_time,
                    'avg_tokens_used': avg_tokens_used,
                    'avg_rating': avg_rating,
                    'rating_distribution': dict(rating_distribution),
                    'popular_topics': {stat.topic: stat.count for stat in topic_stats},
                    'daily_sessions': [
                        {'date': str(session.date), 'count': session.count} 
                        for session in daily_sessions
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка при расчете статистики консультанта: {e}")
            return {}
    
    def get_financial_report(self, period_days: int = 30) -> Dict[str, Any]:
        """Финансовый отчет"""
        return self._get_cached_result(
            "financial_report", 
            self._calculate_financial_report, 
            period_days
        )
    
    def _calculate_financial_report(self, period_days: int) -> Dict[str, Any]:
        """Расчет финансового отчета"""
        try:
            with get_db_context() as db:
                period_start = datetime.utcnow() - timedelta(days=period_days)
                
                # Общий доход
                total_revenue = db.query(func.sum(Project.final_cost)).filter(
                    Project.status == 'completed',
                    Project.updated_at >= period_start
                ).scalar() or 0
                
                # Потенциальный доход (проекты в работе)
                potential_revenue = db.query(func.sum(Project.estimated_cost)).filter(
                    Project.status.in_(['accepted', 'in_progress', 'testing'])
                ).scalar() or 0
                
                # Средний чек
                avg_check = db.query(func.avg(Project.final_cost)).filter(
                    Project.status == 'completed',
                    Project.updated_at >= period_start
                ).scalar() or 0
                
                # Доход по сложности
                revenue_by_complexity = db.query(
                    Project.complexity,
                    func.sum(Project.final_cost).label('revenue')
                ).filter(
                    Project.status == 'completed',
                    Project.updated_at >= period_start
                ).group_by(Project.complexity).all()
                
                # Доход по типам проектов
                revenue_by_type = db.query(
                    Project.project_type,
                    func.sum(Project.final_cost).label('revenue')
                ).filter(
                    Project.status == 'completed',
                    Project.updated_at >= period_start
                ).group_by(Project.project_type).all()
                
                # Динамика по дням
                daily_revenue = db.query(
                    func.date(Project.updated_at).label('date'),
                    func.sum(Project.final_cost).label('revenue')
                ).filter(
                    Project.status == 'completed',
                    Project.updated_at >= period_start
                ).group_by(func.date(Project.updated_at)).all()
                
                return {
                    'total_revenue': total_revenue,
                    'potential_revenue': potential_revenue,
                    'avg_check': avg_check,
                    'revenue_by_complexity': {
                        stat.complexity: stat.revenue for stat in revenue_by_complexity
                    },
                    'revenue_by_type': {
                        stat.project_type: stat.revenue for stat in revenue_by_type
                    },
                    'daily_revenue': [
                        {'date': str(rev.date), 'revenue': float(rev.revenue or 0)} 
                        for rev in daily_revenue
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка при расчете финансового отчета: {e}")
            return {}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Метрики производительности"""
        try:
            with get_db_context() as db:
                # Время ответа консультанта
                avg_response_time = db.query(func.avg(ConsultantQuery.response_time)).scalar() or 0
                
                # Время от заявки до принятия проекта
                avg_acceptance_time = db.query(
                    func.avg(
                        func.extract('epoch', Project.updated_at - Project.created_at) / 3600
                    )
                ).filter(Project.status == 'accepted').scalar() or 0
                
                # Среднее время разработки
                avg_development_time = db.query(func.avg(Project.actual_hours)).filter(
                    Project.actual_hours.isnot(None)
                ).scalar() or 0
                
                # Точность оценок времени
                time_estimates = db.query(
                    Project.estimated_hours,
                    Project.actual_hours
                ).filter(
                    Project.actual_hours.isnot(None),
                    Project.estimated_hours > 0
                ).all()
                
                accuracy = 0
                if time_estimates:
                    accuracies = [
                        1 - abs(est.actual_hours - est.estimated_hours) / est.estimated_hours
                        for est in time_estimates
                    ]
                    accuracy = sum(accuracies) / len(accuracies) * 100
                
                return {
                    'avg_response_time': avg_response_time,
                    'avg_acceptance_time': avg_acceptance_time,
                    'avg_development_time': avg_development_time,
                    'time_estimation_accuracy': accuracy
                }
                
        except Exception as e:
            logger.error(f"Ошибка при расчете метрик производительности: {e}")
            return {}
    
    def get_conversion_funnel(self) -> Dict[str, Any]:
        """Воронка конверсии"""
        try:
            with get_db_context() as db:
                # Общее количество пользователей
                total_users = db.query(User).count()
                
                # Пользователи, создавшие проекты
                users_with_projects = db.query(User).filter(
                    User.projects.any()
                ).count()
                
                # Пользователи с принятыми проектами
                users_with_accepted_projects = db.query(User).filter(
                    User.projects.any(Project.status.in_(['accepted', 'in_progress', 'testing', 'completed']))
                ).count()
                
                # Пользователи с завершенными проектами
                users_with_completed_projects = db.query(User).filter(
                    User.projects.any(Project.status == 'completed')
                ).count()
                
                # Пользователи, использовавшие консультанта
                users_with_consultations = db.query(User).filter(
                    User.consultant_sessions.any()
                ).count()
                
                # Расчет конверсии
                project_creation_rate = (users_with_projects / total_users * 100) if total_users > 0 else 0
                project_acceptance_rate = (users_with_accepted_projects / users_with_projects * 100) if users_with_projects > 0 else 0
                project_completion_rate = (users_with_completed_projects / users_with_accepted_projects * 100) if users_with_accepted_projects > 0 else 0
                consultation_rate = (users_with_consultations / total_users * 100) if total_users > 0 else 0
                
                return {
                    'total_users': total_users,
                    'users_with_projects': users_with_projects,
                    'users_with_accepted_projects': users_with_accepted_projects,
                    'users_with_completed_projects': users_with_completed_projects,
                    'users_with_consultations': users_with_consultations,
                    'project_creation_rate': project_creation_rate,
                    'project_acceptance_rate': project_acceptance_rate,
                    'project_completion_rate': project_completion_rate,
                    'consultation_rate': consultation_rate,
                    'overall_conversion': (users_with_completed_projects / total_users * 100) if total_users > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Ошибка при расчете воронки конверсии: {e}")
            return {}
    
    def get_user_engagement_metrics(self, period_days: int = 30) -> Dict[str, Any]:
        """Метрики вовлеченности пользователей"""
        try:
            with get_db_context() as db:
                period_start = datetime.utcnow() - timedelta(days=period_days)
                
                # Активные пользователи по периодам
                daily_active = db.query(User).filter(
                    User.last_activity >= datetime.utcnow() - timedelta(days=1)
                ).count()
                
                weekly_active = db.query(User).filter(
                    User.last_activity >= datetime.utcnow() - timedelta(days=7)
                ).count()
                
                monthly_active = db.query(User).filter(
                    User.last_activity >= datetime.utcnow() - timedelta(days=30)
                ).count()
                
                # Среднее количество сессий на пользователя
                avg_sessions_per_user = db.query(
                    func.avg(
                        db.query(func.count(ConsultantSession.id))
                        .filter(ConsultantSession.user_id == User.id)
                        .scalar_subquery()
                    )
                ).scalar() or 0
                
                # Среднее количество проектов на пользователя
                avg_projects_per_user = db.query(
                    func.avg(
                        db.query(func.count(Project.id))
                        .filter(Project.user_id == User.id)
                        .scalar_subquery()
                    )
                ).scalar() or 0
                
                # Retention rate (пользователи, вернувшиеся через неделю)
                week_ago = datetime.utcnow() - timedelta(days=7)
                two_weeks_ago = datetime.utcnow() - timedelta(days=14)
                
                new_users_week_ago = db.query(User.id).filter(
                    and_(User.registration_date >= two_weeks_ago, User.registration_date < week_ago)
                ).subquery()
                
                retained_users = db.query(User).filter(
                    and_(
                        User.id.in_(new_users_week_ago),
                        User.last_activity >= week_ago
                    )
                ).count()
                
                total_new_users_week_ago = db.query(User).filter(
                    and_(User.registration_date >= two_weeks_ago, User.registration_date < week_ago)
                ).count()
                
                retention_rate = (retained_users / total_new_users_week_ago * 100) if total_new_users_week_ago > 0 else 0
                
                return {
                    'daily_active_users': daily_active,
                    'weekly_active_users': weekly_active,
                    'monthly_active_users': monthly_active,
                    'avg_sessions_per_user': avg_sessions_per_user,
                    'avg_projects_per_user': avg_projects_per_user,
                    'retention_rate': retention_rate
                }
                
        except Exception as e:
            logger.error(f"Ошибка при расчете метрик вовлеченности: {e}")
            return {}
    
    def generate_full_report(self, period_days: int = 30) -> Dict[str, Any]:
        """Генерация полного отчета"""
        try:
            report = {
                'period_days': period_days,
                'generated_at': datetime.utcnow().isoformat(),
                'user_statistics': self.get_user_statistics(period_days),
                'project_statistics': self.get_project_statistics(period_days),
                'consultant_statistics': self.get_consultant_statistics(period_days),
                'financial_report': self.get_financial_report(period_days),
                'performance_metrics': self.get_performance_metrics(),
                'conversion_funnel': self.get_conversion_funnel(),
                'engagement_metrics': self.get_user_engagement_metrics(period_days)
            }
            
            logger.info(f"Сгенерирован полный отчет за {period_days} дней")
            return report
            
        except Exception as e:
            logger.error(f"Ошибка при генерации полного отчета: {e}")
            return {}
    
    def get_top_users(self, metric: str = 'projects', limit: int = 10) -> List[Dict[str, Any]]:
        """Получение топ пользователей по метрике"""
        try:
            with get_db_context() as db:
                if metric == 'projects':
                    # Топ по количеству проектов
                    top_users = db.query(
                        User,
                        func.count(Project.id).label('count')
                    ).join(Project).group_by(User.id).order_by(
                        func.count(Project.id).desc()
                    ).limit(limit).all()
                    
                elif metric == 'revenue':
                    # Топ по доходу
                    top_users = db.query(
                        User,
                        func.sum(Project.final_cost).label('revenue')
                    ).join(Project).filter(
                        Project.status == 'completed'
                    ).group_by(User.id).order_by(
                        func.sum(Project.final_cost).desc()
                    ).limit(limit).all()
                    
                elif metric == 'consultations':
                    # Топ по консультациям
                    top_users = db.query(
                        User,
                        func.count(ConsultantSession.id).label('count')
                    ).join(ConsultantSession).group_by(User.id).order_by(
                        func.count(ConsultantSession.id).desc()
                    ).limit(limit).all()
                
                else:
                    return []
                
                result = []
                for user_data in top_users:
                    user = user_data[0]
                    value = user_data[1]
                    
                    result.append({
                        'user_id': user.telegram_id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'value': float(value) if value else 0,
                        'registration_date': user.registration_date.isoformat() if user.registration_date else None
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Ошибка при получении топ пользователей: {e}")
            return []
    
    def get_project_trends(self, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """Тренды проектов"""
        try:
            with get_db_context() as db:
                period_start = datetime.utcnow() - timedelta(days=days)
                
                # Тренд создания проектов
                creation_trend = db.query(
                    func.date(Project.created_at).label('date'),
                    func.count(Project.id).label('count')
                ).filter(
                    Project.created_at >= period_start
                ).group_by(func.date(Project.created_at)).order_by('date').all()
                
                # Тренд завершения проектов
                completion_trend = db.query(
                    func.date(Project.updated_at).label('date'),
                    func.count(Project.id).label('count')
                ).filter(
                    Project.status == 'completed',
                    Project.updated_at >= period_start
                ).group_by(func.date(Project.updated_at)).order_by('date').all()
                
                # Тренд дохода
                revenue_trend = db.query(
                    func.date(Project.updated_at).label('date'),
                    func.sum(Project.final_cost).label('revenue')
                ).filter(
                    Project.status == 'completed',
                    Project.updated_at >= period_start
                ).group_by(func.date(Project.updated_at)).order_by('date').all()
                
                return {
                    'creation_trend': [
                        {'date': str(item.date), 'value': item.count}
                        for item in creation_trend
                    ],
                    'completion_trend': [
                        {'date': str(item.date), 'value': item.count}
                        for item in completion_trend
                    ],
                    'revenue_trend': [
                        {'date': str(item.date), 'value': float(item.revenue or 0)}
                        for item in revenue_trend
                    ]
                }
                
        except Exception as e:
            logger.error(f"Ошибка при получении трендов проектов: {e}")
            return {}
    
    def clear_cache(self):
        """Очистка кэша"""
        self.cache.clear()
        logger.info("Кэш аналитики очищен")

# Создаем глобальный экземпляр сервиса
analytics_service = AnalyticsService()

# Функции-обертки для удобства
def get_dashboard_data(period_days: int = 7) -> Dict[str, Any]:
    """Получение данных для дашборда"""
    return {
        'user_stats': analytics_service.get_user_statistics(period_days),
        'project_stats': analytics_service.get_project_statistics(period_days),
        'consultant_stats': analytics_service.get_consultant_statistics(period_days),
        'financial_stats': analytics_service.get_financial_report(period_days),
        'performance_metrics': analytics_service.get_performance_metrics()
    }

def get_weekly_report() -> Dict[str, Any]:
    """Еженедельный отчет"""
    return analytics_service.generate_full_report(7)

def get_monthly_report() -> Dict[str, Any]:
    """Месячный отчет"""
    return analytics_service.generate_full_report(30)