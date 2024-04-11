import sqlite3
from os.path import exists
from utils import print_error


class SqliteDataBase:

    def __init__(self, database_path) -> None:
        # 连接到SQLite数据库
        if not exists(database_path):
            print_error(f"database:'{database_path}' not exists")
        self.conn = sqlite3.connect(database_path)

    def _executeSQL(self, sql_sentence):
        cursor = self.conn.cursor()
        cursor.execute(sql_sentence)
        results = cursor.fetchall()
        cursor.close()
        return results

    def tables(self):
        return self._executeSQL("SELECT name FROM sqlite_master WHERE type='table';")

    def columns(self, table_name):
        return self._executeSQL(f"PRAGMA table_info({table_name})")

    def tableFirstData(self, table_name):
        return self._executeSQL(f"SELECT * FROM {table_name} LIMIT 1")

    def tableCountNum(self, table_name):
        return self._executeSQL(f"SELECT COUNT(*) FROM {table_name}")[0][0]

    def extract_database_info(self, save_table_info_func):
        tables = self.tables()
        table_names = [x[0] for x in tables]
        for name in table_names:
            save_table_info_func(name)

    def tableDataByID(self, table_name, id):
        return self._executeSQL(f"SELECT * FROM {table_name} WHERE id = {id}")
