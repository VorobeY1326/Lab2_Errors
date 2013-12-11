import random
import os
import sys, codecs, locale

"""Классная обертка, иногда вероятно бросающая исключение"""

class Failable:
	def __init__(self, exceptions, probability = 0.5):
		self.exceptions = exceptions
		self.probability = probability
	def mayBeFail(self, function):
		if random.random() > self.probability:
			return function()
		else:
			raise random.choice(self.exceptions)

"""Возможные исключения"""

class AccessDenied(Exception):
	def __init__(self, message):
		self.message = message

class FileNotFound(Exception):
	def __init__(self, message):
		self.message = message

class DiskFailed(Exception):
	def __init__(self, message):
		self.message = message

"""Обертки для вызовов с возможностью исключений"""

class RecursiveDirectoryWalker:
	def __init__(self, topPath):
		self.topPath = topPath
		self.failable = Failable([AccessDenied("directory " + topPath)], 0.1)
	def getFiles(self):
		return self.failable.mayBeFail(self.__getFilesSafe)
	def __getFilesSafe(self):
		filesAll = []
		for root, dirs, files in os.walk(self.topPath):
			for f in files:
				filesAll.append(os.path.abspath(os.path.join(root, f)))
		return filesAll

class FileStream:
	def __init__(self, fileName):
		self.fileName = fileName
		self.file = None
		self.failable = Failable([AccessDenied("file " + fileName), FileNotFound("file " + fileName)], 0.2)
		self.readFailable = Failable([DiskFailed("file " + fileName)], 0.1)
	def open(self):
		self.failable.mayBeFail(self.openSafe)
	def openSafe(self):
		try:
			self.file = open(self.fileName)
			self.stream = iter([x for x in self.file.read().split()])
		except PermissionError:
			raise AccessDenied("file " + fileName)
	def close(self):
		if self.file:
			self.file.close()
	def read(self):
		return self.readFailable.mayBeFail(self.readSafe)
	def readSafe(self):
		try:
			return next(self.stream)
		except StopIteration:
			raise EOFError

"""Собственно, сама программа"""

numbers = []
if (len(sys.argv) < 2):
	print("Usage: " + sys.argv[0] + " directoryname")
	sys.exit()
dir = sys.argv[1]
try:
	directoryWalker = RecursiveDirectoryWalker(dir)
	files = directoryWalker.getFiles()
	for fileName in files:
		file = FileStream(fileName)
		try:
			stream = file.open()
			while 1:
				try:
					str = file.read()
					numbers.append(int(str))
				except DiskFailed:
					print("Warning: reading failed, file - " + fileName)
					break
				except EOFError:
					break
				except ValueError:
					print("Warning: not a number found - " + str)
		except AccessDenied as e:
			print("Warning: cannot access " + e.message)
		except FileNotFound as e:
			print("Warning: cannot find " + e.message)
		except Exception as e:
			print("Warning: file " + fileName + " wasn't opened - " + str(e))
		finally:
			file.close()
except AccessDenied as e:
	print("Sorry, cannot access " + e.message)
if len(numbers) > 0:
	numbers = sorted(numbers)
	print("Sorted numbers:")
	for n in numbers:
		print(n)
else:
	print("No numbers found!")