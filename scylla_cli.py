"""
Simple Scylla REST API client module
"""

import logging
import re

log = logging.getLogger('scylla.cli')

"""
A dictionary that keeps the insertion order
"""
class OrderedDict:
    def __init__(self):
        self._pos = 0
        self._count = 0

        self.by_key = dict()
        self.by_pos = dict()

    def insert(self, key, value):
        assert type(key) is not int
        self.by_key[key] = value
        self.by_pos[self._pos] = key
        self._pos += 1
        self._count += 1

    def __add__(self, key, value):
        self.insert(key, value)

    def __getitem__(self, idx_or_key):
        if type(idx_or_key) is int:
            if idx_or_key not in self.by_pos:
                raise IndexError('OrderedDict index out of range')
            key = self.by_pos[idx_or_key]
        else:
            key = idx_or_key
        return self.by_key[key]

    def __repr__(self):
        s = ''
        for key in self.keys():
            if s:
                s += ', '
            value = self.by_key[key]
            s += f"{{{key}: {value}}}"
        return f"OrderedDict({s})"

    def count(self) -> int:
        return self._count

    def keys(self):
        for i in range(0, self._pos):
            if i not in self.by_pos:
                continue
            yield self.by_pos[i]

    def items(self):
        for key in self.keys():
            yield self.by_key[key]

class ScyllaApiOption:
    # init Command
    def __init__(self, name:str, positional:bool=False, allowed_values=[], help:str=''):
        self.name = name
        self.positional = positional
        self.allowed_values = allowed_values
        self.help = help

    def __repr__(self):
        return f"ApiCommandOption(name={self.name}, positional={self.positional}, allowed_values={self.allowed_values}, help={self.help})"

    def __str__(self):
        return f"option_name={self.name}, positional={self.positional}, allowed_values={self.allowed_values}, help={self.help}"

class ScyllaApiCommand:
    class Method:
        GET = 0
        POST = 1
        kind_strings = ['GET', 'POST']

        def __init__(self, kind=GET, desc:str='', options:OrderedDict=None):
            self.kind = kind
            self.desc = desc
            self.options = options or OrderedDict()

        def __repr__(self):
            return f"Method(kind={self.kind}, desc={self.desc}, options={self.options})"

        def __str__(self):
            s = f"{self.kind_strings[self.kind]}: {self.desc}"
            for opt_name in self.options.keys():
                opt = self.options[opt_name]
                s += f"\n        {opt}"
            return s

        def add_option(self, option:ScyllaApiOption):
            self.options.insert(option.name, option)

    # init Command
    def __init__(self, name:str):
        self.name = name
        self.methods = dict()

    def __repr__(self):
        return f"ApiCommand(name={self.name}, methods={self.methods})"

    def __str__(self):
        s = f"{self.name}:"
        for _, method in self.methods.items():
            method_str = f"{method}"
            re.sub('\n', '\n      ', method_str)
            s += f"\n      {method_str}"
        return s

    def add_method(self, method:Method):
        self.methods[method.kind] = method

class ScyllaApiModule:
    # init Module
    def __init__(self, name:str, commands:OrderedDict=None):
        self.name = name
        self.commands = commands or OrderedDict()

    def __repr__(self):
        return f"ApiModule(name={self.name} commands={self.commands})"

    def __str__(self):
        s = f"{self.name}:"
        for command_name in self.commands.keys():
            command = self.commands[command_name]
            if s:
                s += '\n'
            command_str = f"{command}"
            re.sub('\n', '\n    ', command_str)
            s += f"\n  {command_str}"
        return s

    def add_command(self, command:ScyllaApiCommand):
        self.commands.insert(command.name, command)

class ScyllaApi:
    default_address = 'localhost'
    default_port = 10000

    # init ScyllaApi
    def __init__(self, node_address:str=default_address, port:int=default_port):
        self.node_address = node_address
        self.port = port
        self.modules = OrderedDict()

    def __repr__(self):
        return f"ScyllaApi(node_address={self.node_address}, port={self.port}, modules={self.modules})"

    def __str__(self):
        s = ''
        for module_name in self.modules.keys():
            module = self.modules[module_name]
            if s:
                s += '\n'
            s += f"{module}"
        return s

    def add_module(self, module:ScyllaApiModule):
        self.modules.insert(module.name, module)
