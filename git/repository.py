# Copyright (c) 2009, Rotem Yaari <vmalloc@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of organization nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Rotem Yaari ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Rotem Yaari BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import re
import os
import subprocess

from . import branch
from . import commit
from . import config
from . import exceptions
from . import ref
from . import ref_container
from . import remotes
from .utils import quote_for_shell

class Repository(ref_container.RefContainer):
    ############################# internal methods #############################
    def _getWorkingDirectory(self):
        return '.'
    def _executeGitCommand(self, command, cwd=None):
        if cwd is None:
            cwd = self._getWorkingDirectory()
        returned = subprocess.Popen(command,
                                    shell=True,
                                    cwd=cwd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        returned.wait()
        return returned
    def _executeGitCommandAssertSuccess(self, command, **kwargs):
        returned = self._executeGitCommand(command, **kwargs)
        assert returned.returncode is not None
        if returned.returncode != 0:
            raise exceptions.GitCommandFailedException(command, returned)
        return returned
    def _getOutputAssertSuccess(self, command, **kwargs):
        return self._executeGitCommandAssertSuccess(command, **kwargs).stdout.read()
    def _getMergeBase(self, a, b):
        raise NotImplementedError()
    def getMergeBase(self, a, b):
        repo = self
        if isinstance(b, commit.Commit) and isinstance(b.repo, LocalRepository):
            repo = b.repo
        elif isinstance(a, commit.Commit) and isinstance(a.repo, LocalRepository):
            repo = a.repo
        return repo._getMergeBase(a, b)


############################## remote repositories #############################
class RemoteRepository(Repository):
    def __init__(self, url):
        super(RemoteRepository, self).__init__()
        self.url = url
    def _getRefs(self, prefix):
        output = self._executeGitCommandAssertSuccess("git ls-remote %s" % (self.url,))
        for output_line in output.stdout:
            commit, refname = output_line.split()
            if refname.startswith(prefix):
                yield refname[len(prefix):]
    def _getRefsAsClass(self, prefix, cls):
        return [cls(self, ref) for ref in self._getRefs(prefix)]
    def getBranches(self):
        return self._getRefsAsClass('refs/heads/', branch.RemoteBranch)
############################## local repositories ##############################
class LocalRepository(Repository):
    def __init__(self, path):
        super(LocalRepository, self).__init__()
        self.path = path
        self.config = config.GitConfiguration(self)
    def __repr__(self):
        return "<Git Repository at %s>" % (self.path,)
    def _getWorkingDirectory(self):
        return self.path
    def _getCommitByRefName(self, name):
        return commit.Commit(self, self._getOutputAssertSuccess("git rev-parse %s" % name).strip())
    def _getCommitByPartialHash(self, sha):
        return self._getCommitByRefName(sha)
    ########################### Initializing a repository ##########################
    def init(self, bare=False):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if not os.path.isdir(self.path):
            raise exceptions.GitException("Cannot create repository in %s - "
                               "not a directory" % self.path)
        self._executeGitCommandAssertSuccess("git init %s" % ("--bare" if bare else ""))
    def _asURL(self, repo):
        if isinstance(repo, LocalRepository):
            repo = repo.path
        elif isinstance(repo, RemoteRepository):
            repo = repo.url
        elif not isinstance(repo, basestring):
            raise TypeError("Cannot clone from %r" % (repo,))
        return repo
    def clone(self, repo):
        self._executeGitCommandAssertSuccess("git clone %s %s" % (self._asURL(repo), self.path), cwd=".")
    ########################### Querying repository refs ###########################
    def getBranches(self):
        returned = []
        for branch_name in self._executeGitCommandAssertSuccess("git branch").stdout:
            if branch_name.startswith("*"):
                branch_name = branch_name[1:]
            returned.append(branch.LocalBranch(self, branch_name.strip()))
        return returned
    def getRemotes(self):
        config_dict = self.config.getDict()
        returned = []
        for line in self._getOutputAssertSuccess("git remote show -n").splitlines():
            line = line.strip()
            returned.append(remotes.Remote(self, line, config_dict.get('remote.%s.url' % line.strip())))
        return returned
    def getRemoteByName(self, name):
        return self._getByName(self.getRemotes, name)
    def _getMergeBase(self, a, b):
        returned = self._executeGitCommandAssertSuccess("git merge-base %s %s" % (a, b))
        if returned.returncode == 0:
            return commit.Commit(self, returned.stdout.read().strip())
        # make sure this is not a misc. error with git 
        unused = self.getHead()
        return None
    ################################ Querying Status ###############################
    def containsCommit(self, commit):
        try:
            self._executeGitCommandAssertSuccess("git log -1 %s" % (commit,))
        except exceptions.GitException:
            return False
        return True
    def getHead(self):
        return self._getCommitByRefName("HEAD")
    def _getFiles(self, *flags):
        flags = ["--exclude-standard"] + list(flags)
        return [f.strip()
                for f in self._getOutputAssertSuccess("git ls-files %s" % (" ".join(flags))).splitlines()]
    def getStagedFiles(self):
        if self.isInitialized():
            return [line.split()[-1] for line in
                    self._getOutputAssertSuccess("git diff --staged --raw").splitlines()]
        else:
            return self._getFiles('--cached')
    def getUnchangedFiles(self):
        return self._getFiles()
    def getChangedFiles(self):
        return self._getFiles("--modified")
    def getUntrackedFiles(self):
        return self._getFiles("--others")
    def isInitialized(self):
        try:
            self.getHead()
            return True
        except exceptions.GitException:
            return False
    def isValid(self):
        return os.path.isdir(os.path.join(self.path, ".git")) or \
               (os.path.isfile(os.path.join(self.path, "HEAD")) and os.path.isdir(os.path.join(self.path, "objects")))
    def isWorkingDirectoryClean(self):
        return not (self.getUntrackedFiles() or self.getChangedFiles() or self.getStagedFiles())
    def __contains__(self, thing):
        if isinstance(thing, basestring) or isinstance(thing, commit.Commit):
            return self.containsCommit(thing)
        raise NotImplementedError()
    ################################ Staging content ###############################
    def add(self, path):
        self._executeGitCommandAssertSuccess("git add %s" % quote_for_shell(path))
    def addAll(self):
        return self.add('.')
    ################################## Committing ##################################
    def _normalizeRefName(self, thing):
        if isinstance(thing, ref.Ref):
            thing = thing.getNormalizedName()
        return str(thing)
    def _deduceNewCommitFromCommitOutput(self, output):
        for pattern in [
            # new-style commit pattern
            r"^\[\S+\s+(?:\(root-commit\)\s+)?(\S+)\]",
                        ]:
            match = re.search(pattern, output)
            if match:
                return commit.Commit(self, match.group(1))
        return None
    def commit(self, message):
        output = self._getOutputAssertSuccess("git commit -m %s" % quote_for_shell(message))
        return self._deduceNewCommitFromCommitOutput(output)
    ################################ Changing state ################################
    def createBranch(self, name, startingPoint=None):
        command = "git branch %s" % name
        if startingPoint is not None:
            command += str(startingPoint)
        self._executeGitCommandAssertSuccess(command)
        return branch.LocalBranch(self, name)
    def checkout(self, thing=None, targetBranch=None, files=()):
        if thing is None:
            thing = ""
        command = "git checkout %s" % (self._normalizeRefName(thing),)
        if targetBranch is not None:
            command += " -b %s" % (targetBranch,)
        if files:
            command += " -- %s" % " ".join(files)
        self._executeGitCommandAssertSuccess(command)
    def merge(self, what):
        try:
            self._executeGitCommandAssertSuccess("git merge %s" % (self._normalizeRefName(what)))
        except exceptions.GitException:
            raise NotImplementedError()
    def _reset(self, flag, thing):
        command = "git reset %s %s" % (
            flag,
            self._normalizeRefName(thing))
        self._executeGitCommandAssertSuccess(command)
    def resetSoft(self, thing="HEAD"):
        return self._reset("--soft", thing)
    def resetHard(self, thing="HEAD"):
        return self._reset("--hard", thing)
    def resetMixed(self, thing="HEAD"):
        return self._reset("--mixed", thing)
    def _clean(self, flags):
        self._executeGitCommandAssertSuccess("git clean -q " + flags)
    def cleanIgnoredFiles(self):
        """Cleans files that match the patterns in .gitignore"""
        return self._clean("-f -X")
    def cleanUntrackedFiles(self):
        return self._clean("-f -d")
    ################################# collaboration ################################
    def addRemote(self, name, url):
        self._executeGitCommandAssertSuccess("git remote add %s %s" % (name, url))
        return remotes.Remote(self, name, url)
    def fetch(self, repo=None):
        command = "git fetch"
        if repo is not None:
            command += " "
            command += self._asURL(repo)
        self._executeGitCommandAssertSuccess(command)
    def pull(self, repo=None):
        command = "git pull"
        if repo is not None:
            command += " "
            command += self._asURL(repo)
        self._executeGitCommandAssertSuccess(command)
    def _getRefspec(self, fromBranch=None, toBranch=None, force=False):
        returned = ""
        if fromBranch is not None:
            returned += self._normalizeRefName(fromBranch)
        if returned or toBranch is not None:
            returned += ":"
        if toBranch is not None:
            returned += self._normalizeRefName(toBranch)
        if returned and force:
            returned = "+%s" % returned
        return returned
    def push(self, remote=None, fromBranch=None, toBranch=None, force=False):
        command = "git push"
        #build push arguments
        refspec = self._getRefspec(toBranch=toBranch, fromBranch=fromBranch, force=force)

        if refspec:
            remote = "origin"
        self._executeGitCommandAssertSuccess("git push %s %s" % (
            self._normalizeRefName(remote) if remote is not None else "",
            refspec))
    def rebase(self, src):
        self._executeGitCommandAssertSuccess("git rebase %s" % self._normalizeRefName(src))
    ################################# Configuration ################################
    def getConfig(self):
        return dict(s.split("=",1) for s in self._getOutputAssertSuccess("git config -l"))

################################### Shortcuts ##################################
def clone(source, location):
    returned = LocalRepository(location)
    returned.clone(source)
    return returned
