
try:
    import jnius
except ImportError:
    jnius = None

# LB230912.

class AndroidOri(object):
    def __init__(self):
        if jnius is None:
            return
        self.PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
        self.ActivityInfo = jnius.autoclass('android.content.pm.ActivityInfo')
        self.currentActivity = jnius.cast(
            'android.app.Activity', self.PythonActivity.mActivity)

    def lockOrientation(self):
        if jnius is None:
            return
        self.currentActivity.setRequestedOrientation(
            self.ActivityInfo.SCREEN_ORIENTATION_LOCKED)

    def unLockOrientation(self):
        if jnius is None:
            return
        self.currentActivity.setRequestedOrientation(
            self.ActivityInfo.SCREEN_ORIENTATION_FULL_SENSOR)
