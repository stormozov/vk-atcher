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
    "show_favorites": ("показать избранных", "список избранных"),
    "del_from_favorites": ("удалить из избранных", "убрать из избранного"),
    "add_to_black_list": ("добавить в черный список", "❌"),
    "show_black_list": ("показать черный список", "черный список",
                        "заблокированные"),
    "del_from_black_list": ("убрать из черного списка", "удалить из ЧС"),
}
