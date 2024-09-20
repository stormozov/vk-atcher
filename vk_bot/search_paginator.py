class Paginator:
    def __init__(self, user_info_retriever) -> None:
        self.user_info_retriever = user_info_retriever
        self.offset = 0

    def next(self, user_id: int) -> list[dict]:
        self.offset += 5
        return self.user_info_retriever.search_users(
            user_id=user_id,
            offset=self.offset
        )
