import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from settings import COMMANDS, MESSAGES
from vk_bot import UserInfoRetriever, UserVK
from database.base_funcs import (
    add_bot_user_to_db,
    match_data_layout,
    add_match_user_to_db,
    get_match_info_to_print,
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
        self.found_user_id = None
        # Инициализация пагинатора поиска пользователей
        self.paginator = Paginator(self.received_profile_info)
        # Инициализация счетчика команды "next"
        self.next_command_count = 0
        self.count = 0

    def send_message(self, user_id: int, msg: str) -> None:
        self.vk.method(
            "messages.send",
            {
                "user_id": user_id,
                "message": msg,
                "random_id": 0
            }
        )

    def send_match_info(
            self,
            vk_user_id: int,
            attachment: str = None,
            count: int = 0
    ) -> None:

        info_to_send = match_data_layout(vk_user_id)

        if 0 <= count < len(info_to_send):
            message = info_to_send[count][0]  # Имя пользователя
            url = info_to_send[count][1]  # Ссылка на профиль
            photos = info_to_send[count][2]  # Фото пользователя

            message_text = f'{message}\n{url}'

            if photos:
                attachment = ','.join(photos)

            self.vk.method('messages.send', {
                'user_id': vk_user_id,
                'message': message_text,
                'random_id': 0,
                'attachment': attachment
            })

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
            print(self.received_profile_info.get_user_photos(self.found_user_id))
            # # # Пробую загрузить данные пользователя для поиска мэтчей из базы данных
            # print(add_bot_user_to_db(data))
            # print(get_user_params(self.user_id, session))

            # # # Загружаю мэтч в БД
            # match = self.received_profile_info.search_users(self.user_id)
            # print(self.received_profile_info._add_user_photos_and_url(match))
            # # print("ВЫВОД МАТЧЕЙ")
            # print(match)
            # print(add_match_user_to_db(match, self.user_id))
            # print(get_pic_ids(match,session))

        elif request in COMMANDS["hello"]:
            self.send_message(
                self.user_id,
                MESSAGES["hello"]
            )
            self.send_match_info(self.user_id)
        elif request in COMMANDS["goodbye"]:
            self.count += 1
            self.send_message(self.user_id, MESSAGES["goodbye"])
            self.send_match_info(self.user_id, count=self.count)

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
