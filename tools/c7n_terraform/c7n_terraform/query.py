# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import logging

from unittest.mock import MagicMock
from c7n.manager import ResourceManager
from c7n.actions import ActionRegistry
from c7n.filters import FilterRegistry
from c7n.query import sources, MaxResourceLimit

from c7n_terraform.parser import Parser, TerraformVisitor, VariableResolver


log = logging.getLogger("c7n_terraform.query")
# TODO: Make a NOOP Cache manager
CacheManager = MagicMock()
CacheManager.load.side_effect = [False]
CacheManager.size.return_value = 0


@sources.register("describe-tf")
class DescribeSource:
    _query_cache = None

    def __init__(self, manager):
        self.manager = manager

    def get_resources(self, query):
        if query is None:
            return self.query.blocks
        return list(self.query.iter_blocks(tf_kind=query))

    def augment(self, resources):
        return resources

    @property
    def query(self):
        if not self._query_cache:
            data = Parser().parse_module(self.manager.ctx.options.path)
            self._query_cache = TerraformVisitor(data, self.manager.ctx.options.path)
            self._query_cache.visit()
            VariableResolver(self._query_cache).resolve()
        return self._query_cache


class QueryMeta(type):
    """metaclass to have consistent action/filter registry for new resources."""

    def __new__(cls, name, parents, attrs):
        if "filter_registry" not in attrs:
            attrs["filter_registry"] = FilterRegistry("%s.filters" % name.lower())
        if "action_registry" not in attrs:
            attrs["action_registry"] = ActionRegistry("%s.actions" % name.lower())

        return super(QueryMeta, cls).__new__(cls, name, parents, attrs)


class QueryResourceManager(ResourceManager, metaclass=QueryMeta):
    def __init__(self, data, options):
        super(QueryResourceManager, self).__init__(data, options)
        self.source = self.get_source(self.source_type)
        self._cache = CacheManager

    def get_permissions(self):
        return None

    def get_source(self, source_type):
        return sources.get(source_type)(self)

    def get_client(self):
        return

    def get_model(self):
        return self

    def get_cache_key(self, query):
        return None

    @property
    def source_type(self):
        return self.data.get("source", "describe-tf")

    def get_resource_query(self):
        if "query" in self.data:
            return {"filter": self.data.get("query")}

    def resources(self, query=None):
        q = self.data.get("resource").replace("tf.", "")
        resources = self.source.get_resources(q)
        return self.filter_resources(resources)

    def filter_resources(self, resources, event=None):
        return [
            resource
            for resource in resources
            if len(super().filter_resources([resource.data], event)) > 0
        ]

    def check_resource_limit(self, selection_count, population_count):
        """Check if policy's execution affects more resources then its limit."""
        p = self.ctx.policy
        max_resource_limits = MaxResourceLimit(p, selection_count, population_count)
        return max_resource_limits.check_resource_limits()

    def _fetch_resources(self, query):
        return {}

    def augment(self, resources):
        return resources
