# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import yaml
import rich
import logging

from rich.logging import RichHandler

from c7n.provider import clouds
from c7n.exceptions import PolicyValidationError
from c7n.policy import PolicyCollection, load as policy_load
from c7n_terraform.console.base import console


log = logging.getLogger("c7n_terraform.commands")


def fetch_policies():
    pass


class Options(dict):
    metrics_enabled = metrics = False
    tracer = None
    cache = None
    cache_period = 0
    region = None
    dryrun = False
    account_id = None
    output_dir = "null"
    log_group = "null"

    def __init__(self, terraform_module=None):
        self.path = terraform_module


def load_policies(paths):
    errors = 0
    policies = PolicyCollection.from_data({}, Options())

    for p in paths:
        try:
            collection = policy_load(Options(), p)
        except IOError:
            continue
        except yaml.YAMLError as e:
            rich.print(
                "yaml syntax error loading policy file ({}) error:\n {}".format(p, e)
            )
            errors += 1
            continue
        except ValueError as e:
            rich.print("problem loading policy file ({}) error: {}".format(p, str(e)))
            errors += 1
            continue
        except PolicyValidationError as e:
            rich.print("invalid policy file: {} error: {}".format(p, str(e)))
            errors += 1
            continue

        if collection is None:
            log.debug("Loaded file {}. Contained no policies.".format(p))
        else:
            log.debug("Loaded file {}. Contains {} policies".format(p, len(collection)))
            policies = policies + collection

        # provider initialization
        provider_policies = {}
        for p in policies:
            provider_policies.setdefault(p.provider_name, []).append(p)

        policies = PolicyCollection.from_data({}, Options())
        for provider_name in provider_policies:
            provider = clouds[provider_name]()
            p_options = provider.initialize(Options())
            policies += provider.initialize_policies(
                PolicyCollection(provider_policies[provider_name], p_options),
                p_options)

    return policies


def setup_logging(level):
    if level <= 0:
        # print nothing
        log_level = logging.CRITICAL + 1
    elif level == 1:
        log_level = logging.ERROR
    elif level == 2:
        log_level = logging.WARNING
    elif level == 3:
        # default
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )
