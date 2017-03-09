import inspect, os

frame = inspect.getfile(inspect.currentframe())
exec_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

PROJECT_DIR = ('/').join(exec_path.split('/')[:-2])

FRONTEND_DIR = "%s/frontend" % PROJECT_DIR
DATA_DIR = "%s/data" % PROJECT_DIR
APP_DIR = "%s/thisisthebus" % PROJECT_DIR