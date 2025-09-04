"""
Планировщик фоновых задач для системы уведомлений
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from ..database.database import get_db_context
from ..config.logging import get_logger
from .task_notification_service import task_notification_service

logger = get_logger(__name__)

class TaskScheduler:
    """Планировщик для фоновых задач уведомлений"""
    
    def __init__(self):
        self.is_running = False
        self.task_handle: Optional[asyncio.Task] = None
        
    async def start(self):
        """Запустить планировщик"""
        if self.is_running:
            logger.warning("Планировщик уже запущен")
            return
            
        self.is_running = True
        self.task_handle = asyncio.create_task(self._scheduler_loop())
        logger.info("Планировщик задач запущен")
        
    async def stop(self):
        """Остановить планировщик"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.task_handle:
            self.task_handle.cancel()
            try:
                await self.task_handle
            except asyncio.CancelledError:
                pass
                
        logger.info("Планировщик задач остановлен")
        
    async def _scheduler_loop(self):
        """Основной цикл планировщика"""
        while self.is_running:
            try:
                # Проверяем дедлайны каждые 30 минут
                await self._check_task_deadlines()
                await asyncio.sleep(30 * 60)  # 30 минут
                
            except asyncio.CancelledError:
                logger.info("Планировщик задач прерван")
                break
            except Exception as e:
                logger.error(f"Ошибка в планировщике задач: {e}")
                # Ждем 5 минут перед повторной попыткой при ошибке
                await asyncio.sleep(5 * 60)
                
    async def _check_task_deadlines(self):
        """Проверить дедлайны задач и отправить напоминания"""
        try:
            with get_db_context() as db:
                sent_count = await task_notification_service.check_and_send_deadline_reminders(db)
                if sent_count > 0:
                    logger.info(f"Отправлено {sent_count} напоминаний о дедлайнах")
                    
        except Exception as e:
            logger.error(f"Ошибка при проверке дедлайнов: {e}")

# Глобальный экземпляр планировщика
task_scheduler = TaskScheduler()