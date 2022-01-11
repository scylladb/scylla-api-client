"""
Simple command line arguments parser
"""

import os
import sys

from .api import OrderedDict

class ArgumentParser:
    class Arg:
        def __init__(self, names:list, dest:str, has_param=False, default_param=None, help:str=''):
            self.names = names
            self.dest = dest
            self.has_param = has_param
            self.default_param = default_param
            self.help = help

        def __repr__(self):
            return f"Arg(names={self.names}, dest={self.dest}, has_param={self.has_param}, default_param={self.default_param}, help={self.help})"

    def __init__(self, description:str, extra_args_help:str=None, enable_extra_args:bool=None):
        self.description = description
        self.progname = os.path.basename(sys.argv[0])
        self.args = dict()
        if extra_args_help is not None:
            self.enable_extra_args = True
            self.extra_args_help = extra_args_help
        else:
            self.enable_extra_args = enable_extra_args == True
            self.extra_args_help = '[extra_args...]' if self.enable_extra_args else ''
        self.extra_args = []

        self._raw_args = OrderedDict()
        self._by_name = dict()

        self.add_argument(['-h', '--help'], dest='help', help='show this help message and exit')

    def add_argument(self, names:list, dest:str, has_param=False, default_param=False, help:str=''):
        if type(names) is str:
            names = [names]
        arg = self.Arg(names, dest=dest, has_param=has_param, default_param=default_param, help=help)
        assert len(names)
        self._raw_args.insert(names[0], arg)
        for n in names:
            assert n not in self._by_name, f"arg '{n}' already added"
            self._by_name[n] = arg

    # print help message and exit
    def usage(self, do_exit:bool=True):
        s = f"Usage: {self.progname}:"
        for arg in self._raw_args.items():
            arg_param = f" <{arg.dest.upper()}>" if arg.has_param else ''
            s += f" [{arg.names[0]}{arg_param}]"
        if self.extra_args_help:
            s += f" [{self.extra_args_help}]"
        s += f"\n\n{self.description}\n\n"
        s += "Optional arguments:\n"
        for arg in self._raw_args.items():
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
        if do_exit:
            exit()

    def parse_args(self, argv:list=None):
        if not argv:
            argv = sys.argv
        argc = 0
        if os.path.basename(argv[0]) == self.progname:
            argc += 1
        while argc < len(argv):
            opt = argv[argc]
            param = None
            pos = opt.find('=')
            if pos > 0:
                param = opt[pos+1:]
                opt = opt[:pos]
            if opt in self._by_name:
                argc += 1
                arg = self._by_name[opt]
                if arg.has_param:
                    if param is None:
                        if argc < len(argv) and not argv[argc].startswith('-'):
                            param = argv[argc]
                            argc += 1
                        elif arg.default_param is not None:
                            param = arg.default_param
                        else:
                            print(f"Missing {arg.dest.upper()} parameter for option '{opt}'\n\n")
                            self.usage()
                    self.args[arg.dest] = param
                else:
                    self.args[arg.dest] = True
            elif self.enable_extra_args:
                if opt == '--':
                    argc += 1
                self.extra_args = argv[argc:]
                break
        if self.get('help'):
            self.usage()

    def get(self, arg:str, default_value=None):
        try:
            return self.args[arg]
        except KeyError:
            return default_value

