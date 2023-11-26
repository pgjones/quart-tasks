Quart-Tasks
===========

|Build Status| |docs| |pypi| |python| |license|

Quart-Tasks is a Quart extension that provides scheduled background
tasks.

Quickstart
----------

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

Note: the non-standard cron format (for seconds) is as defined by
`croniter
<https://github.com/kiorky/croniter?tab=readme-ov-file#about-second-repeats>_`.

The tasks will then run in the background as the app itself runs or
they can be run manually via the CLI ``quart run-tasks``.

Contributing
------------

Quart-Tasks is developed on `GitHub
<https://github.com/pgjones/quart-tasks>`_. If you come across an issue,
or have a feature request please open an `issue
<https://github.com/pgjones/quart-tasks/issues>`_. If you want to
contribute a fix or the feature-implementation please do (typo fixes
welcome), by proposing a `merge request
<https://github.com/pgjones/quart-tasks/merge_requests>`_.

Testing
~~~~~~~

The best way to test Quart-Tasks is with `Tox
<https://tox.readthedocs.io>`_,

.. code-block:: console

    $ pip install tox
    $ tox

this will check the code style and run the tests.

Help
----

The Quart-Tasks `documentation
<https://quart-tasks.readthedocs.io/en/latest/>`_ is the best places to
start, after that try searching `stack overflow
<https://stackoverflow.com/questions/tagged/quart>`_ or ask for help
`on gitter <https://gitter.im/python-quart/lobby>`_. If you still
can't find an answer please `open an issue
<https://github.com/pgjones/quart-tasks/issues>`_.


.. |Build Status| image:: https://github.com/pgjones/quart-tasks/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/pgjones/quart-tasks/commits/main

.. |docs| image:: https://readthedocs.org/projects/quart-tasks/badge/?version=latest&style=flat
   :target: https://quart-tasks.readthedocs.io/en/latest/

.. |pypi| image:: https://img.shields.io/pypi/v/quart-tasks.svg
   :target: https://pypi.python.org/pypi/Quart-Tasks/

.. |python| image:: https://img.shields.io/pypi/pyversions/quart-tasks.svg
   :target: https://pypi.python.org/pypi/Quart-Tasks/

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/pgjones/quart-tasks/blob/main/LICENSE
