fork-futures
============

Provides an alternative to [`concurrent.futures.ProcessPoolExecutor`][ProcessPoolExecutor] implemented
using fork.

This means that you can execute local functions in another process, without having to use [`dill`][dill] (and having to dill local variables). The arguments to the function executed are not pickled, only the return values.

`ForkPoolExecutor` can be used as a replacement for [`ProcessPoolExecutor`][ProcessPoolExecutor] and `ForkFuture` as a replacement for [`Future`][Future].

Not all of the [`Executor`][Executor] or [`Future`][Future] API has been implemented.


[ProcessPoolExecutor]: https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor
[Executor]: https://docs.python.org/3/library/concurrent.futures.html#executor-objects
[Future]: https://docs.python.org/3/library/concurrent.futures.html#future-objects
[dill]: https://pypi.org/project/dill/
