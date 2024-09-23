from sqlalchemy.exc import SQLAlchemyError
from database.base import Users, Matches, Session


def add_bot_user_to_db(data_list: list[dict]) -> None:
    session = Session()
    try:
        for item in data_list:
            vk_id = item.get('id')
            first_name = item.get('first_name')
            last_name = item.get('last_name')
            gender = item.get('sex')
            city_id = item.get('city', {}).get('id')

            existing_user = session.query(Users).filter_by(vk_id=vk_id).first()
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
                session.add(new_user)

        session.commit()
        print("Пользователи успешно добавлены/обновлены в базе данных.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при добавлении пользователей: {e}")

    finally:
        session.close()


def get_user_id_by_vk_id(vk_id: int) -> int | None:
    session = Session()
    try:
        user = session.query(Users).filter_by(vk_id=vk_id).first()
        if user:
            return user.user_id
        else:
            print(f"Пользователь с vk_id {vk_id} не найден.")
            return None
    except SQLAlchemyError as e:
        print(f"Произошла ошибка при получении user_id: {e}")
        return None


def add_match_user_to_db(data_list: list[dict], f_user_id) -> None:
    session = Session()
    try:
        for item in data_list:
            vk_id = item.get('id')
            first_name = item.get('first_name')
            last_name = item.get('last_name')
            profile_link = item.get('url')
            photo_id_1 = item.get('photo_id1')
            photo_id_2 = item.get('photo_id2')
            photo_id_3 = item.get('photo_id3')

            user_id = get_user_id_by_vk_id(f_user_id)

            existing_match = session.query(Matches).filter_by(matched_vk_id=vk_id).first()

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
                session.add(new_match)

        session.commit()
        print("Пользователи успешно добавлены/обновлены в базе данных.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при добавлении пользователей: {e}")

    finally:
        session.close()


def get_user_params(user_id, session: Session):
    try:
        user = session.query(Users).filter_by(vk_id=user_id).first()
        if user:
            return {
                "city_id": user.city,
                "sex": user.gender
            }
        else:
            return None
    except SQLAlchemyError as e:
        print(f"Произошла ошибка при получении параметров пользователя: {e}")
        return None


def get_match_info_to_print(f_user_id: int) -> list[dict] | None:
    session = Session()
    user_id = get_user_id_by_vk_id(f_user_id)

    try:
        matches = session.query(Matches).filter_by(user_id=user_id).all()
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
        print(f"Произошла ошибка при получении параметров пользователя: {e}")
        return None


def match_data_layout(f_user_id: int) -> list:
    match_info = get_match_info_to_print(f_user_id)
    all_match_info_list = []

    if match_info:
        for result in match_info:

            match_info_list = []
            match_mess_info = f'{result["first_name"]} {result["last_name"]}'
            match_url_info = result["profile_link"]

            match_info_list.append(match_mess_info)
            match_info_list.append(match_url_info)

            photos = []
            if result.get("photo_id_1"):
                photos.append(
                    f'photo{result["vk_id"]}_{result["photo_id_1"]}')
            if result.get("photo_id_2"):
                photos.append(
                    f'photo{result["vk_id"]}_{result["photo_id_2"]}')
            if result.get("photo_id_3"):
                photos.append(
                    f'photo{result["vk_id"]}_{result["photo_id_3"]}')

            match_info_list.append(photos)

            all_match_info_list.append(match_info_list)

    return all_match_info_list
