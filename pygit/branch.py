from ref import Ref

class Branch(Ref):
    def delete(self):
        self.repo._executeGitCommandAssertSuccess("git branch -D %s" % (self.name,))
