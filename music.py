from os import listdir, makedirs
from os.path import splitext, basename, exists, join, normpath
import shutil
from cloud import CloudBase
from ncm import ncm2xxx
from utils import print_info, recursion_filepaths, print_error
from values import CLOUDMUSIC_DATABASE_PATH, TEMP_DATA_PATH


def copy_music_by_names(track_names, musicbase_path, output_path):
    music_paths = recursion_filepaths(musicbase_path)
    music_names = [splitext(basename(x))[0] for x in music_paths]
    exist_music_names = [splitext(x)[0] for x in listdir(output_path)]

    not_founds = []
    for track_name in track_names:
        if track_name in music_names:
            if track_name in exist_music_names:
                print_info(f"已存在 {track_name}")
                continue
            index = music_names.index(track_name)
            print_info(f"正在移动 {basename(music_paths[index])}")
            if splitext(music_paths[index])[1] == ".ncm":
                ncm2xxx(music_paths[index], join(output_path, track_name))
            else:
                shutil.copy(music_paths[index], output_path)
        else:
            print_info(f"未找到 {track_name}")
            not_founds.append(track_name)
    print(f"\n歌曲共计数:{len(track_names)}")
    print(f"歌曲找到数:{len(track_names)-len(not_founds)}")
    print(f"\n未找到:\n{'\n'.join(not_founds)}")


if __name__ == "__main__":
    cloudmusic_path = normpath(r"D:\CloudMusic")
    output_path = normpath(r"D:\PortableDir\music")
    playlist_count = 105

    cloudmusic_db = CloudBase(CLOUDMUSIC_DATABASE_PATH)
    makedirs(TEMP_DATA_PATH, exist_ok=True)
    cloudmusic_db.extract_database_info(cloudmusic_db.save_table_info)

    if not exists(cloudmusic_path):
        print_error(f"cloudmusic_path: {cloudmusic_path} not exists!")
    makedirs(output_path, exist_ok=True)
    copy_music_by_names(
        cloudmusic_db.trackNamesByLength(playlist_count), cloudmusic_path, output_path
    )
