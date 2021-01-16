import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown
from pymongo import MongoClient

TOKEN = '1598446066:AAE7kO8hr71gKVy19HgoTg-0DlqRcFGuKrs'
client = MongoClient("mongodb+srv://bot:3vN8mvbFffVbNtIx@runaway.kqsps.mongodb.net/blog?retryWrites=true&w=majority")
db = client['todo']
lists = db['list']

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
    
    elif command == '/todo':
        lists.insert_one({'todo':message, 'id':teste})
        update.message.reply_markdown_v2(
            reply_to_message_id=update.message.message_id,
            text=f'I will remember that for you\!'
    )

    elif command == '/show_todos':
        todos = list(lists.find({'id':teste}))
        output = [f'{item["todo"]}' for item in todos]
        x = escape_markdown('\n'.join(output))
        update.message.reply_markdown_v2(
            reply_to_message_id=update.message.message_id,
            text=f'*Your todos:* \n{x}'
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
