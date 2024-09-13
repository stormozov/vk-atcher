import os

from dotenv import load_dotenv

from vk_bot.bot import VKBot

load_dotenv()


if __name__ == '__main__':
    group_token = os.getenv('VK_GROUP_TOKEN')
    bot = VKBot(group_token)
    bot.start()

