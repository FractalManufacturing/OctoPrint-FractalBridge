class PrinterManager:

	def __init__(self, plugin):
		self.plugin = plugin
		self.printer = plugin._printer

	def printFile(self, fileData=None, path=None):
		if fileData:
			if self.plugin.DBManager.getFilePath(fileData['id']):
				self.printer.select_file(path=self.plugin.DBManager.getFilePath(fileData['id']), sd=False, printAfterSelect=True)
			else:
				fileData['print'] = True
				self.plugin.downloadManager.enqueue(fileData)
		elif path:
			self.printer.select_file(path=path, sd=False, printAfterSelect=True)

	def cancelPrint(self):
		self.printer.cancel_print()

	def pausePrint(self):
		self.printer.pause_print()

	def resumePrint(self):
		self.printer.resume_print()

	def connect(self, port=None, baudrate=None, profile=None):
		if self.printer.get_current_connection()[0] == 'Closed':
			self.printer.connect(port=port, baudrate=baudrate, profile=profile)
