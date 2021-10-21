"""
Simple Scylla REST API client module
"""

import logging

log = logging.getLogger('scylla.cli')

class PositionalDict:
    def __init__(self):
        self.pos = 0
        self.by_key = dict()
        self.by_pos = dict()

    def insert(self, key, value):
        assert type(key) is not int
        self.by_key[key] = value
        self.by_pos[self.pos] = key
        self.pos += 1

    def __add__(self, key, value):
        self.insert(key, value)

    def __getitem__(self, key):
        if type(key) is int:
            return self.by_pos[key]
        else:
            return self.by_key[key]

    def __repr__(self):
        s = ''
        for i in range(0, self.pos):
            if i not in self.by_pos:
                continue
            if s:
                s += ', '
            key = self.by_pos[i]
            value = self.by_key[key]
            s += f"{{{key}: {value}}}"
        return f"PositionalDict({s})"

class ApiCommand:
    class Option:
        def __init__(self, name:str, positional:bool=False, can_be_list:bool=False, help:str=''):
            self.name = name
            self.positional = positional
            self.can_be_list = can_be_list
            self.help = help

        def __repr__(self):
            return f"Option(name={self.name}, positional={self.positional}, can_be_list={self.can_be_list}, help={self.help})"

    def __init__(self, name:str, options:PositionalDict):
        self.name = name
        self.options = options

    def __repr__(self):
        return f"ApiCommand(name={self.name}, options={self.options})"

class ApiModule:
    def __init__(self, name:str, commands:PositionalDict):
        self.name = name
        self.commands = commands
