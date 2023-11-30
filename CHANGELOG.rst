0.2.2 2023-11-30
----------------

* Bugfix register the list-tasks command so that is can be used.

0.2.1 2023-11-29
----------------

* Bugfix actually implement the keyword argument cron expression.

0.2.0 2023-11-29
----------------

* Change the name evaulation to match Quart (tasks are now named using
  the function name).
* Allow a specific task to run via the command line by task name.
* Make it easier to test tasks via a test_run(task_name) method.
* Add a command to list the tasks, ``quart list-tasks``.

0.1.0 2023-11-27
----------------

* Basic initial release.
