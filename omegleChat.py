# Libraries
from data import urls, header
import requests
import json
import threading
from datetime import datetime
import sys
import select
import time
from settings import settingClass
from utils import logUtils, directoryUtils

# Directory of every chats
directoryUtils.createIfNotExists("./chats")

# Logger
app = logUtils.setup_logger('app', 'app.log')

# For reading from the terminal without a blocking input
read_list = [sys.stdin]

timeout = 0.1  # seconds
last_work_time = time.time()

class omegle:
    __tags = []
    __lang = ""
    __chats = []
    __firstMessage = ""
    __delayFirstMessage = 0
    __delayResearch = 0

    def __init__(self):
        self.__setuppSettings()
        self.__run()

    def __setuppSettings(self):
        settings = settingClass(-1)
        self.__tags = settings.getTags()
        self.__lang = settings.getLang()
        self.__firstMessage = settings.getFirstMessage()
        self.__delayFirstMessage = settings.getDelayFirstMessage()
        self.__delayResearch = settings.getDelayResearch()

    def __run(self):
        self.__newChat()

    def __newChat(self):
        i = 0
        while True:
            app.info("Looking for new chat")
            self.addNewChat()
            continuare = self.__chats[i].startChat()
            i += 1
            if not continuare:
                break
            else:
                time.sleep(self.__delayResearch)

    def addNewChat(self):
        self.__chats.append(
            subChatTerminal(self.__tags, self.__lang, self.__firstMessage, self.__delayFirstMessage))


class subChatTerminal:
    # noinspection DuplicatedCode
    __tags = []
    __lang = ""
    __uuid = ""
    __firstMessage = ""
    __delayFirstMessage = 0
    _alive = True
    __logger = ""
    __continuare = True

    def __init__(self, tags, lang, firstMessage, delay):
        self.__tags = tags
        self.__lang = lang
        self.__firstMessage = firstMessage
        self.__delayFirstMessage = delay
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y|%H:%M:%S")
        self.__logger = logUtils.setup_logger(dt_string, "./chats/" + dt_string + ".log")

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
        while self._alive:
            global read_list
            # while still waiting for input on at least one file
            while read_list:
                ready = select.select(read_list, [], [], timeout)[0]
                if not ready:
                    if not self.canContinue():
                        break
                else:
                    for file in ready:
                        line = file.readline()
                        if not line:  # EOF, remove file from input list
                            read_list.remove(file)
                        elif line.rstrip():  # optional: skipping empty lines
                            if not self.elaborateMessage(line):
                                break

    def canContinue(self):
        return self._alive

    def elaborateMessage(self, message):
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
            self.log("You: " + message)
        else:
            requests.post(urls["disconnect"],
                          headers=header,
                          data={'id': self.__uuid})
            self._alive = False
            return False
        return True

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
            for i in range(1, match.__len__() - 1):
                self.log(match[i])

        else:
            for i in range(1, output.__len__() - 1):
                self.log(output[i])
        self.log("Found new chat")

    def close(self):
        self._alive = False

    def log(self, msg):
        app.info(msg)
        self.__logger.info(msg)
