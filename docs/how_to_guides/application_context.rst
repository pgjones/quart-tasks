Using the app context
=====================

Tasks invocated by Quart-Tasks run within an application context,
which means the Quart globals ``current_app`` and ``g`` are
available. This allows for storage on ``g``.

For example a DB connection can be made available within the task
using `QuartDB <https://github.com/pgjones/quart-db/>`_,

.. code-block:: python

    from datetime import timdelta

    from quart import g, Quart
    from quart_db import QuartDB
    from quart_tasks import QuartTasks

    app = Quart(__name__)
    quart_db = QuartDB(app)
    quart_tasks = QuartTasks(app)

    @quart_tasks.before_task
    async def setup():
        g.connection = await quart_db.acquire()


    @quart_tasks.after_task
    async def cleanup():
        await quart_db.release(g.connection)
        g.connection = None

    @quart_tasks.periodic(timedelta(seconds=10))
    async def frequent_task():
        # It is likely you'll want to do something more useful
        g.connection.execute("SELECT COUNT(*) FROM visits")
