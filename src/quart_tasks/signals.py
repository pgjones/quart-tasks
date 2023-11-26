from blinker import Namespace

_signals = Namespace()

#: Called if there is an exception during a task invocation, connected
# functions should have a signature of Callable[[str, Exception],
# None] where the first argument is the task name.
got_task_exception = _signals.signal("got-task-exception")
