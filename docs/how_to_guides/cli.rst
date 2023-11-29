Command line usage
==================

By default Quart-Tasks runs whilst the app is serving requests. This
is not required and Quart-Tasks can run standalone via the command,

.. code-block:: sh

    quart run-tasks

This command also accepts an optional task name argument if you only
want to run a specific task.

Alternatively a list of what tasks have been registered can be shown
via the command,

.. code-block:: sh

    quart list-tasks
