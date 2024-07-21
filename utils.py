import json
import logging
from os.path import join
import sys
from values import TEMP_DATA_PATH
from os.path import splitext, basename, join

# 配置日志记录器
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志输出格式
    filename="app.log",  # log日志输出的文件位置和文件名
    filemode="w",  # 文件的写入格式，w为重新写入文件，默认是追加
    format="%(asctime)s - %(name)s - %(levelname)-9s - "  # -8表示占位符，让输出左对齐，输出长度都为8位
    + "%(filename)-8s : %(lineno)s line - %(message)s",  # 日志输出的格式
    datefmt="%Y-%m-%d %H:%M:%S",  # 时间输出的格式
    encoding="utf-8",
)


def print_info(info):
    print(info)
    logging.info(info)


def print_error(error):
    print(error)
    logging.error(error)
    sys.exit(1)


def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False


def save_string(string, file_dir):
    with open(join(TEMP_DATA_PATH, file_dir), "w", encoding="utf-8") as f:
        f.write(string)


def pure_name(path):
    return splitext(basename(path))[0]
