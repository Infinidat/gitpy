#! /usr/bin/python
import os
import unittest
import utils
from pygit import LocalRepository

class CollaborationTest(unittest.TestCase):
    def setUp(self):
        path1 = utils.get_temporary_location()
        path2 = utils.get_temporary_location()
        path2 = os.path.join(path2, "repo")
        self.repo1 = LocalRepository(path1)
        self.repo1.init()
        for i in range(10):
            with open(os.path.join(self.repo1.path, "file_%s.txt" % i), "wb") as output:
                print >>output, "This is file", i
        self.repo1.addAll()
        self.repo1.commit(message="init")
        self.repo2 = LocalRepository(path2)
        self.repo2.clone(self.repo1)
        self.assertTrue(os.path.isdir(self.repo2.path))
    def tearDown(self):
        utils.delete_repository(self.repo1)
        utils.delete_repository(self.repo2)

    def testCollaboration(self):
        new_file_base_name = "new_file.txt"
        new_filename = os.path.join(self.repo1.path, new_file_base_name)
        with open(new_filename, "wb") as f:
            print >> f, "hello there!"
        self.assertTrue(new_file_base_name in self.repo1.getUntrackedFiles())
        self.repo1.addAll()
        self.assertTrue(new_file_base_name in self.repo1.getStagedFiles())
        c = self.repo1.commit(message="add file")
        self.assertFalse(os.path.exists(os.path.join(self.repo2.path, new_file_base_name)))
        self.repo2.pull()
        self.assertTrue(os.path.exists(os.path.join(self.repo2.path, new_file_base_name)))
        self.assertTrue(c in self.repo2)
        
if __name__ == '__main__':
    unittest.main()
