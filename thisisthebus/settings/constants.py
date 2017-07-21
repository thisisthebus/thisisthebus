import inspect, os

frame = inspect.getfile(inspect.currentframe())
exec_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

PROJECT_DIR = ('/').join(exec_path.split('/')[:-2])
PYTHON_APP_DIR = "%s/thisisthebus" % PROJECT_DIR

FRONTEND_DIR = "%s/frontend" % PROJECT_DIR
FRONTEND_APPS_DIR = "%s/apps" % FRONTEND_DIR

DATA_DIR = "%s/data" % PROJECT_DIR
EXPERIENCE_DATA_DIR = "%s/authored/experiences" % DATA_DIR

TIMEZONE_UTC_OFFSET = "-05"