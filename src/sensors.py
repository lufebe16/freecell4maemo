
import logging
try:
    import jnius
except ImportError:
    jnius = None

try:
    from android import activity
except ImportError:
    activity = None

#import time
#from kivy.clock import mainthread

SensorReader = None

if jnius is not None:
    Intent = jnius.autoclass('android.content.Intent')
    Uri = jnius.autoclass('android.net.Uri')
    PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
    currentActivity = jnius.cast('android.app.Activity', PythonActivity.mActivity)
    SensorReader = jnius.autoclass('org.lufebe16.sensor.SensorReader')

#=============================================================================

from kivy.clock import Clock

class sensor_update(object):

  def __init__(self, mode=0, step=0.1):
    self.eventId = None
    self.smX = 0.0
    self.smY = 0.0
    self.smZ = 0.0
    self.lt = 0.0
    self.smode = mode
    self.step = step
    self.reader = None
    if SensorReader is not None:
      self.reader = SensorReader.getInstance()

  # update hook.
  def update(self, x,y,z):
    print('sensors:',x,y,z)

  def run(self, dt):
    logging.info("Sensors: sensor run update")
    if self.reader is not None:
      r = self.reader
      x = r.sensorX
      y = r.sensorY
      z = r.sensorZ
      self.update(x,y,z)
      self.smX = x
      self.smY = y
      self.smZ = z

  def start_reading(self):
    logging.info("Sensors: sensor start update")
    if self.reader is not None:
      self.reader.startListening(currentActivity)
      if self.smode == 0:
        self.eventId = Clock.schedule_interval(self.run,self.step)
      if self.smode == 1:
        self.eventId = Clock.schedule_once(self.run,self.step)

  def stop_reading(self):
    logging.info("Sensors: sensor stop update")
    Clock.unschedule(self.eventId)
    if self.reader is not None:
      self.reader.stopListening()

#=============================================================================
