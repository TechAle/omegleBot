from data import urls, header
import requests
import json
import threading
import logging
import os
from datetime import datetime
import sys
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

def sendMessage(bot, id, msg):
    try:
        bot.sendMessage(chat_id=id, text=msg)
        time.sleep(.1)
    except:
        time.sleep(10)
        sendMessage(bot, id, msg)


app = setup_logger('appTelegram', '../appTelegram.log')


class omegleTelegram:
    __tags = []
    __lang = ""
    __chats = 0
    __firstMessage = ""
    __delayFirstMessage = 0
    __delayResearch = 0

    def __init__(self, idUser, idChat, bot):
        self.__setuppSettings(idUser)
        self.id = idChat
        self.__bot = bot
        self.__continue = True
        self.__run()

    def sendMessage(self, message):
        self.__chats.sendMessages(message)

    def __setuppSettings(self, idConversation):
        settings = settingClass(idConversation)
        self.__tags = settings.getTags()
        self.__lang = settings.getLang()
        self.__firstMessage = settings.getFirstMessage()
        self.__delayFirstMessage = settings.getDelayFirstMessage()
        self.__delayResearch = settings.getDelayResearch()
        self.__skipMessages = settings.getSkipmessages()

    def __run(self):
        threading.Thread(target=self.__newChat).start()

    def __newChat(self):
        while True:
            if not self.__continue:
                break
            if not self.__skipMessages:
                app.info("Looking for new chat")
                sendMessage(self.__bot, self.id, "Looking for new chat")
            self.addNewChat()
            if not self.__chats.startChat():
                break
            time.sleep(self.__delayResearch)

    def close(self):
        self.__continue = False

    def addNewChat(self):
        self.__chats = subChatTelegram(self.__tags, self.__lang, self.__firstMessage, self.__delayFirstMessage, self.id,
                                       self.__bot, self.__skipMessages)



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

    def __init__(self, tags, lang, firstMessage, delay, id, bot, skipMessage):
        self.__tags = tags
        self.__lang = lang
        self.__firstMessage = firstMessage
        self.__delayFirstMessage = delay
        self.__bot = bot
        self.__id = id
        self.__skipmessages = skipMessage
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
        self.sendMessages("first message")
        self.__receivemessages()

    def sendMessages(self, message):
        if message == "first message":
            if self.__firstMessage != "":
                time.sleep(self.__delayFirstMessage)
                requests.post(urls["send"],
                              headers=header,
                              data={'id': self.__uuid, 'msg': self.__firstMessage})
        else:
            self.__elaborateMessage(message)

    def __canContinue(self):
        return self._alive

    def __elaborateMessage(self, message):
        if message == 'quit':
            self.__continuare = False
        elif message == 'typing' or message == 'stoptyping':
            requests.post(urls[message],
                          headers=header,
                          data={'id': self.__uuid})
        elif message.lower() != 'disconnect':
            requests.post(urls["send"],
                          headers=header,
                          data={'id': self.__uuid, 'msg': message})
            self.__log("You: " + message, False)
        else:
            requests.post(urls["disconnect"],
                          headers=header,
                          data={'id': self.__uuid})
            self.__log("Disconnected")
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

            if type(received) is not list or not self._alive:
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

        if not self.__skipmessages:
            self.__log("Found new chat")

    def __log(self, msg, sendBack=True):
        app.info(msg)
        self.__logger.info(msg)
        if sendBack:
            sendMessage(self.__bot, self.__id, msg)
