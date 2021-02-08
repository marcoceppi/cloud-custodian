# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import MagicMock

from c7n.registry import PluginRegistry
from c7n.provider import Provider, clouds

from functools import partial

from c7n_terraform.resources.resource_map import ResourceMap


class Session:
    """Base class for API repository for a specified Cloud API."""

    def __init__(self, **kwargs):
        pass

    def __repr__(self):
        """The object representation.

        Returns:
            str: The object representation.
        """
        return '<tf-session>'

    def client(self, service_name, version, component, **kw):

        return MagicMock()


@clouds.register('tf')
class Terraform(Provider):

    display_name = 'Terraform'
    resource_prefix = 'tf'
    resources = PluginRegistry('%s.resources' % resource_prefix)
    resource_map = ResourceMap

    def initialize(self, options):
        return options

    def initialize_policies(self, policy_collection, options):
        return policy_collection

    def get_session_factory(self, options):
        """Get a credential/session factory for api usage."""
        return Session()


resources = Terraform.resources
