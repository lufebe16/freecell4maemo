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
from base import LBase, LStreamIO

#=============================================================================

class SaFWriter(object):
	def __init__(self, treeuri, filename):

		logging.info("SaFWriter: __init__")

		self.ostream = None
		try:
			uri = Uri.parse(treeuri)
			myDir = DocumentFile.fromTreeUri(CurrentActivity, uri)
			myFile = myDir.findFile(filename);
			if myFile is None:
				myFile = myDir.createFile("", filename);

			logging.info("fileuri: %s" % myFile.getUri().toString())
			logging.info("canRead: %s" % myFile.canRead())
			logging.info("canWrite: %s" % myFile.canWrite())

			self.ostream = CurrentActivity.getContentResolver().openOutputStream(myFile.getUri())
		except:
			print("error opening output stream")
			self.ostream = None

	def __del__(self):

		logging.info("SaFWriter: __del__")

		if self.ostream is not None:
			self.ostream.flush()
			self.ostream.close()

	def write(self, data):
		# data: bytearray

		logging.info("SaFWriter: write")
		try:
			if self.ostream is not None:
				self.ostream.write(data)
		except:
			print("error writing output stream")

#=============================================================================

class SaFReader(object):
	def __init__(self, treeuri, filename):

		self.istream = None
		try:
			uri = Uri.parse(treeuri)
			myDir = DocumentFile.fromTreeUri(CurrentActivity, uri)
			myFile = myDir.findFile(filename);

			logging.info("fileuri: %s" % myFile.getUri().toString())
			logging.info("canRead: %s" % myFile.canRead())
			logging.info("canWrite: %s" % myFile.canWrite())

			self.istream = CurrentActivity.getContentResolver().openInputStream(myFile.getUri())
		except:
			print("error opening input stream")
			self.istream = None

	def __del__(self):

		logging.info("SaFReader: __del__")

		if self.istream is not None:
			self.istream.close()

	def read(self):
		data = None
		logging.info("SaFReader: read")

		try:
			if self.istream is not None:
				data = bytearray()
				b = bytearray(1024)
				l = self.istream.read(b)
				while l>0:
					for i in range(0,l): data.append(b[i])
					l = self.istream.read(b)
		except:
			print("error reading input stream")

		#print("read finally:",data)
		return data

#=============================================================================

class SaF(LStreamIO):
	def __init__(self, rootdir = "myDocuments", ioholder = None):
		super(SaF, self).__init__()

		if jnius is None:
			return

		logging.info("SaF: __init__")

		#self.rootdir = rootdir
		self.root = rootdir
		self.ioholder = ioholder
		self.REQUEST_CODE = 7  # ??
		b = Build()
		v = Version()
		logging.info('SaF: os version: %d' % v.SDK_INT)

		# vc = VCodes()
		# print("vcode N:",vc.N)
		# print("vcode O:",vc.O)
		# print("vcode Q:",vc.Q) # gibts nicht, da wir selbst auf O sind ?
		# sind denn diese klassen vom aktuellen system, nicht von der app ?
		# offensichtlich: denn SDK_INT is auch ein Konstante. liefert auf dem
		# X: 26 !
		# (andere klassen sind aber ganz bestimmt von der App!)

		self.sdkInt = v.SDK_INT

		# die gespeicherte uri aus dem privaten store holen.
		self.store = LStore('.freecell4maemo/path.json')
		self.store.load()
		self.savedUri = self.store.getEntry('myUri')
		logging.info('SaF: Uri from LStore %s' % self.savedUri)


	def act_intent(self):
		logging.info("SaF: act_intent")
		activity.bind(on_activity_result=self.rec_intent)


	def deact_intent(self):
		logging.info("SaF: deact_intent")
		activity.unbind(on_activity_result=self.rec_intent)


	def get_storage(self):
		if jnius is None:
			return None

		logging.info("SaF: get_storage")

		if self.savedUri is not None:
			uri = Uri.parse(self.savedUri)
			tree = DocumentFile.fromTreeUri(CurrentActivity, uri)
			if tree is not None:
				# print("pickedDir:",tree)
				if tree.canRead() and tree.canWrite():
					logging.info('SaF: storage known')
					return tree;

		logging.info('SaF: storage unknown, ask user')
		self.act_intent()
		self.set_intent()
		return None

	def set_intent(self):
		if jnius is None:
			return

		logging.info("SaF: set_intent")

		myintent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)

		# aus GPSLogger:
		myintent.putExtra("android.content.extra.SHOW_ADVANCED", True);
		myintent.putExtra("android.content.extra.FANCY", True);
		# das tut nichts sichtbares.

		myintent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
		myintent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
		myintent.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)

		# /tree/primary:.freecell4maemo
		# /tree/primary%3A.freecell4maemo

		myUri = "content://com.android.externalstorage.documents/tree/primary%3A"
		#myUri = myUri+self.rootdir
		myUri = myUri+"myNewDir" # TEST
		
		print("***myUri test:",myUri)
		
		if self.sdkInt >= 26:
			# erst ab api 26 verfügbar, sonst exception !
			myintent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, myUri);

			# das nützt alles nichts - oder wie lässt sich das zuverlässig
			# testen. Das gerät ist nach dem ersten test natürlich nicht mehr
			# unberührt und erinnert sich u.U.
			pass


		CurrentActivity.startActivityForResult(myintent, self.REQUEST_CODE)


	def writer(self, filename):
		if jnius is None: return None
		if self.savedUri is None: return None
		return SaFWriter(self.savedUri, filename)
		# geht nicht: return SaFWriter(self.savedUri, self.root+"/"+filename)
		# wir können in diesem directory nicht in klassischer art in subdirs
		# navigieren.


	def reader(self, filename):
		if jnius is None: return None
		if self.savedUri is None: return None
		return SaFReader(self.savedUri, filename)
		# geht nicht: return SaFReader(self.savedUri, self.root+"/"+filename)


	@mainthread
	def rec_intent(self, requestCode, resultCode, intent):  # callback
		if jnius is None:
			return

		if requestCode == self.REQUEST_CODE:

			logging.info("SaF: rec_intent")
			msg = ""
			tree_uri = intent.getData()
			# print("getPath:",tree_uri.getPath())
			# z.B: /tree/63EB-7808:freecell
			#  O.K. der selektierte pfad kommt hier in spezieller Form an.
			# print("getEncodedPath;",tree_uri.getEncodedPath())
			# z.B: /tree/primary%3A.freecell4maemo

			myUri = tree_uri.toString()
			print("toString:",myUri,type(myUri))
			# content://com.android.externalstorage.documents/tree/primary%3A.freecell4maemo
			# Das sollte irgendwie gespeichert werden, damit wir beim start
			# überprüfen können, ob schon gesetzt.

			# Soll die Wahl über reboots pesistent machen:
			takeFlags = Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
			CurrentActivity.getContentResolver().takePersistableUriPermission(tree_uri, takeFlags);
			# Ja funktioniert tatsächlich!
			# zu dieser Funktionalität gehören auch:
			#   ContentResolver.getPersistedUriPermissions()
			# um alle diese pesistenten Permissions aufzulisten und
			#   ContentResolver.releasePersistableUriPermission(Uri, int)
			# um solche persistenten Permissions aufzuräumen, falls nötig.

			# uri in den privaten Store speichern.
			self.store.setEntry('myUri',myUri)
			self.store.store()
			self.savedUri = myUri

			# uns als Empfänger wieder abmelden.
			self.deact_intent()

			# installieren wir uns in ioholder.
			if self.ioholder is not None:
				self.ioholder.streamIO = self

#=============================================================================
