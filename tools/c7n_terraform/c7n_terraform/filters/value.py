# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from c7n.filters.core import ValueFilter


class TerraformValueFilter(ValueFilter):
    def get_resource_value(self, k, i):
        resource_value = super().get_resource_value(k, i)
        if resource_value is not None:
            return resource_value

        # handle the possible hack JMES path
        new_k = "[].".join(k.split(".")) + "[]"
        return super().get_resource_value(new_k, i)


    def match(self, i):
        is_match = super().match(i)
        if is_match:
            return True
        # handle possible single-element array
        if isinstance(self.r, list) and len(self.r) == 1 and self.r[0] == self.v:
            return True

        return False
