fork-futures
------------

Provides an alternative to concurrent.futures.ProcessPoolExecutor_ implemented
using fork.

This means that you can execute local functions in another process, without having to use dill_ (and having to dill local variables). The arguments to the function executed are not pickled, only the return values.

``ForkPoolExecutor`` can be used as a replacement for ProcessPoolExecutor_ and ``ForkFuture`` as a replacement for Future_.

Not all of the Executor_ or Future_ API has been implemented.

.. _concurrent.futures.ProcessPoolExecutor: https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor
.. _Executor: https://docs.python.org/3/library/concurrent.futures.html#executor
.. _ProcessPoolExecutor: https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor
.. _Future: https://docs.python.org/3/library/concurrent.futures.html#future
.. _dill: https://pypi.org/project/dill/