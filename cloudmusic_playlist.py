# update: 2024-03-11
# playlistTrackIds：存储不同的收藏列表，具体对应关系，可以使用置空得到。
# playlist_id对应了所需查询的收藏列表，可以通过查询得到一个cloudmusic_playlist_trackids.json，其中包括这个收藏列表的歌曲ID
# dbTrack：存储了所有的歌曲，用ID标识，可以通过查询得到一个cloudmusic_music_info.json，其中包括了这首歌曲的相关信息

# 参考文献：https://www.zhihu.com/question/31816805/answer/350601569
# webdb.db中需要用到的表：web_user_playlist、web_playlist_track、web_track
# web_user_playlist：用于保存登录网易云音乐账户的uid
# web_playlist_track：用于保存所有歌单歌曲信息（所有帐号打开过的所有歌单下的歌曲）
# pid为歌单id，tid为歌曲id，order为排序顺序（就是你歌单中的歌曲顺序）
# web_track：用于保存缓存在webdb.db中的所有歌曲的信息，不管哪个帐号哪个歌单的歌曲，歌曲信息统统保存在这一个表中。但是这个表只有tid（歌曲id）和track（歌曲信息），没有记录每个歌曲所属的歌单信息，我们需要使用sql查询通过左关联将web_playlist_track和web_track这两个表关联起来，导出我们需要的那一个歌单的全部信息。

import json
from os.path import join, splitext, exists, normpath
from os import getenv, listdir, makedirs
import shutil
from utils import *

# 指定执行模式
# 0:仅输出歌单歌曲的名称
# 1:从歌单中转移指定的数据库中存在的歌曲到指定位置
mode = 1

# 你的某个歌单的歌曲数量，用以确定获取哪个歌单的数据
# 如果有多个相同的歌单数量，取第一个
playlist_length = 102

# 指定的文件名称格式化字符串，用{0}代表歌曲名，{1}代表歌手名（已经处理了多个的情况），比如下面的例子代表
# ギターと孤独と蒼い惑星 - 結束バンド，其中{0}代表ギターと孤独と蒼い惑星，而{1}代表結束バンド
format_str = "{1} - {0}"

# 你的音乐数据库路径
my_musicbase_path = normpath(r"D:\PortableDir\music\musicbase")
# 你想要将歌曲保存路径
dst_path = normpath(r"C:\Users\fumen\Desktop\music")

##########################################################
cloudmusic_database_path = join(
    getenv("localappdata"), "Netease", "CloudMusic", "Library", "webdb.dat"
)


def get_playlist_length(playlist_str):
    # 根据cloudmusic_playlist_trackids.json获取歌曲数量
    playlist_info = json.loads(playlist_str)
    return len(playlist_info["trackIds"])


def get_playlist_json_by_length(playlist_length):
    # 根据playlist_length获取对应数量歌单的详细信息
    ress = execute_sql(
        cloudmusic_database_path,
        f"""select jsonStr from playlistTrackIds;""",
    )
    ls = []
    for res in ress:
        l = get_playlist_length(res[0])
        if l == playlist_length:
            return json.loads(res[0])
        else:
            ls.append(l)
    assert False, f"{playlist_length} not found in {ls}"


def extract_track_ids(playlist_info):
    tids = []
    for item in playlist_info["trackIds"]:
        tids.append(item["id"])
    return tids


def get_track_jsons(track_ids):
    # 根据track_ids获取歌曲信息json字符串
    id_values = ",".join(str(id) for id in track_ids)
    ress = execute_sql(
        cloudmusic_database_path,
        f"""select jsonStr from dbTrack WHERE id IN ({id_values});""",
    )
    return [res[0] for res in ress]


def extract_track_info(track_json):
    track_info = json.loads(track_json)
    info = music_info_data()
    info.music_name = track_info["name"]
    info.artist_name_list = [artist["name"] for artist in track_info["artists"]]
    info.album_name = track_info["album"]["albumName"]
    return info


def get_playlist_track_files(playlist_length):
    playlist_info = get_playlist_json_by_length(playlist_length)
    track_ids = extract_track_ids(playlist_info)
    track_jsons = get_track_jsons(track_ids)
    ress = []
    for track_json in track_jsons:
        ress.append(extract_track_info(track_json))
    return ress


def move_playlist_track_files(playlist_length, dst_path):
    """
    根据收藏列表的歌曲数量playlist_length确定一个列表,
    并在本地数据库中查询到对应文件并移动指目的位置dst_path
    """
    if not exists(my_musicbase_path):
        print(f"'{my_musicbase_path}' not exists")
        return
    if exists(dst_path):
        print(f"'{dst_path}' exists")
        return
    makedirs(dst_path, exist_ok=True)

    track_infos = get_playlist_track_files(playlist_length)
    my_music_files = listdir(my_musicbase_path)
    my_music_files_without_ext = [splitext(file)[0] for file in my_music_files]
    indexs = []
    not_founds = []
    for tf in track_infos:
        # 如果音乐数据库存在其他方式下载的文件，在此扩充判定...
        # 网易文件判定
        tf_str = tf.cloudmusic_str(format_str)
        if tf_str in my_music_files_without_ext:
            indexs.append(my_music_files_without_ext.index(tf_str))
        else:
            not_founds.append(tf_str)
    print(f"未找到:\n{'\n'.join(not_founds)}\n")
    for index in indexs:
        print(f"正在移动 {my_music_files[index]}")
        shutil.copy(
            join(my_musicbase_path, my_music_files[index]),
            join(dst_path, my_music_files[index]),
        )


if __name__ == "__main__":
    if mode == 0:
        for res in get_playlist_track_files(playlist_length):
            print(res.cloudmusic_str(format_str))
    elif mode == 1:
        move_playlist_track_files(playlist_length, dst_path)
    else:
        print("wrong mode number!")
