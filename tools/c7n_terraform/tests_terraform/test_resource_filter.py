# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from .tf_common import TfBaseTest, data_dir
from c7n.config import Config


class TestResourceFilter(TfBaseTest):

    def test_resource_filter(self):
        p = self.load_policy(
            {
                'name': 'detect-multiple-resource-types',
                'resource': 'tf.resource.*',
                'mode': {'type': 'static'},
                'filters': [
                    {
                        'type': 'value',
                        'key': 'tf:resource',
                        'value': 'aws_s3_bucket'
                    }
                ]
            }
        )

        resources = p.run()
        self.assertEqual(1, len(resources))
