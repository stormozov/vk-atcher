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
        params_from_db = get_user_params(user_id, self.session)

        if params_from_db:
            city_id = params_from_db.get("city_id", 1)
            sex = params_from_db.get("sex", 1)
        else:
            city_id, sex = 1, 1

        try:
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
            users: list[dict] = response.json()["response"]["items"]

            for item in users:
                found_user_id: int = item.get("id")
                user_photos: list = self.get_user_photos(found_user_id)

                item["url"] = self.get_user_url(item.get("id"))

                if user_photos:
                    item["photo_url1"] = (
                        user_photos[0]
                        if user_photos
                        else None
                    )
                    item["photo_url2"] = (
                        user_photos[1]
                        if len(user_photos) > 1
                        else None
                    )
                    item["photo_url3"] = (
                        user_photos[2]
                        if len(user_photos) > 2
                        else None
                    )

            return users
        except requests.exceptions.RequestException:
            return []

    def save_received_users(self):
        pass
