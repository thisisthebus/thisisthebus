import sys
# from ..settings import constants
sys.path.append("/home/hubcraft/git/thisisthebus")
from thisisthebus.settings.constants import DATA_DIR, FRONTEND_DIR

sys.path.append("/home/hubcraft/git/thisisthesitebuilder")
from thisisthesitebuilder.images import iotd_parser


if __name__ == "__main__":
    try:
        app_path = '/'.join(__file__.split('/')[:5])
        sys.path.append(app_path)
        iotd_parser.parse_iotd(sys.argv[1], DATA_DIR, FRONTEND_DIR)

    except Exception as e:
        import traceback

        traceback.print_exc()
        input("Press Enter to continue...")