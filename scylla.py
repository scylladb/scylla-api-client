#!/usr/bin/env python3
"""
Simple Scylla REST API client
Usage::
    ./scylla.py --help [command [args...]]
"""

from simple_argparser import ArgumentParser
import logging
import sys

baselog = logging.getLogger('scylla.cli')
log = logging.getLogger('scylla.cli.util')

from scylla_cli import ScyllaApi, ScyllaApiModule, ScyllaApiCommand, ScyllaApiOption

def list_module(module:ScyllaApiModule):
    for command_name in module.commands.keys():
        # FIXME, for now dump the object
        # need to pretty print it
        print(f"{module.commands[command_name]}")

def list_api(scylla_api:ScyllaApi, list_modules:bool, list_module_commands:str):
    if list_modules:
        if list_module_commands:
            raise RuntimeError('--list-modules option cannot be used along with --list-module-commands')
        for name in scylla_api.modules.keys():
            print(f"{name}")
        return

    if list_module_commands:
        try:
            list_module(scylla_api.modules[list_module_commands])
        except KeyError:
            print(f"Error: module '{list_module_commands}' not found")
        return

    first = True
    for module_name in scylla_api.modules.keys():
        if not first:
            print('')
        first = False
        print(f'---- {module_name} ----')
        list_module(scylla_api.modules[module_name])

def test(node_address:str, port:int) -> ScyllaApi:
    log.debug('Starting test')

    test_command = ScyllaApiCommand(module_name='test_module', command_name='test_command')
    get_method = ScyllaApiCommand.Method(kind=ScyllaApiCommand.Method.GET, command_name='test_command')
    get_method.add_option(ScyllaApiOption('test_positional_get_option_1', param_type='path', help='help for test_positional_get_option_1'))
    get_method.add_option(ScyllaApiOption('test_get_option_2', help='help for test_get_option_2'))
    test_command.add_method(get_method)

    post_method = ScyllaApiCommand.Method(kind=ScyllaApiCommand.Method.POST, command_name='test_command')
    post_method.add_option(ScyllaApiOption('test_post_option_1', allowed_values=['hello', 'world'], help='help for test_post_option_1'))
    test_command.add_method(post_method)

    log.debug(f"test_command={test_command}")

    assert test_command.methods[ScyllaApiCommand.Method.GET].options[0].name == 'test_positional_get_option_1', f"{test_command.methods[ScyllaApiCommand.Method.GET].options[0].name} != 'test_positional_get_option_1'"
    assert test_command.methods[ScyllaApiCommand.Method.GET].options[1].name == 'test_get_option_2', f"{test_command.methods[ScyllaApiCommand.Method.GET].options[1].name} != 'test_get_option_2'"
    assert test_command.methods[ScyllaApiCommand.Method.POST].options[0].name == 'test_post_option_1', f"{test_command.methods[ScyllaApiCommand.Method.POST].options[0].name} == 'test_post_option_1'"

    test_module = ScyllaApiModule('test_module')
    test_module.add_command(test_command)
    assert test_module.commands.count() == 1, f"Expect len to be 1, but got {test_module.commands.count()}"

    test_command_1 = ScyllaApiCommand(module_name='test_module', command_name='test_command_1')
    get_method = ScyllaApiCommand.Method(kind=ScyllaApiCommand.Method.GET, command_name='test_command_1')
    get_method.add_option(ScyllaApiOption('test_positional_get_option_1_1', param_type='path', help='help for test_positional_get_option_1_1'))
    get_method.add_option(ScyllaApiOption('test_get_option_1_2', help='help for test_get_option_1_2'))
    test_command_1.add_method(get_method)
    test_module.add_command(test_command_1)
    assert test_module.commands.count() == 2, f"Expect len to be 1, but got {test_module.commands.count()}"

    assert test_module.commands[0] == test_command
    assert test_module.commands[1] == test_command_1

    test_api = ScyllaApi()
    test_api.add_module(test_module)

    test_module_1 = ScyllaApiModule('test_module_1')
    assert test_module_1.commands.count() == 0, f"Expect len to be 0, but got {test_module_1.commands.count()}"
    test_module_1.add_command(test_command_1)
    assert test_module_1.commands.count() == 1, f"Expect len to be 1, but got {test_module_1.commands.count()}"

    test_api.add_module(test_module_1)

    log.debug(f"{test_api}")

    assert test_api.modules[0] == test_module
    assert test_api.modules[1] == test_module_1
    assert test_api.modules['test_module'] == test_module
    assert test_api.modules['test_module_1'] == test_module_1

    log.debug('Test done')

    return test_api

