#!/usr/bin/env python3
"""
Simple Scylla REST API client
Usage::
    ./scylla.py --help [command [args...]]
"""

from re import S
from .custom_argparser import ArgumentParser
import logging
import sys
from pprint import PrettyPrinter

baselog = logging.getLogger('scylla.cli')
log = logging.getLogger('scylla.cli.util')

from .api import ScyllaApi, ScyllaApiModule, ScyllaApiCommand, ScyllaApiOption

class Lister:
    def __init__(self, scylla_api:ScyllaApi):
        self.scylla_api = scylla_api

    def list_modules(self):
        print("Available modules:\n")
        for name in self.scylla_api.modules.keys():
            print(f"{name}")

    def list_module_commands(self, module:ScyllaApiModule):
        for command_name in module.commands.keys():
            # FIXME, for now dump the object
            # need to pretty print it
            print(f"{module.commands[command_name]}")

    def list_api(self, list_modules:bool=False, list_module_commands:str=''):
        if list_modules:
            if list_module_commands:
                raise RuntimeError('--list-modules option cannot be used along with --list-module-commands')
            self.list_modules()
            return

        if list_module_commands:
            try:
                self.list_module_commands(self.scylla_api.modules[list_module_commands])
            except KeyError:
                print(f"Error: module '{list_module_commands}' not found")
            return

        first = True
        for module_name in self.scylla_api.modules.keys():
            if not first:
                print('')
            first = False
            print(f'---- {module_name} ----')
            self.list_module_commands(self.scylla_api.modules[module_name])

# FIXME: better name
def load_api(node_address:str, port:str) -> ScyllaApi:
    scylla_api = ScyllaApi(host=node_address, port=port)
    scylla_api.load()
    return scylla_api


def main():
    extra_args_help=f"[module] command [{'|'.join(ScyllaApiCommand.Method.kind_to_str)}] [args...]"
    parser = ArgumentParser(description='Scylla api command line interface.', extra_args_help=extra_args_help)
    parser.add_argument(['-a', '--address'], dest='address', has_param=True,
                        help=f"IP address of server node (default: {ScyllaApi.DEFAULT_HOST})")
    parser.add_argument(['-p', '--port'], dest='port', has_param=True,
                        help=f"api port (default: {ScyllaApi.DEFAULT_PORT})")

    parser.add_argument(['-pp', '--pretty-print'], dest='pprint',
                        help=f"enable pretty print")
    parser.add_argument(['-pp-opts', '--pretty-print-options'], dest='pprint_options', has_param=True,
                        help=f"pretty print options as width[:indent] (default: 200:1)")

    parser.add_argument(['-l', '--list'], dest='list_api', help=f"List all API commands")
    parser.add_argument(['-lm', '--list-modules'], dest='list_modules', help=f"List all API modules")
    parser.add_argument(['-lmc', '--list-module-commands'], dest='list_module_commands', has_param=True,
                        help=f"List all commands in an API module")

    parser.add_argument(['-d', '--debug'], dest='debug', help=f"Turn on debug logging (default=False)")

    parser.parse_args()

    if not parser.args and not parser.extra_args:
        parser.usage()

    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(process)-7d %(name)-25s %(levelname)-8s | %(message)s')
    baselog.setLevel(logging.DEBUG if parser.get('debug') else logging.INFO)

    log.debug('Starting')

    node_address = parser.get('address', ScyllaApi.DEFAULT_HOST)
    port = parser.get('port', ScyllaApi.DEFAULT_PORT)
    scylla_api = load_api(node_address=node_address, port=port)

    # FIXME: load only needed module(s)

    lister = Lister(scylla_api)
    if parser.get('list_api') or parser.get('list_modules') or parser.get('list_module_commands'):
        lister.list_api(parser.get('list_modules'), parser.get('list_module_commands'))
        exit()

    if not parser.extra_args:
        parser.usage(do_exit=False)
        lister.list_modules()
        exit()

    argv = parser.extra_args
    if argv[0].strip(' /') in scylla_api.modules.keys():
        module_name = argv[0].strip(' /')
        argv = argv[1:]
        module = scylla_api.modules[module_name]
        if not argv or argv[0] in ['-h', '--help']:
            lister.list_module_commands(module)
            exit()
        command_name = argv[0].strip(' /')
        argv = argv[1:]
        try:
            command = module.commands[command_name]
        except KeyError:
            print(f"Could not find command '{command_name}' in module '{module_name}'")
            exit(1)
    else:
        command_name = argv[0].strip(' /')
        argv = argv[1:]
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

    pretty_printer = None
    pprint_opts = parser.get('pprint_options', '')
    pprint = parser.get('pprint', pprint_opts != '')
    if pprint:
        width = 200
        indent = 1
        if pprint_opts:
            opts = pprint_opts.split(':')
            try:
                width = int(opts[0])
                indent = int(opts[1])
            except IndexError:
                pass
        pretty_printer = PrettyPrinter(width=width, indent=indent)
    command.invoke(node_address=node_address, port=port, argv=argv, pretty_printer=pretty_printer)

    log.debug('done')
    logging.shutdown()


if __name__ == '__main__':
    main()
