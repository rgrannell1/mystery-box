#!/usr/bin/env python3

"""Box

Usage:
  box up

Description:
   Run
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

    if args['up']:
        vm = DevBox('devbox')
        vm.up(AnsibleConfiguration)


if __name__ == '__main__':
    args = docopt(__doc__, version='Box 1.0')
    main()
