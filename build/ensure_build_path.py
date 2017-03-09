import inspect, os, sys

BUILD_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PROJECT_DIR = ('/').join(BUILD_PATH.split('/')[:-1])

def add_project_dir_to_path():

    sys.path.append(PROJECT_DIR)