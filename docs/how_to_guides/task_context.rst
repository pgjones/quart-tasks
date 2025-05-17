Running within the task context
===============================

It can be useful, especially when testing, to run code within the same
context that the task would run in. Specifically this means that the
before task functions have run and within an app context. To do so
use the ``task_context`` async context,

.. code-block:: python

    from quart import g, Quart
    from quart_db import QuartDB
    from quart_tasks import QuartTasks

    app = Quart(__name__)
    quart_tasks = QuartTasks(app)

    async def test_func():
        async with quart_tasks.task_context():
            await func()
