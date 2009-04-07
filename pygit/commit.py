class Commit(object):
    def __init__(self, repo, sha):
        super(Commit, self).__init__()
        self.hash = str(sha).lower()
        self.repo = repo
    def __repr__(self):
        return self.hash
    def __eq__(self, other):
        if isinstance(other, Commit):
            other = str(other)
        if not isinstance(other, basestring):
            raise TypeError("Comparing %s and %s" % (type(self), type(other))
        return self.hash == other.lower()
     def getParents(self):
        output = self.repo._getOutputAssertSuccess("git rev-list %s --list-parents -1" % self)
        return [Commit(self.repo, sha.strip()) for sha in output.split()[1:]]

