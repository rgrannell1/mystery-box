#!/usr/bin/env python3

"""Box

Usage:
  box up
  box in [--user <user>]
  box start
  box stop

Description:
  Set up a

Options:
  --user <user>    the user to log in as. Either root, or the user configured in .env
"""

import logging
from docopt import docopt
from dotenv import load_dotenv
from ansible import AnsibleConfiguration
from devbox import DevBox

logging.basicConfig(level=logging.INFO)

load_dotenv()


def main():
    """Call the correct CLI command"""

    vm = DevBox('devbox')

    if args['up']:
        vm.up(AnsibleConfiguration)
    elif args['in']:
        vm.into(args['--user'])
    elif args['stop']:
        vm.stop()
    elif args['start']:
        vm.start()


if __name__ == '__main__':
    args = docopt(__doc__, version='Box 1.0')
    main()
