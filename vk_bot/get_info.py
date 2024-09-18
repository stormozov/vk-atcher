import os

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

    def get_user_photos(self):
        pass

    def search_users(self):
        pass


if __name__ == "__main__":
    user_info_retriever = UserInfoRetriever()

    profile_info = user_info_retriever.get_profile_info()

    if profile_info:
        print("Profile Information:")
        print(profile_info)
    else:
        print("Failed to retrieve profile information.")