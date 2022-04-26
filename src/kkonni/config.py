from os.path import dirname, realpath, join

_root_dir = dirname(realpath(__file__))
_resources_dir = join(_root_dir, 'resources')


# -- application configurations -- #

# path to the sqlite3 database file
DB_PATH = join(_resources_dir, 'kkonni.sqlite3')
# path to the static image directory
IMAGE_DIR = join(_root_dir, 'static', 'image')
# secret key!
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

# more reliable cookies
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True

# -- user preferences -- #

# standard date formatting
DATE_FORMAT = "%d.%m.%Y"
