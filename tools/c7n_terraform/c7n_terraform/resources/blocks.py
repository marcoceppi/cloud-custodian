# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import re

from c7n_terraform.provider import resources
from c7n_terraform.query import QueryResourceManager


@resources.register("data")
class Data(QueryResourceManager):
    pass


@resources.register("resource")
class Resource(QueryResourceManager):
    pass


@resources.register("resource.*", match=re.compile(r"resource\..*"))
class ResourceLookup(QueryResourceManager):
    id = "_id"

    def resources(self, query=None):
        _, provider_type = self.data.get("resource").rsplit(".", 1)
        resources = self.source.get_resources("resource")
        resource_count = len(resources)
        resources = self.filter_resources(resources)
        return resources
