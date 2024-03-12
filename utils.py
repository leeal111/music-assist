import sqlite3


def execute_sql(database_path, sql_sentence):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(sql_sentence)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_database_table_names(database_path):
    ress = execute_sql(
        database_path,
        "SELECT name FROM sqlite_master WHERE type='table';",
    )
    print([res[0] for res in ress])


class music_info_data:
    def __init__(self):
        self.artist_name_list = []
        self.music_name = "default"
        self.album_name = "default"

    def cloudmusic_str(self, format_str):
        res = format_str.format(self.music_name, ",".join(self.artist_name_list[:3]))
        return res.replace(":", "")
