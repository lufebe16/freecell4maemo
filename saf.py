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

if jnius is not None:
	Intent = jnius.autoclass('android.content.Intent')
	Uri = jnius.autoclass('android.net.Uri')

	PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
	CurrentActivity = jnius.cast('android.app.Activity', PythonActivity.mActivity)

	# dafür brauchts androidx.preference dependency angabe:
	DocumentsContract = jnius.autoclass('android.provider.DocumentsContract')
	DocumentFile = jnius.autoclass('androidx.documentfile.provider.DocumentFile')

	Build = jnius.autoclass("android.os.Build")
	Version = jnius.autoclass("android.os.Build$VERSION")
	VCodes = jnius.autoclass("android.os.Build$VERSION_CODES")

from lstore import LStore

class SaF(object):
	def __init__(self):
		if jnius is None:
			return
		logging.info("SaF: __init__")

		self.REQUEST_CODE = 7  # ??
		b = Build()
		v = Version()
		print("os version running:",v.SDK_INT)
		vc = VCodes()
		print("vcode N:",vc.N)
		#print("vcode O:",vc.O)
		#print("vcode Q:",vc.Q) # gibts nicht, da wir selbst auf O sind ?
		# sind denn diese klassen vom aktuellen system, nicht von der app ?
		# offensichtlich: denn SDK_INT is auch ein Konstante. liefert auf dem
		# X: 26 !
		# (andere klassen sind aber ganz bestimmt von der App!)

		self.store = LStore('.freecell4maemo/path.json')
		self.store.load()
		self.lasturi = self.store.getEntry('myUri')
		print ("uri from LStore:",self.lasturi)

	def set_intent(self):
		if jnius is None:
			return
		logging.info("SaF: set_intent")
		
		myintent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)

		# aus GPSLogger:
		#myintent.putExtra("android.content.extra.SHOW_ADVANCED", true);
		#myintent.putExtra("android.content.extra.FANCY", true);

		myintent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
		myintent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
		myintent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)


		# /tree/primary:.freecell4maemo
		# /tree/primary%3A.freecell4maemo

		# directory vorgeben?:
		# pickerUri = Uri.parse("/sdcard/.freecell4maemo")
		#pickerUri = Uri.parse("/tree/primary:.freecell4maemo")
		# pickerUri = Uri.parse(str("/tree/primary%3A.freecell4maemo")

		myUri = "content://com.android.externalstorage.documents/tree/primary%3A.freecell4maemo"
		pickerUri = Uri.parse(myUri)
		pickedDir = DocumentFile.fromTreeUri(CurrentActivity, pickerUri)
		print("pickedDir:",pickedDir)
		print("canRead:",pickedDir.canRead())
		print("canWrite:",pickedDir.canWrite())

		myintent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, myUri);
		# das bewirkt nichts.

		# getContentResolver().takePersistableUriPermission(uri, takeFlags);

		CurrentActivity.startActivityForResult(myintent, self.REQUEST_CODE)

		# self.jString = jnius.autoclass('java.lang.String')


	@mainthread
	def rec_intent(self, requestCode, resultCode, intent):  # callback
		if jnius is None:
			return

		if requestCode == self.REQUEST_CODE:

			logging.info("SaF: rec_intent")
			msg = ""
			tree_uri = intent.getData()
			print("getPath:",tree_uri.getPath())
			# /tree/63EB-7808:freecell
			#  O.K. der selektierte pfad kommt hier in spezieller Form an.
			print("getEncodedPath;",tree_uri.getEncodedPath())

			myUri = tree_uri.toString()
			print("toString:",myUri,type(myUri))
            # content://com.android.externalstorage.documents/tree/primary%3A.freecell4maemo
            # Das sollte irgendwie gespeichert werden, damit wir beim start
            # überprüfen können, ob gesetzt.

			self.store.setEntry('myUri',myUri)
			self.store.store()

            # Anwenden:

			# ok. nun gehen wir so vor wie im muster (GPSApplication)
			uri = Uri.parse(myUri)
			print("uri:",uri)

			pickedDir = DocumentFile.fromTreeUri(CurrentActivity, uri)
			print("pickedDir:",pickedDir)

			# Anmerkung: Um ein file zu finden zu bekannter uri:
			#  fromSingleUri(context,uri)

			dbFile = pickedDir.findFile("database_copy.db");
			if dbFile is None:
				dbFile = pickedDir.createFile("", "database_copy.db");

			print("dbfile:",dbFile)
			print("zugeh. uri:",dbFile.getUri().toString())

			print("canRead:",dbFile.canRead())
			print("canWrite:",dbFile.canWrite())

			# Damit liess sich ein leeres file database_copy.db im 
			# ausgewählten Verzeichnis erzeugen!.

			# der java output stream muss dann über den contentresolver bezogen
			# werden. (Da drin ist also die security zuhause.). Einen os Filehandle
			# bekommen wir nicht ?

			# java:
			# output = GPSApplication.getInstance().getContentResolver().openOutputStream(dbFile.getUri(), "rw")

			ostream = CurrentActivity.getContentResolver().openOutputStream(dbFile.getUri(), "rw")
			print("stream:",ostream)

			# das ist ein normales java.io.OutputStream objekt - also android unabh.
			# da lässt sich vielleicht etwas tun!

			s = "hello file extended"
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
