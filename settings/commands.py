"""A module with text commands for the bot.

This module defines a dictionary of commands that the bot can respond to.
The keys of the dictionary are the command names, and the values are lists of
alternative command names.
"""

COMMANDS = {
    "start": ("начать", "старт", "start", "запуск"),
    "hello": ("привет", "hello"),
    "goodbye": ("пока", "goodbye"),
    "show": ("показать", "show", "начать поиск"),
    "next": (
        "next", "следующий", "👎", "следующие",
        "дальше", "продолжить поиск",
    ),
    "add_to_favorites": ("добавить в избранное", "👍"),
}
