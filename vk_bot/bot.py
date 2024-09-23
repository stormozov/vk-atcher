import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from settings import COMMANDS, KEYBOARDS, MESSAGES
from vk_bot import UserInfoRetriever, UserVK
from database.base_funcs import (
    add_bot_user_to_db,
    match_data_layout,
    add_match_user_to_db,
    get_match_info_to_print,
    Session
)
from vk_bot.keyboard import VKKeyboard
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
        self.keyboard = VKKeyboard()
        self.found_user_id = None
        # Инициализация пагинатора поиска пользователей
        self.paginator = Paginator(self.received_profile_info)
        # Инициализация счётчиков команд
        self.next_command_count = 0
        self.match_info_count = 0

    def send_message(
            self,
            user_id: int,
            msg: str,
            btns: list[tuple[str, str]] = None,
            one_time: bool = True,
            inline: bool = False
    ) -> None:
        keyboard_json: str | None = (
            self.keyboard.create_markup(btns, one_time, inline))

        self.vk.method(
            "messages.send",
            {
                "user_id": user_id,
                "message": msg,
                "random_id": 0,
                "keyboard": keyboard_json
            }
        )

    def send_match_info(
            self,
            vk_user_id: int,
            attachment: str = None,
            count: int = 0,
            btns: list[tuple[str, str]] = None,
            one_time: bool = True,
            inline: bool = False
    ) -> None:
        keyboard_json: str | None = (
            self.keyboard.create_markup(btns, one_time, inline))

        match_info = match_data_layout(vk_user_id)

        if 0 <= count < len(match_info):
            username = match_info[count][0]  # Имя пользователя
            profile_url = match_info[count][1]  # Ссылка на профиль
            user_photos = match_info[count][2]  # Фото пользователя

            user_info_text = f'{username}\n{profile_url}'

            if user_photos:
                attachment = ','.join(user_photos)

            self.vk.method('messages.send', {
                'user_id': vk_user_id,
                'message': user_info_text,
                'random_id': 0,
                'attachment': attachment,
                'keyboard': keyboard_json
            })

    def start(self) -> None:
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.strip().lower()
                self.user_id = event.user_id
                self._handle_user_request(request)

    def get_user_id(self) -> int:
        return self.user_id

    def _handle_user_request(self, request: str) -> None:
        if request in COMMANDS["start"]:
            self.send_message(
                self.user_id,
                MESSAGES["start"],
                KEYBOARDS["start"]["btns"]
            )
            #: Получаю информацию о пользователе,
            #: который взаимодействует с ботом
            data = self.received_profile_info.get_profile_info(self.user_id)
            #: Вывожу полученные данные о пользователе в консоль (для отладки)
            # print(data)
            # print(self.received_profile_info.get_user_photos(self.found_user_id))
            #: Загружаю данные пользователя в БД
            add_bot_user_to_db(data)
            # print(get_user_params(self.user_id, session))

            # Делаю поиск подходящих пользователей для мэтчей.
            match = self.received_profile_info.search_users(self.user_id)
            # print(self.received_profile_info._add_user_photos_and_url(match))
            #: (для отладки) Вывожу полученные в ходе поиска данные
            # пользователей
            # print(match)
            #: Загружаю данные найденных подходящих пользователей в БД
            add_match_user_to_db(match, self.user_id)
        elif request in COMMANDS["hello"]:
            self.send_message(
                self.user_id,
                MESSAGES["hello"]
            )
            self.send_match_info(self.user_id)
        elif request in COMMANDS["goodbye"]:
            self.send_message(self.user_id, MESSAGES["goodbye"])
        elif request in COMMANDS["show"]:
            # Обработка введенной команды пользователем "показать, show".
            # При вводе этой команды бот высылает информацию о мэтче по одной
            # и увеличивает счетчик match_info_count на единицу.
            # Счетчик match_info_count нужен для того, чтобы бот высылал
            # один новый мэтч с каждой итерацией.
            self.send_match_info(
                self.user_id,
                count=self.match_info_count,
                btns=KEYBOARDS["card"]["btns"]
            )
            self.match_info_count += 1
        elif request in COMMANDS["next"]:
            # Обработка введенной команды пользователем "следующий, next".
            # При вводе этой команды бот высылает информацию о мэтче по одной
            # и увеличивает счетчик match_info_count на единицу.
            # А также увеличивает счетчик next_command_count на единицу.
            self.send_match_info(
                self.user_id,
                count=self.match_info_count,
                btns=KEYBOARDS["card"]["btns"]
            )
            self.match_info_count += 1

            print("ПАГИНАТОР ПОИСКА")  # Для отладки
            self.next_command_count += 1  # Увеличиваем счетчик команды "next"
            print("Счетчик команды:", self.next_command_count)  # Для отладки

            if self.next_command_count == 2:
                # Если счетчик команды "next" равен 2,
                # то добавляем новый мэтч в базу данных
                match = self.paginator.next(self.user_id)
                add_match_user_to_db(match, self.user_id)

            if self.next_command_count == 3:
                # Если счетчик команды "next" равен 3,
                # то обнуляем счетчик "next_command_count" команды "next"
                # и начинаем отсчет счетчика команды "next" с 0
                self.next_command_count = 0
        else:
            self.send_message(
                self.user_id,
                MESSAGES["unknown_command"]
            )
