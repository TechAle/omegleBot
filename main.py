from settings import settingClass
from omegleChat import omegle
from telegramDirectory import classTelegramBot as tgBot

# Print menu
def menu():
    while True:
        if (choose := input("1) Start chatting\n2) User settings\n3) Start bot\n4) Close")).isnumeric() \
                and (choose := int(choose)) > 0 and choose < 5:
            return choose

# Start chatting with the console
def startChatting():
    omegle()

# Change console's settings
def userSettings():
    settings.modifySettings()
    settings.save()

# Start telegram bot
def startBot():
    tgBot.startBot()

# Close + save settings
def close():
    settings.save()
    quit(0)


# Settings for console
settings = settingClass(-1)

if __name__ == "__main__":
    while True:
        # Cool menu
        {
            1: startChatting,
            2: userSettings,
            3: startBot,
            4: close
        }[menu()]()
