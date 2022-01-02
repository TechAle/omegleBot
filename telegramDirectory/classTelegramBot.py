from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
# Allowed people that can use the bot
allowedId = [21731569]

# Function (decorator) for limiting the people can use the bot
def limitUser(func):
    def wrap(*args, **kwargs):
        if allowedId.__contains__(args[1].message.from_user.id):
            func(args[0], args[1], args[2])
        else:
            args[1].message.reply_text("Not allowed")

    return wrap

class telegramBot:

    nChats = []

    def __init__(self, TOKEN):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.__logger = logging.getLogger(__name__)
        self.__updater = Updater(TOKEN, use_context=True)
        self.__setupHandlers()
        # Start the Bot
        self.__updater.start_polling()
        self.__updater.idle()

    @limitUser
    def __onError(self, update, context):
        self.__logger.warning('Update "%s" caused error "%s"', update, context.error)

    @limitUser
    def __onMessage(self, update, context):
        context.bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)

    @limitUser
    def __onStart(self, update, context):
        update.message.reply_text('Oaic')

    @limitUser
    def __onNewChat(self):
        pass

    @limitUser
    def __onEndChat(self):
        pass

    def __setupHandlers(self):
        # Get the dispatcher to register handlers
        dp = self.__updater.dispatcher

        dp.add_handler(MessageHandler(Filters.text, self.__onMessage))

        dp.add_handler(CommandHandler("start", self.__onStart))
        dp.add_handler(CommandHandler("newchat", self.__onNewChat))
        dp.add_handler(CommandHandler("endchat", self.__onEndChat))

        dp.add_error_handler(self.__onError)
