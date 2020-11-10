class EventHandler:
	CONNECTED = 'Connected'
	DISCONNECTED = 'Disconnected'
	ERROR = 'Error'
	PRINTER_STATE_CHANGED = 'PrinterStateChanged'
	FILE_ADDED = 'FileAdded'
	PRINT_STARTED = 'PrintStarted'
	PRINT_FAILED = 'PrintFailed'
	PRINT_DONE = 'PrintDone'
	PRINT_CANCELLED = 'PrintCancelled'
	PRINT_PAUSED = 'PrintPaused'
	PRINT_RESUMED = 'PrintResumed'

	RELEVANT_EVENTS = [
		CONNECTED,
		DISCONNECTED,
		ERROR,
		PRINTER_STATE_CHANGED,
		FILE_ADDED,
		PRINT_STARTED,
		PRINT_FAILED,
		PRINT_DONE,
		PRINT_CANCELLED,
		PRINT_PAUSED,
		PRINT_RESUMED
	]

	def __init__(self, plugin):
		self.plugin = plugin

	def on_event(self, event, payload):
		if event in self.RELEVANT_EVENTS and self.plugin.ws:
			self.plugin.ws.sendEvent(event, payload)

	def on_file_download_fail(self, error):
		self.plugin._logger.error(error)
		self.plugin.ws.sendData({'event': 'FileDownloadFailed', 'payload': '{}'.format(error)})

	def on_file_storage_fail(self, error):
		self.plugin._logger.error(error)
		self.plugin.ws.sendData({'event': 'FileSaveFailed', 'payload': '{}'.format(error)})
