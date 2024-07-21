from os.path import normpath
import time
from cloud import CloudBase
from musicbase import MusicBase
from utils import print_info
from values import CLOUDMUSIC_DATABASE_PATH

print("开始执行脚本")
cloudmusic_path = normpath(r"C:\CloudMusic") # 网易云下载路径
musicbase_path = normpath(r"D:\音乐") # 音乐库路径
output_path = normpath(r"C:\PortableDir\musicbase") # 结果输出路径
playlist_count = 112 #歌单长度

# 通过网易云数据库求取歌曲名称列表
cloudmusic_db = CloudBase(CLOUDMUSIC_DATABASE_PATH)
names = cloudmusic_db.trackNamesByLength(playlist_count)
time.sleep(1)

# 合并新下载网易云音乐内容
musicBase = MusicBase(musicbase_path)
musicBase.mergeCloud(cloudmusic_path)

# 根据歌曲列表拷贝音乐文件
musicBase.outputMusic(output_path, names)
