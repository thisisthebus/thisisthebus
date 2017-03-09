import sys

from thisisthebus.settings.constants import FRONTEND_DIR

sys.path.append('..')


def get_frontend_apps_dir():
    return "%s/apps" % FRONTEND_DIR
