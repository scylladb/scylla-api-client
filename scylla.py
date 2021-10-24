#!/usr/bin/env python3
"""
Simple Scylla REST API client
Usage::
    ./scylla.py --help [command [args...]]
"""

import argparse
import logging
import os
import sys
from typing import OrderedDict
from rest.scylla_rest_client import ScyllaRestClient

baselog = logging.getLogger('scylla.cli')
log = logging.getLogger('scylla.cli.util')

from scylla_cli import ScyllaApi, ScyllaApiModule, ScyllaApiCommand, ScyllaApiOption, OrderedDict

def list_module(module:ScyllaApiModule):
    print(f"{module.name}:")
    for command_name in module.commands.keys():
        # FIXME, for now dump the object
        # need to pretty print it
        print(f"{'':4}{module.commands[command_name]}")

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
        list_module(scylla_api.modules[module_name])
        if first:
            print('')
            first = False

def test(node_address:str, port:int) -> ScyllaApi:
    log.debug('Starting test')

    test_command = ScyllaApiCommand('test_command')
    get_method = ScyllaApiCommand.Method(ScyllaApiCommand.Method.GET)
    get_method.add_option(ScyllaApiOption('test_positional_get_option_1', positional=True, help='help for test_positional_get_option_1'))
    get_method.add_option(ScyllaApiOption('test_get_option_2', help='help for test_get_option_2'))
    test_command.add_method(get_method)

    post_method = ScyllaApiCommand.Method(ScyllaApiCommand.Method.POST)
    post_method.add_option(ScyllaApiOption('test_post_option_1', allowed_values=['hello', 'world'], help='help for test_post_option_1'))
    test_command.add_method(post_method)

    log.debug(f"test_command={test_command}")

    assert test_command.methods[ScyllaApiCommand.Method.GET].options[0].name == 'test_positional_get_option_1'
    assert test_command.methods[ScyllaApiCommand.Method.GET].options[1].name == 'test_get_option_2'
    assert test_command.methods[ScyllaApiCommand.Method.POST].options[0].name == 'test_post_option_1'

    test_module = ScyllaApiModule('test_module')
    test_module.add_command(test_command)
    assert test_module.commands.count() == 1, f"Expect len to be 1, but got {test_module.commands.count()}"

    test_command_1 = ScyllaApiCommand('test_command_1')
    get_method = ScyllaApiCommand.Method(ScyllaApiCommand.Method.GET)
    get_method.add_option(ScyllaApiOption('test_positional_get_option_1_1', positional=True, help='help for test_positional_get_option_1_1'))
    get_method.add_option(ScyllaApiOption('test_get_option_1_2', help='help for test_get_option_1_2'))
    test_command_1.add_method(get_method)
    test_module.add_command(test_command_1)
    assert test_module.commands.count() == 2, f"Expect len to be 1, but got {test_module.commands.count()}"

    assert test_module.commands[0] == test_command
    assert test_module.commands[1] == test_command_1

    test_api = ScyllaApi(node_address=node_address, port=port)
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
    client = ScyllaRestClient()
    scylla_api = ScyllaApi(node_address=node_address, port=port)

    # FIXME: handle service down, assert minimum version
    top_json = client.get_raw_api_json()
    for module_def in top_json["apis"]:
        # FIXME: handle service down, errors
        module_json = client.get_raw_api_json(f"{module_def['path']}/")
        module_path = module_def['path'].strip(' /')
        module = ScyllaApiModule(module_path, module_def['description'])
        for command_json in module_json["apis"]:
            command_path = command_json['path'].strip(' /')
            if command_path.startswith(module_path):
                command_path = command_path[len(module_path)+1:]
            command = ScyllaApiCommand(command_path)
            for operation_def in command_json["operations"]:
                if operation_def["method"].upper() == "GET":
                    operation = ScyllaApiCommand.Method(ScyllaApiCommand.Method.GET,
                                                        operation_def["summary"])
                elif operation_def["method"].upper() == "POST":
                    operation = ScyllaApiCommand.Method(ScyllaApiCommand.Method.POST,
                                                        operation_def["summary"])
                    for param_def in operation_def["parameters"]:
                        operation.add_option(ScyllaApiOption(param_def["name"],
                                             allowed_values=param_def.get("enum", []),
                                             help=param_def["description"]))
                # FIXME: handle DELETE
                command.add_method(operation)
            module.add_command(command)
        scylla_api.add_module(module)
    return scylla_api

