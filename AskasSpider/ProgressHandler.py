from datetime import datetime


class ProgressHandler():
	filename = 'progress.txt'
	hasChanged = 0

	def append(self, data, newline=True):

		with open(self.filename, 'a') as f:
			f.write(str(datetime.now().time()).split('.')[0] + " " + data)
			if newline:
				f.write('\n')

