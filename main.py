import logging
from secrets import token_hex
from requests import post
from requests.packages import urllib3
from random import randint
import html
import json
import logging
import traceback
from threading import Thread
from os import path
import toml
from sys import exit

from telegram import Update, File, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.utils.helpers import escape_markdown

from tinydb import TinyDB, Query

from kanban.kanban import Kanban
from parser.parser import Parser

from internal.bot_data import bot_data


config = toml.load('./config.toml')['bnb'] \
    if path.exists('./config.toml') \
    else exit('Please set ./config.toml')
TOKEN: str = config['APIKEY']
db: TinyDB = TinyDB('./storage/db-todo.json')
file_db: TinyDB = TinyDB('./storage/db-file.json')
kanban_db: TinyDB = TinyDB('./storage/db-kanban.json')

kanban = Kanban(kanban_db)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ignora aviso de conexao insegura(para snippets.glot.io)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

codepaste_headers = {'Authorization': 'Token c98f9e90-07df-413c-b7a1-8d6e7b6bb1d2',
                     'Content-type': 'application/json'}

file_mimetypes = ['application/pdf', 'application/epub+zip']


def command_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    message_id = update.message.message_id

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
            text=response
        )

    elif command in ['/show_tasks', '/tasks']:
        task = Query()
        todos = db.search(task.user_id == user.id)
        all_tasks = len(todos)

        if all_tasks == 0:
            response = '<b>Nenhuma tarefa!</b>'
        else:
            # adicionar parse de entities '<>' #todo
            tasks = [f' [<code>{item["token"]}</code>] - {item["task"]}' for item in todos]
            user_tasks = '\n'.join(tasks)
            response = f'<b>Suas tarefas ({all_tasks}):</b> \n{user_tasks}'

        update.message.reply_html(
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
            text=response
        )

    elif command in ['/help', '/ajuda']:
        commands = '\n'.join([f'/{cmd}' for cmd in bot_data.command_list])
        response = f"<b>Lista de comandos disponiveis:</b>\n{commands}"

        update.message.reply_html(
            text=response
        )

    elif command in ['/code', '/paste']:
        lang = message.split(' ')[0]
        if lang not in ['python', 'javascript', 'c', 'rust', 'py', 'bash']:
            lang = 'plaintext'
        snippet = ' '.join(message.split(' ')[1:])

        data = {
            "language": lang,
            "title": f'file-{randint(1, 100)}',
            "public": 'false',
            "files": [
                {
                    "name": f'file-{randint(1, 100)}.{lang}',
                    "content": snippet
                }
            ]
        }

        req = post(
            url='https://snippets.glot.io/snippets',
            headers=codepaste_headers,
            data=json.dumps(data),
            verify=False
        )

        if req.status_code == 200:
            snippet_id = req.json()['id']
            response = f'Código salvo em: https://glot.io/snippets/{snippet_id}'
        else:
            response = 'Erro salvando snippet!'

        update.message.reply_html(
            text=response
        )

        # deleta a mensagem com o código
        context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    elif command == '/new_board':
        r = kanban.new_board(user_id=user.id)

        update.message.reply_text(
            text=str(r)
        )

    elif command == '/board':
        # verificar se user.id possui board #todo
        keyboard = [
            [
                InlineKeyboardButton('backlog', callback_data='backlog'),
                InlineKeyboardButton('to do', callback_data='todo'),
            ],
            [
                InlineKeyboardButton('doing', callback_data='doing'),
                InlineKeyboardButton('done', callback_data='done')
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            text='Coluna:',
            reply_markup=reply_markup
        )

    elif command == '/new_task':
        status = message.split(' ')[0]
        task = ' '.join(message.split(' ')[1:])

        _, token = kanban.add_task_to(user.id, status, task)

        update.message.reply_text(
            text=f'Nova tarefa {token} adicionada em {status}'
        )
    elif command == '/move':
        task_token = message.split(' ')[0]
        task = dict()

        board = kanban.get_board(owner_id=user.id)

        for status in board:
            if status in ['board_id', 'owner']:
                pass
            else:
                for token in board[status]:
                    if task_token == token:
                        task['token'] = token
                        task['task'] = board[status][token]
                        task['from'] = status
                        break

        ok = kanban.remove_task(owner_id=user.id, from_status=task['from'], token=task['token'])
        response = f'Tarefa {task["token"]} removida do status atual' \
            if ok else f'Erro remover tarefa do status atual'

        update.message.reply_html(
            text=response
        )


def callback_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    print(update)

    user_id = query.from_user.id
    original_user = query.message.reply_to_message.from_user.id

    query.answer()

    if user_id != original_user:
        return

    status = query.data

    board = kanban.get_board(owner_id=user_id)

    all_tasks = len(board[status])
    tasks = [f' [<code>{token}</code>] - {board[status][token]}' for token in board[status]]
    user_tasks = '\n'.join(tasks)
    response = f'<b>Suas tarefas em {status} ({all_tasks}):</b> \n{user_tasks}'

    keyboard = [
        [
            InlineKeyboardButton('backlog', callback_data='backlog'),
            InlineKeyboardButton('to do', callback_data='todo'),
        ],
        [
            InlineKeyboardButton('doing', callback_data='doing'),
            InlineKeyboardButton('done', callback_data='done')
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=response,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


def document_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    token = token_hex(9)

    document = update.message.document
    from_info = update.message.from_user

    if document.mime_type not in file_mimetypes:
        return

    # file: File = context.bot.get_file(document.file_id)
    file: File = document.get_file()

    data = {
        'token': token,
        'user': {
            'id': from_info.id
        },
        'file': {
            'file_id': document.file_id,
            'file_unique_id': document.file_unique_id,
            'file_name': document.file_name,
            'mime_type': document.mime_type,
            'file_size': document.file_size
        }
    }

    file_db.insert(data)

    update.message.reply_html(
        text=f'File indexed - <code>{token}</code>'
    )


def channel_handler(update: Update, context: CallbackContext) -> None:
    """handle channel messages"""

    chat_id = update.channel_post.chat_id
    message_id = update.channel_post.message_id

    message = update.channel_post
    entities = message.entities

    if len(message.text) <= 9:
        return

    tags = []
    title = []
    desc = []
    url = []

    for entity in entities:
        limit = entity.offset + entity.length
        value = message.text[entity.offset:limit]

        if entity.type == 'hashtag':
            tags.append(value)
        elif entity.type == 'bold':
            title.append(value)
        elif entity.type == 'italic':
            desc.append(value)
        elif entity.type == 'url':
            url.append(value)

    title = '. '.join(title)
    desc = '. '.join(desc)
    content = '\n'.join(url)

    parser = Parser()
    parser.gohugo_parser(title, desc, content, tags, message.date.strftime("%Y-%m-%d"))

    Thread(target=parser.gohugo_save).start()


def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    update.message.reply_html(text=message)


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler(
        bot_data.command_list,
        command_handler)
    )

    dispatcher.add_handler(MessageHandler(Filters.document, document_handler))
    dispatcher.add_handler(MessageHandler(Filters.chat_type.channel, channel_handler))

    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
