# app/services/scheduler.py
import asyncio
import schedule
import time
from datetime import datetime
from threading import Thread
from sqlalchemy.orm import Session

from ..database.database import SessionLocal
from ..config.logging import get_logger
from .project_automation import ProjectAutomationService

logger = get_logger(__name__)


class SchedulerService:
    """Сервис планировщика задач"""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        
    def start(self):
        """Запустить планировщик"""
        if self.is_running:
            logger.warning("Планировщик уже запущен")
            return
            
        self.is_running = True
        
        # Настраиваем расписание
        self._setup_schedule()
        
        # Запускаем в отдельном потоке
        self.thread = Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("Планировщик задач запущен")
    
    def stop(self):
        """Остановить планировщик"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Планировщик задач остановлен")
    
    def _setup_schedule(self):
        """Настроить расписание задач"""
        # Ежедневная проверка в 09:00
        schedule.every().day.at("09:00").do(self._run_daily_checks)
        
        # Проверка просроченных проектов каждые 4 часа
        schedule.every(4).hours.do(self._check_overdue_projects)
        
        # Проверка финансов раз в день в 18:00
        schedule.every().day.at("18:00").do(self._check_financial_status)
        
        # Еженедельный отчет по понедельникам в 10:00
        schedule.every().monday.at("10:00").do(self._generate_weekly_report)
        
        logger.info("Расписание задач настроено")
    
    def _run_scheduler(self):
        """Основной цикл планировщика"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
            except Exception as e:
                logger.error(f"Ошибка в планировщике: {str(e)}")
                time.sleep(60)
    
    def _run_daily_checks(self):
        """Запустить ежедневные проверки"""
        logger.info("Запуск ежедневных проверок...")
        
        try:
            db = SessionLocal()
            automation = ProjectAutomationService(db)
            
            # Запускаем асинхронную функцию в синхронном контексте
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(automation.run_daily_checks())
            loop.close()
            
            db.close()
            logger.info("Ежедневные проверки завершены")
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении ежедневных проверок: {str(e)}")
    
    def _check_overdue_projects(self):
        """Проверить просроченные проекты"""
        logger.info("Проверка просроченных проектов...")
        
        try:
            db = SessionLocal()
            automation = ProjectAutomationService(db)
            
            overdue = automation.check_overdue_projects()
            if overdue:
                logger.warning(f"Найдено {len(overdue)} просроченных проектов")
                
                # Отправляем уведомление
                message = f"⚠️ Обнаружено {len(overdue)} просроченных проектов!"
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(automation.send_notification(message))
                loop.close()
            
            db.close()
            
        except Exception as e:
            logger.error(f"Ошибка при проверке просроченных проектов: {str(e)}")
    
    def _check_financial_status(self):
        """Проверить финансовый статус проектов"""
        logger.info("Проверка финансового статуса...")
        
        try:
            db = SessionLocal()
            automation = ProjectAutomationService(db)
            
            # Проверяем неоплаченные проекты
            unpaid_projects = automation.check_unpaid_projects()
            
            # Проверяем задолженности перед исполнителями
            unpaid_executors = automation.check_unpaid_executors()
            
            if unpaid_projects or unpaid_executors:
                message = "💰 <b>Финансовый отчет:</b>\n\n"
                
                if unpaid_projects:
                    total_debt = sum(p['remaining'] for p in unpaid_projects)
                    message += f"📌 Неоплаченных проектов: {len(unpaid_projects)}\n"
                    message += f"   Общая задолженность: {total_debt:,.0f} ₽\n\n"
                
                if unpaid_executors:
                    total_debt = sum(e['remaining'] for e in unpaid_executors)
                    message += f"👷 Задолженность перед исполнителями: {len(unpaid_executors)}\n"
                    message += f"   Общая сумма: {total_debt:,.0f} ₽\n"
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(automation.send_notification(message))
                loop.close()
            
            db.close()
            
        except Exception as e:
            logger.error(f"Ошибка при проверке финансового статуса: {str(e)}")
    
    def _generate_weekly_report(self):
        """Генерировать еженедельный отчет"""
        logger.info("Генерация еженедельного отчета...")
        
        try:
            db = SessionLocal()
            automation = ProjectAutomationService(db)
            
            summary = automation.get_automation_summary()
            
            message = "📊 <b>Еженедельный отчет</b>\n\n"
            message += f"📁 Всего проектов: {summary.get('total_projects', 0)}\n"
            message += f"⚠️ Просроченных: {summary.get('overdue_count', 0)}\n"
            message += f"💸 Неоплаченных: {summary.get('unpaid_projects_count', 0)}\n"
            message += f"👷 Долги исполнителям: {summary.get('unpaid_executors_count', 0)}\n\n"
            message += f"💰 Ожидается от клиентов: {summary.get('total_unpaid_clients', 0):,.0f} ₽\n"
            message += f"💰 К выплате исполнителям: {summary.get('total_unpaid_executors', 0):,.0f} ₽\n"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(automation.send_notification(message))
            loop.close()
            
            db.close()
            logger.info("Еженедельный отчет отправлен")
            
        except Exception as e:
            logger.error(f"Ошибка при генерации еженедельного отчета: {str(e)}")
    
    def run_task_now(self, task_name: str):
        """Запустить задачу немедленно"""
        tasks = {
            'daily_checks': self._run_daily_checks,
            'overdue_projects': self._check_overdue_projects,
            'financial_status': self._check_financial_status,
            'weekly_report': self._generate_weekly_report
        }
        
        if task_name in tasks:
            logger.info(f"Немедленный запуск задачи: {task_name}")
            tasks[task_name]()
            return True
        else:
            logger.error(f"Неизвестная задача: {task_name}")
            return False


# Глобальный экземпляр планировщика
scheduler = SchedulerService()