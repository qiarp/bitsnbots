import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown

TOKEN = ''

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def command_handler(update: Update, context: CallbackContext) -> None:
    # print(update)
    message = update.message.text
    command = message.split(' ')[0]
    message = escape_markdown(' '.join(message.split(' ')[1:]))
    user = update.message.from_user
    user = user.first_name if user.username is None else user.username

    if command == '/afk':
        update.message.reply_markdown_v2(
            reply_to_message_id=update.message.message_id,
            text=f'{user} *is away from keyboard*\n status: _{message}_'
        )
    elif command in ['/back', '/online', '/returned']:
        update.message.reply_markdown_v2(
            reply_to_message_id=update.message.message_id,
            text=f'{user} *is online*'
        )


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text, command_handler))

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
