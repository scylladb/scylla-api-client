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

import scylla_cli

if __name__ == '__main__':
    default_port = 10000
    default_address = 'localhost'

    parser = argparse.ArgumentParser(description='Scylla api command line interface.')
    parser.add_argument('-a', '--address', dest='address', type=str, default=default_address,
                        help=f"IP address of server node (default: {default_address})")
    parser.add_argument('-p', '--port', dest='port', type=int, default=default_port,
                        help=f"api port (default: {default_port})")
    parser.add_argument('-d', '--debug', dest='debug', action='store_const', const=True, default=False,
                        help=f"Turn on debug logging (default=False)")

    args = argparse.Namespace()
    parser.parse_args(namespace=args)

    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(process)-7d %(name)-25s %(levelname)-8s | %(message)s')
    baselog.setLevel(logging.DEBUG if args.debug else logging.INFO)

    log.debug('Starting')

    log.debug('done')
    logging.shutdown()
