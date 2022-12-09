import os
import sys
from abc import ABC, abstractmethod

#=============================================================================

class LBase(object):
	def __init__(self, **kw):
		super(LBase, self).__init__()

#=============================================================================

class LStreamIO(ABC):
	def __init__(self, **kw):
		super(LStreamIO, self).__init__()

	@abstractmethod
	def writer(self, filename, flags = 'wb'):
		pass

	@abstractmethod
	def reader(self, filename, flags = 'rb'):
		pass

#=============================================================================
