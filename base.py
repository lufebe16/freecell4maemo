import os
import sys
from abc import ABC, abstractmethod
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty

#=============================================================================

class LBase(object):
	def __init__(self, **kw):
		super(LBase, self).__init__()

#=============================================================================

class LStreamIO(ABC):
	def __init__(self, **kw):
		super(LStreamIO, self).__init__()

	@abstractmethod
	def writer(self, filename):
		pass

	@abstractmethod
	def reader(self, filename):
		pass

#=============================================================================

class LStreamIOHolder(EventDispatcher):
	streamIO = ObjectProperty(None)

	def on_streamIO(self,instance,obj):
		#print("Holder: *********** streamIO: new obj at",obj)
		pass

	def __init__(self, **kw):
		super(LStreamIOHolder,self).__init__(**kw)

#=============================================================================
