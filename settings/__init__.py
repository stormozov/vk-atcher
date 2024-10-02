"""Инициализация модулей пакета настроек.

Модули, содержащие настройки бота, импортируются в этот модуль.
"""
from .messages import MESSAGES
from .commands import COMMANDS
from .keyboards import KEYBOARDS


__all__ = [
    "MESSAGES",
    "COMMANDS",
    "KEYBOARDS"
]
