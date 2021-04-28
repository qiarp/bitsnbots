class BotData(object):

    def __init__(self):
        self.current_version = '0.0.2'
        self.command_list = [
            'afk', 'back', 'online', 'returned',
            'todo', 'task', 'show_tasks', 'tasks', 'del_task', 'done',
            'code',
            'help', 'ajuda',
            'board', 'new_board', 'new_task', 'move'
        ]

    @property
    def current_version(self):
        return self._current_version

    @current_version.setter
    def current_version(self, version):
        self._current_version = version


# initialize botdata
bot_data = BotData()
