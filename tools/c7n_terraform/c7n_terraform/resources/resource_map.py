# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

ResourceMap = {
    "tf.module": "c7n_terraform.resources.blocks.Module",
    "tf.output": "c7n_terraform.resources.blocks.Output",
    "tf.provider": "c7n_terraform.resources.blocks.Provider",
    "tf.resource": "c7n_terraform.resources.blocks.Resource",
    "tf.terraform": "c7n_terraform.resources.blocks.Terraform",
    "tf.variable": "c7n_terraform.resources.blocks.Variable",
    "tf.resource.*": "c7n_terraform.resources.blocks.ResourceLookup",
}
