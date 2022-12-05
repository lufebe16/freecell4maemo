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

Uri = jnius.autoclass('android.net.Uri')
DocumentFile = jnius.autoclass('androidx.documentfile.provider.DocumentFile')

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

		self.jString = jnius.autoclass('java.lang.String')


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
			myUri = tree_uri.toString()
            # content://com.android.externalstorage.documents/tree/primary%3A.freecell4maemo

			# ok. nun gehen wir so vor wie im muster (GPSApplication)
			uri = Uri.parse(myUri)
			print("uri:",uri)

			pickedDir = DocumentFile.fromTreeUri(self.currentActivity, uri)
			print("pickedDir:",pickedDir)

			dbFile = pickedDir.createFile("", "database_copy.db");
			print("dbfile:",dbFile)
			print("zugeh. uri:",dbFile.getUri().toString())

			# Damit liess sich ein leeres file database_copy.db im 
			# ausgewählten Verzeichnis erzeugen!.

			# der java output stream muss dann über den contentresolver bezogen
			# werden. (Da drin ist also die security zuhause.). Einen os Filehandle
			# bekommen wir nicht ?

			# java:
			# output = GPSApplication.getInstance().getContentResolver().openOutputStream(dbFile.getUri(), "rw")

			#ostream = self.PythonActivity.getInstance().getContentResolver().openOutputStream(dbFile.getUri(), "rw")
			ostream = self.currentActivity.getContentResolver().openOutputStream(dbFile.getUri(), "rw")
			#ostream = self.currentActivity.getInstance().getContentResolver().openOutputStream(dbFile.getUri(), "rw")
			print("stream:",ostream)
			# das ist ein normales java.io.OutputStream objekt - also android unabh.
			# da lässt sich vielleicht etwas tun!

			s = "hello file"
			ostream.write(s.encode())
			# so get das !!

			ostream.flush()
			ostream.close()

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
