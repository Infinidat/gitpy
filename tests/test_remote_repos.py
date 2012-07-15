#! /usr/bin/python
import unittest
import os
import commands
from utils import get_temporary_location
from gitpy import RemoteRepository
from gitpy.exceptions import NonexistentRefException

class RemoteRepositories(unittest.TestCase):
    def setUp(self):
        self.dirname = get_temporary_location()
        os.mkdir(self.dirname)
        status, output = commands.getstatusoutput("cd %s && git init && git commit -a -m init --allow-empty && git tag tag_name" % self.dirname)
        self.assertEqual(status, 0)
        status, init_hash = commands.getstatusoutput("cd %s && git rev-parse HEAD" % self.dirname)
        self.assertEqual(status, 0)
        self.initHash = init_hash.strip()
    def tearDown(self):
        status, _ = commands.getstatusoutput("rm -rf %s" % self.dirname)
        self.assertEqual(status, 0)
    def testRemoteRepository(self):
        remote_repo = RemoteRepository(self.dirname)
        branches = remote_repo.getBranches()
        self.assertEqual(set(branch.name for branch in branches),
                         set(['master']))
    def testRemoteRepositoryRefResolving(self):
        remote_repo = RemoteRepository(self.dirname)
        for ref_name in ('master', 'tag_name'):
            self.assertEquals(remote_repo._getCommitByRefName(ref_name).hash,
                              self.initHash)
        try:
            remote_repo._getCommitByRefName('nonexistent ref')
        except NonexistentRefException:
            pass # ok
        else:
            self.fail("Did not fail")
                

if __name__ == '__main__':
    unittest.main()
