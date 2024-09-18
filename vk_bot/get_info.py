import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()


class UserInfoRetriever:
    def __init__(self) -> None:
        self.URL = "https://api.vk.com/method/"
        self.TOKEN = os.getenv("VK_TOKEN")
        self.vk_api_version = 5.199

    def get_profile_info(self) -> dict[str, str | int] | None:
        try:
            response = requests.get(
                f"{self.URL}account.getProfileInfo",
                {
                    "access_token": self.TOKEN,
                    "v": self.vk_api_version
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
            else:
                time.sleep(10)
                self.get_user_photos(user_id)
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
            count: int = 12,
            age_from: int = 18,
            age_to: int = 50,
            city_id: int = 1,
            sex: int = 1,
            status: int = 6,
            has_photo: int = 1
    ) -> list[dict] | None:
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

            return response.json()["response"]["items"]
        except requests.exceptions.RequestException:
            return None

    def save_received_users(self):
        pass


if __name__ == "__main__":
    user_info_retriever = UserInfoRetriever()

    profile_info = user_info_retriever.get_profile_info()

    if profile_info:
        print("Profile Information:")
        print(profile_info)
    else:
        print("Failed to retrieve profile information.")