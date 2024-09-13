"""Initialization of the settings package modules.

The modules that contain the bot settings are imported into this module.
"""
from .messages import MESSAGES
from .commands import COMMANDS


__all__ = [
    "MESSAGES",
    "COMMANDS"
]
