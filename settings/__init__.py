"""Initialization of the settings package modules.

The modules that contain the bot settings are imported into this module.
"""
from .messages import MESSAGES
from .commands import COMMANDS
from .keyboards import KEYBOARDS


__all__ = [
    "MESSAGES",
    "COMMANDS",
    "KEYBOARDS"
]
