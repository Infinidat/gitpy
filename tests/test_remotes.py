#! /usr/bin/python
import os
import unittest
from test_commits import CommittedRepositoryTest
from gitpy import LocalRepository
import utils

class RemoteTest(CommittedRepositoryTest):
    def testAddingRemotes(self):
        new_repo = LocalRepository(utils.get_temporary_location())
        new_repo.init()
        with open(os.path.join(new_repo.path, "some_file"), "w") as f:
            f.write("new file\n")
        new_repo.addAll()
        new_repo.commit(message="initial change")
        REMOTE_NAME = 'remote'
        remote = new_repo.addRemote(REMOTE_NAME, self.repo.path)
        self.assertEquals(remote.name, REMOTE_NAME)
        self.assertEquals(remote.url, self.repo.path)
        self.assertFalse(new_repo.containsCommit(self.repo.getHead()))
        remote.fetch()
        remote.prune()
        self.assertTrue(new_repo.containsCommit(self.repo.getHead()))
        branches = list(remote.getBranches())
        self.assertTrue(len(branches) > 0)
        for branch in branches:
            self.assertTrue(type(branch in new_repo.getHead()) is bool)

if __name__ == '__main__':
    unittest.main()
