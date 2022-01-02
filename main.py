from settings import settingClass
from omegleChat import omegle


def menu():
    while True:
        if (choose := input("1) Start chatting\n2) User settings\n3) Start bot\n4) Bot settings\n5) Close")).isnumeric() \
                and (choose := int(choose)) > 0 and choose < 4:
            return choose


def startChatting():
    omegle()


def userSettings():
    settings.modifySettings()
    settings.save()

def startBot():
    pass


def botSettings():
    pass

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
