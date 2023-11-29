import asyncio
from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from quart import Quart

from quart_tasks import QuartTasks
from quart_tasks.extension import _CronTask, _PeriodicTask


def test_periodic_get_next() -> None:
    task = _PeriodicTask(timedelta(seconds=2), "task", lambda: None)
    with freeze_time(datetime(2023, 11, 26, 16, 0)):
        assert task.get_next(datetime.now()) == datetime.now() + timedelta(seconds=2)


@pytest.mark.parametrize(
    "cron, expected",
    [
        ("*/5 * * * *", datetime(2023, 11, 26, 16, 5)),
        ("2 4 * * mon,fri", datetime(2023, 11, 27, 4, 2)),
    ],
)
def test_cron_get_next(cron: str, expected: datetime) -> None:
    task = _CronTask(cron, "task", lambda: None)
    with freeze_time(datetime(2023, 11, 26, 16, 0)):
        assert task.get_next(datetime.now()) == expected


async def test_complete() -> None:
    app = Quart(__name__)
    quart_tasks = QuartTasks(app)

    before = False
    after = False
    has_run = asyncio.Event()

    @quart_tasks.before_task
    async def setup() -> None:
        nonlocal before
        before = True

    @quart_tasks.after_task
    async def cleanup() -> None:
        nonlocal after
        after = True

    @quart_tasks.periodic(timedelta(microseconds=10))
    async def job() -> None:
        has_run.set()

    await app.startup()
    await has_run.wait()
    await app.shutdown()
    assert before
    assert after


async def test_testing() -> None:
    app = Quart(__name__)
    quart_tasks = QuartTasks(app)

    before = False
    after = False
    has_run = asyncio.Event()

    @quart_tasks.before_task
    async def setup() -> None:
        nonlocal before
        before = True

    @quart_tasks.after_task
    async def cleanup() -> None:
        nonlocal after
        after = True

    @quart_tasks.periodic(timedelta(microseconds=10))
    async def job() -> None:
        has_run.set()

    await quart_tasks.test_run("job")
    assert before
    assert after
    assert has_run.is_set()
