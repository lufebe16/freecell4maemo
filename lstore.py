
import json
import os
import sys

from base import LBase, LStreamIO

#=============================================================================

class LOsReader(LBase):
	def __init__(self, path):
		self.path = path
		self.file = None
		try:
			self.file = open(self.path, mode = 'rb')
		except IOError:
			pass

	def __del__(self):
		if self.file is not None:
			self.file.close()

	def read(self):
		if self.file:
			return self.file.read()

#=============================================================================

class LOsWriter(LBase):
	def __init__(self, path):
		self.path = path
		self.file = None
		try:
			self.file = open(self.path, mode = 'wb')
		except IOError:
			pass

	def __del__(self):
		if self.file is not None:
			self.file.close()

	def write(self,data):
		if self.file:
			self.file.write(data)

#=============================================================================

class LOsIO(LStreamIO):
	def __init__(self, rootdir = None):
		self.root = rootdir

	def writer(self, filename):
		if self.root is not None:
			return LOsWriter(self.root+"/"+filename)
		else:
			return LOsWriter(filename)

	def reader(self, filename):
		if self.root is not None:
			return LOsReader(self.root+"/"+filename)
		else:
			return LOsReader(filename)

#=============================================================================

class LStore(LBase):
	def __init__(self, path, **kw):
		super(LStore, self).__init__(**kw)
		self.path = path
		self.state = {}
		self.io = LOsIO()

	def setIO(self, io):
		self.io = io

	def setEntry(self, subject, value):
		self.state[subject] = value

	def getEntry(self, subject):
		if subject in self.state:
			return self.state[subject]
		else:
			return None

	def store(self):

		writer = self.io.writer(self.path)
		data = json.dumps(self.state).encode()
		#print ("store data:",data,"type(data)",type(data))
		writer.write(data)

	def load(self):
		ret = True

		reader = self.io.reader(self.path)
		data = reader.read()
		if data:
			#print ("loaded data:",data,"type is:",type(data))
			self.state = json.loads(data.decode())

		return ret

#=============================================================================
