import requests
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from sqlalchemy.orm import sessionmaker

from settings import COMMANDS, MESSAGES
from vk_bot import UserInfoRetriever, UserVK
from database.base_funcs import add_bot_user_to_db,add_match_user_to_db, get_user_params, Session

session = Session()
class VKBot:
    def __init__(self, group_token: str, db_session: Session) -> None:
        self.user_id = None
        self.token = group_token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)
        self.received_profile_info = UserInfoRetriever(db_session)
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
                self.user_id = event.user_id

    def get_user_id(self) -> int:
        return self.user_id

    def _handle_user_request(self, event: vk_api.longpoll, request: str) \
            -> None:
        if request in COMMANDS["start"]:
            self.send_message(
                event.user_id,
                MESSAGES["start"]
            )
            # Вывожу данные по юзеру в консоль (для дебага)
            # Принт сработает только после выполнения команды start
            # Тесты получения инфо
            data = self.received_profile_info.get_profile_info(event.user_id)
            print(data)
            # # Пробую загрузить данные пользователя для поиска мэтчей из базы данных
            print(add_bot_user_to_db(data))
            print(event.user_id)
            print(get_user_params(event.user_id, session))
            print(self.received_profile_info.search_users(event.user_id))
            # Загружаю мэтч в БД
            match = self.received_profile_info.search_users(event.user_id)
            print(add_match_user_to_db(match, event.user_id))



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
