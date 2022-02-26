import telegram

from data import urls, header
import requests
import json
import threading
from utils import logUtils, directoryUtils
import os
from datetime import datetime
import time
from settings import settingClass


def sendMessage(bot, idChat, msg):
    try:
        bot.sendMessage(chat_id=idChat, text=msg)
        time.sleep(.1)
    except:
        time.sleep(10)
        sendMessage(bot, idChat, msg)


directoryUtils.createIfNotExists("./chatsTelegram")

app = logUtils.setup_logger('appTelegram', './appTelegram.log')


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


class subChatTelegram:
    __tags = []
    __lang = ""
    __uuid = ""
    __firstMessage = ""
    __delayFirstMessage = 0
    _alive = True
    __logger = ""
    __continuare = True
    __firstMessageSent = False
    __typing = False

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
        if not os.path.exists("./chatsTelegram/" + str(id)):
            os.makedirs("./chatsTelegram/" + str(id))
        self.__logger = logUtils.setup_logger(dt_string, "./chatsTelegram/" + str(id) + "/" + dt_string + ".log")

    def startChat(self):
        self.__newChat()
        self.__startWriting()
        if self.__typing:
            self.__bot.send_chat_action(chat_id=self.__id, action=telegram.ChatAction.TYPING)
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
            self.__firstMessageSent = True
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
                        self.__log("He left the chat", skipMessage=self.__skipmessages and not self.__firstMessageSent)
                        break
                    elif received[0][0] == "gotMessage":
                        if received[0].__len__() > 1:
                            self.__log("He: " + received[0][1])
                    elif received[0][0] == "typing":
                        self.__bot.send_chat_action(chat_id=self.__id, action=telegram.ChatAction.TYPING)
                        self.__typing = True
                    elif received[0][0] == "stoppedTyping":
                        self.__bot.send_chat_action(chat_id=self.__id, action=telegram.ChatAction.TYPING)
                        self.__typing = False

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
            if type(match) is list:
                for i in range(1, match.__len__() - 1):
                    self.__log(match[i], skipMessage=self.__skipmessages)

        else:
            for i in range(1, output.__len__() - 1):
                self.__log(output[i], skipMessage=self.__skipmessages)

        self.__log("Found new chat", skipMessage=self.__skipmessages)

    def __log(self, msg, sendBack=True, skipMessage=False):
        app.info(msg)
        self.__logger.info(msg)
        if sendBack and not skipMessage:
            sendMessage(self.__bot, self.__id, msg)
