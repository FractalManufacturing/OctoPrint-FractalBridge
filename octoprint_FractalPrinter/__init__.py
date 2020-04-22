# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
import threading
import time
import json
from .connection import WebsocketManager
from .events import EventHandler
from .download import DownloadManager
from .printer import PrinterManager
from .database import DBManager
from .storage import StorageManager
from octoprint.filemanager import FileDestinations



class FractalPrinterPlugin(octoprint.plugin.StartupPlugin,
							octoprint.plugin.EventHandlerPlugin,
							octoprint.plugin.SettingsPlugin,
							octoprint.plugin.TemplatePlugin):


	def __init__(self):
		self.lock = threading.RLock()
		self.eventHandler = EventHandler(self)
		self.ws = None
		self.downloadManager = None
		self.printerManager = None
		self.DBManager = None
		self.storageManager = None

	# StartupPlugin mixin

	def on_after_startup(self):
		self._logger.info("Server started. Attempting connection")
		self.DBManager = DBManager('files.db')
		self.downloadManager = DownloadManager(self)
		self.printerManager = PrinterManager(self)
		self.storageManager = StorageManager(self)
		self.connect_to_sv()

		self._file_manager.add_folder(destination=FileDestinations.LOCAL, path='/Fractal/')

	# EventHandlerPlugin mixin

	def on_event(self, event, payload):
		self.eventHandler.on_event(event, payload)

	# SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			token="",
		)

	# TemplatePlugin mixin

	def get_template_configs(self):
		return [
			dict(type="settings", name='Fractal',  custom_bindings=False)
		]

	# Custom methods

	def connect_to_sv(self):
		self.ws = WebsocketManager(url="ws://181.167.199.140:8000/ws/printer/",
								plugin=self,
								on_ws_message=self.on_server_receive)

		thread = threading.Thread(target=self.ws.run, daemon=True)
		thread.start()

	def disconnect_from_sv(self):
		self.ws = None

	def on_server_receive(self, ws, raw_message):

		try:
			parsed_message = json.loads(raw_message)
			directive = parsed_message['directive'] if 'directive' in parsed_message else None
			extra = parsed_message['extra'] if 'extra' in parsed_message else None

			if directive == 'authenticate':
				self.ws.authenticate()

			if directive == 'cancel':
				self.printerManager.cancelPrint()

			if directive == 'pause':
				self.printerManager.pausePrint()

			if directive == 'resume':
				self.printerManager.resumePrint()

			if directive == 'report':
				pass

			if directive == 'download':
				self.downloadManager.enqueue(extra)

			if directive == 'print':
				self.printerManager.printFile(extra)

			if 'error' in parsed_message:
				self._logger.error(parsed_message['error'])

		except Exception as e:
			self._logger.error('Error receiving message from server', e)

	def get_token(self):
		return self._settings.get(['token'])



__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = FractalPrinterPlugin()
