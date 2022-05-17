from pirc522 import RFID
import threading


class Reader(threading.Thread): 
    daemon = True
    latest_uid = []
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
        uid, data = [], []
        (error, tag_type) = rfid.request()
        if not error:
            (error, uid_raw) = rfid.anticoll()
            if not error:
                uid = ':'.join('{:03d}'.format(a) for a in uid_raw)
                if not rfid.select_tag(uid_raw):
                    for ii in range(0, 64):
                        if not rfid.card_auth(rfid.auth_a, ii, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid_raw):
                            data.append(rfid.read(ii)[1])
                    rfid.stop_crypto()

        if len(data) != 64:
            data = []
        return uid, data
