# coding: utf-8

from slackbot.bot import Bot
from slackbot_settings import API_TOKEN
import slack
client = slack.WebClient(token=API_TOKEN)


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    print("start bot")
    main()
