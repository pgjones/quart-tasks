import asyncio
import logging
import sys
import zoneinfo
from datetime import datetime, timedelta, tzinfo
from typing import Awaitable, Callable, cast, List, Optional, Protocol, Tuple, TypeVar, Union

import click
from croniter import croniter
from quart import Quart
from quart.cli import pass_script_info, ScriptInfo

from .signals import got_task_exception
from .store import MemoryStore, TaskStoreABC

try:
    from asyncio import TaskGroup
except ImportError:
    from taskgroup import TaskGroup  # type: ignore

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

log = logging.getLogger(__name__)


class _TaskProtocol(Protocol):
    func: Callable
    name: str

    def get_next(self, start_time: datetime) -> datetime: ...


class _PeriodicTask:
    def __init__(self, period: timedelta, name: str, func: Callable) -> None:
        self.func = func
        self.name = name
        self.period = period

    def get_next(self, start_time: datetime) -> datetime:
        return start_time + self.period

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.period}, {self.name})"


class _CronTask:
    def __init__(self, cron_expression: str, name: str, func: Callable) -> None:
        self.croniter = croniter(cron_expression, ret_type=datetime)
        self.func = func
        self.name = name
        self.cron_expression = cron_expression

    def get_next(self, start_time: datetime) -> datetime:
        return self.croniter.get_next(start_time=start_time)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.cron_expression}, {self.name})"


