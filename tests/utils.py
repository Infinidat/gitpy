import hashlib
import os
import time
import random
import shutil
import itertools
from gitpy import LocalRepository

_filename_gen = (os.path.join("/tmp", "temp___%s" % i) for i in itertools.count())

def get_temporary_location():
    for path in _filename_gen:
        if not os.path.exists(path):
            return os.path.realpath(path)

def delete_repository(repo):
    shutil.rmtree(repo.path)

def create_repo():
    returned = LocalRepository(get_temporary_location())
    returned.init()
    for i in range(10):
        filename = "file_%s.txt" % i
        full_filename = os.path.join(returned.path, filename)
        with open(full_filename, "wb") as f:
            print >>f, "initial content"
        returned.add(filename)
    returned.commit(message="initial")
    return returned

def commit_change(repo):
    filename = random.choice(repo.getUnchangedFiles())
    with open(os.path.join(repo.path, filename), "ab") as f:
        print >>f, "Change at", time.asctime()
    repo.add(filename)
    return repo.commit(message="auto change at %s" % time.asctime())

def get_repo_contents(repo):
    returned = {}
    path = repo.path
    if not path.endswith(os.sep):
        path += os.sep
    for dirpath, dirnames, filenames in os.walk(path):
        if '.git' in dirnames:
            dirnames.remove('.git')
        for filename in filenames:
            full_filename = os.path.join(dirpath, filename)
            returned[full_filename[len(path):]] = hashlib.sha512(open(full_filename, "rb").read()).hexdigest()
    return returned
