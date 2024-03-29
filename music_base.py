import base64
import binascii
import glob
import json
from os import listdir, makedirs
from os.path import normpath, isdir, join, exists, splitext, basename
import shutil
import struct
from Crypto.Cipher import AES
from mutagen.flac import Picture, FLAC
from mutagen.id3 import ID3, APIC

# 你的网易云音乐下载保存路径
cloudmusic_musicbase_path = normpath(r"C:\Users\fumen\PersonalDir\music")
# 你想保存到的路径
my_musicbase_path = normpath(r"music")

##########################################################
cloudmusic_vipmusic_dir = "VipSongsDownload"


def check_jpeg_header(data):
    if len(data) >= 2 and data[0] == 0xFF and data[1] == 0xD8:
        return True
    return False


def set_album_art(image_data, file_path):

    if not check_jpeg_header(image_data):
        print(f"{basename(file_path)} 的图片元数据不是jpg格式!")
        return

    ext = splitext(file_path)[1][1:]

    if ext == "flac":
        picture = Picture()
        picture.type = 3  # 3 表示封面（Cover）
        picture.desc = "Front Cover"  # 图片描述
        picture.mime = "image/jpeg"  # 图片的MIME类型，根据实际情况设置
        picture.data = image_data
        flac = FLAC(file_path)
        flac.clear_pictures()  # 清除现有的图片数据
        flac.add_picture(picture)  # 添加新的图片数据
        flac.save()
    elif ext == "mp3":
        audio = ID3(file_path)
        apic = APIC(3, "image/jpeg", 3, "Front Cover", image_data)
        audio.clear()
        audio.add(apic)
        audio.save()
    else:
        print(f"unknown file type: {ext}")


def ncm2xxx(src, dst):

    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    unpad = lambda s: s[0 : -(s[-1] if type(s[-1]) == int else ord(s[-1]))]

    f = open(src, "rb")
    header = f.read(8)
    assert binascii.b2a_hex(header) == b"4354454e4644414d"

    f.seek(2, 1)
    key_length = f.read(4)
    key_length = struct.unpack("<I", bytes(key_length))[0]
    key_data = f.read(key_length)
    key_data_array = bytearray(key_data)
    for i in range(0, len(key_data_array)):
        key_data_array[i] ^= 0x64
    key_data = bytes(key_data_array)

    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]

    key_length = len(key_data)
    key_data = bytearray(key_data)
    key_box = bytearray(range(256))
    c = 0
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = key_box[i]
        c = (swap + last_byte + key_data[key_offset]) & 0xFF
        key_offset += 1
        if key_offset >= key_length:
            key_offset = 0
        key_box[i] = key_box[c]
        key_box[c] = swap
        last_byte = c

    meta_length = f.read(4)
    meta_length = struct.unpack("<I", bytes(meta_length))[0]
    meta_data = f.read(meta_length)
    meta_data_array = bytearray(meta_data)
    for i in range(0, len(meta_data_array)):
        meta_data_array[i] ^= 0x63
    meta_data = bytes(meta_data_array)
    meta_data = base64.b64decode(meta_data[22:])

    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode("utf-8")[6:]
    meta_data = json.loads(meta_data)

    crc32 = f.read(4)
    crc32 = struct.unpack("<I", bytes(crc32))[0]

    f.seek(5, 1)
    image_size = f.read(4)
    image_size = struct.unpack("<I", bytes(image_size))[0]
    image_data = f.read(image_size)

    m = open(dst + "." + meta_data["format"], "wb")
    chunk = bytearray()
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break
        for i in range(1, chunk_length + 1):
            j = i & 0xFF
            chunk[i - 1] ^= key_box[
                (key_box[j] + key_box[(key_box[j] + j) & 0xFF]) & 0xFF
            ]
        m.write(chunk)
    m.close()
    f.close()

    set_album_art(image_data, dst + "." + meta_data["format"])


def move_cloudmusic_musicbase():
    makedirs(my_musicbase_path, exist_ok=True)
    dirs = []
    for file in listdir(cloudmusic_musicbase_path):
        src_path = join(cloudmusic_musicbase_path, file)
        dst_path = join(my_musicbase_path, file)
        if exists(dst_path):
            print(f"已存在 {file}")
            continue
        if isdir(src_path):
            dirs.append(file)
        else:
            print(f"正在移动 {file}")
            shutil.copy(src_path, dst_path)

    if cloudmusic_vipmusic_dir in dirs:
        vip_musicbase_path = join(cloudmusic_musicbase_path, cloudmusic_vipmusic_dir)
        for file in listdir(vip_musicbase_path):
            if not file.endswith("ncm"):
                continue
            file_without_ext = splitext(file)[0]
            src_path = join(vip_musicbase_path, file)
            dst_path = join(my_musicbase_path, file_without_ext)

            if len(glob.glob(glob.escape(dst_path) + ".*")) > 0:
                print(f"已存在 {file}")
                continue
            print(f"正在移动 {file}")
            ncm2xxx(src_path, dst_path)


if __name__ == "__main__":
    move_cloudmusic_musicbase()
    # ncm2xxx(
    #     normpath(r"test\インタビュア - H△G.ncm"),
    #     normpath(r"test\インタビュア - H△G"),
    # )
