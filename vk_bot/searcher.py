"""Модуль с классом для поиска пользователей.

Для поиска пользователей используется API метод users.search.
"""
import math
import time

import requests

from database.db_funcs import UserDBManager, TargetUserSearcher
from vk_bot import UserInfoRetriever


class UserSearcher:
    """Класс для поиска пользователей."""
    def __init__(self, token: str, vk_api_version: float) -> None:
        """Инициализация класса для поиска пользователей.

        Args:
            token (str): Токен для доступа к API.
            vk_api_version (float): Версия API.
        """
        self.token = token
        self.vk_api_version = vk_api_version
        self.URL = "https://api.vk.com/method/"
        self.user_db = UserDBManager()
        self.user_info = UserInfoRetriever(self.token, self.vk_api_version)
        self.target_searcher = TargetUserSearcher()

    def search_users(
        self,
        user_id: int,
        count: int = 1000,
        age_from: int = 18, 
        age_to: int = 50, 
        status: int = 6, 
        has_photo: int = 1
    ) -> list[dict]:
        """Метод для поиска пользователей по заданным параметрам.

        Args:
            user_id (int): ID пользователя.
            count (int): Количество пользователей для возвращения.
                По умолчанию 1000.
            age_from (int): Нижняя граница возраста. По умолчанию 18.
            age_to (int): Верхняя граница возраста. По умолчанию 50.
            status (int): Статус пользователя. По умолчанию 6.
            has_photo (int): Наличие фотографии. По умолчанию 1.

        Returns:
            list[dict]: Список словарей с данными о найденных пользователях.
        """
        city_id, sex = self._get_user_city_id_and_sex(user_id)
        return self._process_users_with_photos_and_url(
            user_id,
            count, 
            age_from, 
            age_to, 
            city_id, 
            sex, 
            status, 
            has_photo
        )

    def _get_user_city_id_and_sex(self, user_id: int) -> tuple[int, int]:
        """Метод для получения ID города и пола пользователя, использующего бота

        Args:
            user_id (int): ID пользователя, который использует бота.

        Returns:
            tuple[int, int]: Кортеж из ID города и пола пользователя.
        """
        params_from_db: dict = self.user_db.get_user_params(user_id)
        
        if params_from_db:
            city_id = params_from_db.get("city_id", 1)
            sex = params_from_db.get("sex", 1)
        else:
            city_id, sex = 1, 1
        
        return city_id, sex

    def _process_users_with_photos_and_url(
        self,
        user_id: int,
        count: int,
        age_from: int, 
        age_to: int, 
        city_id: int, 
        sex: int, 
        status: int, 
        has_photo: int
    ) -> list[dict]:
        """Метод для обработки найденных пользователей с фотографиями.

        Args:
            user_id (int): ID пользователя, который использует бота.
            count (int): Количество пользователей для возвращения.
            age_from (int): Нижняя граница возраста. По умолчанию 18.
            age_to (int): Верхняя граница возраста. По умолчанию 50.
            city_id (int): ID города. По умолчанию 1.
            sex (int): Пол пользователя. По умолчанию 1.
            status (int): Статус пользователя. По умолчанию 6.
            has_photo (int): Наличие фотографии. По умолчанию 1.

        Returns:
            list[dict]: Список словарей с данными о найденных пользователях.
        """
        try:
            users = self._fetch_users_from_search(
                user_id,
                count, 
                age_from, 
                age_to, 
                city_id, 
                sex, 
                status, 
                has_photo
            )
            return self._add_user_photos_and_url(users)
        except requests.exceptions.RequestException:
            return []

    def _fetch_users_from_search(
        self,
        user_id: int,
        count: int, 
        age_from: int, 
        age_to: int, 
        city_id: int, 
        sex: int, 
        status: int, 
        has_photo: int
    ) -> list[dict[str, int | str]]:
        """Метод для получения списка пользователей с фотографиями.

        В данном методе отправляется GET-запрос с параметрами, а также
        производится фильтрация по активности найденного пользователя и
        включен ли найденный пользователь в список избранных или черный
        список пользователя, взаимодействующего с ботом.

        Args:
            user_id (int): ID пользователя, который использует бота.
            count (int): Количество пользователей для возвращения.
            age_from (int): Нижняя граница возраста. По умолчанию 18.
            age_to (int): Верхняя граница возраста. По умолчанию 50.
            city_id (int): ID города. По умолчанию 1.
            sex (int): Пол пользователя. По умолчанию 1.
            status (int): Статус пользователя. По умолчанию 6.
            has_photo (int): Наличие фотографии. По умолчанию 1.

        Returns:
            list[dict[str, int | str]]: Список словарей с данными
                о найденных пользователях.
        """
        params = {
            "access_token": self.token,
            "v": self.vk_api_version,
            "count": count,
            "age_from": age_from,
            "age_to": age_to,
            "city_id": city_id,
            "sex": 2 if sex == 1 else 1,
            "status": status,
            "has_photo": has_photo,
            "fields": "city, bdate, last_seen"
        }
        response = requests.get(f"{self.URL}users.search", params)
        active_users = self._pass_inactive_users(
            response.json()["response"]["items"]
        )
        target_users = self.target_searcher.get_target_users(
            list(active_users.values()), user_id
        )
        
        return list(target_users.values())

    def _add_user_photos_and_url(self, users: list[dict]) -> list[dict]:
        """Метод для добавления фотографий пользователей в словари.

        Args:
            users (list[dict]): Список словарей с данными о пользователях,
                для которых нужно добавить фотографии.

        Returns:
            list[dict]: Список словарей с данными о пользователях с фотографиями
        """
        for item in users:
            found_user_id: int = item.get("id")
            user_photos = self.user_info.get_user_photos(found_user_id)
            item["url"] = self.user_info.get_user_url(item.get("id"))

            if user_photos:
                for i in range(3):
                    item[f"photo_id{i + 1}"] = (
                        user_photos[i]
                        if i < len(user_photos)
                        else None
                    )
        return users

    def _pass_inactive_users(self, data: list[dict]) -> dict:
        """Метод для фильтрации активных пользователей.

        В данном методе производится фильтрация активных пользователей
        по времени последнего посещения. Если время последнего посещения
        меньше 10 дней, то пользователь является активным и добавляется
        в словарь. В противном случае он не пропускается.

        Args:
            data (list[dict]): Список словарей с данными о пользователях.

        Returns:
            dict: Словарь с активными пользователями.
        """
        active_users = {}
        
        for user in data:
            last_visit_time = user.get('last_seen', {}).get('time', 0)
            time_difference = self._get_time_difference(last_visit_time)

            if time_difference < 10:
                active_users[user['id']] = user

        return active_users

    @staticmethod
    def _get_time_difference(last_visit_time: int) -> int:
        """Метод для получения разницы между текущим временем и временем
        последнего посещения пользователя.

        Args:
            last_visit_time (int): Время последнего посещения пользователя.

        Returns:
            int: Разница между текущим временем и временем
                последнего посещения пользователя в днях.
        """
        current_time = int(time.time())
        return math.ceil((current_time - last_visit_time) / (60 * 60 * 24))
