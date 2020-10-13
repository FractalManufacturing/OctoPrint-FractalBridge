import sqlite3
import os

class DBManager():

	def __init__(self, plugin, db_name):
		self.db_name = os.path.join(plugin.get_plugin_data_folder(), db_name)
		self.setupDB()

	def setupDB(self):
		conn = sqlite3.connect(self.db_name)
		c = conn.cursor()

		c.execute("""CREATE TABLE IF NOT EXISTS print_files (id INTEGER PRIMARY KEY, filename TEXT, path TEXT)""")

		conn.commit()
		conn.close()

	def resetDB(self):
		conn = sqlite3.connect(self.db_name)
		c = conn.cursor()

		c.execute("""DROP TABLE IF EXISTS print_files""")
		c.execute("""CREATE TABLE IF NOT EXISTS print_files (id INTEGER PRIMARY KEY, filename TEXT, path TEXT)""")

		conn.commit()
		conn.close()

	def getFilePath(self, fileId):
		conn = sqlite3.connect(self.db_name)
		c = conn.cursor()

		t = (fileId, )
		c.execute('SELECT * FROM print_files WHERE id=?', t)

		data = c.fetchone()
		if data is None:
			conn.commit()
			conn.close()

			return None

		conn.commit()
		conn.close()

		return data[2]

	def addFile(self, fileData, overwrite=True):

		if overwrite:
			self.removeFile(fileData)

		conn = sqlite3.connect(self.db_name)
		c = conn.cursor()

		t = (fileData['id'], fileData['filename'], fileData['path'])
		c.execute('INSERT INTO print_files VALUES (?, ?, ?)', t)

		conn.commit()
		conn.close()

	def removeFile(self, fileData):
		conn = sqlite3.connect(self.db_name)
		c = conn.cursor()

		t = (fileData['id'], )
		c.execute('DELETE FROM print_files WHERE id=?', t)

		conn.commit()
		conn.close()

	def isPresent(self, fileData):
		conn = sqlite3.connect(self.db_name)
		c = conn.cursor()

		t = (fileData['id'],)
		c.execute('SELECT * FROM print_files WHERE id=?', t)

		data = c.fetchone()

		conn.commit()
		conn.close()

		if data is None:
			return False

		else:
			return data[0] == fileData['id'] and data[1] == fileData['filename']
