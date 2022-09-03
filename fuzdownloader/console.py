import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    FileSizeColumn,
    Progress,
    SpinnerColumn,
    track,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TotalFileSizeColumn,
    TransferSpeedColumn,
)

from .context import *
from .param import *


class RichConsole:
    def __init__(self) -> None:
        self.cnsl = Console()
        self.single_progress = None
        self.single_progress_task_id = None

    def create_single_progress(self, content="", total=100) -> None:
        self.single_progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            SpinnerColumn(spinner_name="arc", finished_text="✓"),
            BarColumn(),
            TextColumn("[{task.completed}/{task.total}]\t"),
            TextColumn(context.console_t("remaining")),
            TimeRemainingColumn(),
            TextColumn(context.console_t("elapsed")),
            TimeElapsedColumn(),
        )
        self.single_progress.start()
        self.single_progress_task_id = self.single_progress.add_task(
            SINDENT + content, total=total
        )

    def update_single_progress(self, content="", advance=0) -> None:
        self.single_progress.update(
            self.single_progress_task_id, advance=advance, description="　　" + content
        )

    def advance_single_progress(self, advance=1) -> None:
        self.single_progress.update(self.single_progress_task_id, advance=advance)

    def terminal_single_progress(self) -> None:
        self.single_progress.stop()

    def panel(
        self,
        renderable,
        *,
        title=None,
        title_align="center",
        subtitle=None,
        subtitle_align="center",
        safe_box=None,
        expand=True,
        style="none",
        border_style="none",
        width=None,
        height=None,
        padding=(0, 1),
        highlight=False
    ) -> None:
        self.cnsl.print(
            Panel(
                renderable,
                title=title,
                title_align=title_align,
                subtitle=subtitle,
                subtitle_align=subtitle_align,
                safe_box=safe_box,
                expand=expand,
                style=style,
                border_style=border_style,
                width=width,
                height=height,
                padding=padding,
                highlight=highlight,
            )
        )


rich = RichConsole()
