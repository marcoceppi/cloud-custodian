# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

import re

from datetime import datetime

from c7n_terraform.provider import resources
from c7n_terraform.query import QueryResourceManager


@resources.register('data')
class Data(QueryResourceManager):
    pass