# Mini command line arguments parser
class ArgumentParser:
    class Arg:
        def __init__(self, names:list[str], dest:str, has_param=False, default=None, help:str=''):
            self.names = names
            self.dest = dest
            self.has_param = has_param
            self.default = default
            self.help = help

        def __repr__(self):
            return f"Arg(names={self.names}, dest={self.dest}, has_param={self.has_param}, default={self.default}, help={self.help})"

    def __init__(self, description:str):
        self.description = description
        self.progname = os.path.basename(sys.argv[0])
        self.extra_args = []

        self._args = OrderedDict()
        self._by_name = dict[str, self.Arg]()
        self._arg_values = dict()

        self.add_argument(['-h', '--help'], dest='help', help='show this help message and exit')

    def add_argument(self, names:list[str], dest:str, has_param=False, default=None, help:str=''):
        if type(names) is str:
            names = [names]
        arg = self.Arg(names, dest=dest, has_param=has_param, default=default, help=help)
        assert len(names)
        self._args.insert(names[0], arg)
        for n in names:
            assert n not in self._by_name, f"arg '{n}' already added"
            self._by_name[n] = arg
        if default is not None:
            self._arg_values[arg.dest] = arg.default
        elif not has_param:
            self._arg_values[arg.dest] = False

    # print help message and exit
    def usage(self):
        s = f"Usage: {self.progname}:"
        for arg in self._args.items():
            arg_param = f" <{arg.dest.upper()}>" if arg.has_param else ''
            s += f" [{arg.names[0]}{arg_param}]"
        s += f"\n\n{self.description}\n\n"
        s += "Optional arguments:\n"
        for arg in self._args.items():
            arg_name = arg.names[0] if len(arg.names) == 1 else '|'.join(arg.names)
            arg_param = f" <{arg.dest.upper()}>" if arg.has_param else ''
            justify = 21
            arg_pfx = f"  {arg_name}{arg_param}".ljust(justify)
            s += arg_pfx
            if arg.help:
                if len(arg_pfx) > justify:
                    s += f"\n{''.ljust(justify+1)}"
                else:
                    s += ' '
                s += arg.help
            s += '\n'
        print(f"{s}")
        exit

    def parse_args(self, argv:list[str]=None):
        if not argv:
            argv = sys.argv
        argc = 0
        if os.path.basename(argv[0]) == self.progname:
            argc += 1
        while argc < len(argv):
            opt = argv[argc]
            if opt in self._by_name:
                argc += 1
                arg = self._by_name[opt]
                if arg.has_param:
                    if argc < len(argv):
                        param = argv[argc]
                        argc += 1
                    else:
                        print(f"Missing {arg.dest.upper()} parameter for option '{opt}'\n\n")
                        self.usage()
                    self._arg_values[arg.dest] = param
                else:
                    self._arg_values[arg.dest] = True
            else:
                self.extra_args = argv[argc:]
                break
        if self.get('help'):
            self.usage()

    def get(self, arg:str):
        try:
            return self._arg_values[arg]
        except KeyError:
            return None

if __name__ == '__main__':
    parser = ArgumentParser(description='Scylla api command line interface.')
    parser.add_argument(['-a', '--address'], dest='address', has_param=True, default=ScyllaApi.default_address,
                        help=f"IP address of server node (default: {ScyllaApi.default_address})")
    parser.add_argument(['-p', '--port'], dest='port', has_param=True, default=ScyllaApi.default_port,
                        help=f"api port (default: {ScyllaApi.default_port})")

    parser.add_argument(['-l', '--list'], dest='list_api', help=f"List all API commands")
    parser.add_argument('--list-modules', dest='list_modules', help=f"List all API modules")
    parser.add_argument('--list-module-commands', dest='list_module_commands', has_param=True,
                        help=f"List all commands in an API module")

    parser.add_argument(['-d', '--debug'], dest='debug', help=f"Turn on debug logging (default=False)")
    parser.add_argument(['-t', '--test'], dest='test', help=f"Run test (default=False)")

    parser.parse_args()

    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(process)-7d %(name)-25s %(levelname)-8s | %(message)s')
    baselog.setLevel(logging.DEBUG if parser.get('debug') else logging.INFO)

    log.debug('Starting')

    if parser.get('test'):
        scylla_api = test(parser.get('address'), parser.get('port'))
    else:
        # for now
        scylla_api = load_api(parser.get('address'), parser.get('port'))

    # FIXME: load only needed module(s)

    if parser.get('list_api') or parser.get('list_modules') or parser.get('list_module_commands'):
        list_api(scylla_api, parser.get('list_modules'), parser.get('list_module_commands'))

    log.debug('done')
    logging.shutdown()
