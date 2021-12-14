from os.path import dirname, realpath, join


_root_dir = dirname(realpath(__file__))
_resources_dir = join(_root_dir, 'resources')


DB_PATH = join(_resources_dir, 'kkonni.db')
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
