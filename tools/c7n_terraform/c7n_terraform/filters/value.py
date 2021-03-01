
from c7n.filters.core import ValueFilter


class TerraformValueFilter(ValueFilter):
    def get_resource_value(self, k, i):
        return super().get_resource_value(k, i)

    def match(self, i):
        return super().match(i)
