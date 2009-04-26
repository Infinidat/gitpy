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
    def commitSomeChange(self, name="new change"):
        previous = self.repo.getHead()
        filename = self.makeSomeChange()
        self.repo.add(filename)
        returned =  self.repo.commit(message=name)
        self.assertNotEquals(self.repo.getHead(), previous)
        return returned


class Committing(CommittedRepositoryTest):
    def testCommitFields(self):
        c = self.commitSomeChange()
        c.getAuthorName()
        c.getAuthorEmail()
        c.getDate()
        c.getSubject()
        c.getMessageBody()

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

class TestMergeBase(CommittedRepositoryTest):
    def testMergeBase(self):
        c1 = self.commitSomeChange("c1")
        c2 = self.commitSomeChange("c2")
        self.assertEquals(c1 & c2, c1)
        self.assertEquals(self.repo.getMergeBase(c1, c2), c1)
        self.repo.resetHard(c1.getParents()[0])
        c3 = self.commitSomeChange("c3")
        self.assertEquals(c1.getParents(), c3.getParents())
        self.assertEquals(c3 & c2, c3.getParents()[0])
        self.assertTrue(c3.getParents()[0] in c3)
        self.assertTrue(c1 in c2)
        self.assertFalse(c2 in c3)
        self.assertFalse(c3 in c2)

if __name__ == '__main__':
    unittest.main()
