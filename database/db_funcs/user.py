"""Модуль для работы с пользователями.

Модуль содержит в себе класс и методы для работы с пользователями и базой данных
"""
from sqlalchemy.exc import SQLAlchemyError

from database.base import Matches, Session, Users


class UserDBManager:
    """Класс для работы с пользователями и базой данных."""
    def __init__(self) -> None:
        """Инициализирует объект для работы с пользователями."""
        self.session = Session()

    def add_bot_user_to_db(self, data_list: list[dict]) -> None:
        """Добавляет пользователя в базу данных.

        Args:
            data_list (list[dict]): Список словарей с данными пользователя.
        """
        try:
            for item in data_list:
                vk_id = item.get('id')
                first_name = item.get('first_name')
                last_name = item.get('last_name')
                gender = item.get('sex')
                city_id = item.get('city', {}).get('id')

                existing_user = self.get_user_by_vk_id(vk_id)

                if existing_user:
                    existing_user.first_name = first_name
                    existing_user.last_name = last_name
                    existing_user.gender = gender
                    existing_user.city = city_id
                else:
                    new_user = Users(
                        vk_id=vk_id,
                        first_name=first_name,
                        last_name=last_name,
                        gender=gender,
                        city=city_id
                    )
                    self.session.add(new_user)

            self.session.commit()
            print("Пользователи успешно добавлены/обновлены в базе данных.")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Ошибка при добавлении пользователей: {e}")
        finally:
            self.session.close()

    def add_match_user_to_db(self, match_data: list[dict], f_user_id: int) \
            -> None:
        """Добавляет мэтч в базу данных.

        Args:
            match_data (list[dict]): Список словарей с данными мэтча.
            f_user_id (int): ID пользователя VK, для которого добавляется мэтч.
        """
        try:
            for item in match_data:
                vk_id = item.get('id')
                first_name = item.get('first_name')
                last_name = item.get('last_name')
                profile_link = item.get('url')
                photo_id_1 = item.get('photo_id1')
                photo_id_2 = item.get('photo_id2')
                photo_id_3 = item.get('photo_id3')

                user_id = self.get_user_id_by_vk_id(f_user_id)

                existing_match = self.get_user_matches(
                    matched_vk_id=vk_id, return_all=False
                )

                if existing_match:
                    existing_match.first_name = first_name
                    existing_match.last_name = last_name
                    existing_match.profile_link = profile_link
                    existing_match.photo_id_1 = photo_id_1
                    existing_match.photo_id_2 = photo_id_2
                    existing_match.photo_id_3 = photo_id_3
                else:
                    new_match = Matches(
                        user_id=user_id,
                        matched_vk_id=vk_id,
                        first_name=first_name,
                        last_name=last_name,
                        profile_link=profile_link,
                        photo_id_1=photo_id_1,
                        photo_id_2=photo_id_2,
                        photo_id_3=photo_id_3
                    )
                    self.session.add(new_match)
            self.session.commit()
            print("Пользователи успешно добавлены/обновлены в базе данных.")
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Ошибка при добавлении пользователей: {e}")
        finally:
            self.session.close()

    def match_data_layout(self, f_user_id: int) -> list[list]:
        """Подготавливает данные о мэтчах для вывода в чат бота.

        Args:
            f_user_id (int): ID пользователя VK.

        Returns:
            list: Список списков с данными о мэтчах.
        """
        match_info: list[dict] = self.get_match_info_to_print(f_user_id)
        all_match_info_list = []

        if match_info:
            for result in match_info:
                match_info_list = []
                match_mess_info = f"{result["first_name"]} {result["last_name"]}"
                match_url_info: str = result["profile_link"]
                match_vk_id: int = result["vk_id"]

                match_info_list.append(match_mess_info)
                match_info_list.append(match_url_info)
                match_info_list.append(match_vk_id)

                photos = []
                if result.get("photo_id_1"):
                    photos.append(
                        f'photo{result["vk_id"]}_{result["photo_id_1"]}'
                    )
                if result.get("photo_id_2"):
                    photos.append(
                        f'photo{result["vk_id"]}_{result["photo_id_2"]}'
                    )
                if result.get("photo_id_3"):
                    photos.append(
                        f'photo{result["vk_id"]}_{result["photo_id_3"]}'
                    )

                match_info_list.append(photos)
                all_match_info_list.append(match_info_list)

        return all_match_info_list

    def get_match_info_to_print(self, f_user_id: int) -> list[dict] | None:
        """Получает информацию о мэтчах для вывода в чат бота.

        Args:
            f_user_id (int): ID пользователя VK.

        Returns:
            list: Список словарей с информацией о мэтчах.
            None: Если мэтчи не найдены или произошла ошибка при получении
                данных из базы данных.
        """
        user_id: int = self.get_user_id_by_vk_id(f_user_id)

        try:
            matches = self.get_user_matches(
                user_id=user_id, return_all=True
            )

            if matches:
                result_list = []
                for match in matches:
                    match_dict = {
                        "first_name": match.first_name,
                        "last_name": match.last_name,
                        "profile_link": match.profile_link,
                        "vk_id": match.matched_vk_id
                    }
                    if match.photo_id_1:
                        match_dict["photo_id_1"] = match.photo_id_1
                    if match.photo_id_2:
                        match_dict["photo_id_2"] = match.photo_id_2
                    if match.photo_id_3:
                        match_dict["photo_id_3"] = match.photo_id_3

                    result_list.append(match_dict)

                return result_list
            else:
                return None
        except SQLAlchemyError as e:
            print(
                f"Произошла ошибка при получении параметров пользователя: {e}"
            )
            return None

    def get_user_params(self, user_id: int) -> dict | None:
        """Получает параметры пользователя из базы данных.

        Args:
            user_id (int): ID пользователя VK.

        Returns:
            dict: Словарь с параметрами пользователя.
            None: Если произошла ошибка при получении данных из базы данных
                или пользователь не найден.
        """
        try:
            user = self.get_user_by_vk_id(user_id)
            return (
                {
                    "city_id": user.city,
                    "sex": user.gender
                }
                if user
                else None
            )
        except SQLAlchemyError as e:
            print(
                f"Произошла ошибка при получении параметров пользователя: {e}"
            )
            return None

    def get_user_id_by_vk_id(self, vk_id: int) -> int | None:
        """Получает ID пользователя из базы данных по его VK ID.

        Args:
            vk_id (int): ID пользователя VK.

        Returns:
            int: ID пользователя из базы данных.
            None: Если произошла ошибка при получении данных из базы данных
                или пользователь не найден.
        """
        try:
            user = self.get_user_by_vk_id(vk_id)
            return (
                user.user_id
                if user
                else (print(f"Пользователь с vk_id {vk_id} не найден.") or None)
            )
        except SQLAlchemyError as e:
            print(f"Произошла ошибка при получении user_id: {e}")
            return None

    def get_user_by_vk_id(self, user_id: int) -> Users | None:
        """Получает запись пользователя из базы данных по его VK ID.

        Args:
            user_id (int): ID пользователя VK.

        Returns:
            Users: Запись пользователя из базы данных.
            None: Если произошла ошибка при получении данных из базы данных
                или пользователь не найден.
        """
        return self.session.query(Users).filter_by(vk_id=user_id).first()

    def get_user_matches(
            self,
            user_id: int = None,
            matched_vk_id: int = None,
            return_all: bool = False
    ) -> list[Matches] | Matches | None:
        """Получает мэтчи пользователя из базы данных.

        Args:
            user_id (int): ID пользователя. По умолчанию None.
                Нельзя передавать вместе с matched_vk_id.
            matched_vk_id (int): ID пользователя, с которым совпадают мэтчи.
                По умолчанию None. Нельзя передавать вместе с user_id.
            return_all (bool): Возвращать все мэтчи пользователя или
                только первый. По умолчанию False. Если True, то возвращаются
                все запись мэтчей. Если False, то возвращается только первый.

        Returns:
            list[Matches] | Matches: Список мэтчей пользователя или
                мэтч пользователя.
            list: Пустой список, если произошла ошибка при получении данных из
                базы данных или пользователь не найден.
            None: Если произошла ошибка при получении данных из базы данных
                или пользователь не найден.
        """
        try:
            query = self.session.query(Matches)

            query = (
                query.filter_by(user_id=user_id)
                if user_id
                else query.filter_by(matched_vk_id=matched_vk_id)
            )

            return query.all() if return_all else query.first()
        except SQLAlchemyError as e:
            print(
                f"Произошла ошибка при получении параметров пользователя: {e}"
            )
            return []
