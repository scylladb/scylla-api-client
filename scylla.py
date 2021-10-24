#!/usr/bin/env python3
"""
Simple Scylla REST API client
Usage::
    ./scylla.py --help [command [args...]]
"""

import argparse
import logging

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
def load_api(node_address:str, port:int) -> ScyllaApi:
    scylla_api = ScyllaApi()
    scylla_api.load(node_address, port)
    return scylla_api

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scylla api command line interface.')
    parser.add_argument('-a', '--address', dest='address', type=str, default=ScyllaApi.default_address,
                        help=f"IP address of server node (default: {ScyllaApi.default_address})")
    parser.add_argument('-p', '--port', dest='port', type=int, default=ScyllaApi.default_port,
                        help=f"api port (default: {ScyllaApi.default_port})")

    parser.add_argument('-l', '--list', dest='list_api', action='store_const', const=True, default=False,
                        help=f"List all API commands")
    parser.add_argument('--list-modules', dest='list_modules', action='store_const', const=True, default=False,
                        help=f"List all API modules")
    parser.add_argument('--list-module-commands', dest='list_module_commands', type=str,
                        help=f"List all commands in an API module")

    parser.add_argument('command', nargs='?',
                        help=f"API command to invoke. module/command can be use to specify a command in a module")
    parser.add_argument('command_args', nargs='*',
                        help=f"Optional arguments for the API command. Use `command -h` to print the command help message and exit")

    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True, default=False,
                        help=f"Turn on debug logging (default=False)")
    parser.add_argument('-t', '--test', dest='test', action='store_const', const=True, default=False,
                        help=f"Run test (default=False)")

    args = argparse.Namespace()
    parser.parse_args(namespace=args)

    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(process)-7d %(name)-25s %(levelname)-8s | %(message)s')
    baselog.setLevel(logging.DEBUG if args.debug else logging.INFO)

    log.debug('Starting')

    if args.test:
        scylla_api = test(args.address, args.port)
    else:
        # for now
        scylla_api = load_api(args.address, args.port)

    # FIXME: load only needed module(s)

    if args.list_api or args.list_modules or args.list_module_commands:
        list_api(scylla_api, args.list_modules, args.list_module_commands)
        exit

    if args.command:
        command_name = args.command.strip(' /')
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

        command.invoke(node_address=args.address, port=args.port, argv=args.command_args)

    log.debug('done')
    logging.shutdown()
