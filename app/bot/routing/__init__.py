"""Модуль маршрутизации для Telegram бота"""

from .callback_router import CallbackRouter, get_callback_router, callback_router

__all__ = ['CallbackRouter', 'get_callback_router', 'callback_router']