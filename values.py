from os import getenv
from os.path import join

TEMP_DATA_PATH = "data"
CLOUDMUSIC_DATABASE_PATH = join(
    getenv("localappdata"), "Netease", "CloudMusic", "Library", "webdb.dat"
)
