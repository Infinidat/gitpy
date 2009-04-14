#! /usr/bin/python
import unittest
import os
import commands
from utils import get_temporary_location
from utils import delete_repository
from git import LocalRepository
from git.exceptions import GitException

class EmptyRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.dirname = get_temporary_location()
        self.repo = LocalRepository(self.dirname)
        self.assertFalse(os.path.exists(self.dirname))
    def tearDown(self):
        if os.path.exists(self.dirname):
            delete_repository(self.repo)

class BasicRepositories(EmptyRepositoryTest):
    def testRepositoryInit(self):
        self.repo.init()
        self.failUnless(os.path.isdir(self.dirname))
        self.failUnless(os.path.isdir(os.path.join(self.dirname, ".git")))
    def testRepositoryInitWhenExists(self):
        os.mkdir(self.dirname)
        self.repo.init()
        self.failUnless(os.path.isdir(self.dirname))
        self.failUnless(os.path.isdir(os.path.join(self.dirname, ".git")))

class ModifiedRepositoryTest(EmptyRepositoryTest):
    FILENAME = "test.txt"
    def setUp(self):
        super(ModifiedRepositoryTest, self).setUp()
        self.repo.init()
        with open(os.path.join(self.repo.path, self.FILENAME), "wb") as f:
            print >>f, "Hey!"

class ModifiedRepositories(ModifiedRepositoryTest):
    def testStatus(self):
        untracked = self.repo.getUntrackedFiles()
        self.assertEquals(untracked, [self.FILENAME])
    def testAdding(self):
        untracked_files = self.repo.getUntrackedFiles()
        for u in untracked_files:
            self.repo.add(u)
        self.assertEquals(self.repo.getStagedFiles(), untracked_files)
    def testCommitting(self):
        self.repo.addAll()
        self.assertNotEquals(self.repo.getStagedFiles(), [])
        c = self.repo.commit(message="test commit")

if __name__ == '__main__':
    unittest.main()
