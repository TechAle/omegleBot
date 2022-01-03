from settings import settingClass
from omegleChat import omegle
from telegramDirectory import classTelegramBot as tgBot


def menu():
    while True:
        if (choose := input("1) Start chatting\n2) User settings\n3) Start bot\n4) Close")).isnumeric() \
                and (choose := int(choose)) > 0 and choose < 5:
            return choose


def startChatting():
    omegle()


def userSettings():
    settings.modifySettings()
    settings.save()


def startBot():
    tgBot.startBot()


def close():
    settings.save()
    quit(0)


settings = settingClass(-1)

if __name__ == "__main__":
    while True:
        {
            1: startChatting,
            2: userSettings,
            3: startBot,
            4: close
        }[menu()]()
