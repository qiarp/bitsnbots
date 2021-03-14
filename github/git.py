from git import Repo

track_repo = '../bytesnbits/'


class Git:
    def __init__(self):
        self.repo = Repo(f'{track_repo}')
        return

    def push_changes(self, filepath: str) -> bool:
        try:
            self.repo.git.add([f'content/feed/{filepath}'])
            self.repo.index.commit('automatic feed update')
            origin = self.repo.remote(name='origin')
            origin.push()
            return True
        except Exception as e:
            print(e)
            return False
