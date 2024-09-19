import os

from dotenv import load_dotenv
from database.base_funcs import Session


from vk_bot.bot import VKBot

load_dotenv()


if __name__ == '__main__':
    db_session = Session()
    group_token = os.getenv('VK_GROUP_TOKEN')
    bot = VKBot(group_token, db_session)
    bot.start()
