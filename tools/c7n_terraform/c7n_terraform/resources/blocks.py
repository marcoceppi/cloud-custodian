# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import re

from datetime import datetime

from c7n_terraform.provider import resources
from c7n_terraform.query import QueryResourceManager


@resources.register('data')
class Data(QueryResourceManager):
    pass


@resources.register('resource')
class Resource(QueryResourceManager):
    pass


@resources.register("resource.*", match=re.compile(r"resource\..*"))
class ResourceLookup(QueryResourceManager):
    def resources(self, query=None):
        _, name = self.data.get("resource").rsplit(".", 1)
        resources = self.source.get_resources("resource")

        resource_count = len(resources)
        resources = self.filter_resources(resources)

        # Check if we're out of a policies execution limits.
        if self.data == self.ctx.policy.data:
            self.check_resource_limit(len(resources), resource_count)
        return resources
