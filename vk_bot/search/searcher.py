import math
import time

import requests

from database.db_funcs import UserDBManager
from database.db_funcs.target_searcher import get_target_users
from vk_bot import UserInfoRetriever



class UserSearcher:
    def __init__(self, token: str, vk_api_version: float):
        self.token = token
        self.vk_api_version = vk_api_version
        self.URL = "https://api.vk.com/method/"
        self.user_db = UserDBManager()
        self.user_info = UserInfoRetriever(self.token, self.vk_api_version)

    def search_users(
        self,
        user_id: int,
        count: int = 100,
        age_from: int = 18, 
        age_to: int = 50, 
        status: int = 6, 
        has_photo: int = 1, 
        offset: int = 0
    ) -> list[dict]:
        city_id, sex = self._get_user_city_id_and_sex(user_id)
        return self._process_users_with_photos_and_url(
            count, 
            age_from, 
            age_to, 
            city_id, 
            sex, 
            status, 
            has_photo, 
            offset
        )

    def _get_user_city_id_and_sex(self, user_id: int) -> tuple[int, int]:
        params_from_db: dict = self.user_db.get_user_params(user_id)
        
        if params_from_db:
            city_id = params_from_db.get("city_id", 1)
            sex = params_from_db.get("sex", 1)
        else:
            city_id, sex = 1, 1
        
        return city_id, sex

    def _process_users_with_photos_and_url(
        self,
        count: int,
        age_from: int, 
        age_to: int, 
        city_id: int, 
        sex: int, 
        status: int, 
        has_photo: int, 
        offset: int
    ) -> list[dict]:
        try:
            users = self._fetch_users_from_search(
                count, 
                age_from, 
                age_to, 
                city_id, 
                sex, 
                status, 
                has_photo, 
                offset
            )
            return self._add_user_photos_and_url(users)
        except requests.exceptions.RequestException:
            return []

    def _fetch_users_from_search(
        self,
        count: int, 
        age_from: int, 
        age_to: int, 
        city_id: int, 
        sex: int, 
        status: int, 
        has_photo: int, 
        offset: int
    ) -> list[dict[str, int | str]]:
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
            "fields": "city, bdate, last_seen",
            "offset": offset
        }
        response = requests.get(f"{self.URL}users.search", params)
        active_users = self._pass_inactive_users(
            response.json()["response"]["items"]
        )
        target_users = get_target_users(list(active_users.values()),self.user_id) #### ВОТ ЗДЕСЬ 2ОЙ АРГУМЕНТ
        
        return list(target_users.values())

    def _add_user_photos_and_url(self, users: list[dict]) -> list[dict]:
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
        active_users = {}
        
        for user in data:
            last_visit_time = user.get('last_seen', {}).get('time', 0)
            time_difference = self._get_time_difference(last_visit_time)

            if time_difference < 10:
                active_users[user['id']] = user

        return active_users

    @staticmethod
    def _get_time_difference(last_visit_time: int) -> int:
        current_time = int(time.time())
        return math.ceil((current_time - last_visit_time) / (60 * 60 * 24))





