import requests
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from settings import COMMANDS, MESSAGES
from vk_bot import UserInfoRetriever, UserVK


class VKBot:
    def __init__(self, group_token: str) -> None:
        self.token = group_token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)
        self.received_profile_info = UserInfoRetriever()
        self.user_info = UserVK()

    def send_message(self, user_id: int, msg: str) -> None:
        self.vk.method(
            "messages.send",
            {
                "user_id": user_id,
                "message": msg,
                "random_id": 0
            }
        )

    def start(self) -> None:
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.strip().lower()
                self._handle_user_request(event, request)

    def _handle_user_request(self, event: vk_api.longpoll, request: str) \
            -> None:
        if request in COMMANDS["start"]:
            self.send_message(
                event.user_id,
                MESSAGES["start"]
            )
            # Вывожу данные по юзеру в консоль (для дебага)
            # Принт сработает только после выполнения команды start
            print(self.received_profile_info.get_profile_info(event.user_id))
        elif request in COMMANDS["hello"]:
            self.send_message(
                event.user_id,
                MESSAGES["hello"]
            )
        elif request in COMMANDS["goodbye"]:
            self.send_message(
                event.user_id,
                MESSAGES["goodbye"]
            )
        else:
            self.send_message(
                event.user_id,
                MESSAGES["unknown_command"]
            )
