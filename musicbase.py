from os import listdir, makedirs, walk
import shutil
from ncm import ncm2xxx
from utils import print_error, print_info, pure_name, recursion_filepaths
from os.path import splitext, basename, exists, join, isfile


class MusicBase:
    def __init__(self, base_path):
        if not exists(base_path):
            print_error(f"musicbase_path: {base_path} not exists!")
        self.base_path = base_path

    def getPaths(self):
        file_list = []
        for root, _, files in walk(self.base_path):
            for file in files:
                file_path = join(root, file)
                if (
                    file_path.endswith("mp3")
                    or file_path.endswith("flac")
                    or file_path.endswith("ncm")
                ):
                    file_list.append(file_path)
        return file_list

    def getNames(self):
        music_names = [splitext(basename(x))[0] for x in self.getPaths()]
        return music_names

    def mergeCloud(self, cloudmusic_path):
        vip_path = join(cloudmusic_path, "VipSongsDownload")
        move_path = join(self.base_path, "网易云音乐")
        music_names = self.getNames()

        # 移动未加锁文件
        if not exists(cloudmusic_path):
            return
        for file in listdir(cloudmusic_path):
            file_path = join(cloudmusic_path, file)
            name = pure_name(file_path)
            if isfile(file_path):
                if name not in music_names:
                    shutil.copy(file_path, move_path)
                    print_info(f"成功复制 {name}")
                else:
                    print_info(f"已存在 {name}")

        # 移动加锁文件
        if not exists(vip_path):
            return
        for file in listdir(vip_path):
            file_path = join(vip_path, file)
            name = pure_name(file_path)
            if isfile(file_path):
                if name not in music_names:
                    ncm2xxx(file_path, join(move_path, name))
                    print_info(f"成功复制 {name}")
                else:
                    print_info(f"已存在 {name}")

    def outputMusic(self, output_path, track_names):
        """根据指定的歌曲列表名称，从指定的歌曲数据库中复制歌曲到指定的目标文件夹下

        Args:
        track_names (list[str]): 名称列表
        musicbase_path (str): 歌曲数据库路径
        output_path (str): 目标文件夹路径
        """
        print_info("尝试转移查询到的歌曲列表...")
        makedirs(output_path, exist_ok=True)
        music_paths = self.getPaths()
        music_names = self.getNames()
        exist_music_names = [splitext(x)[0] for x in listdir(output_path)]
        not_founds = []

        for track_name in track_names:
            if track_name in music_names:
                if track_name in exist_music_names:
                    print_info(f"已存在 {track_name}")
                    continue
                index = music_names.index(track_name)
                shutil.copy(music_paths[index], output_path)
                print_info(f"成功移动 {basename(music_paths[index])}")
            else:
                print_info(f"未找到 {track_name}")
                not_founds.append(track_name)

        print(f"\n歌曲共计数:{len(track_names)}")
        print(f"歌曲找到数:{len(track_names)-len(not_founds)}")
        print(f"\n未找到:\n{'\n'.join(not_founds)}")
