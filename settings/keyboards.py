""" Модуль с клавиатурными настройками.

Каждый элемент клавиатуры представлен словарем с настройками.
"""

KEYBOARDS = {
	"start": {
		"btns": [
			("Начать поиск", "positive"),
			("Помощь", "primary"),
		],
		"one_time": True,
		"inline": False
	},
	"help": {
		"btns": [
			("Начать поиск", "positive"),
		],
		"one_time": True,
		"inline": False,
	},
	"card": {
		"btns": [
			("👍", "positive"),
			("👎", "secondary"),
			("❌", "negative")
		],
		"one_time": True,
		"inline": False
	},
	"add_to_favorites": {
		"btns": [
			("Продолжить поиск", "positive"),
			("Список избранных", "secondary"),
		],
		"one_time": True,
		"inline": False
	},
	"del_from_favorites": {
		"btns": [
			("Продолжить поиск", "positive"),
			("Убрать из избранного", "secondary"),
		],
		"one_time": True,
		"inline": False
	},
	"next": {
		"btns": [
			("Продолжить поиск", "positive"),
		],
		"one_time": True,
		"inline": False
	},
	"add_to_black_list": {
		"btns": [
			("Продолжить поиск", "positive"),
			("Черный список", "secondary"),
		],
		"one_time": True,
		"inline": False
	},
	"del_from_black_list": {
		"btns": [
			("Продолжить поиск", "positive"),
			("Убрать из черного списка", "secondary"),
		],
		"one_time": True,
		"inline": False
	}
}
