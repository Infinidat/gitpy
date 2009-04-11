import os
import shutil
import itertools

_filename_gen = (os.path.join("/tmp", "temp___%s" % i) for i in itertools.count())

def get_temporary_location():
    for path in _filename_gen:
        if not os.path.exists(path):
            return path

def delete_repository(repo):
    shutil.rmtree(repo.path)

