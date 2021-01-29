from tinydb import TinyDB, Query
from secrets import token_hex


class Kanban:
    def __init__(self, storage: TinyDB):
        self.db = storage

    def new_board(self, user_id: str):
        token = token_hex(4)
        board = {
            'board_id': token,
            'owner': user_id,
            'backlog': {

            },
            'todo': {

            },
            'doing': {

            },
            'done': {

            }
        }
        return self.db.insert(board)

    def get_board(self, owner_id: str):
        board = Query()
        user_board = self.db.search(board.owner == owner_id)[0]

        return user_board

    def add_task_to(self, owner_id: str, status: str, task: str):
        # add task to status in owner board
        # get owner board
        # based on that board
        # insert new key: task into status
        token = token_hex(1)

        board = Query()
        user_board = self.db.search(board.owner == owner_id)[0]

        user_board[status][token] = task

        return self.db.update(user_board, board.owner == owner_id), token

