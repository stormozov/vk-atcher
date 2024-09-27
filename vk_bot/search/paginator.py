from .searcher import UserSearcher


class Paginator:
    def __init__(self, token: str, vk_api_version: float) -> None:
        self.searcher = UserSearcher(token, vk_api_version)
        self.offset = 0

    def next(self, user_id: int) -> list[dict]:
        self.offset += 10
        return self.searcher.search_users(
            user_id=user_id,
            offset=self.offset
        )
