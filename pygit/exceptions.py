class GitException(Exception):
    def __init__(self, msg):
        super(GitException, self).__init__()
        self.msg = msg
    def __repr__(self):
        return "%s: %s" % (type(self).__name__, self.msg)
    __str__ = __repr__

class GitCommandFailedException(GitException):
    def __init__(self, command, popen):
        super(GitCommandFailedException, self).__init__(None)
        self.command = command
        self.stderr = popen.stderr.read()
        self.stdout = popen.stdout.read()
        self.popen = popen
        self.msg = "Command %s failed (%s):\n%s\n%s" % (command, popen.returncode,
                              self.stderr, self.stdout)

