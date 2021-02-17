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


class DynamicPluginRegistry(PluginRegistry):
    """Extends PluginRegistry to allow for a fallback other than None
    Will also test if a key is a regular expression pattern and matches
    the name requested
    """

    def __init__(self, plugin_type, fallback=None):
        super().__init__(plugin_type)
        self.fallback = fallback

    def get(self, name):
        factory = super().get(name)

        if factory:
            return factory

        return next(
            (
                v
                for k, v in self._factories.items()
                if hasattr(v, "pattern") and v.pattern.match(name)
            ),
            self.get_fallback(),
        )

    def get_fallback(self):
        if not self.fallback:
            return None
        return self._factories.get(self.fallback)

    def register(self, name, **kwargs):
        matcher = kwargs.pop("match", None)
        wrapper = super().register(name, **kwargs)

        def new_wrapper(klass):
            newcls = wrapper(klass)
            if matcher:
                newcls.pattern = matcher

        return new_wrapper


@clouds.register('tf')
class Terraform(Provider):

    display_name = 'Terraform'
    resource_prefix = 'tf'
    resources = DynamicPluginRegistry("%s.resources" % resource_prefix, "tf.resource.*")
    resource_map = ResourceMap

    def initialize(self, options):
        return options

    def initialize_policies(self, policy_collection, options):
        return policy_collection

    def get_session_factory(self, options):
        """Get a credential/session factory for api usage."""
        return Session()


resources = Terraform.resources
