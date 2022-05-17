from pirc522 import RFID
import py_cui
import threading

data_window_title = "Data | UID ___:___:___:___:___"


class Window:
    def __init__(self, root: py_cui.PyCUI):
        self.root = root
        # widgets
        #  data window
        self.root.set_on_draw_update_func(self.grab_latest)
        self.data_window = self.root.add_text_block(
            data_window_title, 0, 0, column_span=2, row_span=4
        )
        self.data_window.set_selectable(False)
        #  scroll menu
        self.scroll_menu = self.root.add_scroll_menu("Format", 3, 3)
        self.scroll_menu.add_item_list(["Hexadecimal", "Decimal", "Reader"])
        self.scroll_menu.set_on_selection_change_event(
            self.grab_latest
        )  # amazing functionality
        # instance reader object
        self.read_obj = Reader()
        self.read_obj.start()

    def grab_latest(self):
        menu_index = self.scroll_menu.get_selected_item_index()

        # update window title
        data_title = data_window_title[0:11] + self.read_obj.latest_uid
        menu_titles = [" | HEX", " | DEC", " | RDR"]
        data_title = data_title + menu_titles[menu_index]

        data_raw = self.read_obj.latest_data
        data_text = ""

        for i, row in enumerate(data_raw):
            if menu_index == 0:
                row = " ".join(["{:02X}".format(x) for x in row])
            elif menu_index == 1:
                row = " ".join(["{:03d}".format(x) for x in row])
            elif menu_index == 2:
                row = " ".join(["{:}".format(x) for x in row])
            if row:
                data_text = data_text + "[{:2d}] ".format(i) + str(row) + "\n"

        self.data_window.set_title(data_title)
        self.data_window.set_text(data_text)


class Reader(threading.Thread):
    daemon = True
    latest_uid = data_window_title[11:30]
    latest_data = [[]]

    def __init__(self):
        super().__init__()
        self.rfid = RFID()
        self.util = self.rfid.util()

    def run(self):
        rfid = self.rfid

        # pirc522 read loop
        while True:
            rfid.wait_for_tag()

            uid, data = self.read_card()

            if data:
                self.latest_data = data
            self.latest_uid = uid

    def read_card(self):
        rfid = self.rfid
        uid, data = data_window_title[11:30], []

        (error, tag_type) = rfid.request()
        if not error:
            (error, uid_raw) = rfid.anticoll()
            if not error:
                uid = ":".join("{:03d}".format(a) for a in uid_raw)
                if not rfid.select_tag(uid_raw):
                    for ii in range(0, 64):
                        if not rfid.card_auth(
                            rfid.auth_a,
                            ii,
                            [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
                            uid_raw,
                        ):
                            data.append(rfid.read(ii)[1])
                    rfid.stop_crypto()

        if len(data) != 64:
            data = []
        return uid, data


def main():
    root = py_cui.PyCUI(4, 4)
    root.toggle_unicode_borders()
    root.set_refresh_timeout(1)
    root.set_title("RFID Util")
    wrapper = Window(root)
    root.start()


main()
