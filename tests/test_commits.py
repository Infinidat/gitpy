#! /usr/bin/python
import unittest
import random
import os
import time
from test_basic import ModifiedRepositoryTest

class CommittedRepositoryTest(ModifiedRepositoryTest):
    def setUp(self):
        super(CommittedRepositoryTest, self).setUp()
        self.repo.addAll()
        self.repo.commit(message="initial")
    def makeSomeChange(self):
        filename = random.choice(self.repo.getUnchangedFiles())
        full_filename = os.path.join(self.repo.path, filename)
        with open(full_filename, "ab") as f:
            print >>f, "some change at", time.asctime()
        return filename
    def commitSomeChange(self):
        filename = self.makeSomeChange()
        self.repo.add(filename)
        return self.repo.commit(message="new change")


class Committing(CommittedRepositoryTest):
    def testCommitFields(self):
        c = self.commitSomeChange()
        #todo: write this...
class TestReset(CommittedRepositoryTest):
    def testHardReset(self):
        c = self.commitSomeChange()
        parent = c.getParents()[0]
        self.assertTrue(parent != c)
        self.assertTrue(parent.hash != c.hash)
        for syntax in ("HEAD^", parent, "%s^" % (c,)):
            self.repo.resetHard(syntax)
            self.assertEquals(self.repo.getHead(), parent)
            self.assertNotEquals(self.repo.getHead(), c)
            self.repo.resetHard(c)
            self.assertEquals(self.repo.getHead(), c)
    def testSoftReset(self):
        c = self.commitSomeChange()
        modified_files = c.getChange()
        for syntax in ("HEAD^", c.getParents()[0], "%s^" % (c,)):
            self.repo.resetSoft(syntax)
            self.assertEquals(self.repo.getChangedFiles(), modified_files)
            self.repo.resetHard(c)


if __name__ == '__main__':
    unittest.main()
