Adding tasks at runtime
=======================

A task added using the decorator form will be added at import time and
hence start during the app's startup. However, if the task can only be
defined at runtime or should only start at runtime it is better to use
the alternative task addition forms,

.. code-block:: python

    async def infrequent_task():
        ...

    tasks.add_cron_task(infrequent_task, "*/5 * * * *)

    async def frequent_task():
        ...

    tasks.add_periodic_task(timedelta(seconds=5), frequent_task)
