Testing a task
==============

To test a task Quart-Tasks provides a special ``test_run`` method,

.. code-block:: python

    quart_tasks = QuartTasks(app)

    @quart_tasks.periodic(timedelta(seconds=2))
    async def my_task() -> None:
        ...  # Do something

    async def test_my_task() -> None:
        quart_tasks.test_run("my_task")
        assert ...  # Task has resulted in expected changes

This is better than running ``my_task`` directly as it ensures that
the before and after task functions are called.

If the task raises and exception that will be raised from the
``test_run`` method e.g.

.. code-block:: python

    async def test_my_task_raises() -> None:
        with pytest.raises(Exception):  # For example
            quart_tasks.test_run("my_task")
