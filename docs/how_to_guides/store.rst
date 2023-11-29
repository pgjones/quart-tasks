Persist job schedules
=====================

The default memory store used by Quart-Tasks is wiped every time the
app restarts. This is problematic if a task's invocation is missed
during a restart - as there is no way for Quart-Tasks to know and
hence it skips the invocation.

It is possible to change the store to one that persists invocation
times. If a task invocation is missed the store will return the
previous invocation thereby prompting a new invocation straight after
startup.

An example of a persisting store is shown below using `Quart-DB
<https://github.com/pgjones/quart-db>`_, note it is assumed the
database has a table called ``jobs`` with the columns ``name`` and
``executed`` with a unique constraint on the ``name`` column,

.. code-block:: python

    from quart import Quart
    from quart_db import QuartDB
    from quart_tasks import QuartTasks, TaskStoreABC

    app = Quart(__name__)
    quart_db = QuartDB(app)

    class DBStore(TaskStoreABC):
        def __init__(self) -> None:
            pass

        async def startup(self) -> None:
            pass

        async def get(self, key: str, default: datetime) -> datetime:
            async with quart_db.connection() as connection:
                result = await connection.fetch_val(
                    "SELECT executed FROM jobs WHERE name = :name",
                    {"name": key},
                )
                return default if result is None else result

        async def set(self, key: str, executed: datetime) -> None:
            async with quart_db.connection() as connection:
                await connection.execute(
                    """INSERT INTO jobs (name, executed)
                            VALUES (:name, :executed)
                       ON CONFLICT name DO UPDATE
                               SET executed = :executed""",
                    {"name": key, "executed": executed},
                )

        async def shutdown(self) -> None:
            pass

     quart_tasks = QuartTasks(app, store=DBStore())
