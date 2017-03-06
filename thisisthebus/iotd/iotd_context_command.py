import sys

if __name__ == "__main__":
    try:
        app_path = '/'.join(__file__.split('/')[:5])
        sys.path.append(app_path)
        from iotd_parser import parse_iotd
        parse_iotd(sys.argv[1])

    except Exception as e:
        import traceback

        traceback.print_exc()
        input("Press Enter to continue...")