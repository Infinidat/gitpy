from .ref import Ref
from .files import ModifiedFile

SHA1_LENGTH = 40

class Commit(Ref):
    def __init__(self, repo, sha):
        sha = str(sha).lower()
        if len(sha) < SHA1_LENGTH:
            sha = repo._getCommitByPartialHash(sha).hash
        super(Commit, self).__init__(repo, sha)
        self.hash = sha
    def __repr__(self):
        return self.hash
    def __eq__(self, other):
        if isinstance(other, Commit):
            other = str(other)
        if not isinstance(other, basestring):
            raise TypeError("Comparing %s and %s" % (type(self), type(other)))
        return (self.hash == other.lower())
    def getParents(self):
        output = self.repo._getOutputAssertSuccess("git rev-list %s --parents -1" % self)
        return [Commit(self.repo, sha.strip()) for sha in output.split()[1:]]
    def getChange(self):
        returned = []
        for line in self.repo._getOutputAssertSuccess("git diff --raw %s" % self):
            _, _, _, _, _, filename = line.split()
            returned.append(ModifiedFile(filename))
        return returned

