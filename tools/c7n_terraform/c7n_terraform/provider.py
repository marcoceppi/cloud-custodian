# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from c7n.registry import PluginRegistry
from c7n.provider import Provider, clouds

from functools import partial

from c7n_terraform.resources.resource_map import ResourceMap


@clouds.register('terraform')
class Terraform(Provider):

    display_name = 'Terraform'
    resource_prefix = 'tf'
    resources = PluginRegistry('%s.resources' % resource_prefix)
    resource_map = ResourceMap

    def initialize(self, options):
        return options

    def initialize_policies(self, policy_collection, options):
        return policy_collection

    # def get_session_factory(self, options):
    #     """Get a credential/session factory for api usage."""
    #     return partial(Session, project_id=options.account_id)


resources = Terraform.resources
