"""
Simple Scylla REST API client module
"""

import logging
import re
import json

from rest.scylla_rest_client import ScyllaRestClient

log = logging.getLogger('scylla.cli')

"""
A dictionary that keeps the insertion order
"""
class OrderedDict:
    def __init__(self):
        self._pos = 0
        self._count = 0
        self._cur_pos = 0

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

    def __len__(self):
        return len(self.by_key)

    def __iter__(self):
        self._cur_pos = 0
        return self

    def __next__(self):
        next_key = self.by_pos[self._cur_pos]
        self._cur_pos += 1
        if self._cur_pos >= self._count:
            raise StopIteration
        return next_key

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
        log.debug(f"Created {self.__repr__()}")

    def __repr__(self):
        return f"ApiCommandOption(name={self.name}, positional={self.positional}, allowed_values={self.allowed_values}, help={self.help})"

    def __str__(self):
        return f"option_name={self.name}, positional={self.positional}, allowed_values={self.allowed_values}, help={self.help}"

class ScyllaApiCommand:
    class Method:
        GET = 0
        POST = 1
        DELETE = 2
        kind_strings = ['GET', 'POST', 'DELETE']

        def __init__(self, kind=GET, desc:str='', options:OrderedDict=None):
            self.kind = kind
            self.desc = desc
            self.options = options or OrderedDict()
            log.debug(f"Created {self.__repr__()}")

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
        log.debug(f"Created {self.__repr__()}")

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

    def load_json(self, command_json:dict):
        log.debug(f"Loading: {json.dumps(command_json, indent=4)}")
        for operation_def in command_json["operations"]:
            operation = None
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
            elif operation_def["method"].upper() == "DELETE":
                operation = ScyllaApiCommand.Method(ScyllaApiCommand.Method.DELETE,
                                                    operation_def["summary"])
                for param_def in operation_def["parameters"]:
                    operation.add_option(ScyllaApiOption(param_def["name"],
                                            allowed_values=param_def.get("enum", []),
                                            help=param_def["description"]))

            if operation:
                self.add_method(operation)
            else:
                log.warn(f"Operation not supported yet: {json.dumps(operation_def, indent=4)}")

class ScyllaApiModule:
    # init Module
    def __init__(self, name:str, desc:str='', commands:OrderedDict=None):
        self.desc = desc
        self.name = name
        self.commands = commands or OrderedDict()
        log.debug(f"Created {self.__repr__()}")

    def __repr__(self):
        return f"ApiModule(name={self.name}, desc={self.desc}, commands={self.commands})"

    def __str__(self):
        s = f"{self.name}: {self.desc}"
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
    def __init__(self):
        self.modules = OrderedDict()
        self.client = None

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

    def load(self, node_address:str=default_address, port:int=default_port):
        self.client = ScyllaRestClient(host=node_address, port=port)

        # FIXME: handle service down, assert minimum version
        top_json = self.client.get_raw_api_json()
        for module_def in top_json["apis"]:
            # FIXME: handle service down, errors
            module_json = self.client.get_raw_api_json(f"{module_def['path']}/")
            module_path = module_def['path'].strip(' /')
            module = ScyllaApiModule(module_path, module_def['description'])
            for command_json in module_json["apis"]:
                command_path = command_json['path'].strip(' /')
                if command_path.startswith(module_path):
                    command_path = command_path[len(module_path)+1:]
                command = ScyllaApiCommand(command_path)
                command.load_json(command_json)
                module.add_command(command)
            self.add_module(module)
