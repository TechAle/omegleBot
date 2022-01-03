import os.path
import json


def sceltaInput():
    while True:
        if (value := input(
                "1) tags\n2) lang\n3) first message\n4) delay first message\n5) delay research\n6) Exit")).isnumeric() \
                and (value := int(value)) > 0 and value < 7:
            return value


def checkDirectoryExists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return False
    return True


class settingClass:
    __tags = []
    __lang = "it"
    __firstMessage = ""
    __delayFirstMessage = 0
    __delayResearch = 0
    __skipMessages = False

    def getTags(self):
        return self.__tags

    def setTag(self, tag, operation):
        if operation == "add":
            self.__tags.append(tag)
        else:
            self.__tags.pop(self.__tags.index(tag))

    def getLang(self):
        return self.__lang

    def setLang(self, lang):
        self.__lang = lang

    def getFirstMessage(self):
        return self.__firstMessage

    def setFirstMessage(self, message):
        self.__firstMessage = message

    def getDelayFirstMessage(self):
        return self.__delayFirstMessage

    def setDelayFirstMessage(self, delay):
        self.__delayFirstMessage = delay

    def getDelayResearch(self):
        return self.__delayResearch

    def setDelayResearch(self, delay):
        self.__delayResearch = delay

    def getSkipmessages(self):
        return self.__skipMessages

    def setSkipMessage(self, value):
        self.__skipMessages = value == "yes"

    def __init__(self, idSettings):
        self.__id = idSettings
        if idSettings == -1:
            self.__load()
        else:
            self.__loadTelegram(idSettings)

    def __loadTelegram(self, idSetting):
        if checkDirectoryExists("id"):
            if os.path.isfile("id/" + str(idSetting) + ".json"):
                self.loadFile("id/" + str(idSetting) + ".json")
                return -1

    def __load(self):
        if os.path.isfile("settings.json"):
            self.loadFile("settings.json")

    def loadFile(self, file):
        self.__tags.clear()

        data = json.load(open(file, "r"))

        self.__lang = data["lang"] if "lang" in data else "it"

        if "tags" in data:
            self.__tags = data["tags"]

        if "firstMessage" in data:
            self.__firstMessage = data["firstMessage"]

        if "delayFirstMessage" in data:
            self.__delayFirstMessage = data["delayFirstMessage"]

        if "delayResearch" in data:
            self.__delayResearch = data["delayResearch"]

        if "skipMessages" in data:
            self.__skipMessages = data["skipMessages"]

    def save(self):
        path = 'settings.json'
        if self.__id != -1:
            checkDirectoryExists("id")
            path = "./id/" + str(self.__id) + ".json"
        json.dump({
            'lang': self.__lang,
            'tags': self.__tags,
            'firstMessage': self.__firstMessage,
            'delayFirstMessage': self.__delayFirstMessage,
            'delayResearch': self.__delayResearch,
            'skipMessages' : self.__skipMessages
        }, open(path, 'w'), indent=4)

    def changeTags(self):
        for i, tag in enumerate(self.__tags):
            print(str(i + 1) + " " + tag)
        inp = input("Number: Remove, other: Add new tag")
        if inp.isnumeric():
            self.__tags.pop(int(inp) - 1)
        else:
            self.__tags.append(inp)

    def changeLang(self):
        self.__lang = input("Lang: ")

    def changeFirstMessage(self):
        self.__firstMessage = input("First message: ")

    def changeDelayFirstMessage(self):
        self.__delayFirstMessage = float(input("Delay first message: "))

    def changeDelayResearch(self):
        self.__delayResearch = float(input("Delay research: "))

    def modifySettings(self):
        while True:
            scelta = sceltaInput()
            {
                1: self.changeTags,
                2: self.changeLang,
                3: self.changeFirstMessage,
                4: self.changeDelayFirstMessage,
                5: self.changeDelayResearch,
                6: lambda: None
            }[scelta]()
            if scelta == 6:
                break
