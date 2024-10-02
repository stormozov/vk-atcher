"""Модуль с классом для работы с ботом.

Этот модуль является основным компонентом бота и содержит ключевые функции.
В него передаются токены для доступа к VK API, а также импортируются другие
модули, необходимые для работы таких функций, как поиск пользователей,
черный список, список избранных и база данных."""
import re

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from database.db_funcs import (
    BlackListDBManager, FavoritesDBManager, UserDBManager
)
from settings import COMMANDS, KEYBOARDS, MESSAGES
from vk_bot import UserInfoRetriever
from vk_bot.keyboard import VKKeyboard
from vk_bot.searcher import UserSearcher

VK_URL_PATTERN = r"https://vk\.com/id(\d+)"


class VKBot:
    """Класс для работы с ботом."""
    def __init__(self, group_token: str, vk_token: str, db_session) -> None:
        """Инициализация бота.

        Инициализация всех необходимых зависимых модулей.

        Args:
            group_token (str): Токен для доступа к группе Vk.
            vk_token (str): Токен для доступа к VK API.
            db_session: Сессия базы данных.
        """
        self.user_id = None
        self.group_token = group_token
        self.vk_token = vk_token
        self.vk_api_version = 5.199
        self.session = db_session
        self.vk = vk_api.VkApi(token=self.group_token)
        self.longpoll = VkLongPoll(self.vk)
        self.user_db = UserDBManager()
        self.favorites_db = FavoritesDBManager()
        self.black_list_db = BlackListDBManager()
        self.received_profile_info = UserInfoRetriever(
            self.vk_token, self.vk_api_version
        )
        self.keyboard = VKKeyboard()
        # Инициализация поискового объекта
        self.searcher = UserSearcher(self.vk_token, self.vk_api_version)
        # Инициализация счетчика актуального мэтча
        self.match_info_count = 0
        # Для хранения полученного актуального списка мэтчей.
        # Нужен для работы со списком избранных и черным списком.
        self.current_match_list = None
        # Для хранения состояний выбранного действия в меню.
        # Ключ - id пользователя, значение - состояние в меню
        self.USER_STATE = {}

    def send_message(
            self,
            user_id: int,
            msg: str,
            btns: dict[str, list[tuple[str, str]] | bool] | None = None,
            attachment: str = None,
    ) -> None:
        """Метод для отправки сообщения пользователю.

        Поддерживает отправку с кнопками и вложениями.

        Args:
            user_id (int): ID пользователя.
            msg (str): Текст сообщения.
            btns (dict[str, list[tuple[str, str]] | bool] | None, optional):
                Кнопки необходимые для отображения с сообщением.
                По умолчанию None.
            attachment (str, optional): Вложения (фото). По умолчанию None.
        """
        keyboard_json: str | None = self.keyboard.create_markup(btns)

        self.vk.method(
            "messages.send",
            {
                "user_id": user_id,
                "message": msg,
                "keyboard": keyboard_json,
                "attachment": attachment,
                "random_id": 0
            }
        )

    def send_match_info(
            self,
            vk_user_id: int,
            count: int = 0,
            btns: dict[str, list[tuple[str, str]] | bool] | None = None,
            attachment: str = None
    ) -> list:
        """Метод для отправки актуального списка мэтчей пользователю.

        Args:
            vk_user_id (int): ID пользователя.
            count (int, optional): Счетчик актуального списка мэтчей.
                По умолчанию 0.
            btns (dict[str, list[tuple[str, str]] | bool] | None, optional):
                Кнопки необходимые для отображения с сообщением.
                По умолчанию None.
            attachment (str, optional): Вложения (фото). По умолчанию None.

        Returns:
            list: Актуальный список мэтчей.
        """
        match_info = self.user_db.match_data_layout(vk_user_id)

        if 0 <= count < len(match_info):
            user_name_lastname = match_info[count][0]
            user_profile_url = match_info[count][1]
            user_photos = match_info[count][3]

            user_info_text = f'{user_name_lastname}\n{user_profile_url}'

            if user_photos:
                attachment = ','.join(user_photos)

            self.send_message(
                vk_user_id,
                user_info_text,
                btns,
                attachment
            )
        elif count == len(match_info):
            self.send_message(vk_user_id, MESSAGES["no_more_matches"])

        return match_info

    def start(self) -> None:
        """Метод для запуска бота и прослушивания событий."""
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.strip().lower()
                self.user_id = event.user_id
                self._handle_user_request(request)

    def _handle_user_request(self, request: str) -> None:
        """Метод для обработки запроса пользователя.

        Пользователь отправляет сообщение боту. Это сообщение обрабатывается
        по указанным командам и вызывает соответствующие методы.
        При несуществующей команде бот отправляет сообщение об ошибке.

        Args:
            request (str): Запрос пользователя.
        """
        if request in COMMANDS["start"]:
            self._handle_start_command()
        elif request in COMMANDS["help"]:
            self._handle_help_command()
        elif request in COMMANDS["hello"]:
            self._handle_hello_command()
        elif request in COMMANDS["goodbye"]:
            self._handle_goodbye_command()
        elif request in COMMANDS["next"] or request in COMMANDS["show"]:
            self._handle_next_command()
        elif request in COMMANDS["add_to_favorites"]:
            self._handle_add_to_favorites_command()
        elif request in COMMANDS["show_favorites"]:
            self._handle_show_favorites_command()
        elif request in COMMANDS["add_to_black_list"]:
            self._handle_add_to_black_list_command()
        elif request in COMMANDS["show_black_list"]:
            self._handle_show_black_list_command()
        elif request in COMMANDS["del_from_black_list"]:
            self._handle_delete_from_black_list_command()
        elif request in COMMANDS["del_from_favorites"]:
            self._handle_delete_from_favorites_command()
        elif re.match(VK_URL_PATTERN, request):
            self._handle_url_request(request)
        else:
            self._handle_unknown_command()

    def _handle_start_command(self) -> None:
        """Метод для обработки команды start."""
        self.send_message(
            self.user_id,
            MESSAGES["start"],
            KEYBOARDS["start"]
        )
        #: Получаю информацию о пользователе,
        #: который взаимодействует с ботом
        data = self.received_profile_info.get_profile_info(self.user_id)
        #: Загружаю данные пользователя в БД
        self.user_db.add_bot_user_to_db(data)
        # Делаю поиск подходящих пользователей для мэтчей.
        match = self.searcher.search_users(self.user_id)
        #: Загружаю данные найденных подходящих пользователей в БД
        self.user_db.add_match_user_to_db(match, self.user_id)

    def _handle_help_command(self) -> None:
        """Метод для обработки команды help."""
        self.send_message(self.user_id, MESSAGES["help_1"])
        self.send_message(self.user_id, MESSAGES["help_2"])
        self.send_message(self.user_id, MESSAGES["help_3"])
        self.send_message(self.user_id, MESSAGES["help_4"], KEYBOARDS["help"])

    def _handle_hello_command(self) -> None:
        """Метод для обработки команды hello."""
        self.send_message(
            self.user_id,
            MESSAGES["hello"]
        )

    def _handle_goodbye_command(self) -> None:
        """Метод для обработки команды goodbye."""
        self.send_message(self.user_id, MESSAGES["goodbye"])

    def _handle_next_command(self) -> None:
        """Метод для обработки команды next."""
        self.current_match_list = self.send_match_info(
            self.user_id,
            self.match_info_count,
            KEYBOARDS["card"]
        )
        self.match_info_count += 1  # Увеличиваем счетчик подходящих юзеров

    def _handle_add_to_favorites_command(self) -> None:
        """Метод для обработки команды add_to_favorites."""
        self.favorites_db.add_match_to_favorites(
            self.user_id,
            self.current_match_list,
            self.match_info_count - 1
        )
        self.send_message(
            self.user_id,
            MESSAGES["add_to_favorites"],
            KEYBOARDS["add_to_favorites"]
        )

    def _handle_show_favorites_command(self) -> None:
        """Метод для обработки команды show_favorites."""
        self.send_message(
            self.user_id,
            self.favorites_db.show_favorites(self.user_id),
            KEYBOARDS["del_from_favorites"]
        )

    def _handle_add_to_black_list_command(self) -> None:
        """Метод для обработки команды add_to_black_list."""
        self.black_list_db.add_match_to_black_list(
            self.user_id,
            self.current_match_list,
            self.match_info_count - 1
        )
        self.send_message(
            self.user_id,
            MESSAGES["add_to_black_list"],
            KEYBOARDS["add_to_black_list"]
        )

    def _handle_show_black_list_command(self) -> None:
        """Метод для обработки команды show_black_list."""
        self.send_message(
            self.user_id,
            self.black_list_db.show_black_list(self.user_id),
            KEYBOARDS["del_from_black_list"]
        )

    def _handle_delete_from_black_list_command(self) -> None:
        """Метод для обработки команды delete_from_black_list."""
        self.send_message(
            self.user_id,
            MESSAGES["del_from_black_list_instruction"],
            KEYBOARDS["next"]
        )
        self.USER_STATE[self.user_id] = 'delete_blacklist'

    def _handle_delete_from_favorites_command(self) -> None:
        """Метод для обработки команды delete_from_favorites."""
        self.send_message(
            self.user_id,
            MESSAGES["del_from_favorites_instruction"],
            KEYBOARDS["next"]
        )
        self.USER_STATE[self.user_id] = 'delete_favorites'

    def _handle_url_request(self, request: str) -> None:
        """Метод для обработки URL-запроса."""
        match = re.match(VK_URL_PATTERN, request)
        del_user_id = int(match.group(1))

        if self.USER_STATE.get(self.user_id) == 'delete_blacklist':
            self.black_list_db.remove_from_black_list(
                self.user_id, del_user_id
            )
            self.send_message(
                self.user_id,
                f"Пользователь с ID {del_user_id} "
                f"был удален из черного списка.",
                KEYBOARDS["next"]
            )
        if self.USER_STATE.get(self.user_id) == 'delete_favorites':
            self.favorites_db.remove_from_favorites(
                self.user_id, del_user_id
            )
            self.send_message(
                self.user_id,
                f"Пользователь с ID {del_user_id} "
                f"был удален из избранного.",
                KEYBOARDS["next"]
            )
            self.USER_STATE[self.user_id] = None

    def _handle_unknown_command(self) -> None:
        """Метод для обработки неизвестной команды."""
        self.send_message(self.user_id, MESSAGES["unknown_command"])
