from database.base import Favorites, Session
from database.db_funcs.user import UserDBManager
from settings import MESSAGES


class FavoritesDBManager:

    def __init__(self) -> None:
        self.session = Session()
        self.user_db = UserDBManager()

    def add_match_to_favorites(
            self, user_id: int, favorites: list, selected_match: int
    ) -> None:
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
        result = "\n".join(
            [
                f"{i}. {favorite.first_name} {favorite.last_name} "
                f"— {favorite.profile_link}"
                for i, favorite in enumerate(favorites, start=1)
            ]
        )
        return f"{MESSAGES['show_favorites']}\n\n{result}"

    def _get_existing_favorite_entry(
            self,
            user_id: int,
            favorite_vk_id: int = None,
            return_all: bool = False
    ) -> Favorites | list[Favorites] | None:
        query = self.session.query(Favorites).filter_by(user_id=user_id)

        if favorite_vk_id is not None:
            query = query.filter_by(favorite_vk_id=favorite_vk_id)

        return query.all() if return_all else query.first()
