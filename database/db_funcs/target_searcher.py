"""Модуль для поиска пользователей в избранных и черном списке пользователя
в базе данных.

Модуль содержит в себе класс и методы для поиска пользователей в избранных и
черном списке пользователя в базе данных.
"""
from sqlalchemy.exc import SQLAlchemyError
from database.base import BlackList, Favorites, Session
from database.db_funcs.user import UserDBManager


class TargetUserSearcher:
    """Класс для поиска пользователей в избранных и черном списке пользователя
    в базе данных."""
    def __init__(self):
        """Инициализирует объект для поиска целевого пользователя."""
        self.user_db = UserDBManager()
        self.session = Session()

    def get_target_users(self, candidates: list[dict], target_user_vk_id: int) \
            -> dict[int, dict[str, int | str | dict[str, int | str]] | bool]:
        """Получает информацию о целевом пользователе.

        Args:
            candidates (list[dict]): Список кандидатов для поиска.
            target_user_vk_id (int): ID целевого пользователя.

        Returns:
            dict[int, dict[str, int | str | dict[str, int | str]] | bool]:
                Словарь с ID пользователя и его информацией. Если
                пользователь не найден, возвращает False.
        """
        filtered_users = {}

        for candidate in candidates:
            target_vk_id = candidate.get('id', {})
            user_id = self.user_db.get_user_id_by_vk_id(target_user_vk_id)
            rejected_ids = self.get_blocked_and_favorites_by_vk_id(user_id)

            if (target_vk_id not in rejected_ids['blocked']
                    and target_vk_id not in rejected_ids['favorites']):
                # Если пользователь не в черном списке и не в избранных,
                # то добавляем его в словарь
                filtered_users[candidate['id']] = candidate

        return filtered_users

    def get_blocked_and_favorites_by_vk_id(self, user_id: int) \
            -> dict[str, list[int]]:
        """Получает ID заблокированных и избранных пользователей.

        Args:
            user_id (int): ID пользователя.

        Returns:
            dict[str, list[int]]: Словарь с ID заблокированных и
                избранных пользователей.
        """
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
        """Получает ID заблокированных и избранных пользователей из базы данных.

        Args:
            table_type (str): Тип таблицы: blocked или favorites.
            user_id (int): ID пользователя.

        Returns:
            list[int]: Список ID заблокированных и избранных пользователей.
        """
        query = self.session.query(
            BlackList.blocked_vk_id
            if table_type == "blocked"
            else Favorites.favorite_vk_id
        )
        return [item[0] for item in query.filter_by(user_id=user_id).all()]
