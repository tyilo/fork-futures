from concurrent.futures import Executor
import os
import pickle
import signal


class ForkFuture:
	def __init__(self, executor, fn, *args, **kwargs):
		self.executor = executor
		r, w = os.pipe()
		pid = os.fork()
		if pid == 0:
			os.close(r)
			try:
				try:
					result = (True, fn(*args, **kwargs))
				except BaseException as e:
					result = (False, e)

				with os.fdopen(w, 'wb') as f:
					pickle.dump(result, f)
			finally:
				# Make sure no finally or __exit__ handlers are called
				os.kill(os.getpid(), signal.SIGTERM)
		else:
			os.close(w)
			self.fd = r
			self.worker_pid = pid
			executor.worker_pids.add(pid)

	def cancel(self):
		pass

	def result(self):
		with os.fdopen(self.fd, 'rb') as f:
			success, result = pickle.load(f)
			self.executor.worker_pids.remove(self.worker_pid)

			if success:
				return result
			else:
				raise result


class ForkPoolExecutor(Executor):
	def __init__(self):
		self.worker_pids = set()

	def submit(self, fn, *args, **kwargs):
		f = ForkFuture(self, fn, *args, **kwargs)
		return f

	def kill(self):
		for pid in self.worker_pids:
			os.kill(pid, signal.SIGKILL)

	def shutdown(self, wait=True):
		if wait == False:
			return
		for pid in self.worker_pids:
			os.waitpid(pid, 0)
