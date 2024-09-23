from vk_api.keyboard import VkKeyboard


class VKKeyboard:
    @staticmethod
    def _create_layout(
            btns: list[tuple[str, str]],
            one_time: bool = False,
            inline: bool = False
    ) -> VkKeyboard | None:
        if not isinstance(btns, list):
            return None

        keyboard = VkKeyboard(one_time, inline)

        for btn in btns:
            if (not isinstance(btn, tuple) or len(btn) != 2
                    or not all(isinstance(x, str) for x in btn)):
                return None

            keyboard.add_button(btn[0], btn[1])

        return keyboard

    def create_markup(
            self,
            btns: list[tuple[str, str]] | None = None,
            one_time: bool = True,
            inline: bool = False
    ) -> str | None:
        if not btns:
            return None

        keyboard = self._create_layout(btns, one_time, inline)
        return keyboard.get_keyboard()
