#! /usr/bin/python
import unittest
import utils

class CollaborationTest(unittest.TestCase):
    def setUp(self):
        path1 = utils.get_temporary_location()
        path2 = utils.get_temporary_location()
        self.repo1 = LocalRepository(path1)
        self.repo1.init()
        self.repo2 = LocalRepository(path2)
        self.repo2.init()
        for repo in (self.repo1, self.repo2):
            for i in range(10):
                with open(os.path.join(repo.path, "file_%s.txt" % i), "wb") as output:
                    print >>output, "This is file", i
            repo.addAll()
            repo.commit()
    def tearDown(self):
        utils.delete_repository(repo1)
        utils.delete_repository(repo2)

if __name__ == '__main__':
    unittest.main()
