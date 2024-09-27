from sqlalchemy.exc import SQLAlchemyError
from database.base import BlackList, Favorites, Session
from database.db_funcs.user import UserDBManager


class TargetUserSearcher:
    def __init__(self):
        self.user_db = UserDBManager()
        self.session = Session()

    def get_target_users(self, candidates: list[dict], user_vk_id: int) -> dict:
        target_users = {}

        for candidate in candidates:
            target_vk_id = candidate.get('id', {})
            candidate_id = self.user_db.get_user_id_by_vk_id(user_vk_id)
            rejected_ids = self.get_blocked_and_favorites_by_vk_id(candidate_id)

            if (target_vk_id not in rejected_ids['blocked']
                    and target_vk_id not in rejected_ids['favorites']):
                target_users[candidate['id']] = candidate

        return target_users

    def get_blocked_and_favorites_by_vk_id(self, candidate_id: int) \
            -> dict[str, list[int]]:
        result = {"blocked": [], "favorites": []}

        user_id = self.user_db.get_user_id_by_vk_id(candidate_id)

        if not user_id:
            return result

        try:
            blocked_ids = self._get_ids_by_table_type("blocked", user_id)
            favorite_ids = self._get_ids_by_table_type("favorites", user_id)

            result["blocked"] = [item[0] for item in blocked_ids]
            result["favorites"] = [item[0] for item in favorite_ids]
        except SQLAlchemyError as e:
            print(f"Произошла ошибка при получении данных: {e}")

        return result

    def _get_ids_by_table_type(self, table_type: str, user_id: int):
        query = self.session.query(
            BlackList.blocked_vk_id
            if table_type == "blocked"
            else Favorites.favorite_vk_id
        )
        return query.filter_by(user_id=user_id).all()
