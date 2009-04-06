import os
import itertools

def get_temporary_location():
    for path in (os.path.join("/tmp", "temp___%s" % i) for i in itertools.count()):
        if not os.path.exists(path):
            return path
