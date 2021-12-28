from data import urls, header
import requests
import json
import threading
import time
import logging
import os
from datetime import datetime

if not os.path.exists("./chats"):
    os.makedirs("./chats")

formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


app = setup_logger('app', 'app.log')


class omegle:
    __tags = []
    __lang = ""
    __chats = []
    __id = 0
    __firstMessage = ""
    __delayFirstMessage = 0

    def __init__(self, tags, lang, firstMessage, delayFirstMessage):
        self.__tags = tags
        self.__lang = lang
        self.__firstMessage = firstMessage
        self.__delayFirstMessage = delayFirstMessage
        self.__run()

    def __run(self):
        self.__newChat()

    def __newChat(self):
        i = 0
        while True:
            self.__chats.append(subChat(self.__tags, self.__lang, self.__id, self.__firstMessage, self.__delayFirstMessage))
            self.__id += 1
            continuare = self.__chats[i].startChat()
            i+=1
            if not continuare:
                break


class subChat:
    __tags = []
    __lang = ""
    __uuid = ""
    __firstMessage = ""
    __delayFirstMessage = 0
    _id = 0
    _alive = True
    __logger = ""
    __continuare = True

    def __init__(self, tags, lang, idChat, firstMessage, delay):
        self.__tags = tags
        self.__lang = lang
        self.__id = idChat
        self.__firstMessage = firstMessage
        self.__delayFirstMessage = delay
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y|%H:%M:%S")
        self.__logger = setup_logger(dt_string, "./chats/" + dt_string + ".log")

    def startChat(self):
        self.__newChat()
        self.__startWriting()
        return self.__continuare

    def __startWriting(self):
        send = threading.Thread(target=self.sendMessages)
        receive = threading.Thread(target=self.receivemessages)
        send.start()
        receive.start()
        while send.is_alive() and receive.is_alive() and self._alive:
            time.sleep(1)

        send.join()

    def sendMessages(self):
        if self.__firstMessage != "":
            time.sleep(self.__delayFirstMessage)
            requests.post(urls["send"],
                          headers=header,
                          data={'id': self.__uuid, 'msg': self.__firstMessage})
        while True:
            message = input("")
            if not self._alive:
                output = message
                break
            if message == 'typing' or message == 'stoptyping':
                requests.post(urls[message],
                              headers=header,
                              data={'id': self.__uuid})
            elif message != 'disconnect':
                requests.post(urls["send"],
                              headers=header,
                              data={'id': self.__uuid, 'msg': message})
                self.log(message)
            else:
                requests.post(urls["disconnect"],
                              headers=header,
                              data={'id': self.__uuid})
                output = input("Disconnected, do you wanna continue?")
                self.log("Disconnected")
                break
        if output.lower().startswith('n'):
            self.__continuare = False

    def receivemessages(self):
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
                        print("Disconnected, do you wanna continue?")
                        self.log("He left the chat")
                        break
                    elif received[0][0] == "gotMessage":
                        if received[0].__len__() > 1:
                            self.log("He: " + received[0][1])

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
            if match.__len__() > 1:
                if match[0][0] == "commonLikes":
                    self.log("Tags: " + match[0][1].__str__())
                if match.__len__() > 2:
                    if match[1].__len__() > 1:
                        self.log(match[1][1])

        else:
            a = 0

    def close(self):
        self._alive = False

    def log(self, msg):
        app.info(msg)
        self.__logger.info(msg)
