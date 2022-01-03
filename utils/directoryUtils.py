import os

def createIfNotExists(path):
    if not os.path.exists("./chats"):
        os.makedirs("./chats")