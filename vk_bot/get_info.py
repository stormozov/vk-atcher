import math
import os
import time

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
                    "fields": "city, bdate, sex, relation, has_photo, last_seen"
                }
            )
            return response.json()["response"]
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    def get_user_url(user_id: int) -> str:
        return f"https://vk.com/id{user_id}"

    def get_user_photos(self, user_id: int) -> list[str] | None:
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
                photos = data['response']
                return self._get_best_3_photos_id(photos)
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    def _find_largest_photo(dict_sizes: dict[str, int | str]) -> int:
        return (
            dict_sizes["width"]
            if dict_sizes["width"] >= dict_sizes["height"]
            else dict_sizes["height"]
        )

    def _get_best_3_photos_id(self, photos: dict) -> list[str] | None:
        if not photos or 'items' not in photos:
            return None

        photos_dict = {}

        for photo in photos['items']:
            largest = max(photo['sizes'], key=self._find_largest_photo)
            likes = photo['likes']['count']

            if isinstance(likes, int) and isinstance(largest, dict):
                photo_id = str(photo['id'])
                photos_dict[photo_id] = (largest['url'], likes)

        if not photos_dict:
            return None

        sorted_tuples = sorted(
            photos_dict.items(),
            key=lambda item: item[1][1],
            reverse=True
        )
        return [id_ for id_, _ in sorted_tuples[:3]]

    def search_users(
            self,
            user_id: int,
            count: int = 10,
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
            "access_token": self.TOKEN,
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

        active_users = self.pass_inactive_users(response.json()["response"]["items"])

        return list(active_users.values())

    def _add_user_photos_and_url(self, users: list[dict]) -> list[dict]:
        for item in users:
            found_user_id: int = item.get("id")
            user_photos: list[str] = self.get_user_photos(found_user_id)

            item["url"] = self.get_user_url(item.get("id"))

            if user_photos:
                for i in range(3):
                    item[f"photo_id{i + 1}"] = (
                        user_photos[i]
                        if i < len(user_photos)
                        else None
                    )
        return users
    @staticmethod
    def pass_inactive_users(data: list[dict]) -> dict:
        users = {}
        current_time = int(time.time())
        for user in data:
            last_visit_time = user.get('last_seen', {}).get('time', 0)
            time_difference = math.ceil((current_time - last_visit_time) / (60 * 60 * 24))
            if time_difference < 10:
                users[user['id']] = user

        return users