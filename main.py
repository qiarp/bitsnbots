import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown

from tinydb import TinyDB, Query

TOKEN: str = '1598446066:AAE7kO8hr71gKVy19HgoTg-0DlqRcFGuKrs'
db: TinyDB = TinyDB('./db-todo.json')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def echoer(update: Update, context: CallbackContext) -> None:
    print(update)


def command_handler(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    command = ''.join(message.split('@')[:1]).split(' ')[0]
    message = escape_markdown(' '.join(message.split(' ')[1:]))
    user = update.message.from_user
    user_name = user.first_name if user.username is None else user.username

    if len(message) != 0:
        response = f'{user_name} *is away from keyboard*\n status: _{message}_'
    else:
        response = f'{user_name} *is away from keyboard*'

    if command == '/afk':
        update.message.reply_markdown_v2(
            reply_to_message_id=update.message.message_id,
            text=response
        )
    
    elif command in ['/back', '/online', '/returned']:
        update.message.reply_markdown_v2(
            reply_to_message_id=update.message.message_id,
            text=f'{user_name} *is online*'
        )
    
    elif command == '/todo':
        db.insert({'user_id': user.id, 'task': message})

        update.message.reply_text(
            reply_to_message_id=update.message.message_id,
            text='Tarefa salva! Use /show_tasks para visualizar todas as suas tarefas'
        )

    elif command == '/show_tasks':
        task = Query()
        todos = db.search(task.user_id == user.id)
        tasks = [f'- {item["task"]}' for item in todos]
        user_tasks = escape_markdown('\n'.join(tasks))

        update.message.reply_html(
            reply_to_message_id=update.message.message_id,
            text=f'<b>Suas tarefas:</b> \n{user_tasks}'
        )
    

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler(
        ['afk', 'back', 'online', 'returned', 'todo', 'show_tasks'],
        command_handler)
    )
    dispatcher.add_handler(MessageHandler(Filters.text, echoer))

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
