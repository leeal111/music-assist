import sqlite3
from os.path import exists
from utils import print_error
from values import CLOUDMUSIC_DATABASE_PATH


class SqliteDataBase:

    def __init__(self, database_path: str) -> None:
        """初始化数据库连接。如果路径文件不存在，则报错。

        Args:
            database_path (str): 数据库路径
        """

        if not exists(database_path):
            print_error(f"database:'{database_path}' not exists")
        self.conn = sqlite3.connect(database_path)

    def executeSQL(self, sql_sentence):
        """执行SQL语句，并返回全部结果

        Args:
            sql_sentence (str): SQL语句

        Returns:
            list[Any]: 查询结果
        """
        cursor = self.conn.cursor()
        cursor.execute(sql_sentence)
        results = cursor.fetchall()
        cursor.close()
        return results

    def tableNames(self):
        """返回数据库中所有表的表名

        Returns:
            list[str]: 表名列表
        """
        tmp = self.executeSQL("SELECT name FROM sqlite_master WHERE type='table';")
        res = [x[0] for x in tmp]
        return res

    def columnInfos(self, table_name):
        """返回数据表的列信息

        Args:
            table_name (str): 表名

        Returns:
            Any: 列信息。意义参考PRAGMA table_info的输出。
        """
        return self.executeSQL(f"PRAGMA table_info({table_name})")

    def tableFirstData(self, table_name):
        """返回表的数据样例。对于为空的情况，可以使用异常处理，但是此处直接交给了调用方处理。"""
        tmp = self.executeSQL(f"SELECT * FROM {table_name} LIMIT 1")
        return tmp

    def tableCountNum(self, table_name):
        """返回表的元素个数。"""
        return self.executeSQL(f"SELECT COUNT(*) FROM {table_name}")[0][0]


if __name__ == "__main__":
    sd = SqliteDataBase(CLOUDMUSIC_DATABASE_PATH)
    print(sd.tableNames())
    print(sd.columnInfos(sd.tableNames()[0]))
    print(sd.tableFirstData(sd.tableNames()[0]))
    print(sd.tableCountNum("s"))
