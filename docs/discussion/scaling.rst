Scaling with Quart-Tasks
========================

As you add more, or more computationally intensive, tasks you will
find the performance of the web server suffers as the event loop
spends more time on the tasks than serving requests. When this happens
it is best to split the runtimes so that the web server doesn't run
tasks (via the ``QUART_TASKS_WHILST_SERVING`` configuration setting)
and the task runtime only runs tasks (via the ``quart run-tasks``
command).

Also note that CPU bound tasks should ideally be defined as a sync
function so that it is run in a thread.
