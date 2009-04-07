import os
import subprocess

from . import branch
from . import exceptions
from . import ref

class Repository(object):
    def getBranches(self):
        raise NotImplementedError()
    ############################# internal methods #############################
    def _getWorkingDirectory(self):
        return '.'
    def _executeGitCommand(self, command):
        returned = subprocess.Popen(command,
                                    shell=True,
                                    cwd=self._getWorkingDirectory(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        returned.wait()
        return returned
    def _executeGitCommandAssertSuccess(self, command):
        returned = self._executeGitCommand(command)
        assert returned.returncode is not None
        if returned.returncode != 0:
            import pdb
            pdb.set_trace()
            raise exceptions.GitCommandFailedException(command, returned)
        return returned
    def _getOutputAssertSuccess(self, command):
        return self._executeGitCommandAssertSuccess(command).stdout.read()

############################## remote repositories #############################
class RemoteRepository(Repository):
    def __init__(self, url):
        super(RemoteRepository, self).__init__()
        self.url = url
    def getRefs(self):
        output = self._executeGitCommandAssertSuccess("git ls-remote %s" % (self.url,))
        for output_line in output.stdout:
            commit, refname = output_line.split()
            for prefix, cls in [('refs/heads/', branch.Branch),
                                ('refs/tags/', None),
                                ('refs/remotes/', None),
                                ('', ref.Ref)]:
                if refname.startswith(prefix):
                    if cls is not None:
                        yield cls(self, refname[len(prefix):])
                    break
    def getBranches(self):
        return [ref for ref in self.getRefs()
                if isinstance(ref, branch.Branch)]

############################## local repositories ##############################
class LocalRepository(Repository):
    def __init__(self, path):
        super(LocalRepository, self).__init__()
        self.path = path
    def _getWorkingDirectory(self):
        return self.path
    def _getCommitByRefName(self, name):
        return commit.Commit(self, self._getOutputAssertSuccess("git rev-parse %s" % name).strip())
    ########################### Initializing a repository ##########################
    def init(self, bare=False):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if not os.path.isdir(self.path):
            raise exceptions.GitException("Cannot create repository in %s - "
                               "not a directory" % self.path)
        self._executeGitCommandAssertSuccess("git init %s" % ("--bare" if bare else ""))
    ########################### Querying repository refs ###########################
    def getBranches(self):
        for branch_name in self._executeGitCommandAssertSuccess("git branch").stdout:
            branch_name = strip()
            if branch_name.startswith("*"):
                brach_name = brach_name[1:]
            yield branch.Branch(self, brach_name.strip())
    def getRefs(self):
        raise NotImplementedError()
    ################################ Querying Status ###############################
    def _getFiles(self, *flags):
        flags = ["--exclude-standard"] + list(flags)
        return [f.strip()
                for f in self._getOutputAssertSuccess("git ls-files %s" % (" ".join(flags))).splitlines()]
    def getUntrackedFiles(self):
        return self._getFiles("--others")
