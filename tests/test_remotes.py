#! /usr/bin/python
import unittest
from test_commits import CommittedRepositoryTest
from git import LocalRepository
import utils

class RemoteTest(CommittedRepositoryTest):
    def testAddingRemotes(self):
        new_repo = LocalRepository(utils.get_temporary_location())
        new_repo.init()
        REMOTE_NAME = 'remote'
        remote = new_repo.addRemote(REMOTE_NAME, self.repo.path)
        self.assertEquals(remote.name, REMOTE_NAME)
        self.assertEquals(remote.url, self.repo.path)
        self.assertFalse(new_repo.containsCommit(self.repo.getHead()))
        remote.fetch()
        self.assertTrue(new_repo.containsCommit(self.repo.getHead()))

if __name__ == '__main__':
    unittest.main()
