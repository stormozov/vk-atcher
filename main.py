import os

from dotenv import load_dotenv
from database.base import Session


from vk_bot.bot import VKBot

load_dotenv()


if __name__ == '__main__':
    db_session = Session()
    group_token = os.getenv('VK_GROUP_TOKEN')
    vk_token = os.getenv("VK_TOKEN")
    bot = VKBot(group_token, vk_token, db_session)
    bot.start()
