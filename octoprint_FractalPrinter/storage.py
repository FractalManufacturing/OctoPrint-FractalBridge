from octoprint.filemanager import DiskFileWrapper
from octoprint.filemanager.destinations import FileDestinations
import octoprint.filemanager

from octoprint.server import eventManager
from octoprint.events import Events

class StorageManager:

	def __init__(self, plugin):
		self.plugin = plugin
		self.file_manager = plugin._file_manager

	def save_to_local_folder(self, currentFilename, currentPath, pathToFolder = '/Fractal/', print=False):
		wrapper = DiskFileWrapper(currentFilename, currentPath)
		canonPath, canonFilename = self.file_manager.canonicalize(FileDestinations.LOCAL, wrapper.filename)

		futureFilename = self.file_manager.sanitize_name(FileDestinations.LOCAL, canonFilename)
		futurePath = self.file_manager.sanitize_path(FileDestinations.LOCAL, pathToFolder)

		futureFullPath = self.file_manager.join_path(FileDestinations.LOCAL, futurePath, futureFilename)
		futureFullPathInStorage = self.file_manager.path_in_storage(FileDestinations.LOCAL, futureFullPath)

		if not self.plugin._printer.can_modify_file(futureFullPathInStorage, False):
			self.plugin.eventHandler.on_file_storage_fail("Impossible to save file to local storage")
			return None

		try:
			added_file = self.file_manager.add_file(FileDestinations.LOCAL, futureFullPathInStorage, wrapper,
											  allow_overwrite=True,
											  display=canonFilename)

		except octoprint.filemanager.storage.StorageError as e:
			self.plugin._logger.error(e.message)

			if e.code == octoprint.filemanager.storage.StorageError.INVALID_FILE:
				self.plugin.eventHandler.on_file_storage_fail("Could not upload the file \"{}\", invalid type".format(wrapper.filename))
				return None
			else:
				self.plugin.eventHandler.on_file_storage_fail("Could not upload the file \"{}\"".format(wrapper.filename))
				return None

		path = self.file_manager.path_on_disk(FileDestinations.LOCAL, added_file)

		if print:
			self.plugin.printerManager.printFile(path=path)

		# eventManager.fire(Events.UPLOAD, {"name": futureFilename,
		# 								  "path": added_file,
		# 								  "target": FileDestinations.LOCAL})

		return path
