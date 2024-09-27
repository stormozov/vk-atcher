from sqlalchemy.exc import SQLAlchemyError
from database.base import BlackList, Favorites
from database.db_funcs.user import UserDBManager

def get_blocked_and_favorites_by_vk_id(vk_id: int) -> dict:
    result = {"blocked": [], "favorites": []}

    db_manager = UserDBManager()

    user_id = db_manager.get_user_id_by_vk_id(vk_id)

    if not user_id:
        return result

    try:
        blocked_ids = db_manager.session.query(BlackList.blocked_vk_id).filter_by(user_id=user_id).all()
        result["blocked"] = [item[0] for item in blocked_ids]

        favorite_ids = db_manager.session.query(Favorites.favorite_vk_id).filter_by(user_id=user_id).all()
        result["favorites"] = [item[0] for item in favorite_ids]

    except SQLAlchemyError as e:
        print(f"Произошла ошибка при получении данных: {e}")

    return result
#
# vk_id = 187551636
# test_data = get_blocked_and_favorites_by_vk_id(vk_id)
# print(test_data)
# if 826505081 in test_data["blocked"]:
#     print("djambo")
#
#
# test_data = [{'id': 212243301, 'bdate': '16.2.1999', 'city': {'id': 37, 'title': 'Владивосток'}, 'last_seen': {'platform': 2, 'time': 1727343770}, 'track_code': 'a8bb20d2Pjg2yK1dFBVRvvoqGD_PNdO0ctcE5jhFc8h5zrLF_n1ZUSGcoWASEFK1ysSTrkswu7p01ATmNiMBoQ', 'first_name': 'Анна', 'last_name': 'Ахмадова', 'can_access_closed': True, 'is_closed': False}, {'id': 286233937, 'bdate': '19.1.2004', 'city': {'id': 37, 'title': 'Владивосток'}, 'last_seen': {'platform': 2, 'time': 1727448170}, 'track_code': '60ca59aaTVcwUjWNhCqVyxt4iXJ1uy_EqOSfRHkG2nLwnk1xRCwqPidUPrXVJZbKLZYI4Pe-R8qu559Ed2CoGw', 'first_name': 'Алёна', 'last_name': 'Егорова', 'can_access_closed': True, 'is_closed': False}]
def get_target_users(data:list[dict],vk_id:int) -> dict:
    db_manager = UserDBManager()
    target_users = {}
    for user in data:
        target_vk_id = user.get('id', {})
        rejected_ids = get_blocked_and_favorites_by_vk_id(db_manager.get_user_id_by_vk_id(vk_id))

        if target_vk_id not in rejected_ids['blocked'] and target_vk_id not in rejected_ids['favorites']:
            target_users[user['id']] = user

    return target_users


