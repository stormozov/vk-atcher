import requests
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from sqlalchemy.orm import sessionmaker

from settings import COMMANDS, MESSAGES
from vk_bot import UserInfoRetriever, UserVK
from database.base_funcs import (
    add_bot_user_to_db,
    add_match_user_to_db,
    get_user_params,
    Session
)
from vk_bot.search_paginator import Paginator

session = Session()


class VKBot:
    def __init__(self, group_token: str, db_session: Session) -> None:
        self.user_id = None
        self.token = group_token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpoll = VkLongPoll(self.vk)
        self.received_profile_info = UserInfoRetriever(db_session)
        self.user_info = UserVK()
        # Инициализация пагинатора поиска пользователей
        self.paginator = Paginator(self.received_profile_info)
        # Инициализация счетчика команды "next"
        self.next_command_count = 0

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
                self.user_id = event.user_id
                self._handle_user_request(request)

    def get_user_id(self) -> int:
        return self.user_id

    def _handle_user_request(self, request: str) \
            -> None:
        if request in COMMANDS["start"]:
            self.send_message(
                self.user_id,
                MESSAGES["start"]
            )
            # Вывожу данные по юзеру в консоль (для дебага)
            # Принт сработает только после выполнения команды start
            # Тесты получения инфо
            data = self.received_profile_info.get_profile_info(self.user_id)
            print(data)
            # # Пробую загрузить данные пользователя для поиска мэтчей из базы данных
            print(add_bot_user_to_db(data))
            print(self.user_id)
            print(get_user_params(self.user_id, session))
            # print(self.received_profile_info.search_users(event.user_id))
            # Загружаю мэтч в БД
            match = self.received_profile_info.search_users(self.user_id)
            print("ВЫВОД МАТЧЕЙ")
            # print(match)
            print(add_match_user_to_db(match, self.user_id))
        elif request in COMMANDS["hello"]:
            self.send_message(
                self.user_id,
                MESSAGES["hello"]
            )
        elif request in COMMANDS["goodbye"]:
            self.send_message(
                self.user_id,
                MESSAGES["goodbye"]
            )
        elif request in COMMANDS["next"]:
            print("ПАГИНАТОР ПОИСКА")  # Для дебага
            self.next_command_count += 1  # Увеличиваем счетчик команды "next"
            print("Счетчик команды:", self.next_command_count)  # Для дебага

            if self.next_command_count == 4:
                # Если счетчик команды "next" равен 4,
                # то добавляем новый матч в базу данных
                match = self.paginator.next(self.user_id)
                add_match_user_to_db(match, self.user_id)

            if self.next_command_count == 5:
                # Если счетчик команды "next" равен 5,
                # то выводим пока что только сообщение и сбрасываем счетчик
                self.send_message(
                    self.user_id,
                    "Следующие 5 пользователей"
                )
                self.next_command_count = 0
        else:
            self.send_message(
                self.user_id,
                MESSAGES["unknown_command"]
            )
