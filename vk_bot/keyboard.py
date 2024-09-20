from vk_api.keyboard import VkKeyboard


class VKKeyboard:
    @staticmethod
    def create_keyboard(
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

    def build_keyboard(
            self,
            btns: list[tuple[str, str]],
            one_time: bool = False,
            inline: bool = False
    ) -> str | None:
        keyboard = self.create_keyboard(btns, one_time, inline)
        return keyboard.get_keyboard()
