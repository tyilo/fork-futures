from concurrent.futures import ProcessPoolExecutor
from fork_futures import ForkPoolExecutor
import time
import math


class FakePoolExecutor:
	def map(self, func, *iterables):
		for args in zip(*iterables):
			yield func(*args)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass


EXECUTOR_CLS = [ForkPoolExecutor, ProcessPoolExecutor, FakePoolExecutor]


def exception_f(n):
	raise Exception('should be expected')

def slow_fact(n):
	r = 1
	for i in range(1, n):
		r *= i
	return r

def dummy(arg):
	return None

def identity(arg):
	return arg


PROCESSES = 5
FACT_N = 10**5 + 3 * 10**4
LARGE_INPUT = [[42] * 10**8 for _ in range(PROCESSES)]
TESTS = [
	('Exception test', exception_f, [None] * PROCESSES, identity),
	('Slow factorial test', slow_fact, list(range(FACT_N, FACT_N + PROCESSES)), math.log10),
	('Large input test', dummy, LARGE_INPUT, identity),
	('Large input/output test', identity, LARGE_INPUT, len),
]


if __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('--debug', action='store_true')
	args = parser.parse_args()
	debug = args.debug

	for name, f, arg_lists, out_f in TESTS:
		print(f'{name}:')
		for cls in EXECUTOR_CLS:
			with cls() as executor:
				print(f'  {cls.__name__}:')
				start = time.time()
				with cls() as executor:
					try:
						for i, res in enumerate(executor.map(f, arg_lists)):
							if debug:
								print(f'    {i} {out_f(res)}')
					except BaseException as e:
						print(f'    Got exception: {e}')
				print(f'  Took {time.time() - start:.2f} s')
				print()
