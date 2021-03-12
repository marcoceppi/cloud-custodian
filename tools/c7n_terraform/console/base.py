# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from rich.console import Console, render_group
from rich.theme import Theme
from rich.style import Style
from rich.text import Text
from rich.syntax import Syntax
from rich.rule import Rule


style = {
    "pass": "[green bold]•[/]",
    "skipped": "[dark grey dim bold]•[/]",
    "failure": "[red bold]F[/]",
    "error": "[red bold]E[/]",
}


class Status:
    success = "pass"
    skip = "skipped"
    fail = "failure"
    error = "error"

    @staticmethod
    def icon(status):
        s = style.get(status)
        if not s:
            raise KeyError("Not a valid status")
        return s


theme = Theme(
    {
        "pass": "green",
        "skipped": "bright_black",
        "failure": "red",
        "error": "red",
        "info": "dim cyan",
        "warning": "magenta",
        "danger": "bold red",
        "scenario": "green",
        "action": "green",
        "section_title": "bold cyan",
        "logging.level.notset": Style(dim=True),
        "logging.level.debug": Style(color="white", dim=True),
        "logging.level.info": Style(color="blue"),
        "logging.level.warning": Style(color="red"),
        "logging.level.error": Style(color="red", bold=True),
        "logging.level.critical": Style(color="red", bold=True),
        "logging.level.success": Style(color="green", bold=True),
    }
)

console = Console(theme=theme, log_path=False)


def setup_console(force_color=None):
    global console
    kwargs = {
        "theme": theme,
        "log_path": False,
    }

    if force_color is not None:
        kwargs["force_terminal"] = force_color
        kwargs["width"] = 151
        kwargs["no_color"] = not force_color

    console = Console(**kwargs)


@render_group()
def source_contexts(resource, before=3, after=3, prefix=None):
    source = resource.get("source")
    data = resource.get("data", {})
    filters = data.get("c7n:MatchedFilters")

    if not source or not filters:
        return

    def extract_token(s):
        s = s.strip()
        if " " in s:
            return s.split(" ")[0]
        return s

    # TODO: this is not going to actually work for complex matches
    matches = [ln for ln, line in source["lines"] if extract_token(line) in filters]

    if not matches:
        matches = [source["start"]]

    file_name = None

    if prefix:
        try:
            file_name = resource["path"].relative_to(prefix)
        except ValueError:
            pass

    if not file_name:
        file_name = resource["path"]

    yield Text(str(file_name))

    for ln in matches:
        start = ln - before
        end = ln + after

        if start < source["start"]:
            start = source["start"]

        if end > source["end"]:
            end = source["end"]

        code = [line for lnx, line in source["lines"] if start <= lnx <= end]

        yield Syntax(
            "".join(code),
            lexer_name="terraform",
            background_color="default",
            line_numbers=True,
            start_line=start,
            highlight_lines=[ln],
        )

        if len(matches) > 1:
            yield Rule(style="white dim")
