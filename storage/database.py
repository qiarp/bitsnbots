import sqlite3


class Database:
    def __init__(self):
        self.db = sqlite3.connect('./storage/storage.db')
        self.cursor = self.db.cursor()
        self.log = False

        # run me
        self.setup()

    def setup(self):
        setup = """
        CREATE TABLE IF NOT EXISTS indexing (
            id SERIAL,
            title TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            date TIMESTAMP,
            type VARCHAR(200)
        );
        """

        self.cursor.execute(setup)

        self.db.commit()

        self.log = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.db.close()
