"""Is a file really on this disk? On a Mac, a file that iCloud has offloaded still shows up in the folder but reading it waits for a download (minutes, or forever on a bad
connection). Such a file is flagged "dataless" by the system; the runs skip it for now and pick it up in a later run, once it has been downloaded."""
import os
SF_DATALESS = 0x40000000


def is_local(path):
    try:
        return not (getattr(os.stat(path), "st_flags", 0) & SF_DATALESS)
    except OSError:
        return False
