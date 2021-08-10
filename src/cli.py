#!/usr/bin/env python3

"""Mystery-Box: The Box! The Box!

Usage:
  box up [--memory <memory>] [--disk <disk>] [--backend <backend>] [--playbook <str>]
  box in [--user <user>]
  box configure [--playbook <str>]
  box test
  box start
  box stop
  box (-h|--help)

Description:
  Set up my development environment:

  * repeatably
  * with no manual intervention
  * against VM host I need

  By default, `box` provisions a multipass VM via cloud-init and Ansible.

Options:
  --user <user>        the user to log in as. Either root, or the user configured in .env.
  --memory <memory>    the RAM memory to provision the instances with. [default: 3G]
  --disk <disk>        the disk-space to provision the instances with. [default: 30G]
  --backend <backend>  which technology should be used to host the development box? [default: multipass]
  --playbook <str>     path to an Ansible playbook for provisioning this instance.
  -h,--help            show this documentation
"""

from docopt import docopt
from dotenv import load_dotenv
from hardware_backends import DevBoxProvisioner

load_dotenv()


def main(args):
    """Call the correct CLI command"""

    vm = DevBoxProvisioner.create('multipass', 'devbox')

    if args['up']:
        vm.up({
            'disk': args['--disk'],
            'memory': args['--memory'],
            'playbook': args['--playbook']
        })
    elif args['in']:
        vm.into(args['--user'])
    elif args['stop']:
        vm.stop()
    elif args['start']:
        vm.start()
    elif args['test']:
        vm.test()
    elif args['configure']:
        vm.configure(args['--playbook'])


if __name__ == '__main__':
    args = docopt(__doc__, version='Box 1.0')
    main(args)
