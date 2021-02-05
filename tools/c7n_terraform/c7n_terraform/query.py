import logging

from c7n.manager import ResourceManager
from c7n.query import sources, MaxResourceLimit


log = logging.getLogger('c7n_terraform.query')


@sources.register('describe-tf')
class DescribeSource:

    def __init__(self, manager):
        self.manager = manager
        #self.query = ResourceQuery(manager.session_factory)

    def get_resources(self, query):
        if query is None:
            query = {}
        return self.query.filter(self.manager, **query)

    def get_permissions(self):
        return

    def augment(self, resources):
        return resources


class QueryResourceManager(ResourceManager):

    def __init__(self, data, options):
        super(QueryResourceManager, self).__init__(data, options)
        self.source = self.get_source(self.source_type)

    def get_permissions(self):
        return self.source.get_permissions()

    def get_source(self, source_type):
        return sources.get(source_type)(self)

    def get_client(self):
        return

    def get_model(self):
        return self.resource_type

    def get_cache_key(self, query):
        return {'source_type': self.source_type, 'query': query,
                'service': self.resource_type.service,
                'version': self.resource_type.version,
                'component': self.resource_type.component}

    def get_resource(self, resource_info):
        return self.resource_type.get(self.get_client(), resource_info)

    @property
    def source_type(self):
        return self.data.get('source', 'describe-gcp')

    def get_resource_query(self):
        if 'query' in self.data:
            return {'filter': self.data.get('query')}

    def resources(self, query=None):
        q = query or self.get_resource_query()
        key = self.get_cache_key(q)
        resources = self._fetch_resources(q)
        self._cache.save(key, resources)

        resource_count = len(resources)
        resources = self.filter_resources(resources)

        # Check if we're out of a policies execution limits.
        if self.data == self.ctx.policy.data:
            self.check_resource_limit(len(resources), resource_count)
        return resources

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
