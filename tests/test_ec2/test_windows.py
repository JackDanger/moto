from __future__ import unicode_literals
import sure  # noqa

from moto import mock_ec2


@mock_ec2
def test_windows():
    pass
