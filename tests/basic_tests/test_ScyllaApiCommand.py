from pytest import fixture
from scylla_cli import OrderedDict, ScyllaApiCommand


def test_command():
    command = ScyllaApiCommand(name="test")
    assert command.name == "test"

