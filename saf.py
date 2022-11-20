# skizze:

import logging
try:
	import jnius
except ImportError:
	jnius = None

try:
  from android import activity
except ImportError:
  activity = None

import time
from kivy.clock import mainthread

'''
# tip für synchron ?

IntentFilter intF = new IntentFilter("ACTIVITY.THAT.YOU.WANT.TO.LAUNCH");

Instrumentation instrumentation = new Instrumentation();

Instrumentation.ActivityMonitor monitor = instrumentation.addMonitor(intF, null, true);
Intent i = new Intent("ACTIVITY.THAT.YOU.WANT.TO.LAUNCH");
instrumentation.startActivitySync(i);
'''

class SaF(object):
	def __init__(self):
		if jnius is None:
			return
		logging.info("SaF: __init__")
		self.PythonActivity = jnius.autoclass(
			'org.kivy.android.PythonActivity')
		self.currentActivity = jnius.cast(
			'android.app.Activity', self.PythonActivity.mActivity)
		self.Intent = jnius.autoclass('android.content.Intent')
		self.REQUEST_CODE = 7  # ??
		self.DocumentsContract = jnius.autoclass('android.provider.DocumentsContract')

		# dafür brauchts androidx.preference dependency angabe!
		self.DocumentFile = jnius.autoclass('androidx.documentfile.provider.DocumentFile')

	def set_intent(self):
		if jnius is None:
			return
		logging.info("SaF: set_intent")
		
		myintent = self.Intent(self.Intent.ACTION_OPEN_DOCUMENT_TREE)

		# aus GPSLogger:
		#myintent.putExtra("android.content.extra.SHOW_ADVANCED", true);
		#myintent.putExtra("android.content.extra.FANCY", true);

		myintent.addFlags(self.Intent.FLAG_GRANT_READ_URI_PERMISSION)
		myintent.addFlags(self.Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
		myintent.addFlags(self.Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

		self.currentActivity.startActivityForResult(myintent, self.REQUEST_CODE)

		# das geht. (blockiert aber den UI Thread. startet vorerst schwarz).
		#self.done = False
		#while self.done == False:
		#	time.sleep(1)


	@mainthread
	def rec_intent(self, requestCode, resultCode, intent):  # callback
		if jnius is None:
			return
		#if not resultCode == OK # oder sowas
		#	return
		if requestCode == self.REQUEST_CODE:
			logging.info("SaF: rec_intent")
			msg = ""
			tree_uri = intent.getData()
			print("getPath:",tree_uri.getPath())
			# /tree/63EB-7808:freecell
			#  O.K. der selektierte pfad kommt hier in spezieller Form an.
			print("getEncodedPath;",tree_uri.getEncodedPath())
			print("toString:",tree_uri.toString())

			'''
			Also das funktioniert soweit.
			Für die Anwendung jedoch brauchen wir androidx klassen.
			(z.B.
			  - androidx.documentfile.provider.DocumentFile
			  - androidx.preference.PreferenceManager
			)
			Diese werden von pyjnius (noch) nicht unterstützt müssten
			also in java selbst programmiert werden.
			'''

	def act_intent(self):
		logging.info("SaF: act_intent")
		activity.bind(on_activity_result=self.rec_intent)

	def deact_intent(self):
		logging.info("SaF: deact_intent")
		activity.unbind(on_activity_result=self.rec_intent)
