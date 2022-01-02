from data import urls, header
import requests
import json
import threading
import logging
import os
from datetime import datetime
import sys
import select
import time
from settings import settingClass

# noinspection DuplicatedCode
read_list = [sys.stdin]

timeout = 0.1  # seconds
last_work_time = time.time()

if not os.path.exists("../chatsTelegram"):
    os.makedirs("../chatsTelegram")

# noinspection DuplicatedCode
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


app = setup_logger('appTelegram', '../appTelegram.log')


class omegleTelegram:
    __tags = []
    __lang = ""
    __chats = 0
    __firstMessage = ""
    __delayFirstMessage = 0
    __delayResearch = 0

    def __init__(self, idConversation, bot):
        self.__setuppSettings(idConversation)
        self.__run()
        self._bot = bot

    def sendMessage(self, message):
        self.__chats.sendMessages(message)

    def __setuppSettings(self, idConversation):
        settings = settingClass(idConversation)
        self.__tags = settings.getTags()
        self.__lang = settings.getLang()
        self.__firstMessage = settings.getFirstMessage()
        self.__delayFirstMessage = settings.getDelayFirstMessage()
        self.__delayResearch = settings.getDelayResearch()
        self.__id = idConversation

    def __run(self):
        self.__newChat()

    def __newChat(self):
        while True:
            app.info("Looking for new chat")
            self.addNewChat()
            continuare = self.__chats.startChat()
            if not continuare:
                break
            else:
                time.sleep(self.__delayResearch)

    def addNewChat(self):
        self.__chats = subChatTelegram(self.__tags, self.__lang, self.__firstMessage, self.__delayFirstMessage, self.__id)


# noinspection DuplicatedCode
class subChatTelegram:
    __tags = []
    __lang = ""
    __uuid = ""
    __firstMessage = ""
    __delayFirstMessage = 0
    _alive = True
    __logger = ""
    __continuare = True

    def __init__(self, tags, lang, firstMessage, delay, id):
        self.__tags = tags
        self.__lang = lang
        self.__firstMessage = firstMessage
        self.__delayFirstMessage = delay
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y|%H:%M:%S")
        if not os.path.exists("../chatsTelegram/" + str(id)):
            os.makedirs("../chatsTelegram/" + str(id))
        self.__logger = setup_logger(dt_string, "../chatsTelegram/" + str(id) + "/" + dt_string + ".log")

    def startChat(self):
        self.__newChat()
        self.__startWriting()
        return self.__continuare

    def __startWriting(self):
        receive = threading.Thread(target=self.__receivemessages)
        receive.start()
        self.sendMessages("first message")

    def sendMessages(self, message):
        if self.__firstMessage != "" and message == "first message":
            time.sleep(self.__delayFirstMessage)
            requests.post(urls["send"],
                          headers=header,
                          data={'id': self.__uuid, 'msg': self.__firstMessage})
        else:
            self.__elaborateMessage(message)

    def __canContinue(self):
        return self._alive

    def __elaborateMessage(self, message):
        message = message[:-1]
        if message == 'quit':
            self.__continuare = False
        elif message == 'typing' or message == 'stoptyping':
            requests.post(urls[message],
                          headers=header,
                          data={'id': self.__uuid})
        elif message != 'disconnect':
            requests.post(urls["send"],
                          headers=header,
                          data={'id': self.__uuid, 'msg': message})
            self.__log("You: " + message)
        else:
            requests.post(urls["disconnect"],
                          headers=header,
                          data={'id': self.__uuid})
            self._alive = False
            return False
        return True

    def __receivemessages(self):
        while True:
            received = json.loads(
                requests.post(urls["event"],
                              headers=header,
                              data={'id': self.__uuid}).content
            )

            if type(received) is not list:
                break

            if received.__len__() > 0:
                if received[0].__len__() > 0:
                    if received[0][0] == "strangerDisconnected":
                        self._alive = False
                        self.__log("He left the chat")
                        break
                    elif received[0][0] == "gotMessage":
                        if received[0].__len__() > 1:
                            self.__log("He: " + received[0][1])

    def __newChat(self):
        url = urls["start"].replace("{TOPICS}", self.__tags.__str__().replace("\'", "\"")) \
            .replace("{LANG}", self.__lang)
        output = requests.post(url,
                               headers=header)
        output = json.loads(output.content)
        self.__uuid = output["clientID"]
        if output["events"][0][0] == "waiting":
            match = requests.post(urls["event"],
                                  headers=header,
                                  data={'id': self.__uuid})
            match = json.loads(match.content)
            for i in range(1, match.__len__() - 1):
                self.__log(match[i])

        else:
            for i in range(1, output.__len__() - 1):
                self.__log(output[i])
        self.__log("Found new chat")

    def __close(self):
        self._alive = False

    def __log(self, msg):
        app.info(msg)
        self.__logger.info(msg)


b = omegleTelegram(0, 0)
