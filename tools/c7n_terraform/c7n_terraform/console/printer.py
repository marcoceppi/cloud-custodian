# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from rich import box
from rich.console import RenderGroup
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from c7n_terraform.console.base import console as default_console, source_contexts, Status


class TestCase:

    def __init__(self, name):
        self.name = name
        self.results = []

    def start(self):
        pass

    def add_result(self, result, policy, resources):
        self.results.append({
            'resources': resources,
            'policy': policy,
            'result': result,
        })

    def finish(self):
        pass


class Printer:

    def __init__(self, console=None):
        self.console = console or default_console
        self.cases = {}

    def add_test_case(self, name):
        if name not in self.cases:
            self.cases[name] = TestCase(name)

        return self.cases[name]

    def start_test_case(self, name):
        if name not in self.cases:
            return self.add_test_case(name)
        self.cases[name].start()

        return self.cases[name]

    def add_test_result(self, name, result, policy, resources):
        self.cases[name].add_result(result, policy, resources)
        return self.cases[name]

    def complete_test_case(self, name):
        self.cases[name].finish()

    def print_summary(self):
        pass


class FullPrinter(Printer):

    _padding = None

    def __init__(self, console=None):
        super().__init__(console)
        self._grid = {}

    @property
    def padding(self):
        if self._padding:
            return self._padding

        pad = 0
        for case in self.cases.values():
            l = len(case.name)
            if l > pad:
                pad = l

        self._padding = pad + 2
        return self._padding

    def add_test_case(self, name):
        super().add_test_case(name)
        self._grid[name] = Table(
            "Policy",
            "Context",
            show_header=False,
            show_edge=False,
            expand=True,
            show_lines=True,
            box=box.HEAVY,
        )

    def start_test_case(self, name):
        super().start_test_case(name)
        self.console.print(name, style="cyan", end=" " * (self.padding - len(name)))

    def add_test_result(self, name, result, policy, resources):
        c = super().add_test_result(name, result, policy, resources)
        self.console.print(Status.icon(result), end="")
        if result == Status.success:
            return c

        self._grid[name].add_row(
            f"[bold]{policy.name}[/]\n\n[bold]Description: [/]{policy.data.get('description', '')}",
            RenderGroup(*[source_contexts(resource) for resource in resources]),
        )

        return c

    def complete_test_case(self, name):
        super().complete_test_case(name)
        self.console.print("")

    def print_summary(self):
        for case in self.cases.values():
            failures = any([result["result"] != Status.success for result in case.results])

            if not failures:
                continue

            self.console.print(
                Panel(
                    self._grid[case.name],
                    title=Text(case.name, style="cyan bold"),
                    border_style="red",
                    width=150,
                )
            )
