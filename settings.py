import os.path
import json


def sceltaInput():
    while True:
        if (value := input(
                "1) tags\n2) lang\n3) first message\n4) delay first message\n5) delay research\n6) Exit")).isnumeric() \
                and (value := int(value)) > 0 and value < 7:
            return value


class settingClass:
    __tags = []
    __lang = ""
    __firstMessage = ""
    __delayFirstMessage = 0
    __delayResearch = 0

    def getTags(self):
        return self.__tags

    def getLang(self):
        return self.__lang

    def getFirstMessage(self):
        return self.__firstMessage

    def getDelayFirstMessage(self):
        return self.__delayFirstMessage

    def getDelayResearch(self):
        return self.__delayResearch

    def __init__(self):
        self.__load()

    def __load(self):
        if os.path.isfile("settings.json"):
            self.__tags.clear()

            data = json.load(open("settings.json", "r"))

            self.__lang = data["lang"] if "lang" in data else "en"

            if "tags" in data:
                self.__tags = data["tags"]

            if "firstMessage" in data:
                self.__firstMessage = data["firstMessage"]

            if "delayFirstMessage" in data:
                self.__delayFirstMessage = data["delayFirstMessage"]

            if "delayResearch" in data:
                self.__delayResearch = data["delayResearch"]

    def save(self):
        json.dump({
            'lang': self.__lang,
            'tags': self.__tags,
            'firstMessage': self.__firstMessage,
            'delayFirstMessage': self.__delayFirstMessage,
            'delayResearch': self.__delayResearch
        }, open('settings.json', 'w'), indent=4)

    def changeTags(self):
        for i, tag in enumerate(self.__tags):
            print(str(i + 1) + " " + tag)
        inp = input("Number: Remove, other: Add new tag")
        if inp.isnumeric():
            self.__tags.pop(int(inp)-1)
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
