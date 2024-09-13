import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


class VKBot:
    def __init__(self, group_token: str) -> None:
        self.token = group_token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)

    def send_message(self, user_id: int, message: str) -> None:
        self.vk.method(
            "messages.send",
            {
                "user_id": user_id,
                "message": message,
                "random_id": 0
            }
        )

    def start(self) -> None:
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.strip().lower()

                if request in ("начать", "старт", "start", "запуск"):
                    self.send_message(
                        event.user_id,
                        "Привет! Я бот Atcher. Я помогаю найти "
                        "новые знакомства 🧡❤\n\n"
                        "При поиске 🔎 бот 🤖 учитывает ваш город 🏙, "
                        "возраст 🔞 и пол 🧒🧑\n Данные берутся из "
                        "вашего профиля вконтакте.\n\n"
                        "Желаем вам удачи в поиске!\n\n"
                        "------------------------------------------------\n"
                        "Версия бота: 1.0.0\n"
                        "Авторы: "
                        "Сергей Тормозов и Дмитрий Куренков\n"
                        "GitHub repository: https://github.com/stormozov/vk-atcher"
                    )
