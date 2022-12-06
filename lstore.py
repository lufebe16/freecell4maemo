
import json
import os
import sys

#=============================================================================

class LBase(object):
    def __init__(self, **kw):
        super(LBase, self).__init__()

#=============================================================================

class LStore(LBase):
    def __init__(self, path, **kw):
        super(LStore, self).__init__(**kw)
        self.path = path
        self.state = {}

    def setEntry(self, subject, value):
        self.state[subject] = value

    def getEntry(self, subject):
        if subject in self.state:
            return self.state[subject]
        else:
            return None

    def store(self):
        try:
            fj = open(self.path, mode = 'w')
        except IOError:
            return

        try:
            json.dump(self.state, fj)
        except Exception:
            pass

        try:
            fj.close()
        except Exception:
            pass

    def load(self):
        ret = True
        try:
            fj = open(self.path)
        except IOError:
            ret = False
            return ret

        try:
            self.state = json.load(fj)
        except Exception:
            ret = False

        try:
            fj.close()
        except Exception:
            pass

        return ret

#=============================================================================
