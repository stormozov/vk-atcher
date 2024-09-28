from sqlalchemy.exc import SQLAlchemyError
from database.base import BlackList, Favorites, Session
from database.db_funcs.user import UserDBManager


class TargetUserSearcher:
    def __init__(self):
        self.user_db = UserDBManager()
        self.session = Session()

    def get_target_users(self, candidates: list[dict], target_user_vk_id: int) \
            -> dict[int, dict[str, int | str | dict[str, int | str]] | bool]:
        filtered_users = {}

        for candidate in candidates:
            target_vk_id = candidate.get('id', {})
            user_id = self.user_db.get_user_id_by_vk_id(target_user_vk_id)
            rejected_ids = self.get_blocked_and_favorites_by_vk_id(user_id)

            if (target_vk_id not in rejected_ids['blocked']
                    and target_vk_id not in rejected_ids['favorites']):
                filtered_users[candidate['id']] = candidate

        return filtered_users

    def get_blocked_and_favorites_by_vk_id(self, user_id: int) \
            -> dict[str, list[int]]:
        if not user_id:
            return {"blocked": [], "favorites": []}

        try:
            blocked_ids = self._get_ids_by_table_type("blocked", user_id)
            favorite_ids = self._get_ids_by_table_type("favorites", user_id)

            return {"blocked": blocked_ids, "favorites": favorite_ids}
        except SQLAlchemyError as e:
            print(f"Произошла ошибка при получении данных: {e}")
            return {"blocked": [], "favorites": []}

    def _get_ids_by_table_type(self, table_type: str, user_id: int) \
            -> list[int]:
        query = self.session.query(
            BlackList.blocked_vk_id
            if table_type == "blocked"
            else Favorites.favorite_vk_id
        )
        return [item[0] for item in query.filter_by(user_id=user_id).all()]
