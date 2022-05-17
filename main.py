import py_cui

try:
    from reader import reader
except:
    pass


class NFC:
    def uid():
        dict = {"UID": "FFF:FFF:FFF:FFF"}
        return dict["UID"]

    def data():
        array = ["01:\tDE AD BE EF"]
        return array


class GUI:
    def __init__(self, root: py_cui.PyCUI):
        self.root = root
        try:
            self.readerobj = reader.Reader()
            self.readerobj.start()
        except:
            self.root.set_title("Offline")
        # WIDGETS
        # data window
        self.top_left = self.root.add_text_block(
            "Data",
            0,
            0,
            column_span=4,
            row_span=6,
        )
        self.top_left.set_selectable(False)
        # scroll menu
        self.scroll_menu = self.root.add_scroll_menu(
            "Energy Sources",
            0,
            4,
            column_span=2,
            row_span=2,
        )
        self.scroll_menu_list = {
            "Energy Sources": [
                "Electrical",
                "Hydraulic",
                "Pneumatic",
                "Gravity",
                "Thermal",
                "Chemical",
                "Natural Gas",
                "Mechanical",
                "Water",
                "Steam",
            ],
        }
        self.scroll_menu.add_item_list(self.scroll_menu_list["Energy Sources"])
        self.scroll_menu.add_key_command(
            py_cui.keys.KEY_RIGHT_ARROW, self.scroll_menu_right
        )
        self.scroll_menu.add_key_command(py_cui.keys.KEY_ENTER, self.scroll_menu_right)
        self.scroll_menu.add_key_command(
            py_cui.keys.KEY_LEFT_ARROW, self.scroll_menu_left
        )
        self.root.set_on_draw_update_func(self.grab_latest)

    def scroll_menu_right(self):
        self.selection = self.scroll_menu.get_selected_item_index()
        branch = self.scroll_menu.get_title()
        if branch == "Energy Sources":
            self.scroll_menu.set_title("Confirm")
            self.scroll_menu.clear()
            self.scroll_menu.add_item_list(
                [
                    f"Assign card as {self.scroll_menu_list['Energy Sources'][self.selection]}",
                    "Go Back",
                ]
            )
        elif branch == "Confirm" and self.selection == 0:
            return
        else:
            self.scroll_menu_left()

    def scroll_menu_left(self):
        self.scroll_menu.set_title("Energy Sources")
        self.scroll_menu.clear()
        self.scroll_menu.add_item_list(self.scroll_menu_list["Energy Sources"])
        self.scroll_menu.set_selected_item_index(self.selection)

    def grab_latest(self):  # monster
        try:
            data = self.readerobj.latest_data
        except:
            data = []
        try:
            uid = self.readerobj.latest_uid
        except:
            uid = []
        data_text = ""
        for i, row in enumerate(data):
            row = " ".join(["{:02X}".format(x) for x in row])
            if row:
                data_text = data_text + "[{:2d}] ".format(i) + str(row) + "\n"

        self.top_left.set_title(uid)
        self.top_left.set_text(data_text)


root = py_cui.PyCUI(6, 6)
root.set_title(NFC.uid())
root.toggle_unicode_borders()
root.set_refresh_timeout(1)
wrapper = GUI(root)
root.start()
