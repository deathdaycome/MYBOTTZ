"""
Сервис уведомлений о просроченных платежах через Telegram
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional
import requests
from app.config.logging import get_logger

logger = get_logger(__name__)

# Путь к БД
DB_PATH = os.getenv('DATABASE_PATH', '/app/data/bot.db')
if not os.path.exists(DB_PATH):
    DB_PATH = 'data/bot.db'


class PaymentNotificationService:
    """Сервис для отправки уведомлений о просроченных платежах"""

    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_telegram_message(self, chat_id: int, message: str, parse_mode: str = "HTML") -> bool:
        """Отправить сообщение в Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info(f"Уведомление о платеже отправлено пользователю {chat_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка отправки уведомления пользователю {chat_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке уведомления: {e}")
            return False

    def check_overdue_payments(self) -> List[dict]:
        """
        Проверить просроченные платежи

        Returns:
            List[dict]: Список просроченных платежей с информацией о проектах и клиентах
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Получаем просроченные платежи (due_date прошла, status != PAID)
            cursor.execute("""
                SELECT
                    p.id,
                    p.type,
                    p.amount,
                    p.due_date,
                    p.description,
                    p.project_id,
                    p.client_id,
                    pr.title as project_title,
                    u.telegram_id,
                    u.username
                FROM payments p
                LEFT JOIN projects pr ON p.project_id = pr.id
                LEFT JOIN users u ON p.client_id = u.id
                WHERE p.status != 'PAID'
                AND p.due_date IS NOT NULL
                AND DATE(p.due_date) < DATE('now')
                ORDER BY p.due_date ASC
            """)

            overdue_payments = []
            for row in cursor.fetchall():
                overdue_payments.append({
                    'id': row[0],
                    'type': row[1],
                    'amount': row[2],
                    'due_date': row[3],
                    'description': row[4],
                    'project_id': row[5],
                    'client_id': row[6],
                    'project_title': row[7],
                    'client_telegram_id': row[8],
                    'client_username': row[9]
                })

            conn.close()
            return overdue_payments

        except Exception as e:
            logger.error(f"Ошибка при проверке просроченных платежей: {e}")
            return []

    def check_upcoming_payments(self, days_ahead: int = 3) -> List[dict]:
        """
        Проверить предстоящие платежи (за N дней до даты платежа)

        Args:
            days_ahead: За сколько дней до платежа отправлять напоминание

        Returns:
            List[dict]: Список предстоящих платежей
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    p.id,
                    p.type,
                    p.amount,
                    p.due_date,
                    p.description,
                    p.project_id,
                    p.client_id,
                    pr.title as project_title,
                    u.telegram_id,
                    u.username
                FROM payments p
                LEFT JOIN projects pr ON p.project_id = pr.id
                LEFT JOIN users u ON p.client_id = u.id
                WHERE p.status != 'PAID'
                AND p.due_date IS NOT NULL
                AND DATE(p.due_date) BETWEEN DATE('now') AND DATE('now', '+' || ? || ' days')
                ORDER BY p.due_date ASC
            """, (days_ahead,))

            upcoming_payments = []
            for row in cursor.fetchall():
                upcoming_payments.append({
                    'id': row[0],
                    'type': row[1],
                    'amount': row[2],
                    'due_date': row[3],
                    'description': row[4],
                    'project_id': row[5],
                    'client_id': row[6],
                    'project_title': row[7],
                    'client_telegram_id': row[8],
                    'client_username': row[9]
                })

            conn.close()
            return upcoming_payments

        except Exception as e:
            logger.error(f"Ошибка при проверке предстоящих платежей: {e}")
            return []

    def notify_overdue_payment(self, payment: dict) -> bool:
        """
        Отправить уведомление о просроченном платеже

        Args:
            payment: Информация о платеже

        Returns:
            bool: Успешность отправки
        """
        try:
            # Определяем, кому отправлять (клиенту или менеджеру проекта)
            telegram_id = payment.get('client_telegram_id')

            if not telegram_id:
                logger.warning(f"У платежа {payment['id']} нет Telegram ID для уведомления")
                return False

            # Рассчитываем количество дней просрочки
            due_date = datetime.fromisoformat(payment['due_date'].replace('Z', '+00:00'))
            days_overdue = (datetime.now() - due_date).days

            # Формируем сообщение
            message = f"""
