#! /usr/bin/python
import unittest
import os
import commands
from utils import get_temporary_location
from utils import delete_repository
from gitpy import LocalRepository
from gitpy import find_repository
from gitpy.exceptions import GitException

class EmptyRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.dirname = get_temporary_location()
        self.repo = LocalRepository(self.dirname)
        self.assertFalse(os.path.exists(self.dirname))
        self.assertFalse(self.repo.isValid())
    def tearDown(self):
        if os.path.exists(self.dirname):
            delete_repository(self.repo)

class BasicRepositories(EmptyRepositoryTest):
    def testRepositoryInit(self):
        self.repo.init()
        self.assertTrue(self.repo.isValid())
        self.failUnless(os.path.isdir(self.dirname))
        self.failUnless(os.path.isdir(os.path.join(self.dirname, ".git")))
    def testConfiguration(self):
        self.repo.init()
        self.repo.config.setParameter('a.b.c', 2)
        self.assertEquals(self.repo.config.getParameter('a.b.c'), '2')
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
        self.assertFalse(self.repo.isWorkingDirectoryClean())

class ModifiedRepositories(ModifiedRepositoryTest):
    def testStatus(self):
        untracked = self.repo.getUntrackedFiles()
        self.assertEquals(untracked, [self.FILENAME])
    def testAdding(self):
        untracked_files = self.repo.getUntrackedFiles()
        for u in untracked_files:
            self.repo.add(u)
        self.assertEquals(self.repo.getStagedFiles(), untracked_files)
        self.assertFalse(self.repo.isWorkingDirectoryClean())
    def testCommitting(self):
        self.repo.addAll()
        self.assertNotEquals(self.repo.getStagedFiles(), [])
        c = self.repo.commit(message="test commit")
        self.assertTrue(self.repo.isWorkingDirectoryClean())
        self.assertEquals(self.repo.getStagedFiles(), [])

class CleaningUntrackedFiles(ModifiedRepositoryTest):
    def _clean(self):
        self.repo.cleanUntrackedFiles()
        self.failIf(self.repo.getUntrackedFiles())
    def testCleaningUpUntrackedFiles(self):
        with open(os.path.join(self.repo.path, "dirty_file"), "wb") as f:
            print >> f, "data"
        self.failUnless(self.repo.getUntrackedFiles())
        self._clean()
        #check directory cleanups
        dirpath = os.path.join(self.repo.path, "unused_directory") 
        os.mkdir(dirpath)
        self._clean()
        self.failIf(os.path.exists(dirpath))

class TestAPI(ModifiedRepositoryTest):
    def test_find_repository(self):
        prev_path = os.path.realpath(".")
        subpath = os.path.join(self.repo.path, "a", "b", "c")
        os.makedirs(subpath)
        os.chdir(subpath)
        try:
            repo = find_repository()
        finally:
            os.chdir(prev_path)
        self.failUnless(repo.path == self.repo.path)

if __name__ == '__main__':
    unittest.main()
