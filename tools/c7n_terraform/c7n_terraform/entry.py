# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import c7n_terraform.provider  # noqa


def initialize_tf():
    """Load terraform provider"""

    # load shared registered resources
    import c7n_terraform.query
    import c7n_terraform.policy # noqa
