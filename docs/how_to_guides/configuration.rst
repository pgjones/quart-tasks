Configuring Quart-Tasks
=======================

The following configuration options are used by Quart-Tasks. They
should be set as part of the standard `Quart configuration
<https://pgjones.gitlab.io/quart/how_to_guides/configuration.html>`_.

================================ ============ ================
Configuration key                type         default
-------------------------------- ------------ ----------------
QUART_TASKS_TIMEZONE             str          UTC
QUART_TASKS_WHILST_SERVING       bool         True
================================ ============ ================

``QUART_TASKS_TIMEZONE`` specifies the timezone the scheduled cron
tasks should run in.

``QUART_TASKS_WHILST_SERVING`` if set to ``False`` disable tasks from
running whilst the app is serving. (You'll likely want to use the
``run-tasks`` command with this option).
