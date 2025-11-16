"""
Async Scheduler for Gulf of Mexico

Provides non-blocking async execution with cooperative multitasking.
"""

from typing import Optional
import time

from gulfofmexico.builtin import (
    GulfOfMexicoPromise,
    GulfOfMexicoValue,
    GulfOfMexicoUndefined,
)


@dataclass
class AsyncTask:
    """Represents a pending async task."""

    promise: GulfOfMexicoPromise
    code_statements: list
    namespaces: list
    when_watchers: list
    current_statement: int = 0
    is_complete: bool = False


@dataclass
class DelayedTask:
    """Represents a task to execute after a delay."""

    execute_after: float  # Unix timestamp
    code_statements: list
    namespaces: list
    when_watchers: list


class AsyncScheduler:
    """
    Cooperative async scheduler for Gulf of Mexico.

    Maintains queues of pending async tasks and delayed (after) tasks.
    Provides tick() method to advance execution of all pending work.
    """

    def __init__(self):
        self.pending_tasks: list[AsyncTask] = []
        self.delayed_tasks: list[DelayedTask] = []
        self.tick_count: int = 0

    def register_async_task(
        self,
        promise: GulfOfMexicoPromise,
        code_statements: list,
        namespaces: list,
        when_watchers: list,
    ) -> None:
        """Register a new async task for cooperative execution."""
        task = AsyncTask(
            promise=promise,
            code_statements=code_statements,
            namespaces=namespaces,
            when_watchers=when_watchers,
            current_statement=0,
            is_complete=False,
        )
        self.pending_tasks.append(task)

    def register_delayed_task(
        self,
        delay_seconds: float,
        code_statements: list,
        namespaces: list,
        when_watchers: list,
    ) -> None:
        """Register a task to execute after a delay."""
        task = DelayedTask(
            execute_after=time.time() + delay_seconds,
            code_statements=code_statements,
            namespaces=namespaces,
            when_watchers=when_watchers,
        )
        self.delayed_tasks.append(task)

    def tick(self) -> int:
        """
        Execute one step of all pending work.

        Returns the number of tasks that made progress.
        """
        from gulfofmexico.interpreter import interpret_code_statements

        self.tick_count += 1
        progress_count = 0
        current_time = time.time()

        # Process delayed tasks that are ready
        ready_delayed = []
        remaining_delayed = []
        for task in self.delayed_tasks:
            if current_time >= task.execute_after:
                ready_delayed.append(task)
            else:
                remaining_delayed.append(task)

        self.delayed_tasks = remaining_delayed

        for task in ready_delayed:
            # Execute delayed task immediately
            interpret_code_statements(
                task.code_statements,
                task.namespaces,
                [],  # No async statements - execute synchronously
                task.when_watchers,
                {},
                [],
            )
            progress_count += 1

        # Process async tasks - execute one statement per task per tick
        remaining_tasks = []
        for task in self.pending_tasks:
            if task.is_complete:
                continue

            if task.current_statement >= len(task.code_statements):
                # Task completed
                task.is_complete = True
                if task.promise:
                    # Resolve promise with undefined (no explicit return)
                    task.promise.value = GulfOfMexicoUndefined()
                progress_count += 1
                continue

            # Execute one statement
            statement_group = task.code_statements[task.current_statement]
            try:
                result = interpret_code_statements(
                    [statement_group],  # Execute one statement group
                    task.namespaces,
                    [],  # No async - we're the scheduler
                    task.when_watchers,
                    {},
                    [],
                )

                # Check if this was a return statement
                if result is not None:
                    task.is_complete = True
                    if task.promise:
                        task.promise.value = result
                    progress_count += 1
                else:
                    task.current_statement += 1
                    remaining_tasks.append(task)
                    progress_count += 1
            except Exception:
                # Task failed - mark complete and don't add back
                task.is_complete = True
                if task.promise:
                    task.promise.value = GulfOfMexicoUndefined()
                # Re-raise to propagate error
                raise

        self.pending_tasks = remaining_tasks
        return progress_count

    def has_pending_work(self) -> bool:
        """Check if there are any pending or delayed tasks."""
        return len(self.pending_tasks) > 0 or len(self.delayed_tasks) > 0

    def run_until_complete(self, max_ticks: int = 10000) -> None:
        """Run the scheduler until all work is complete or max_ticks reached."""
        ticks = 0
        while self.has_pending_work() and ticks < max_ticks:
            self.tick()
            ticks += 1
            if ticks >= max_ticks:
                raise RuntimeError(f"Async scheduler exceeded {max_ticks} ticks")

    def clear(self) -> None:
        """Clear all pending tasks (useful for REPL reset)."""
        self.pending_tasks.clear()
        self.delayed_tasks.clear()
        self.tick_count = 0


# Global scheduler instance
_global_scheduler: Optional[AsyncScheduler] = None


def get_scheduler() -> AsyncScheduler:
    """Get or create the global async scheduler."""
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = AsyncScheduler()
    return _global_scheduler


def reset_scheduler() -> None:
    """Reset the global scheduler (useful for testing/REPL)."""
    global _global_scheduler
    _global_scheduler = AsyncScheduler()
