
try:
    import jnius
except ImportError:
    jnius = None

# LB230912.

class AndroidScreen(object):
    def __init__(self):
        if jnius is None:
            return
        self.PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
        self.ActivityInfo = jnius.autoclass('android.content.pm.ActivityInfo')
        self.currentActivity = jnius.cast(
            'android.app.Activity', self.PythonActivity.mActivity)

    def fullscreen(self,fullscreen=True):
        if jnius is not None:
            SDLActivity = jnius.autoclass('org.libsdl.app.SDLActivity')
            SDLActivity.setWindowStyle(fullscreen)

    def getRotation(self):
        if jnius is None:
            return
        context = self.currentActivity
        display = context.getDisplay()
        rot = display.getRotation()
        return rot

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

    def setLandscapeOrientation(self):
        if jnius is None:
            return
        self.currentActivity.setRequestedOrientation(
            self.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE)

    def setPortraitOrientation(self):
        if jnius is None:
            return
        self.currentActivity.setRequestedOrientation(
            self.ActivityInfo.SCREEN_ORIENTATION_PORTRAIT)

    def setSensorOrientation(self):
        if jnius is None:
            return
        self.currentActivity.setRequestedOrientation(
            self.ActivityInfo.SCREEN_ORIENTATION_SENSOR)

    def setUnspecifiedOrientation(self):
        if jnius is None:
            return
        self.currentActivity.setRequestedOrientation(
            self.ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED)
