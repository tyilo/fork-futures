from concurrent.futures import Executor
import os
import pickle
import signal


class ForkFuture:
	def __init__(self, executor, fn, *args, **kwargs):
		self._executor = executor

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
			self._done = False
			self._result = None
			self._exception = None
			self._done_callbacks = []

			os.close(w)
			self._fd = r
			self._worker_pid = pid
			self._executor.worker_pids.add(pid)

	def _callback(self, f):
		try:
			f(self)
		except Exception as e:
			print(f'Got exception from callback: {e}')
			pass

	def _wait(self, timeout=None):
		if self._done:
			return

		with os.fdopen(self._fd, 'rb') as f:
			success, result = pickle.load(f)
			self._executor.worker_pids.remove(self._worker_pid)

			if success:
				self._result = result
			else:
				self._exception = result

		self._done = True
		for f in self._done_callbacks:
			self._callback(f)

		self._done_callbacks = None

	def result(self, timeout=None):
		self._wait(timeout)
		if self._exception != None:
			raise self._exception
		else:
			return self._result

	def exception(self, timeout=None):
		return self._exception

	def add_done_callback(self, fn):
		if self._done:
			self._callback(fn)
		else:
			self._done_callbacks += [fn]

	def cancel(self):
		return self._done

	def cancelled(self):
		return False

	def running(self):
		return not self._done

	def done(self):
		return self._done

	def set_running_or_notify_cancel(self):
		raise NotImplementedError()

	def set_result(self, result):
		raise NotImplementedError()

	def set_exception(self, result):
		raise NotImplementedError()


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