<b>⚠️ ПРОСРОЧЕННЫЙ ПЛАТЁЖ</b>

<b>Проект:</b> {payment.get('project_title', 'Не указан')}
<b>Тип платежа:</b> {self._format_payment_type(payment['type'])}
<b>Сумма:</b> {payment['amount']:,.0f} ₽
<b>Дата платежа:</b> {payment['due_date'][:10]}
<b>Просрочка:</b> {days_overdue} дн.

{payment.get('description', '')}

❗️ Пожалуйста, произведите оплату как можно скорее.
            """.strip()

            return self.send_telegram_message(telegram_id, message)

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о просроченном платеже: {e}")
            return False

    def notify_upcoming_payment(self, payment: dict) -> bool:
        """
        Отправить уведомление о предстоящем платеже

        Args:
            payment: Информация о платеже

        Returns:
            bool: Успешность отправки
        """
        try:
            telegram_id = payment.get('client_telegram_id')

            if not telegram_id:
                logger.warning(f"У платежа {payment['id']} нет Telegram ID для уведомления")
                return False

            # Рассчитываем количество дней до платежа
            due_date = datetime.fromisoformat(payment['due_date'].replace('Z', '+00:00'))
            days_until = (due_date - datetime.now()).days

            # Формируем сообщение
            message = f"""
<b>🔔 НАПОМИНАНИЕ О ПЛАТЕЖЕ</b>

<b>Проект:</b> {payment.get('project_title', 'Не указан')}
<b>Тип платежа:</b> {self._format_payment_type(payment['type'])}
<b>Сумма:</b> {payment['amount']:,.0f} ₽
<b>Дата платежа:</b> {payment['due_date'][:10]}
<b>Осталось:</b> {days_until} дн.

{payment.get('description', '')}

Пожалуйста, подготовьте оплату заранее.
            """.strip()

            return self.send_telegram_message(telegram_id, message)

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о предстоящем платеже: {e}")
            return False

    def _format_payment_type(self, payment_type: str) -> str:
        """Форматировать тип платежа для отображения"""
        types = {
            'PREPAYMENT': 'Предоплата',
            'MILESTONE': 'Этап',
            'FINAL': 'Финальный платёж',
            'ADDITIONAL': 'Дополнительный'
        }
        return types.get(payment_type, payment_type)

    def send_payment_notifications(self) -> dict:
        """
        Отправить все уведомления о платежах (просроченные + предстоящие)

        Returns:
            dict: Статистика отправленных уведомлений
        """
        try:
            stats = {
                'overdue_checked': 0,
                'overdue_sent': 0,
                'upcoming_checked': 0,
                'upcoming_sent': 0
            }

            # Проверяем просроченные платежи
            overdue_payments = self.check_overdue_payments()
            stats['overdue_checked'] = len(overdue_payments)

            for payment in overdue_payments:
                if self.notify_overdue_payment(payment):
                    stats['overdue_sent'] += 1

            # Проверяем предстоящие платежи (за 3 дня)
            upcoming_payments = self.check_upcoming_payments(days_ahead=3)
            stats['upcoming_checked'] = len(upcoming_payments)

            for payment in upcoming_payments:
                if self.notify_upcoming_payment(payment):
                    stats['upcoming_sent'] += 1

            logger.info(f"Уведомления о платежах: просрочено {stats['overdue_sent']}/{stats['overdue_checked']}, "
                       f"предстоящие {stats['upcoming_sent']}/{stats['upcoming_checked']}")

            return stats

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомлений о платежах: {e}")
            return {'error': str(e)}


# Глобальный экземпляр сервиса
payment_notification_service = PaymentNotificationService()
