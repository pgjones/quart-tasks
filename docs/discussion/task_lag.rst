Task lag
========

Quart-Tasks works by sleeping till a task is due to be invoked and
then waking to invoke the task. This means the task may not be invoked
at the exact time specified by either the cron format or period. The
difference between the specified time and actual start time is termed
the lag.

In addition each task must finish an invocation before the next
invocation can start, so if the period between invocations is shorter
than the execution time the lag will only increase.
