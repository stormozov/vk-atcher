import math

import time

import requests
from database.db_funcs import UserDBManager


class UserInfoRetriever:
    def __init__(self, token: str, vk_api_version: float) -> None:
        self.URL = "https://api.vk.com/method/"
        self.TOKEN = token
        self.vk_api_version = vk_api_version
        self.user_db = UserDBManager()

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
