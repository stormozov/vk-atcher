import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from settings import COMMANDS, MESSAGES


class VKBot:
    def __init__(self, group_token: str) -> None:
        self.token = group_token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)

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

                if request in COMMANDS["start"]:
                    self.send_message(
                        event.user_id,
                        MESSAGES["start"]
                    )
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
