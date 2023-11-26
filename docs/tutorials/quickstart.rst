.. _quickstart:

Quickstart
==========

Quart-Tasks is used by associating it with an app and then registering
scheduled tasks,

.. code-block:: python

   from quart import Quart
   from quart_tasks import QuartTasks

   app = Quart(__name__)
   tasks = QuartTasks(app)

   @tasks.cron("*/5 * * * *")  # every 5 minutes
   async def infrequent_task():
       ...  # Do something

   @tasks.cron(
       seconds="*1/0",  # every 10 seconds
       minutes="*",
       hours="*",
       day_of_month="*",
       month="*",
       day_of_week="*",
   )
   async def frequent_task():
       ...  # Do something

   @tasks.periodic(timedelta(seconds=10))
   async def regular_task():
       ...  # Do Something
