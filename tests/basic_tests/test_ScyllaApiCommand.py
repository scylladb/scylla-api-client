from pytest import fixture
from scylla_cli.api import OrderedDict, ScyllaApiCommand


def test_command():
    command = ScyllaApiCommand(module_name="module1", command_name="command1",
                               host="localhost", port="10000")
    assert command.module_name == "module1"
    assert command.name == "command1"
    assert len(command.methods) == 0
