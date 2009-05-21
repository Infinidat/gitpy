#! /usr/bin/python
import unittest
import os
import random
from test_commits import CommittedRepositoryTest
from git.exceptions import MergeConflict

class TestBasicConflicts(CommittedRepositoryTest):
    def _changeFile(self, filename):
        with open(os.path.join(self.repo.path, filename), "ab") as f:
            print >>f, "new change", random.random()
        self.repo.add(filename)
        self.repo.commit("new change")
    def testBasicConflicts(self):
        commit = self.commitSomeChange()
        filename = commit.getChangedFiles()[0].filename
        master = self.repo.getCurrentBranch()
        branch1 = self.repo.createBranch('b1', master)
        self.repo.checkout(branch1)
        self._changeFile(filename)
        branch2 = self.repo.createBranch('b2', master)
        self.repo.checkout(branch2)
        self._changeFile(filename)
        try:
            self.repo.merge(branch1)
        except MergeConflict, e:
            pass
        else:
            self.fail()
if __name__ == '__main__':
    unittest.main()
