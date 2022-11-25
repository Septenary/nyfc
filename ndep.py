import nfc, time


def on_startup(targets):
    started = time.asctime()
    print("Started: " + str(started))
    return targets


def on_discover(target):
    discovered = time.asctime()
    print("Discovered: " + str(discovered))
    return True


"""
When a Tag is found and activated, the on-connect callback function returning False means that 
the tag presence loop shall not be run but the nfc.tag.Tag object returned immediately. 
A more useful callback function could do something with the tag 
and return True for requesting a presence loop that makes clf.connect() return only after the tag is gone.
"""
# TODO: Add more useful callback function that returns True only after the tag is gone.


def on_connect(tag):
    connected = time.asctime()
    print("Connected: " + str(connected))
    return lambda tag: False


def on_release(tag):
    released = time.asctime()
    print("Connected: " + str(released))
    # The tag object may be used for cleanup actions but not for communication.
    return tag


rdwr_options = {
    # 'targets': ['212F', '424F'],
    "on-startup": on_startup,
    "on-discover": on_discover,
    "on-connect": on_connect,
}

with nfc.ContactlessFrontend("udp") as clf:
    print("Device found: " + str(clf))
    tag = clf.connect(rdwr=rdwr_options)
    if tag:
        print(tag)
        if tag.ndef:
            assert tag.ndef is not None and tag.ndef.length > 0
            # assert tag.ndef.records[0].type == 'urn:nfc:wkt:T'
            assert tag.ndef.has_changed is False
            print(tag.ndef.message.pretty())
            for record in tag.ndef.records:
                print(record)

"""
The tag.ndef.records attribute contains a list of NDEF Records decoded from tag.ndef.octets with the ndeflib package. 
Each record has common and type-specific methods and attributes for content access.
"""
# print(record.type + record.uri)
