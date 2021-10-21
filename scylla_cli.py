"""
Simple Scylla REST API client module
"""

import logging

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
    def __init__(self, name:str, positional:bool=False, can_be_list:bool=False, help:str=''):
        self.name = name
        self.positional = positional
        self.can_be_list = can_be_list
        self.help = help

    def __repr__(self):
        return f"ApiCommandOption(name={self.name}, positional={self.positional}, can_be_list={self.can_be_list}, help={self.help})"

class ScyllaApiCommand:
    # init Command
    def __init__(self, name:str, options:OrderedDict=None):
        self.name = name
        self.options = options or OrderedDict()

    def __repr__(self):
        return f"ApiCommand(name={self.name}, options={self.options})"

    def add_option(self, option:ScyllaApiOption):
        self.options.insert(option.name, option)

class ScyllaApiModule:
    # init Module
    def __init__(self, name:str, commands:OrderedDict=None):
        self.name = name
        self.commands = commands or OrderedDict()

    def __repr__(self):
        return f"ApiModule(name={self.name} commands={self.commands})"

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

    def add_module(self, module:ScyllaApiModule):
        self.modules.insert(module.name, module)
