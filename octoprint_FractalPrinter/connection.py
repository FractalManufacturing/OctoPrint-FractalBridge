import websocket
import threading
import json
import time

class WebsocketManager():

	def __init__(self, url, plugin, on_ws_message=None, on_ws_error=None, on_ws_close=None):

		def on_open(ws):
			plugin._logger.info('Fractal connection enabled')
			self.plugin.printerManager.connect()

		def on_message(ws, message):
			if on_ws_message:
				on_ws_message(ws, message)
			else:
				plugin._logger.info(message)

		def on_error(ws, error):
			if on_ws_error:
				on_ws_error(ws, error)
			else:
				plugin._logger.error(error)

		def on_close(ws):
			if on_ws_close:
				on_ws_close(ws)
			else:
				plugin._logger.info('Connection closed')

		self.lock = threading.RLock()
		self.plugin = plugin
		self.ws = websocket.WebSocketApp(url=url,
												on_open=on_open,
												on_message=on_message,
												on_error=on_error,
												on_close=on_close)


	def run(self):
		self.ws.run_forever()

	@property
	def is_connected(self):
		return self.ws.sock and self.ws.sock.connected

	def sendData(self, data):
		with self.lock:
			if self.is_connected:
				self.ws.send(data=json.dumps(self.secure_data(data)))
			else:
				self.plugin._logger.error('Unable to send data. Websocket not connected')

	def sendEvent(self, event, payload):
		data = {'event': event,
				'payload': payload
				}

		self.sendData(data)

	def authenticate(self):
		data = self.secure_data({'event': 'authenticate'})
		self.sendData(data)

	def secure_data(self, data):
		if 'token' not in data:
			data['token'] = self.plugin.get_token()
		return data