class QuartTasks:
    def __init__(
        self,
        app: Optional[Quart] = None,
        *,
        store: Optional[TaskStoreABC] = None,
        tzinfo: Optional[tzinfo] = None,
    ) -> None:
        self._store: TaskStoreABC
        if store is None:
            self._store = MemoryStore()
        else:
            self._store = store
        self._tasks: List[_TaskProtocol] = []
        self._tzinfo = tzinfo
        self.after_task_funcs: list[Callable[[], Awaitable[None]]] = []
        self.before_task_funcs: list[Callable[[], Awaitable[None]]] = []

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        app.extensions["QUART_TASKS"] = self
        app.before_serving(self._before_serving)
        if self._tzinfo is None:
            self._tzinfo = zoneinfo.ZoneInfo(app.config.get("QUART_TASKS_TIMEZONE", "UTC"))
        app.cli.add_command(_run_tasks_command)
        app.cli.add_command(_list_tasks_command)
        self._app = app

    def cron(
        self,
        cron_expression: Optional[str] = None,
        /,
        *,
        seconds: Optional[str] = None,
        minutes: Optional[str] = None,
        hours: Optional[str] = None,
        day_of_month: Optional[str] = None,
        month: Optional[str] = None,
        day_of_week: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Add a cron task.

        This is designed to be used as a decorator, if used to
        decorate a synchronous function, the function will be wrapped
        in :func:`~quart.utils.run_sync` and run in a thread executor
        (with the wrapped function returned).

        The cron definition can either be given in the cron format, or
        as individual arguments. See for example
        https://crontab.guru/. An example usage,

        .. code-block:: python

            @app.cron("*/5 * * * *)
            async def infrequent_task():
                ...

        Arguments:
            cron_expression: The cron defintion.
            seconds: The seconds part of the cron definition.
            minutes: The minutes part of the cron definition.
            hours: The hours part of the cron definition.
            day_of_month: The day of month part of the cron definition.
            month: The month part of the cron definition.
            day_of_week: The day of week part of the cron definition.
            name: Name of the task, defaults to the function name.
        """

        if cron_expression is None and (
            minutes is None
            or hours is None
            or day_of_month is None
            or month is None
            or day_of_week is None
        ):
            raise ValueError("cron_expression or all individual parts must be specified")
        if cron_expression is None:
            cron_expression = f"{minutes} {hours} {day_of_month} {month} {day_of_week}"
            if seconds is not None:
                cron_expression = f"{cron_expression} {seconds}"

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            nonlocal name

            if name is None:
                name = func.__name__

            self._tasks.append(_CronTask(cron_expression, name, func))
            return func

        return decorator

    def periodic(
        self, period: timedelta, *, name: Optional[str] = None
    ) -> Callable[[Callable[P, T]], Callable[P, T]]:
        """Add a periodic task.

        This is designed to be used as a decorator, if used to
        decorate a synchronous function, the function will be wrapped
        in :func:`~quart.utils.run_sync` and run in a thread executor
        (with the wrapped function returned).

        .. code-block:: python

            @app.periodic(timedelta(seconds=5))
            async def frequent_task():
                ...

        Arguments:
            period: The period between task invocations.
            name: Name of the task, defaults to the function name.
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            nonlocal name

            if name is None:
                name = func.__name__

            self._tasks.append(_PeriodicTask(period, name, func))
            return func

        return decorator

    def before_task(
        self,
        func: Callable[[], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]:
        """Add a before task function.

        This will allow the function provided to be called once before
        any invocation of a task. This runs within the same app
        context as the task invocation.

        This is designed to be used as a decorator, if used to
        decorate a synchronous function, the function will be wrapped
        in :func:`~quart.utils.run_sync` and run in a thread executor
        (with the wrapped function returned). An example usage,

        .. code-block:: python

            @app.before_task
            async def func():
                ...

        Arguments:
            func: The function itself.

        """
        self.before_task_funcs.append(func)
        return func

    def after_task(
        self,
        func: Callable[[], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]:
        """Add a after task function.

        This will allow the function provided to be called once after
        any invocation of a task. This runs within the same app
        context as the task invocation.

        This is designed to be used as a decorator, if used to
        decorate a synchronous function, the function will be wrapped
        in :func:`~quart.utils.run_sync` and run in a thread executor
        (with the wrapped function returned). An example usage,

        .. code-block:: python

            @app.after_task
            async def func():
                ...

        Arguments:
            func: The function itself.

        """
        self.after_task_funcs.append(func)
        return func

    async def run(self, task_name: Optional[str] = None) -> None:
        await self._store.startup()
        async with TaskGroup() as task_group:
            for task in self._tasks:
                if task_name is None or task_name == task.name:
                    task_group.create_task(self._run_task(task))
        await self._store.shutdown()

    async def test_run(self, task_name: str) -> None:
        try:
            task = next(task for task in self._tasks if task_name == task.name)
        except StopIteration:
            raise ValueError(f"Task {task_name} not found")

        await self._store.startup()
        try:
            await self._invoke_task(task, reraise=True)
        finally:
            await self._store.shutdown()

    async def _run_task(self, task: _TaskProtocol) -> None:
        while not self._app.shutdown_event.is_set():
            wait, target = await self._get_next(task)
            log.debug("Task %s sleeping for %d", task.name, wait)
            await _sleep_or_shutdown(wait, cast(asyncio.Event, self._app.shutdown_event))

            if self._app.shutdown_event.is_set():
                return

            start = datetime.now(self._tzinfo)
            lag = (start - target).total_seconds()
            log.debug("Task %s lagged for %d", task.name, lag)

            await self._invoke_task(task)
            await self._store.set(task.name, start)

    async def _invoke_task(self, task: _TaskProtocol, *, reraise: bool = False) -> None:
        async with self._app.app_context():
            await self._preprocess_task()
            try:
                await self._app.ensure_async(task.func)()
            except Exception as error:
                await self._handle_exception(task, error)
                if reraise:
                    raise error
            finally:
                await self._postprocess_task()

    async def _before_serving(self) -> None:
        if self._app.config.get("QUART_TASKS_WHILST_SERVING", True):
            self._app.background_tasks.add(asyncio.get_event_loop().create_task(self.run()))

    async def _preprocess_task(self) -> None:
        for function in self.before_task_funcs:
            await self._app.ensure_async(function)()

    async def _postprocess_task(self) -> None:
        for function in self.after_task_funcs:
            await self._app.ensure_async(function)()

    async def _handle_exception(self, task: _TaskProtocol, error: Exception) -> None:
        await got_task_exception.send_async(
            self, _sync_wrapper=self._app.ensure_async, name=task.name, exception=error  # type: ignore # noqa
        )
        self._app.logger.error("Exception", exc_info=sys.exc_info())

    async def _get_next(self, task: _TaskProtocol) -> Tuple[Union[int, float], datetime]:
        now = datetime.now(self._tzinfo)
        next_execution = task.get_next(await self._store.get(task.name, now))
        return max((next_execution - now).total_seconds(), 0), next_execution


@click.command("run-tasks")
@click.argument("task_name", required=False)
@pass_script_info
def _run_tasks_command(info: ScriptInfo, task_name: Optional[str] = None) -> None:
    app = info.load_app()

    async def _inner() -> None:
        app.config["QUART_TASKS_WHILST_SERVING"] = False
        await app.startup()
        try:
            await app.extensions["QUART_TASKS"].run(task_name)
        finally:
            await app.shutdown()

    asyncio.run(_inner())


@click.command("list-tasks")
@pass_script_info
def _list_tasks_command(info: ScriptInfo) -> None:
    app = info.load_app()

    headers = ["Task name", "Schedule"]
    rows = []
    for task in app.extensions["QUART_TASKS"]._tasks:
        if isinstance(task, _CronTask):
            rows.append([task.name, task.cron_expression])
        elif isinstance(task, _PeriodicTask):
            rows.append([task.name, str(task.period)])

    rows.insert(0, headers)
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    rows.insert(1, ["-" * w for w in widths])
    template = "  ".join(f"{{{i}:<{w}}}" for i, w in enumerate(widths))

    for row in rows:
        click.echo(template.format(*row))


async def _sleep_or_shutdown(seconds: Union[int, float], shutdown_event: asyncio.Event) -> None:
    _, pending = await asyncio.wait(
        [
            asyncio.create_task(asyncio.sleep(seconds)),
            asyncio.create_task(shutdown_event.wait()),
        ],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.wait(pending)
