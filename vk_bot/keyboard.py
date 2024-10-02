"""Модуль для создания клавиатуры."""
from vk_api.keyboard import VkKeyboard


class VKKeyboard:
    """Класс для создания клавиатуры."""
    def create_markup(
            self,
            btns: dict[str, list[tuple[str, str]] | bool] | None = None
    ) -> str | None:
        """Метод для создания клавиатуры.

        Args:
            btns (dict[str, list[tuple[str, str]] | bool] | None, optional):
                Кнопки клавиатуры. По умолчанию None.

        Returns:
            str: Клавиатура в формате JSON.
            None: Если параметр btns не является словарем.
        """
        keyboard = self._create_layout(btns)

        if keyboard is not None:
            return keyboard.get_keyboard()

    def _create_layout(
            self,
            btns: dict[str, list[tuple[str, str]] | bool] | None = None
    ) -> VkKeyboard | None:
        """Метод для создания разметки клавиатуры.

        Args:
            btns (dict[str, list[tuple[str, str]] | bool] | None, optional):
                Кнопки клавиатуры. По умолчанию None.

        Returns:
            VkKeyboard: Клавиатура.
            None: Если параметр btns не является словарем.
        """
        if not self._validate_buttons_dict(btns):
            return None

        keyboard = VkKeyboard(btns.get("one_time"), btns.get("inline"))

        for btn in btns["btns"]:
            if not self._validate_button(btn):
                return None

            keyboard.add_button(btn[0], btn[1])

        return keyboard

    @staticmethod
    def _validate_buttons_dict(
            btns: dict[str, list[tuple[str, str]] | bool] | None) -> bool:
        """Метод для проверки корректности словаря с кнопками клавиатуры.

        Args:
            btns (dict[str, list[tuple[str, str]] | bool] | None, optional):
                Кнопки клавиатуры. По умолчанию None.

        Returns:
            bool: Результат проверки.
        """
        if not isinstance(btns, dict) or not isinstance(btns.get("btns"), list):
            return False

        if (not isinstance(btns.get("one_time"), bool)
                or not isinstance(btns.get("inline"), bool)):
            return False

        return True

    @staticmethod
    def _validate_button(btn: tuple[str, str]) -> bool:
        """Метод для проверки корректности кнопки клавиатуры.

        Args:
            btn (tuple[str, str]): Кнопка клавиатуры.

        Returns:
            bool: Результат проверки.
        """
        if (not isinstance(btn, tuple) or len(btn) != 2
                or not all(isinstance(x, str) for x in btn)):
            return False

        return True
