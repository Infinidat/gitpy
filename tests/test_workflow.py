#! /usr/bin/python
import unittest
import utils
from gitpy import LocalRepository
from gitpy import clone

class TestWorkflows(unittest.TestCase):
    def setUp(self):
        self.repo = utils.create_repo()
    def tearDown(self):
        utils.delete_repository(self.repo)

    def assertReposEqual(self, repo1, repo2):
        self.assertEquals(utils.get_repo_contents(repo1),
                          utils.get_repo_contents(repo2))

    def testCloneModifyPush(self):
        new_repo = LocalRepository(utils.get_temporary_location())        
        new_repo.clone(self.repo)
        #checkout a different branch to comply with git 1.7.0
        prev_branch = self.repo.getCurrentBranch()
        self.repo.checkout(self.repo.createBranch('temp'))        
        self.assertReposEqual(self.repo, new_repo)
        utils.commit_change(new_repo)
        new_repo.push()
        self.repo.checkout(prev_branch)        
        self.assertReposEqual(self.repo, new_repo)        
        utils.delete_repository(new_repo)
    def testCloneRebaseModifyPush(self):
        new_repo = LocalRepository(utils.get_temporary_location())
        new_repo.clone(self.repo)
        prev_branch = self.repo.getCurrentBranch()
        #checkout a different branch to comply with git 1.7.0
        self.repo.checkout(self.repo.createBranch('temp'))
        self.assertReposEqual(self.repo, new_repo)
        utils.commit_change(self.repo)
        utils.commit_change(new_repo)
        new_repo.fetch()
        new_repo.rebase('origin/master')
        new_repo.push()
        self.repo.checkout(prev_branch)
        self.assertReposEqual(self.repo, new_repo)        
        utils.delete_repository(new_repo)
    def testCloneModifyPushToBranch(self):
        new_repo = clone(self.repo, utils.get_temporary_location())
        prev_branch = self.repo.getCurrentBranch()
        self.repo.checkout(self.repo.createBranch('temp'))
        branch = new_repo.createBranch('work')
        new_repo.checkout(branch)
        utils.commit_change(new_repo)
        new_repo.push(self.repo, fromBranch=branch, toBranch='work')
        self.repo.checkout(prev_branch)
        self.assertTrue(self.repo.getBranchByName('work').getHead() == new_repo.getHead())

if __name__ == '__main__':
    unittest.main()
