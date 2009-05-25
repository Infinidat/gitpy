#! /usr/bin/python
import os
import unittest
from test_commits import CommittedRepositoryTest

class TestStashes(CommittedRepositoryTest):
    def testStashing(self):
        filename = os.path.join(self.repo.path, self.makeSomeChange())
        changed_contents = open(filename, "rb").read()
        self.repo.saveStash()
        self.assertNotEquals(open(filename, "rb").read(), changed_contents)
        self.repo.popStash()
        self.assertEquals(open(filename, "rb").read(), changed_contents)
        

if __name__ == '__main__':
    unittest.main()
