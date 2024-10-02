"""Модуль для работы с избранным списком пользователя.

Модуль содержит в себе класс и методы для работы с избранным списком
пользователя и базой данных.
"""
from database.base import Favorites, Session
from database.db_funcs.user import UserDBManager
from settings import MESSAGES


class FavoritesDBManager:
    """Класс для работы с избранным списком пользователя и базой данных."""
    def __init__(self) -> None:
        """Инициализирует объект для работы с избранным списком пользователя."""
        self.session = Session()
        self.user_db = UserDBManager()

    def add_match_to_favorites(
            self, user_id: int, favorites: list, selected_match: int
    ) -> None:
        """Добавляет предложенного мэтча в избранный список пользователя.

        Args:
            user_id (int): ID пользователя VK, для которого добавляется мэтч.
            favorites (list): Список потенциальных мэтчей с их данными.
            selected_match (int): Индекс выбранного мэтча в списке.
        """
        vk_user_id = self.user_db.get_user_id_by_vk_id(user_id)

        if not vk_user_id:
            return

        favorite_vk_id = favorites[selected_match][2]
        first_name, last_name = favorites[selected_match][0].split()

        existing_entry = self._get_existing_favorite_entry(
            vk_user_id, favorite_vk_id
        )

        if existing_entry:
            return

        new_favorite_entry = Favorites(
            user_id=vk_user_id,
            favorite_vk_id=favorite_vk_id,
            first_name=first_name,
            last_name=last_name,
            profile_link=favorites[selected_match][1]
        )

        self.session.add(new_favorite_entry)
        self.session.commit()

    def remove_from_favorites(self, user_id: int, del_user_id: int) -> None:
        """Удаляет выбранного пользователя из избранных.

        Args:
            user_id (int): ID пользователя VK, для которого осуществляется
                удаление.
            del_user_id (int): ID пользователя VK, которого нужно удалить
        """
        vk_user_id = self.user_db.get_user_id_by_vk_id(user_id)

        if not vk_user_id:
            return

        favorites = self._get_existing_favorite_entry(
            vk_user_id, return_all=True
        )

        if not favorites:
            return

        blacklisted_entry = next((
            entry
            for entry in favorites
            if entry.favorite_vk_id == del_user_id
        ), None)

        if not blacklisted_entry:
            return

        blacklisted_entry = self.session.merge(blacklisted_entry)
        self.session.delete(blacklisted_entry)
        self.session.commit()

    def show_favorites(self, user_id: int) -> str | None:
        """Выводит в чат пользователя его список избранных.

        Args:
            user_id (int): ID пользователя VK, для которого нужно вывести
                список избранных.

        Returns:
            str: Строка с информацией об избранных, если список избранных
                не пуст.
            None: Если список избранных пуст.
        """
        vk_user_id = self.user_db.get_user_id_by_vk_id(user_id)

        if not vk_user_id:
            return

        favorites = self._get_existing_favorite_entry(
            vk_user_id, return_all=True
        )

        if not favorites:
            return MESSAGES["favorites_is_empty"]

        return self._format_favorites_string(favorites)

    @staticmethod
    def _format_favorites_string(favorites: list) -> str:
        """Форматирует строку с информацией об избранных.

        Args:
            favorites (list): Список избранных.

        Returns:
            str: Строка с информацией об избранных.
        """
        result = "\n".join([
            f"{i}. {favorite.first_name} {favorite.last_name} "
            f"— {favorite.profile_link}"
            for i, favorite in enumerate(favorites, start=1)
        ])
        return f"{MESSAGES['show_favorites']}\n\n{result}"

    def _get_existing_favorite_entry(
            self,
            user_id: int,
            favorite_vk_id: int = None,
            return_all: bool = False
    ) -> Favorites | list[Favorites] | None:
        """Получает запись избранных для конкретного пользователя.

        Args:
            user_id (int): ID пользователя VK, избранных которого проверяется.
            favorite_vk_id (int, optional): ID избранных пользователя VK.
                По умолчанию None.
            return_all (bool, optional): Флаг для возврата всех записей.
                По умолчанию False.

        Returns:
            Favorites: Запись избранных.
            list[Favorites]: Список записей избранных.
            None: Если ничего не найдено.
        """
        query = self.session.query(Favorites).filter_by(user_id=user_id)

        if favorite_vk_id is not None:
            query = query.filter_by(favorite_vk_id=favorite_vk_id)

        return query.all() if return_all else query.first()
