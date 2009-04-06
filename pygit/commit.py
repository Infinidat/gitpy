class Commit(object):
    def __init__(self, hash, repo):
        super(Commit, self).__init__()
        self.hash = str(hash).lower()
        self.repo = repo
    def __repr__(self):
        return self.hash
    def __eq__(self, other):
        if isinstance(other, Commit):
            other = str(other)
        if not isinstance(other, basestring):
            raise TypeError("Comparing %s and %s" % (type(self), type(other))
        return self.hash == other.lower()
