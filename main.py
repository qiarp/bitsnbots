import logging
from secrets import token_hex

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown

from tinydb import TinyDB, Query

TOKEN: str = '1598446066:AAEkQ1ZuJkpJQQluUI2gUnyU1ERCu7IJab8'
db: TinyDB = TinyDB('./storage/db-todo.json')

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
    
    elif command in ['/todo', '/task']:
        token = token_hex(4)
        if len(message) <= 3:
            response = "Informe a tarefa! <code>/todo minha task</code>"
        else:
            db.insert({'token': token, 'user_id': user.id, 'task': message})
            response = f'Tarefa <code>{token}</code> salva! ' \
                       f'Use /show_tasks para visualizar todas as suas tarefas'

        update.message.reply_html(
            reply_to_message_id=update.message.message_id,
            text=response
        )

    elif command in ['/show_tasks', '/tasks']:
        task = Query()
        todos = db.search(task.user_id == user.id)
        all_tasks = len(todos)

        if all_tasks == 0:
            response = '<b>Nenhuma tarefa!</b>'
        else:
            tasks = [f' [<code>{item["token"]}</code>] - {item["task"]}' for item in todos]
            user_tasks = '\n'.join(tasks)
            response = f'<b>Suas tarefas ({all_tasks}):</b> \n{user_tasks}'

        update.message.reply_html(
            reply_to_message_id=update.message.message_id,
            text=response
        )

    elif command in ['/del_task', '/done']:
        task_token = message.split(' ')[0]
        task = Query()
        del_task = len(db.remove((task.user_id == user.id) & (task.token == task_token)))

        if del_task == 1:
            response = f'<b>Tarefa {task_token} removida!</b>'
        else:
            response = 'Nenhuma tarefa correspondente'

        update.message.reply_html(
            reply_to_message_id=update.message.message_id,
            text=response
        )


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler(
        ['afk', 'back', 'online', 'returned',
         'todo', 'task', 'show_tasks', 'tasks', 'del_task', 'done'],
        command_handler)
    )
    dispatcher.add_handler(MessageHandler(Filters.text, echoer))

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
