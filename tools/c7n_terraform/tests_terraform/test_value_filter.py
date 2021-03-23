# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from .tf_common import TfBaseTest, data_dir
from c7n.config import Config


class TestValueFilter(TfBaseTest):

    def test_value_filter(self):
        p = self.load_policy(
            {
                'name': 'detect-acl-public-read',
                'resource': 'tf.resource.aws_s3_bucket',
                'mode': {'type': 'static'},
                'filters': [
                    {
                        'type': 'value',
                        'key': 'acl',
                        'value': 'public-read'
                    }
                ]
            }
        )

        resources = p.run()
        self.assertEqual(1, len(resources))

    def test_value_path(self):
        p = self.load_policy(
            {
                'name': 'detect-website-error-document',
                'resource': 'tf.resource.aws_s3_bucket',
                'mode': {'type': 'static'},
                'filters': [
                    {
                        'type': 'value',
                        'key': 'website.error_document',
                        'value': 'error.html'
                    }
                ]
            }
        )
        resources = p.run()
        self.assertEqual(1, len(resources))
