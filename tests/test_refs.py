from test_commits import CommittedRepositoryTest

class RefTest(CommittedRepositoryTest):
    def testComparingRefs(self):
        #get two different objects, marking the same branch
        branch1 = self.repo.getBranches()[0]
        branch2 = self.repo.getBranches()[0]
        self.assertTrue(branch2 == branch1)
        self.assertFalse(branch2 != branch1)
        branch3 = self.repo.createBranch('test_branch')
        self.assertFalse(branch1 == branch3)
        self.assertTrue(branch3 != branch1)
