#! /usr/bin/python
import unittest
import os
import commands
from utils import get_temporary_location
from pygit import LocalRepository
from pygit.exceptions import GitException

class EmptyRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.dirname = get_temporary_location()
        self.repo = LocalRepository(self.dirname)
        self.assertFalse(os.path.exists(self.dirname))
    def tearDown(self):
        if os.path.exists(self.dirname):
            status, _ = commands.getstatusoutput("rm -rf %s" % self.dirname)
            self.assertEqual(status, 0)

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

unittest.main()
