import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from settings import COMMANDS, KEYBOARDS, MESSAGES
from vk_bot import UserInfoRetriever, UserVK
from database.base_funcs import (
    add_bot_user_to_db,
    add_match_to_favorites,
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
        # Для хранения полученного актуального списка мэтчей.
        # Нужен для работы со списком избранных и черным списком.
        self.current_match_list = None

    def send_message(
            self,
            user_id: int,
            msg: str,
            btns: dict[str, list[tuple[str, str]] | bool] | None = None
    ) -> None:
        keyboard_json: str | None = self.keyboard.create_markup(btns)

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
            btns: dict[str, list[tuple[str, str]] | bool] | None = None
    ) -> list:
        keyboard_json: str | None = self.keyboard.create_markup(btns)
        match_info = match_data_layout(vk_user_id)

        if 0 <= count < len(match_info):
            username = match_info[count][0]  # Имя пользователя
            profile_url = match_info[count][1]  # Ссылка на профиль
            user_photos = match_info[count][3]  # Фото пользователя

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

        return match_info

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
                KEYBOARDS["start"]
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
        elif request in COMMANDS["next"] or request in COMMANDS["show"]:
            # Обработка введенной команды пользователем "следующий, next",
            # и/или обработка введенной команды пользователем "показать, show".
            # При вводе этой команды бот высылает по одной информацию о мэтче
            # и увеличивает счетчик match_info_count на единицу.
            # А также увеличивает счетчик next_command_count на единицу.
            self.current_match_list = self.send_match_info(
                self.user_id,
                count=self.match_info_count,
                btns=KEYBOARDS["card"]
            )
            self.match_info_count += 1

            print("ПАГИНАТОР ПОИСКА")  # Для отладки
            self.next_command_count += 1  # Увеличиваем счетчик команды "next"
            print("Счетчик команды:", self.next_command_count)  # Для отладки

            if self.next_command_count == 3:
                # Если счетчик команды "next" или "show" равен 3,
                # то добавляем новые мэтчи в базу данных и сбрасываем счетчик
                # "next_command_count" на 0.
                # Т.е. если у нас есть 3 мэтча, то новые мэтчи будут добавлены
                # в базу данных при достижении пользователем 3 мэтча.
                match = self.paginator.next(self.user_id)
                add_match_user_to_db(match, self.user_id)
                self.next_command_count = 0
        elif request in COMMANDS["add_to_favorites"]:
            add_match_to_favorites(
                self.user_id,
                self.current_match_list,
                self.match_info_count - 1
            )
            self.send_message(
                self.user_id,
                MESSAGES["add_to_favorites"],
                KEYBOARDS["add_to_favorites"]
            )
        else:
            self.send_message(
                self.user_id,
                MESSAGES["unknown_command"]
            )
