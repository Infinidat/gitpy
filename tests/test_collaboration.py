#! /usr/bin/python
import os
import unittest
import utils
from git import LocalRepository
from git import RemoteRepository
from git.exceptions import NonexistentRefException

class CollaborationTest(unittest.TestCase):
    def setUp(self):
        path1 = utils.get_temporary_location()
        path2 = utils.get_temporary_location()
        path2 = os.path.join(path2, "repo")
        self.repo1 = LocalRepository(path1)
        self.repo1.init()
        for i in range(10):
            with open(os.path.join(self.repo1.path, "file_%s.txt" % i), "wb") as output:
                print >>output, "This is file", i
        self.repo1.addAll()
        self.repo1.commit(message="init")
        self.repo2 = LocalRepository(path2)
        self.repo2.clone(self.repo1)
        self.assertTrue(os.path.isdir(self.repo2.path))
    def tearDown(self):
        utils.delete_repository(self.repo1)
        utils.delete_repository(self.repo2)

    def testRemotePushBranches(self):
        b = self.repo2.createBranch("branch")
        self.repo1.createBranch('remote_branch')
        self.repo2.fetch()
        remote_branch = self.repo2.getRemoteByName('origin').getBranchByName('remote_branch')
        b.setRemoteBranch(remote_branch)
        self.assertEquals(b.getRemoteBranch(), remote_branch)
        b.setRemoteBranch(None)
        self.assertEquals(b.getRemoteBranch(), None)
    def testCollaboration(self):
        new_file_base_name = "new_file.txt"
        new_filename = os.path.join(self.repo1.path, new_file_base_name)
        with open(new_filename, "wb") as f:
            print >> f, "hello there!"
        self.assertTrue(new_file_base_name in self.repo1.getUntrackedFiles())
        self.repo1.addAll()
        self.assertTrue(any(f.filename == new_file_base_name for f in self.repo1.getStagedFiles()))
        c = self.repo1.commit(message="add file")
        self.assertFalse(os.path.exists(os.path.join(self.repo2.path, new_file_base_name)))
        self.repo2.pull()
        self.assertTrue(os.path.exists(os.path.join(self.repo2.path, new_file_base_name)))
        self.assertTrue(c in self.repo2)
    def testRemoteBranchDeletion(self):
        self.repo1.createBranch("testme")
        self.repo2.fetch()
        remote_branch = self.repo2.getRemoteByName("origin").getBranchByName("testme")
        self.assertEquals(remote_branch.getHead(), self.repo1.getBranchByName("testme").getHead())
        remote_branch.delete()
        try:
            self.repo1.getBranchByName("testme")
        except NonexistentRefException:
            pass
        else:
            self.fail("Did not fail!")
        
if __name__ == '__main__':
    unittest.main()
