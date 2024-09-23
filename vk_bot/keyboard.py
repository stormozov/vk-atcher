from vk_api.keyboard import VkKeyboard


class VKKeyboard:
    def create_markup(
            self,
            btns: dict[str, list[tuple[str, str]] | bool] | None = None
    ) -> str | None:
        keyboard = self._create_layout(btns)

        if keyboard is not None:
            return keyboard.get_keyboard()

    def _create_layout(
            self,
            btns: dict[str, list[tuple[str, str]] | bool] | None = None
    ) -> VkKeyboard | None:
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
        if not isinstance(btns, dict) or not isinstance(btns.get("btns"), list):
            return False

        if (not isinstance(btns.get("one_time"), bool)
                or not isinstance(btns.get("inline"), bool)):
            return False

        return True

    @staticmethod
    def _validate_button(btn: tuple[str, str]) -> bool:
        if (not isinstance(btn, tuple) or len(btn) != 2
                or not all(isinstance(x, str) for x in btn)):
            return False

        return True
