"""Outputs for user info."""

import git
import rich
import rich.console
import rich.live
import rich.progress
import rich.table

# 1. Define the known operation names
OP_CODES = [
    "BEGIN",
    "CHECKING_OUT",
    "COMPRESSING",
    "COUNTING",
    "END",
    "FINDING_SOURCES",
    "RECEIVING",
    "RESOLVING",
    "WRITING",
]

# 2. Build the map using a dictionary comprehension
# It maps the integer value to its string name
OP_CODE_MAP = {getattr(git.RemoteProgress, op_code): op_code for op_code in OP_CODES}

PROGRESS_TOTAL = rich.progress.Progress(
    rich.progress.TextColumn("Project: [progress.description]{task.description:30}"),
    rich.progress.BarColumn(),
    rich.progress.MofNCompleteColumn(),
)
PROGRESS_PROJECT = rich.progress.Progress(
    rich.progress.TextColumn("Step:    [progress.description]{task.description:30}"),
    rich.progress.BarColumn(),
    rich.progress.TextColumn("[green][progress.completed]{task.completed}%"),
)
TASK_TOTAL = PROGRESS_TOTAL.add_task(description="", total=0)
TASK_PROJECT = PROGRESS_PROJECT.add_task(description="", total=100)
TABLE = rich.table.Table()
CONSOLE = rich.console.Console()
LIVE = rich.live.Live(console=CONSOLE, refresh_per_second=10)
LIVE.start()


class CloneProgress(git.RemoteProgress):
    """Override git.RemoteProgress to update progress bars."""

    last_op_code = None

    def update(self, op_code: str, cur_count: int, max_count: int | None = None, message: str = "") -> None:
        """Get updates from git, pass to rich output."""
        # If the op_code changes, reset the counter and change name on the progress bar.
        if op_code != self.last_op_code:
            PROGRESS_PROJECT.reset(TASK_PROJECT)
            self.last_op_code = op_code

        # Caulcate the percentage done for this op_code
        percent = 0
        if max_count:
            percent = int((cur_count / max_count) * 100)
        description = OP_CODE_MAP.get(op_code, "").title()

        # Update the project's progress bar
        PROGRESS_PROJECT.update(TASK_PROJECT, description=description, completed=percent)
        # Push to terminal
        LIVE.update(rich.console.Group(TABLE, PROGRESS_PROJECT, PROGRESS_TOTAL), refresh=True)
