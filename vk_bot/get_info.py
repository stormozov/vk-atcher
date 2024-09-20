import os
import time
import random

import requests
from dotenv import load_dotenv
from database.base_funcs import get_user_params, Session

load_dotenv()


class UserInfoRetriever:
    def __init__(self, db_session: Session) -> None:
        self.URL = "https://api.vk.com/method/"
        self.TOKEN = os.getenv("VK_TOKEN")
        self.vk_api_version = 5.199
        self.session = db_session

    def get_profile_info(self, user_id: int) -> dict[str, str | int] | None:
        try:
            response = requests.get(
                f"{self.URL}users.get",
                {
                    "access_token": self.TOKEN,
                    "v": self.vk_api_version,
                    "user_ids": user_id,
                    "fields": "city, bdate, sex, relation, has_photo"
                }
            )
            return response.json()["response"]
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    def get_user_url(user_id: int) -> str:
        return f"https://vk.com/id{user_id}"

    def get_user_photos(self, user_id: int) -> list[dict] | None:
        try:
            response = requests.get(
                f"{self.URL}photos.get",
                {
                    "access_token": self.TOKEN,
                    "v": self.vk_api_version,
                    "owner_id": user_id,
                    "album_id": "profile",
                    "extended": 1,
                    "photo_sizes": 0
                }
            )
            data = response.json()

            if 'response' in data:
                photos = data['response']['items']
                return self._get_best_photos(photos)
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    def _get_best_photos(photos: list[dict], count: int = 3) \
            -> list[str] | None:
        if not photos:
            return None

        sorted_photos: list[dict[str, int]] = sorted(
            photos,
            key=lambda x: x['likes']['count'],
            reverse=True
        )

        return [
            photo["sizes"][-1]["url"]
            for photo in sorted_photos[:count]
        ]

    def search_users(
            self,
            user_id: int,
            count: int = 5,
            age_from: int = 18,
            age_to: int = 50,
            status: int = 6,
            has_photo: int = 1
    ) -> list[dict]:
        city_id, sex = self._get_user_city_id_and_sex(user_id)

        return self._process_users_with_photos_and_url(
            count,
            age_from,
            age_to,
            city_id,
            sex,
            status,
            has_photo
        )

    def _get_user_city_id_and_sex(self, user_id: int) -> tuple[int, int]:
        params_from_db = get_user_params(user_id, self.session)

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
            has_photo: int
    ) -> list[dict]:
        try:
            users = self._fetch_users_from_search(
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
            count: int,
            age_from: int,
            age_to: int,
            city_id: int,
            sex: int,
            status: int,
            has_photo: int
    ) -> list[dict[str, int | str]]:
        params = {
            "access_token": self.TOKEN,
            "v": self.vk_api_version,
            "count": count,
            "age_from": age_from,
            "age_to": age_to,
            "city_id": city_id,
            "sex": 2 if sex == 1 else 1,
            "status": status,
            "has_photo": has_photo,
            "fields": "city, bdate"
        }
        response = requests.get(f"{self.URL}users.search", params)

        return response.json()["response"]["items"]

    def _add_user_photos_and_url(self, users: list[dict]) -> list[dict]:
        for item in users:
            found_user_id: int = item.get("id")
            user_photos: list[dict] = self.get_user_photos(found_user_id)

            item["url"] = self.get_user_url(item.get("id"))

            if user_photos:
                for i in range(3):
                    item[f"photo_url{i + 1}"] = (
                        user_photos[i]
                        if i < len(user_photos)
                        else None
                    )
        return users
