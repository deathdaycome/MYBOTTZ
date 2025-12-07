"""
Common background tasks for the CRM system

This module contains shared tasks that don't belong to a specific module.
"""

from app.core.celery_app import celery_app, BaseTask
from app.core.logging import logger


# Import task examples
from app.core.celery_app import (
    example_task,
    example_async_task,
    example_chain_task,
    cleanup_old_results,
    health_check_task,
)

__all__ = [
    "celery_app",
    "BaseTask",
    "example_task",
    "example_async_task",
    "example_chain_task",
    "cleanup_old_results",
    "health_check_task",
    "send_email_task",
    "send_notification_task",
]


# ============================================
# EMAIL TASKS
# ============================================

@celery_app.task(name="app.tasks.send_email_task", base=BaseTask, bind=True)
def send_email_task(self, to_email: str, subject: str, body: str, html: bool = False):
    """
    Send email task (placeholder - implement actual email logic)

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        html: Whether body is HTML
    """
    try:
        logger.info(
            "send_email_started",
            task_id=self.request.id,
            to_email=to_email,
            subject=subject,
        )

        # TODO: Implement actual email sending
        # Example:
        # import smtplib
        # from email.message import EmailMessage
        # msg = EmailMessage()
        # msg.set_content(body)
        # msg['Subject'] = subject
        # msg['From'] = 'noreply@crm.local'
        # msg['To'] = to_email
        # s = smtplib.SMTP('localhost')
        # s.send_message(msg)
        # s.quit()

        logger.info(
            "send_email_completed",
            task_id=self.request.id,
            to_email=to_email,
        )

        return {"status": "success", "to_email": to_email, "subject": subject}

    except Exception as e:
        logger.error(
            "send_email_failed",
            task_id=self.request.id,
            to_email=to_email,
            error=str(e),
            exc_info=True,
        )
        raise


# ============================================
# NOTIFICATION TASKS
# ============================================

@celery_app.task(name="app.tasks.send_notification_task", base=BaseTask, bind=True)
def send_notification_task(self, user_id: int, title: str, message: str, type: str = "info"):
    """
    Send notification to user (Telegram, push, etc.)

    Args:
        user_id: User ID to send notification to
        title: Notification title
        message: Notification message
        type: Notification type (info, warning, error, success)
    """
    try:
        logger.info(
            "send_notification_started",
            task_id=self.request.id,
            user_id=user_id,
            title=title,
            type=type,
        )

        # TODO: Implement actual notification sending
        # Example: Send Telegram message, push notification, etc.

        logger.info(
            "send_notification_completed",
            task_id=self.request.id,
            user_id=user_id,
        )

        return {
            "status": "success",
            "user_id": user_id,
            "title": title,
            "type": type,
        }

    except Exception as e:
        logger.error(
            "send_notification_failed",
            task_id=self.request.id,
            user_id=user_id,
            error=str(e),
            exc_info=True,
        )
        raise
