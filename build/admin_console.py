

from ensure_build_path import add_project_dir_to_path, BUILD_PATH

add_project_dir_to_path()

if __name__ == "__main__":
    import django
    django.setup()

import os

import json

from site_builders import complete_build, get_hashes
from thisisthebus.where.build import process_places
from thisisthebus.where.location import new_location

os.environ['TERM'] = 'xterm'
from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem


class MainMenu(CursesMenu):

    @property
    def currently_active_menu(self):
        return self._currently_active_menu

    @currently_active_menu.setter
    def currently_active_menu(self, value):
        self._currently_active_menu = value


def main_menu():
    hashes = get_hashes()

    with open("%s/last_build.json" % BUILD_PATH, "r") as f:
        most_recent_hashes = json.loads(f.read())

    same_data = "(d)" if hashes['data'] != most_recent_hashes['data'] else ""
    same_app = "(a)" if hashes['app'] != most_recent_hashes['app'] else ""

    selection_menu = MainMenu()
    selection_menu.append_item(FunctionItem("New Location", new_location))
    # selection_menu.append_item(FunctionItem("Process Places", process_places, kwargs={"wait_at_end":True}))
    selection_menu.append_item(FunctionItem("Build Entire Site %s %s" % (same_data, same_app), complete_build, kwargs={"django_setup":True}))
    selection_menu.show()

if __name__ == "__main__":
    main_menu()