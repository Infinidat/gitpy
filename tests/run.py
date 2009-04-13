#! /usr/bin/python
import os
import sys
import subprocess

import_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if __name__ == '__main__':
    failed = []
    for dirpath, _, filenames in os.walk(os.path.dirname(__file__)):
        for filename in filenames:
            if not filename.startswith("test_"):
                continue
            if not filename.endswith(".py"):
                continue
            filename = os.path.join(dirpath, filename)
            print filename, "..."
            sys.stdout.flush()
            p = subprocess.Popen(filename, env=dict(PYTHONPATH=import_path))
            p.wait()
            if p.returncode != 0:
                print "\tFailed!"
                failed.append(filename)
            else:
                print "\tOK!"
    if failed:
        print "*" * 80
        print "* SOME TESTS FAILED:"
        for f in failed:
            print "*", f
        print "*" * 80
