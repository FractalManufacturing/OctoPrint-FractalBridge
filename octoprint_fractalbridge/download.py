import threading
import queue
import requests


class Worker(threading.Thread):

	def __init__(self, manager):
		super(Worker, self).__init__()
		self.manager = manager
		self.plugin = manager.plugin
		self.daemon = True

	def run(self):
		queue = self.manager.queue

		while True:
			fileData = queue.get()

			if fileData == 'end':
				return

			if 'url' in fileData:
				download_endpoint = fileData['url']
				download_url = self.plugin._settings.get(['api_url']) + download_endpoint
				filename = fileData['filename']
				print_after = fileData['print_after']
				added_file = None

				try:
					r = requests.get(url=download_url, stream=True)
					fullPath = "%s/%s" % (self.plugin._basefolder, filename)

					if r.status_code == 200:
						with open(fullPath, 'wb') as file:
							chunk_size = 50000
							for chunk in r.iter_content(chunk_size):
								file.write(chunk)

					r.raise_for_status()

					added_file = self.plugin.storageManager.save_to_local_folder(filename, fullPath, print_after=print_after)

				except Exception as e:
					self.manager.plugin._logger.error('Error downloading file', e)
					self.plugin.eventHandler.on_file_download_fail('File downlaod error')

				if added_file:
					fileData['path'] = added_file
					self.plugin.DBManager.addFile(fileData)

			else:
				self.manager.plugin._logger.error('No download URL in printInfo')

			queue.task_done()

class DownloadManager:

	def __init__(self, plugin):
		self.plugin = plugin
		self.workers = []
		self.queue = queue.Queue()
		for i in range(1):
			worker = Worker(self)
			self.workers.append(worker)
			worker.start()

	def enqueue(self, printInfo):
		self.queue.put(printInfo)


	def terminateWorkers(self):
		for i in range(len(self.workers)):
			self.queue.put('end')
