#! /usr/bin/python
import unittest
import os
import commands
from utils import get_temporary_location
from pygit import LocalRepository
from pygit.exceptions import GitException

class BasicRepositories(unittest.TestCase):
    def setUp(self):
        self.dirname = get_temporary_location()
        self.repo = LocalRepository(self.dirname)
        self.assertFalse(os.path.exists(self.dirname))
    def tearDown(self):
        if os.path.exists(self.dirname):
            status, _ = commands.getstatusoutput("rm -rf %s" % self.dirname)
            self.assertEqual(status, 0)
    def testRepositoryInit(self):
        self.repo.init()
        self.failUnless(os.path.isdir(self.dirname))
        self.failUnless(os.path.isdir(os.path.join(self.dirname, ".git")))
    def testRepositoryInitWhenExists(self):
        os.mkdir(self.dirname)
        self.repo.init()
        self.failUnless(os.path.isdir(self.dirname))
        self.failUnless(os.path.isdir(os.path.join(self.dirname, ".git")))

unittest.main()
