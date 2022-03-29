from pytest import fixture
from scylla_api_client.api import ScyllaApiModule, OrderedDict


@fixture
def list_command():
    commands = OrderedDict()
    commands.insert("compaction", "run_compaction")
    commands.insert("nodetool", "run_nodetoo")
    return commands


def test_Module(list_command):
    module = ScyllaApiModule(name="test1", commands=list_command)

    assert module.name == "test1"
    for pos, command in enumerate(list_command):
        assert command in module.commands.keys()
        assert list(module.commands.keys())[pos] == command
        assert module.commands[command] == list_command[command]
