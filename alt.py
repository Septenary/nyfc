import collections
import json
import py_cui
from collections import deque
import time

try:
    from reader import reader
except:
    print("Offline Mode. Are you on dev?")

__version__ = "0.0.4"


class altManager:
    def __init__(self, root: py_cui.PyCUI):
        """
        root: root of py_cui window
        object_buffer: active json object

        """
        self.root = root
        self.object_buffer = {
            "physical": {
                "machine": "0",
                "energy source": "None",
                "point": "0",
            },
            "ownership": {
                "company": "Acme Inc.",
                "contact": "+1800555555",
            },
            "time": {
                "first": "1653000000",
                "recent": "1653000000",
            },
        }
        self.energy_source = {
            "Electrical": py_cui.YELLOW_ON_BLACK,
            "Hydraulic": py_cui.YELLOW_ON_BLACK,
            "Pneumatic": py_cui.YELLOW_ON_BLACK,
            "Gravity": py_cui.MAGENTA_ON_BLACK,
            "Thermal": py_cui.MAGENTA_ON_BLACK,
            "Mechanical": py_cui.MAGENTA_ON_BLACK,
            "Chemical": py_cui.GREEN_ON_BLACK,
            "Natural Gas": py_cui.GREEN_ON_BLACK,
            "Water": py_cui.CYAN_ON_BLACK,
            "Steam": py_cui.CYAN_ON_BLACK,
        }
        self.recent_typed = collections.deque(maxlen=12)
        # WIDGETS
        self.so_menu = self.root.add_scroll_menu(
            "Set Object",
            0,
            0,
            row_span=5,
            column_span=3,
        )
        self.eo_menu = self.root.add_scroll_menu(
            "Edit Object",
            0,
            3,
            row_span=5,
            column_span=3,
        )
        self.vo_menu = self.root.add_block_label(
            "Object",
            0,
            6,
            row_span=2,
            column_span=6,
            pady=-1,
        )
        self.wo_menu = self.root.add_button(
            "Write to Disk",
            5,
            0,
            column_span=6,
            command=self.wo_object,
        )
        self.wi_menu = self.root.add_button(
            "Read from Disk",
            6,
            0,
            column_span=6,
            command=self.wi_object,
        )
        # KEYS
        self.so_menu.add_key_command(py_cui.keys.KEY_LEFT_ARROW, self.root.lose_focus)
        self.so_menu.add_key_command(py_cui.keys.KEY_RIGHT_ARROW, self.edit_object)
        self.eo_menu.add_key_command(py_cui.keys.KEY_LEFT_ARROW, self.set_object)
        self.eo_menu.add_key_command(py_cui.keys.KEY_RIGHT_ARROW, self.write_object)
        self.wo_menu.add_key_command(py_cui.keys.KEY_ENTER, self.wo_object)
        self.wi_menu.add_key_command(py_cui.keys.KEY_ENTER, self.wi_object)
        # HELP TEXT
        self.so_menu.set_help_text(
            "Select field to edit. ⇅ and ⇄ to navigate. Esc to exit."
        )
        self.eo_menu.set_help_text(
            "Select edit to stage. Use ⇅ and ⇄ to navigate. Esc to cancel."
        )
        # COLORS
        for ii in self.energy_source.items():
            self.vo_menu.add_text_color_rule(ii[0], ii[1], "contains", "regex")
            self.eo_menu.add_text_color_rule(ii[0], ii[1], "contains", "regex")
        self.so_menu.add_text_color_rule(
            "$",
            py_cui.WHITE_ON_BLACK,
            "notstartswith",
            selected_color=py_cui.BLACK_ON_WHITE,
        )
        self.eo_menu.add_text_color_rule(
            "Text Input", py_cui.GREEN_ON_BLACK, "contains"
        )
        self.wo_menu.set_color(1)
        self.wi_menu.set_color(1)
        # WIDGETS
        self.vo_menu.toggle_border()
        self.vo_menu.set_selectable(False)
        self.set_object()
        self.edit_object()
        self.view_object()
        self.root.lose_focus()
        # TODO: remove
        self.nfc_text = self.root.add_text_block(
            "",
            3,
            6,
            row_span=2,
            column_span=6,
            pady=-2,
        )
        self.nfc_data()

    def set_object(self):
        self.root.move_focus(self.so_menu)
        index = self.so_menu.get_selected_item_index()
        text = []
        for _, ii in self.object_buffer.items():
            text += ii
        self.so_menu.clear()
        try:
            self.so_menu.set_selected_item_index(index)
        except:
            pass
        self.so_menu.add_item_list(text)

    def edit_object(self):
        self.root.move_focus(self.eo_menu)
        text = self.so_menu.get_item_list()[self.so_menu.get_selected_item_index()]
        self.eo_menu.clear()
        if text == "energy source":
            self.eo_menu.add_item_list(self.energy_source.keys())
        else:
            # Suggestions and recents
            if text == "first" or text == "recent":
                self.eo_menu.add_item_list([str(round(time.time()))])
            self.eo_menu.add_item_list(["Text Input"] + list(self.recent_typed)[::-1])
            if text == "machine" or text == "point":
                self.eo_menu.add_item_list(list(range(1, 13)))
            if text == "company":
                self.eo_menu.add_item("Acme Inc.")
            if text == "contact":
                self.eo_menu.add_item("+")

    def view_object(self):
        text = ""
        for _, ii in self.object_buffer.items():
            for jj in ii:
                text += f"{str(jj)+':' : <18}{str(ii[jj]) : <24}\n"
        self.vo_menu.set_title("Object Information\n" + text)

    def write_object(self, *arg):
        so_attr = self.so_menu.get_item_list()[self.so_menu.get_selected_item_index()]
        eo_attr = self.eo_menu.get_item_list()[self.eo_menu.get_selected_item_index()]
        for _, ii in self.object_buffer.items():
            if so_attr in ii.keys():
                if eo_attr != "Text Input":
                    ii[so_attr] = self.eo_menu.get_item_list()[
                        self.eo_menu.get_selected_item_index()
                    ]
                    break
                elif not arg:
                    self.root.show_text_box_popup("attr", self.write_object)
                else:
                    arg = str(arg[0])
                    ii[so_attr] = arg
                    self.recent_typed.append(arg)
                    self.edit_object()
        self.view_object()

    def wo_object(self):
        try:
            with open("object_file.json", "w") as write_file:
                json.dump(self.object_buffer, write_file)
        except:
            self.root.show_warning_popup("Failed", "Write failed")
        else:
            self.root.show_message_popup("Success", "Write sucessful")

    def wi_object(self):
        try:
            with open("object_file.json", "r") as read_file:
                self.object_buffer = json.load(read_file)
        except:
            self.root.show_error_popup("Failed", "Read failed")
        else:
            self.root.show_message_popup("Success", "Read sucessful")
            self.view_object()

    # TODO: Remove
    def nfc_data(self):
        data = ""
        try:
            readerobj = reader.Reader()
            readerobj.start()
            for i, row in enumerate(data):
                row = " ".join(["{:02X}".format(x) for x in row])
                if row:
                    data = data + "[{:2d}] ".format(i) + str(row) + "\n"
        except:
            uid = "OFFLINE"
        self.nfc_text.set_title(uid)
        self.nfc_text.set_text(data)


root = py_cui.PyCUI(12, 12)
root.toggle_unicode_borders()
root.set_title("nyfc " + __version__)
root.set_refresh_timeout(0.25)  # performance?
wrapper = altManager(root)
root.start()