# FIXME: better name
def load_api(node_address:str, port:str) -> ScyllaApi:
    scylla_api = ScyllaApi(host=node_address, port=port)
    scylla_api.load()
    return scylla_api


if __name__ == '__main__':
    extra_args_help=f"[module/]command [{'|'.join(ScyllaApiCommand.Method.kind_to_str)}] [args...]"
    parser = ArgumentParser(description='Scylla api command line interface.', extra_args_help=extra_args_help)
    parser.add_argument(['-a', '--address'], dest='address', has_param=True,
                        help=f"IP address of server node (default: {ScyllaApi.DEFAULT_HOST})")
    parser.add_argument(['-p', '--port'], dest='port', has_param=True,
                        help=f"api port (default: {ScyllaApi.DEFAULT_PORT})")

    parser.add_argument(['-l', '--list'], dest='list_api', help=f"List all API commands")
    parser.add_argument('--list-modules', dest='list_modules', help=f"List all API modules")
    parser.add_argument('--list-module-commands', dest='list_module_commands', has_param=True,
                        help=f"List all commands in an API module")

    parser.add_argument(['-d', '--debug'], dest='debug', help=f"Turn on debug logging (default=False)")
    parser.add_argument(['-t', '--test'], dest='test', help=f"Run test (default=False)")

    parser.parse_args()

    if not parser.args and not parser.extra_args:
        parser.usage()

    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(process)-7d %(name)-25s %(levelname)-8s | %(message)s')
    baselog.setLevel(logging.DEBUG if parser.get('debug') else logging.INFO)

    log.debug('Starting')

    node_address = parser.get('address', ScyllaApi.DEFAULT_HOST)
    port = parser.get('port', ScyllaApi.DEFAULT_PORT)
    if parser.get('test'):
        scylla_api = test(node_address=node_address, port=port)
    else:
        # for now
        scylla_api = load_api(node_address=node_address, port=port)

    # FIXME: load only needed module(s)

    if parser.get('list_api') or parser.get('list_modules') or parser.get('list_module_commands'):
        list_api(scylla_api, parser.get('list_modules'), parser.get('list_module_commands'))
        exit()

    if parser.extra_args:
        command_name = parser.extra_args[0].strip(' /')
        sep = command_name.find('/')
        if sep > 0:
            module_name = command_name[:sep]
            command_name = command_name[sep+1:]
            try:
                module = scylla_api.modules[module_name]
            except KeyError:
                print(f"Could not find module '{module_name}'")
                exit(1)
            try:
                command = module.commands[command_name]
            except KeyError:
                print(f"Could not find command '{command_name}' in module '{module_name}'")
                exit(1)
        else:
            module = None
            command = None
            for m in scylla_api.modules.items():
                try:
                    command = m.commands[command_name]
                    if not module:
                        module = m
                    else:
                        print(f"Command '{command_name}' exists in multiple modules. Specify 'module/command' to uniquely identify the command.")
                        exit(1)
                except KeyError:
                    pass
            if not command:
                print(f"Could not find command '{command_name}'")
                exit(1)

        argv = parser.extra_args[1:]
        command.invoke(node_address=node_address, port=port, argv=argv)

    log.debug('done')
    logging.shutdown()
