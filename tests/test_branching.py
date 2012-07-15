#! /usr/bin/python
import os
import unittest
import gitpy
from gitpy.branch import LocalBranchAlias
from test_commits import CommittedRepositoryTest

class TestBranching(CommittedRepositoryTest):
    def testBranching(self):
        branch_name = 'some_branch'
        branch = self.repo.createBranch(branch_name)
        self.assertTrue(branch in self.repo.getBranches())
        self.assertEquals(branch.name, branch_name)
        self.assertEquals(branch.getHead(), self.repo.getHead())
        return branch
    def testBranchDeletion(self):
        branch = self.testBranching()
        branch.delete()
    def testBranchingAndCommitting(self):
        branch = self.testBranching()
        new_commit = self.commitSomeChange()
        self.assertEquals(self.repo.getCommits(branch, self.repo.getCurrentBranch()), [new_commit])
        self.assertNotEquals(self.repo.getHead(), branch.getHead())
        return branch
    def testNewCommits(self):
        branch = self.testBranching()
        new_commit = self.commitSomeChange()
        new_commits = self.repo.getCurrentBranch().getNewCommits(branch)
        self.assertEquals(new_commits, [new_commit])
    def testMerging1(self):
        branch = self.testBranchingAndCommitting()
        prev_head = self.repo.getHead()
        self.repo.merge(branch)
        self.assertNotEquals(self.repo.getHead(), branch.getHead())
        self.assertTrue(branch.getHead() in self.repo.getHead().getParents())
    def testMerging2(self):
        branch = self.testBranching()
        self.repo.checkout(branch)
        self.commitSomeChange()
        master_branch = [b for b in self.repo.getBranches() if b.name == 'master'][0]
        self.assertNotEquals(branch.getHead(), master_branch.getHead())
        self.repo.checkout(master_branch)
        self.assertEquals(self.repo.getHead(), master_branch.getHead())
        self.assertNotEquals(self.repo.getHead(), branch.getHead())
        self.assertTrue(self.repo.getHead() in branch.getHead().getParents())
        self.repo.merge(branch)
        self.assertEquals(self.repo.getHead(), branch.getHead())
    def testBranchAliasing(self):
        """
        Test an isotheric feature in git:
        when a branch points to a 'ref: heads/bla', it is actually an alias to that
        branch...
        """
        branch = self.repo.createBranch('new_branch')
        with open(os.path.join(self.repo.path, ".git", "refs", "heads", "alias_branch"), "wb") as alias_branch_file:
            print >> alias_branch_file, "ref: refs/heads/new_branch"

        branch = self.repo.getBranchByName('alias_branch')
        self.failUnless(isinstance(branch, LocalBranchAlias))
        self.failUnless(branch.name == 'alias_branch')
        self.failUnless(branch.dest == 'new_branch')
        

if __name__ == '__main__':
    unittest.main()
