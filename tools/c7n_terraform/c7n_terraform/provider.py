# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import MagicMock
import re

from c7n.registry import PluginRegistry
from c7n.provider import Provider, clouds

from c7n_terraform.resources.resource_map import ResourceMap
from c7n_terraform.filters.value import TerraformValueFilter

class Session:
    """Base class for API repository for a specified Cloud API."""

    def __init__(self, **kwargs):
        pass

    def __repr__(self):
        """The object representation.

        Returns:
            str: The object representation.
        """
        return "<tf-session>"

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

    def register(self, name, klass=None, condition=True,
                 condition_message="Missing dependency for {}",
                 aliases=None, match=None):
        if not condition and klass:
            return klass
        # invoked as function
        if klass:
            klass.type = name
            klass.type_aliases = aliases
            if match:
                klass.pattern = match
            self._factories[name] = klass
            return klass

        # invoked as class decorator
        def _register_class(klass):
            if not condition:
                return klass
            self._factories[name] = klass
            if match:
                klass.pattern = match
            klass.type = name
            klass.type_aliases = aliases
            return klass
        return _register_class


@clouds.register("tf")
class Terraform(Provider):

    display_name = "Terraform"
    resource_prefix = "tf"
    resources = DynamicPluginRegistry("%s.resources" % resource_prefix, "tf.resource.*")
    resource_map = ResourceMap

    def initialize(self, options):
        return options

    def initialize_policies(self, policy_collection, options):
        """Update the default execution mode to static if it's not already set"""
        for p in policy_collection:
            if not p.data.get('mode'):
                p.data['mode'] = {'type': 'static'}

        return policy_collection

    @staticmethod
    def initialize_resource(resource_class):
        resource_class.filter_registry.register('value', TerraformValueFilter)

    def get_session_factory(self, options):
        """Get a credential/session factory for api usage."""
        return Session()

    @classmethod
    def get_resource_types(cls, resource_types):
        to_add = set()
        to_remove = set()
        # TODO? Maybe? default_resource = cls.resources.fallback
        for resource_type in resource_types:
            if resource_type in cls.resource_map.keys():
                continue
            for resource in cls.resource_map.keys():
                if re.match("^"+resource+"$", resource_type):
                    to_add.add(resource)
                    to_remove.add(resource_type)
        resource_types.extend(to_add)
        resource_types = list(set(resource_types) - to_remove)
        return super().get_resource_types(resource_types)

resources = Terraform.resources
