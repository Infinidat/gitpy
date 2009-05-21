#! /usr/bin/python
import unittest
import git
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
        

if __name__ == '__main__':
    unittest.main()
