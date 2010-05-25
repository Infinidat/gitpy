#! /usr/bin/python
import unittest
import git
from git.tag import LocalTag, RemoteTag
from test_commits import CommittedRepositoryTest

class TestTags(CommittedRepositoryTest):
    def _assertTagsMatching(self, tags_list, tag_class, name_list):
        self.assertEquals(len(tags_list), len(name_list), "Lengths of tag lists mismatch")
        for tag, name in zip(tags_list, name_list):
            self.assertTrue(isinstance(tag, tag_class))
            self.assertEquals(tag.name, name)
    def testLocalTags(self):
        remote_repo = git.RemoteRepository(self.repo.path)
        self.assertEquals(self.repo.getTags(), [])
        self.assertEquals(remote_repo.getTags(), [])
        self.repo.createTag('bla')
        local_tags = self.repo.getTags()
        remote_tags = remote_repo.getTags()
        self._assertTagsMatching(local_tags, LocalTag, ['bla'])
        self._assertTagsMatching(remote_tags, RemoteTag, ['bla'])
    def testTagsWithStartingPoint(self):
        tag_1 = self.repo.createTag('tag_1')
        old_head = self.repo.getHead()
        self.assertEquals(tag_1.getHead(), old_head)
        self.commitSomeChange()
        tag_2 = self.repo.createTag('tag_2')
        self.assertEquals(tag_2.getHead(), self.repo.getHead())
        self.assertNotEquals(tag_2.getHead(), tag_1.getHead())
        tag_3 = self.repo.createTag('tag_3', startingPoint=old_head)
        self.assertEquals(tag_3.getHead(), old_head)
        tag_4 = self.repo.createTag('tag_4', startingPoint=tag_3)
        self.assertEquals(tag_4.getHead(), tag_3.getHead())

if __name__ == '__main__':
    unittest.main()
