class ModifiedFile(object):
    def __init__(self, filename):
        super(ModifiedFile, self).__init__()
        self.filename = filename
    def __repr__(self):
        return self.filename
