# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
import threading
import json
import flask
from .connection import WebsocketManager
from .events import EventHandler
from .download import DownloadManager
from .printer import PrinterManager
from .database import DBManager
from .storage import StorageManager
from octoprint.filemanager import FileDestinations



class FractalBridgePlugin(octoprint.plugin.StartupPlugin,
							octoprint.plugin.EventHandlerPlugin,
							octoprint.plugin.SettingsPlugin,
							octoprint.plugin.TemplatePlugin,
							octoprint.plugin.AssetPlugin,
							octoprint.plugin.BlueprintPlugin):


	def __init__(self):
		self.lock = threading.RLock()
		self.eventHandler = EventHandler(self)
		self.token = None
		self.ws = None
		self.ws_thread = None
		self.downloadManager = None
		self.printerManager = None
		self.DBManager = None
		self.storageManager = None

	# StartupPlugin mixin

	def on_after_startup(self):
		self._logger.info("Server started. Attempting connection")
		self.DBManager = DBManager(self, 'files.db')
		self.downloadManager = DownloadManager(self)
		self.printerManager = PrinterManager(self)
		self.storageManager = StorageManager(self)

		self.token = self._settings.get(['token'])
		self._logger.info(self.token)
		self.connect_to_sv()

		self._file_manager.add_folder(destination=FileDestinations.LOCAL, path='/Fractal/')

	# EventHandlerPlugin mixin

	def on_event(self, event, payload):
		self.eventHandler.on_event(event, payload)

	# SettingsPlugin mixin

	def get_settings_defaults(self):

		# api_url = 'https://fractal.tech'
		api_url = 'http://localhost:8000'
		# ws_url = 'wss://fractal.tech/ws/printer/'
		ws_url = 'ws://localhost:8000/ws/printer/'

		return dict(
			token="",
			api_url=api_url,
			ws_url=ws_url
		)

	# TemplatePlugin mixin

	def get_template_configs(self):
		return [
			dict(type="settings", name='Fractal', custom_bindings=True)
		]

	# AssetPlugin mixin

	def get_assets(self):
		return dict(
			js=['js/fractalbridge.js'],
			css=["css/fractalbridge.css"]
		)

	# BlueprintPlugin mixin

	@octoprint.plugin.BlueprintPlugin.route("/connect", methods=["POST"])
	def connect_from_octoprint_frontend(self):
		if 'token' in flask.request.values:
			self.token = flask.request.values['token']
		self.connect_to_sv()
		return flask.make_response('connected')

	@octoprint.plugin.BlueprintPlugin.route("/disconnect", methods=["GET"])
	def disconnect_from_octoprint_frontend(self):
		self.disconnect_from_sv()
		return flask.make_response('disconnected')

	@octoprint.plugin.BlueprintPlugin.route("/status", methods=["GET"])
	def get_connection_status(self):
		if self.ws:
			return flask.make_response(json.dumps({'connected': self.ws.is_connected}))
		return flask.make_response(json.dumps({'connected': False}))

	@octoprint.plugin.BlueprintPlugin.route("/reset_db", methods=["GET"])
	def resetDB(self):
		self.DBManager.resetDB()
		return flask.make_response('DB reset')

	# Custom methods

	def connect_to_sv(self):
		if not self.token:
			self._logger.info("No Token provided")
			return
		if not self.ws:
			ws_url = self._settings.get(['ws_url'])
			self.ws = WebsocketManager(url=ws_url,
									plugin=self,
									on_ws_message=self.on_server_receive)
		else:
			self.ws.stop()

		self.ws_thread = threading.Thread(target=self.ws.run, kwargs={'reconnect': True})
		self.ws_thread.daemon = True
		self.ws_thread.start()

	def disconnect_from_sv(self):
		if self.ws:
			self.ws.stop()

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
				status = self.printerManager.reportStatus()
				status.update({'event': 'report'})
				self.ws.sendData(status)

			if directive == 'filament':
				self.printerManager.changeFilament(extra)

			if directive == 'download':
				self.downloadManager.enqueue(extra)

			if directive == 'print':
				self.printerManager.printFile(extra)

			if directive == 'nuke':
				self.DBManager.resetDB()

			if 'error' in parsed_message:
				self.ws.stop()
				self._logger.error(parsed_message['error'])

		except Exception as e:
			self._logger.error('Error receiving message from server', e)

	def get_token(self):
		return self.token



__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = FractalBridgePlugin()
