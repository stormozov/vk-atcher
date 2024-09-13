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

    def handle_new_user(self, user_id: int) -> None:
        received_info: dict = self.received_profile_info.get_profile_info()
        received_user_url = self.received_profile_info.get_user_url(user_id)

        if self.user_info.get_user_info()["id"] is None:
            self.user_info.set_user_info(
                user_id, received_info, received_user_url
            )

    def start(self) -> None:
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.strip().lower()

                if request in COMMANDS["start"]:
                    self.handle_new_user(event.user_id)
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
