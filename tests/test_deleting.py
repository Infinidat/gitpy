import os
from test_commits import CommittedRepositoryTest

class DeletionTest(CommittedRepositoryTest):
    def testDeletingFile(self):
        filename = self.makeSomeChange()
        full_filename = os.path.join(self.repo.path, filename)
        self.repo.addAll()
        self.repo.commit(message="test")
        self.assertTrue(os.path.exists(full_filename))
        self.repo.delete(filename)
        self.assertFalse(os.path.exists(full_filename))
        self.repo.resetHard()
        self.assertTrue(os.path.exists(full_filename))
        self.repo.delete(filename)
        self.repo.commit(message="test")
        self.assertFalse(os.path.exists(full_filename))
        self.repo.resetHard()
        self.assertFalse(os.path.exists(full_filename))
