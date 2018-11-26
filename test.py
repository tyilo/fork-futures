from concurrent.futures import ProcessPoolExecutor
from fork_futures import ForkPoolExecutor
import time
import math
import os


class FakePoolExecutor:
	def __init__(self, *args, **kwargs):
		pass

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


PROCESSES = os.cpu_count() or 1
FACT_N = 10**5 + 3 * 10**4
LARGE_INPUT = [[42] * 10**7 for _ in range(PROCESSES)]
TESTS = [
	('Exception test', exception_f, [None] * PROCESSES, identity, None),
	('Slow factorial test', slow_fact, list(range(FACT_N, FACT_N + PROCESSES)), math.log10, None),
	('Slow factorial test with 2 workers', slow_fact, list(range(FACT_N, FACT_N + PROCESSES)), math.log10, 2),
	('Large input test', dummy, LARGE_INPUT, identity, None),
	('Large input/output test', identity, LARGE_INPUT, len, None),
]


if __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('--debug', action='store_true')
	args = parser.parse_args()
	debug = args.debug

	print(f'Using {PROCESSES} processes')
	print()

	for name, f, arg_lists, out_f, max_workers in TESTS:
		print(f'{name}:')
		for cls in EXECUTOR_CLS:
			with cls() as executor:
				print(f'  {cls.__name__}:')
				start = time.time()
				with cls(max_workers=max_workers) as executor:
					try:
						for i, res in enumerate(executor.map(f, arg_lists)):
							if debug:
								print(f'    {i} {out_f(res)}')
					except BaseException as e:
						print(f'    Got exception: {e}')
				print(f'  Took {time.time() - start:.2f} s')
				print()
