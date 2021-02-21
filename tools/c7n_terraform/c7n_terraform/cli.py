# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import typer
import rich
import logging

from enum import Enum
from pathlib import Path
from typing import List

from c7n_terraform.commands import load_policies, setup_logging


app = typer.Typer()
log = logging.getLogger("c7n_terraform.cli")


class OutputReporter(str, Enum):
    junit = "junit"
    json = "json"


@app.command()
def validate(name: str):
    typer.echo(f"Hello {name}")


@app.command()
def run(
    paths: List[Path] = typer.Argument(
        ..., help="Path(s) to terraform modules to check"
    ),
    policies: List[Path] = typer.Option(
        ..., "--policy", "-p", help="One or more policies sources for checking"
    ),
    verbose: int = typer.Option(3, "--verbose", "-v", count=True),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Mute output"),
    color: bool = typer.Option(True, help="Show rich, colorized output"),
    reporter: OutputReporter = typer.Option(
        OutputReporter.junit, help="Output formatting, requires --output"
    ),
    output: Path = typer.Option(
        None, "--output", "-o", help="File to output run data to"
    ),
    policy_filter: List[str] = typer.Option(
        None, "--filter-policy", "-f", help="Only use named/matched policies"
    ),
    resource_filter: List[str] = typer.Option(
        None,
        "--filter-resource",
        "-t",
        help="Only use policies with the given resource type",
    ),
):
    # Load policies and extract all `tf` policies
    # Find all "terraform modules"
    # Loop over each module and throw policies at it
    # Collect and display output

    setup_logging(verbose if not quiet else 0)
    policy_files = []
    modules = set()

    for p in policies:
        if not p.exists():
            continue

        if p.is_file():
            policy_files.append(p)

        policy_files.extend(list(p.rglob("*.y*ml")))

    for m in paths:
        if not m.exists():
            # Chuck it into an error and move on
            rich.print("[red] {} is not a valid path".format(m.resolve()))
            raise typer.Exit(1)

        matched_files = list(m.rglob("*.tf"))
        matched_files.extend(list(m.rglob("*.tf.json")))

        for match in matched_files:
            modules.add(match.parent)

    all_policies = load_policies(policy_files)
    collection = all_policies.filter(policy_filter or [], resource_filter or [])
    rich.print(policy_files)
    rich.print(collection.policies)
    rich.print(modules)

    for module in modules:
        log.info(f"Evaluating {str(module)}.")
        for policy in collection:
            log.info(f" - Running Policy: {policy.name}")
            policy.ctx.options.path = module
            policy()
