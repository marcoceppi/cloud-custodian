import c7n_terraform.provider  # noqa


def initialize_tf():
    """Load terraform provider"""

    # load shared registered resources
    import c7n_terraform.query
    import c7n_terraform.resources.blocks  # noqa
