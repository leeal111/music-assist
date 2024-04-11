import json
from os.path import basename, splitext
from utils import is_valid_json, print_error, print_info, save_string
from sqlite import SqliteDataBase


class CloudBase(SqliteDataBase):
    def __init__(self, database_path):
        super().__init__(database_path)

    def playlists(self):
        return self._executeSQL("select * from playlistTrackIds;")

    def offlineTracksByID(self, id):
        return self.tableDataByID("offlineTrack", f'"track-{id}"')

    def trackNamesByLength(self, given_playlist_length):
        playlists = self.playlists()
        playlist_lengths = []
        for item in playlists:
            playlist_json = json.loads(item[1])["trackIds"]
            playlist_lengths.append(len(playlist_json))
            if len(playlist_json) == given_playlist_length:
                track_names = []
                for item in playlist_json:
                    track_id = item["id"]
                    data = self.offlineTracksByID(track_id)
                    if len(data) == 0:
                        print_info(f"track_id: {track_id} 不存在")
                    else:
                        track_path = data[0][3]
                        track_name = splitext(basename(track_path))[0]
                        track_names.append(track_name)
                return track_names
        print_error(
            f"given_playlist_length: {given_playlist_length} 不在 playlist_lengths:{playlist_lengths} 里面"
        )

    def save_table_info(self, table_name):
        data = self.tableFirstData(table_name)
        columns = self.columns(table_name)
        if len(data) != 0:
            data = [x for x in data[0]]
            for i, column in enumerate(columns):
                if column[2] == "TEXT" and is_valid_json(data[i]):
                    save_string(data[i], f"{table_name}-{column[1]}.json")
                    data[i] = "json_string"

        save_string(
            "\n".join(
                [
                    str(self.tableCountNum(table_name)),
                    str([x[1:3] for x in columns]),
                    str(data),
                ]
            ),
            f"{table_name}.txt",
        )
