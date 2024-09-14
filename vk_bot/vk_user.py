from vk_bot.utils import calculate_age


class UserVK:
	def __init__(self) -> None:
		self.id = None
		self.first_name = None
		self.last_name = None
		self.age = None
		self.sex = 0
		self.bdate = None
		self.city_id = None
		self.city_title = None
		self.relation = None
		self.url = None

	def get_user_info(self) -> dict[str, str | int | None]:
		return {
			"id": self.id,
			"first_name": self.first_name,
			"last_name": self.last_name,
			"age": self.age,
			"sex": self.sex,
			"bdate": self.bdate,
			"city_id": self.city_id,
			"city_title": self.city_title,
			"relation": self.relation,
			"url": self.url
		}

	def set_user_info(self, user_id: int, user_info: dict, url: str) -> None:
		self.id = user_id
		self.first_name = user_info.get("first_name")
		self.last_name = user_info.get("last_name")
		self.age = calculate_age(user_info.get("bdate"))
		self.sex = user_info.get("sex")
		self.bdate = user_info.get("bdate")
		self.city_id = user_info.get("city").get("id")
		self.city_title = user_info.get("city").get("title")
		self.relation = user_info.get("relation")
		self.url = url
