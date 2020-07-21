class PrinterManager:

	def __init__(self, plugin):
		self.plugin = plugin
		self.printer = plugin._printer

	def changeFilament(self, filamentData=None):
		if filamentData is None:
			filamentData = {'tool': 0, 'temperature': 210}

		# tool_name = "tool{}".format(filamentData['tool'])
		# self.printer.set_temperature(tool_name, filamentData['temperature'])
		self.printer.commands(["M109 S{}".format(filamentData['temperature']), "M600"])

	def printFile(self, fileData=None, path=None):
		if fileData:
			if self.plugin.DBManager.getFilePath(fileData['id']):
				self.printer.select_file(path=self.plugin.DBManager.getFilePath(fileData['id']), sd=False, printAfterSelect=True)
			else:
				fileData['print_after'] = True
				self.plugin.downloadManager.enqueue(fileData)
		elif path:
			self.printer.select_file(path=path, sd=False, printAfterSelect=True)

	def reportStatus(self):
		return self.printer.get_current_data()

	def cancelPrint(self):
		self.printer.cancel_print()

	def pausePrint(self):
		self.printer.pause_print()

	def resumePrint(self):
		self.printer.resume_print()

	def connect(self, port=None, baudrate=None, profile=None):
		if self.printer.get_current_connection()[0] == 'Closed':
			self.printer.connect(port=port, baudrate=baudrate, profile=profile)
