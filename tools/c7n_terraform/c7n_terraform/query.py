import logging

from pathlib import Path

from unittest.mock import MagicMock
from c7n.manager import ResourceManager
from c7n.actions import ActionRegistry
from c7n.filters import FilterRegistry
from c7n.query import sources, MaxResourceLimit

from c7n_terraform.parser import Parser, TerraformVisitor, VariableResolver


log = logging.getLogger('c7n_terraform.query')


@sources.register('describe-tf')
class DescribeSource:

    def __init__(self, manager):
        self.manager = manager
        tmp = Path("/home/marco/Projects/stacklet/cloud-custodian/tools/c7n_terraform/tests_terraform/data/aws-complete")
        data = Parser().parse_module(tmp)
        self.query = TerraformVisitor(data, tmp)
        self.query.visit()
        resolver = VariableResolver(self.query)
        resolver.resolve()

    def get_resources(self, block):
        cmd = self.query.iter_blocks if block else self.query.blocks
        return [block.to_dict() for block in cmd(tf_kind=block)]

    def get_permissions(self):
        return

    def augment(self, resources):
        return resources

class QueryMeta(type):
    """metaclass to have consistent action/filter registry for new resources."""
    def __new__(cls, name, parents, attrs):
        if 'filter_registry' not in attrs:
            attrs['filter_registry'] = FilterRegistry(
                '%s.filters' % name.lower())
        if 'action_registry' not in attrs:
            attrs['action_registry'] = ActionRegistry(
                '%s.actions' % name.lower())

        return super(QueryMeta, cls).__new__(cls, name, parents, attrs)

# TODO: Make a NOOP Cache manager
CacheManager = MagicMock()
CacheManager.load.side_effect = [False]
CacheManager.size.return_value = 0

class QueryResourceManager(ResourceManager, metaclass=QueryMeta):

    def __init__(self, data, options):
        super(QueryResourceManager, self).__init__(data, options)
        self.source = self.get_source(self.source_type)
        self._cache = CacheManager

    def get_permissions(self):
        return self.source.get_permissions()

    def get_source(self, source_type):
        return sources.get(source_type)(self)

    def get_client(self):
        return

    def get_model(self):
        return self

    def get_cache_key(self, query):
        return None

    def get_resource(self, resource_info):
        return self.source.get(resource_info)

    @property
    def source_type(self):
        return self.data.get('source', 'describe-tf')

    def get_resource_query(self):
        if 'query' in self.data:
            return {'filter': self.data.get('query')}

    def resources(self, query=None):
        q = self.data.get('resource').replace('tf.', '')
        resources = self.source.get_resources(q)

        resource_count = len(resources)
        resources = self.filter_resources(resources)

        # Check if we're out of a policies execution limits.
        if self.data == self.ctx.policy.data:
            self.check_resource_limit(len(resources), resource_count)
        return resources

    def filter_resources(self, resources, event=None):
        to_filter = [resource.data for resource in resources]
        print(to_filter)
        return super().filter_resources(to_filter, event)

    def check_resource_limit(self, selection_count, population_count):
        """Check if policy's execution affects more resources then its limit.
        """
        p = self.ctx.policy
        max_resource_limits = MaxResourceLimit(p, selection_count, population_count)
        return max_resource_limits.check_resource_limits()

    def _fetch_resources(self, query):
        return {}

    def augment(self, resources):
        return resources
