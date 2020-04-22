from enum import Enum

class RelevantEvents(Enum):
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

	@classmethod
	def to_list(cls):
		return [item.value for item in cls]

class EventHandler:

	def __init__(self, plugin):
		self.plugin = plugin

	def on_event(self, event, payload):
		if event in RelevantEvents.to_list():
			self.plugin.ws.sendEvent(event, payload)

	def on_file_storage_fail(self, error):
		self.plugin._logger.error(error)
		self.plugin.ws.sendData({'event': 'FileSaveFailed', 'payload': '{}'.format(error)})
