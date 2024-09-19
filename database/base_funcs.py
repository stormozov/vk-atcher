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


def get_user_id_by_vk_id(vk_id: int) -> int:
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
            photo_url_1 = item.get('photo_url1')
            photo_url_2 = item.get('photo_url2')
            photo_url_3 = item.get('photo_url3')

            user_id = get_user_id_by_vk_id(f_user_id)

            existing_match = session.query(Matches).filter_by(matched_vk_id=vk_id).first()

            if existing_match:
                existing_match.first_name = first_name
                existing_match.last_name = last_name
                existing_match.profile_link = profile_link
                existing_match.photo_url_1 = photo_url_1
                existing_match.photo_url_2 = photo_url_2
                existing_match.photo_url_3 = photo_url_3
            else:
                # Добавляем нового пользователя
                new_match = Matches(
                    user_id=user_id,
                    matched_vk_id=vk_id,
                    first_name=first_name,
                    last_name=last_name,
                    profile_link=profile_link,
                    photo_url_1=photo_url_1,
                    photo_url_2=photo_url_2,
                    photo_url_3=photo_url_3
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
