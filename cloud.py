import json
from os import makedirs
from os.path import basename, splitext
from utils import is_valid_json, print_error, print_info, save_string
from sqlite import SqliteDataBase
from values import CLOUDMUSIC_DATABASE_PATH, TEMP_DATA_PATH


class CloudBase(SqliteDataBase):
    def __init__(self, database_path):
        super().__init__(database_path)

    def playlistidTrackidsDict(self):
        """返回由歌单id为键，歌曲id列表为值的字典"""
        tmp = self.executeSQL("select * from playlistTrackIds;")
        res = {}
        for x in tmp:
            res[x[0]] = [x["id"] for x in json.loads(x[1])["trackIds"]]
        return res

    def offlineTrackNameByID(self, id):
        """返回根据歌曲id在离线歌曲表中查找到的歌曲名称"""
        tmp = self.executeSQL(f'SELECT * FROM "offlineTrack" WHERE id = "track-{id}"')
        if len(tmp) != 1:
            # print_info(f"in offlineTracksByID find '{len(tmp)}' result by id '{id}'")
            return None
        return splitext(basename(tmp[0][3]))[0]

    def dbTrackNameByID(self, id):
        """返回根据歌曲id在db表中查找到的歌曲名称"""
        tmp = self.executeSQL(f'SELECT * FROM "dbTrack" WHERE id = "{id}"')
        if len(tmp) != 1:
            # print_info(f"in offlineTracksByID find '{len(tmp)}' result by id '{id}'")
            return None
        track_info = json.loads(tmp[0][1])
        name_str = track_info["name"]
        authors = track_info["artists"]
        author_str = ",".join([x["name"] for x in authors][:3])
        return f"{author_str} - {name_str}"

    def trackNamesByLength(self, given_playlist_length):
        """返回根据指定歌单列表长度查询到的歌单歌曲名称列表"""
        print_info("尝试从歌单长度获取歌单歌曲名称列表")
        ptd = self.playlistidTrackidsDict()
        _playlist_lengths = []
        for trackids in ptd.values():
            _playlist_lengths.append(len(trackids))
            if len(trackids) == given_playlist_length:
                trackNames = []
                for id in trackids:
                    name = self.dbTrackNameByID(id)
                    if name is None:
                        print_info(f"track_id: {id} 不存在或者重复存在")
                    else:
                        trackNames.append(name)

                if len(trackNames) != given_playlist_length:
                    print_info(
                        f"歌曲名称列表仅查询到{len(trackNames)}项，应查询到{given_playlist_length}项"
                    )
                else:
                    print_info(f"歌曲名称列表查询到{len(trackNames)}项")
                return trackNames
        print_error(
            f"given_playlist_length: {given_playlist_length} 不在 playlist_lengths:{_playlist_lengths} 里面"
        )

    def table_detailed_info(
        self,
    ):
        """遍历数据库的所有表，打印所有表的元素信息和相应的示例元素。对于存在特殊jsonstr的元素信息，还会生成json文件。"""
        makedirs(TEMP_DATA_PATH, exist_ok=True)
        tables = self.tableNames()
        for table_name in tables:

            data = self.tableFirstData(table_name)
            columns = self.columnInfos(table_name)

            # 遍历元素信息，查看是否存在有效的jsonstr。存在则用外部json文件保存，内部用json_string替换。
            if len(data) != 0:
                data = data[0]
                data = [x for x in data]  # tuple to list
                for i, column in enumerate(columns):
                    if column[2] == "TEXT" and is_valid_json(data[i]):
                        save_string(data[i], f"{table_name}-{column[1]}.json")
                        data[i] = "json_string"

            # 保存元素信息
            save_string(
                "\n".join(
                    [
                        f"元素个数：{str(self.tableCountNum(table_name))}",
                        f"列名称和类型：{str([x[1:3] for x in columns])}",
                        f"示例数据：{str(data)}",
                    ]
                ),
                f"{table_name}.txt",
            )


if __name__ == "__main__":
    cb = CloudBase(CLOUDMUSIC_DATABASE_PATH)
    # print(cb.tableFirstData("offlineTrack"))
    cb.table_detailed_info()
    # print(cb.playlistid_trackids_dict())
