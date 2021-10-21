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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scylla api command line interface.')
    parser.add_argument('-a', '--address', dest='address', type=str, default=ScyllaApi.default_address,
                        help=f"IP address of server node (default: {ScyllaApi.default_address})")
    parser.add_argument('-p', '--port', dest='port', type=int, default=ScyllaApi.default_port,
                        help=f"api port (default: {ScyllaApi.default_port})")
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
        log.debug('Starting test')

        test_command = ScyllaApiCommand('test_command')
        test_command.add_option(ScyllaApiOption('test_positional_option_1', positional=True, help='help for test_positional_option_1'))
        test_command.add_option(ScyllaApiOption('test_option_2', help='help for test_option_2'))
    
        test_module = ScyllaApiModule('test_module')
        test_module.add_command(test_command)

        test_api = ScyllaApi()
        test_api.add_module(test_module)

        log.info(f"{test_api}")

        log.debug('Test done')

    log.debug('done')
    logging.shutdown()
