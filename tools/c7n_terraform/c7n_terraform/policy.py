# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import time

from c7n import utils
from c7n.policy import PolicyExecutionMode, execution
from c7n.version import version as c7n_version

from c7n_terraform.version import version


@execution.register('static')
class StaticMode(PolicyExecutionMode):
    """Static mode execution of a policy.

    Used when a policy evaluates filters and actions against files on disk.
    """

    schema = utils.type_schema('static')

    def run(self, *args, **kw):
        if not self.policy.is_runnable():
            return []

        with self.policy.ctx:
            self.policy.log.debug(
                "Running policy:%s resource:%s c7n:%s c7n-terraform:%s",
                self.policy.name, self.policy.resource_type,
                c7n_version, version)

            s = time.time()
            resources = self.policy.resource_manager.resources()
            rt = time.time() - s

            self.policy.log.debug(
                "policy:%s resource:%s count:%d time:%0.2f" % (
                    self.policy.name,
                    self.policy.resource_type,
                    len(resources), rt))
            self.policy.ctx.metrics.put_metric(
                "ResourceCount", len(resources), "Count", Scope="Policy")
            self.policy.ctx.metrics.put_metric(
                "ResourceTime", rt, "Seconds", Scope="Policy")

            if not resources:
                return []

            at = time.time()
            for a in self.policy.resource_manager.actions:
                s = time.time()
                with self.policy.ctx.tracer.subsegment('action:%s' % a.type):
                    results = a.process(resources)
                self.policy.log.debug(
                    "policy:%s action:%s"
                    " resources:%d"
                    " execution_time:%0.2f" % (
                        self.policy.name, a.name,
                        len(resources), time.time() - s))
                if results:
                    self.policy._write_file(
                        "action-%s" % a.name, utils.dumps(results))
            at = time.time() - at
            self.policy.ctx.metrics.put_metric(
                "ActionTime", at, "Seconds", Scope="Policy")
            return list(resources)
