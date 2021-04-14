from tinydb import TinyDB, Query, where
from tinydb.operations import delete
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

    def remove_task(self, owner_id: str, from_status: str, token: str) -> bool:
        board = Query()
        user_board = self.db.search(board.owner == owner_id)[0]
        
        try:
            board = user_board.copy()

            # print(self.db.update(delete(token), where(user_board[from_status]) == owner_id))
            return True
        except Exception as e:
            print(e)
            return False
