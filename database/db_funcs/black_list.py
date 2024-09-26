from database.base import BlackList, Session
from database.db_funcs.user import UserDBManager
from settings import MESSAGES


class BlackListDBManager:
    def __init__(self) -> None:
        self.session = Session()
        self.user_db = UserDBManager()

    def add_match_to_black_list(
            self, user_id: int, black_list: list, selected_match: int
    ) -> None:
        vk_user_id = self.user_db.get_user_id_by_vk_id(user_id)

        if not vk_user_id:
            return

        blocked_vk_id = black_list[selected_match][2]
        first_name, last_name = black_list[selected_match][0].split()

        existing_entry = self._get_existing_black_list_entry(
            vk_user_id, blocked_vk_id
            )

        if existing_entry:
            return

        new_blocked_entry = BlackList(
            user_id=vk_user_id,
            blocked_vk_id=blocked_vk_id,
            first_name=first_name,
            last_name=last_name,
            profile_link=black_list[selected_match][1]
        )

        self.session.add(new_blocked_entry)
        self.session.commit()

    def remove_from_black_list(self, user_id: int, del_user_id: int) -> None:
        vk_user_id = self.user_db.get_user_id_by_vk_id(user_id)

        if not vk_user_id:
            return

        black_list = self._get_existing_black_list_entry(
            vk_user_id, return_all=True
        )

        if not black_list:
            return

        black_listed_entry = next((
            entry
            for entry in black_list
            if entry.blocked_vk_id == del_user_id
        ), None)

        if not black_listed_entry:
            return

        black_listed_entry = self.session.merge(black_listed_entry)
        self.session.delete(black_listed_entry)
        self.session.commit()

    def show_black_list(self, user_id: int) -> str | None:
        vk_user_id = self.user_db.get_user_id_by_vk_id(user_id)

        if not vk_user_id:
            return

        blacklist = self._get_existing_black_list_entry(
            vk_user_id, return_all=True
            )

        if not blacklist:
            return MESSAGES["black_list_is_empty"]

        return self._format_black_list_string(blacklist)

    @staticmethod
    def _format_black_list_string(black_list: list) -> str:
        result = "\n".join(
            [
                f"{i}. {black_listed.first_name} {black_listed.last_name} "
                f"— {black_listed.profile_link}"
                for i, black_listed in enumerate(black_list, start=1)
            ]
        )
        return f"{MESSAGES['show_black_list']}\n\n{result}"

    def _get_existing_black_list_entry(
            self,
            user_id: int,
            blocked_vk_id: int = None,
            return_all: bool = False
    ) -> BlackList | list[BlackList] | None:
        query = self.session.query(BlackList).filter_by(user_id=user_id)

        if blocked_vk_id is not None:
            query = query.filter_by(blocked_vk_id=blocked_vk_id)

        return query.all() if return_all else query.first()
