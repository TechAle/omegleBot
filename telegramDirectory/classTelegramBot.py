from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import credentials
from telegramDirectory.omegleTelegram import omegleTelegram

# Allowed people that can use the bot
allowedId = [217315169]


# Function (decorator) for limiting the people can use the bot
def limitUser(func):
    def wrap(*args, **kwargs):
        if allowedId.__contains__(args[1].message.from_user.id):
            func(args[0], args[1], args[2])
        else:
            args[1].message.reply_text("Not allowed")

    return wrap


def sendMessage(update, context, message):
    context.bot.sendMessage(chat_id=update.message.chat_id, text=message)

globalBot = 0

class telegramBot:
    nChats = []

    def __init__(self, TOKEN):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.__logger = logging.getLogger(__name__)
        self.__updater = Updater(TOKEN, use_context=True)
        self.__setupHandlers()
        global globalBot
        globalBot = self.__updater.bot
        # Start the Bot
        self.__updater.start_polling()
        self.__updater.idle()

    @limitUser
    def __onError(self, update, context):
        self.__logger.warning('Update "%s" caused error "%s"', update, context.error)

    @limitUser
    def __onMessage(self, update, context):
        for chat in self.nChats:
            if chat.id == update.effective_chat.id:
                chat.sendMessage(update.message.text)

    @limitUser
    def __onStart(self, update, context):
        update.message.reply_text('Oaic')

    @limitUser
    def __onNewChat(self, update, context):
        for chat in self.nChats:
            if chat.id == update.effective_chat.id:
                sendMessage(update, context, "A chat is already opened")
                return -1
        self.nChats.append(omegleTelegram(update.message.from_user.id, update.effective_chat.id, globalBot))

    @limitUser
    def __onEndChat(self, update, context):
        for chat in self.nChats:
            if chat.id == update.effective_chat.id:
                self.nChats.pop(chat)
                return -1
        sendMessage(update, context, "You havent opened a chat")

    def __setupHandlers(self):
        # Get the dispatcher to register handlers
        dp = self.__updater.dispatcher

        dp.add_handler(CommandHandler("start", self.__onStart))
        dp.add_handler(CommandHandler("newchat", self.__onNewChat))
        dp.add_handler(CommandHandler("endchat", self.__onEndChat))

        dp.add_handler(MessageHandler(Filters.text, self.__onMessage))

        dp.add_error_handler(self.__onError)


telegramBot(credentials.TOKEN)
