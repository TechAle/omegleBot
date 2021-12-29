import os.path
import json


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
        pass

    def modifySettings(self):
        pass
