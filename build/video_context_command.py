# This path stuff is nonsense.  TODO: Turn these into real projects.

import inspect, os, sys
this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
PROJECT_DIR = ('/').join(this_path.split('/')[:-1])
GIT_DIR = ('/').join(this_path.split('/')[:-2])
sys.path.append(PROJECT_DIR)
from thisisthebus.settings.constants import DATA_DIR, FRONTEND_DIR
sys.path.append("%s/thisisthesitebuilder" % GIT_DIR)
from thisisthesitebuilder.images import image_parser


if __name__ == "__main__":
    try:
        app_path = '/'.join(__file__.split('/')[:5])
        sys.path.append(app_path)
        image_parser.parse_video(sys.argv[1], DATA_DIR, FRONTEND_DIR)

    except Exception as e:
        import traceback

        traceback.print_exc()
        input("Press Enter to continue...")