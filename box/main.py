#!/usr/bin/env python3

"""Mystery-Box: The Box! The Box!

Usage:
  box up [--config <str>]
  box in [--user <user>] [--config <str>]
  box configure [--playbook <str>]
  box start
  box stop
  box delete
  box (-h|--help)

Description:
  Set up my development environment:

  * repeatably
  * with no manual intervention
  * against VM host I need

  By default, `box` provisions a multipass VM via cloud-init and Ansible.

Options:
  --config <str>       the path to a box configuration file
  --user <user>        the user to log in as. Either root, or the user configured in .env.
  --memory <memory>    the RAM memory to provision the instances with. [default: 3G]
  --disk <disk>        the disk-space to provision the instances with. [default: 30G]
  --backend <backend>  which technology should be used to host the development box? [default: multipass]
  --playbook <str>     path to an Ansible playbook for provisioning this instance.
  -h,--help            show this documentation
"""

from docopt import docopt
from src.box import hardware_backends

def main():
    """Call the correct CLI command"""

    args = docopt(__doc__, version='Box 1.0')

    vm = hardware_backends.DevBoxProvisioner.multipass('devbox')

    if args['up']:
        vm.up()
    elif args['in']:
        vm.into({
            'user': args['--user'],
            'config': args['--config']
        })
    elif args['stop']:
        vm.stop()
    elif args['start']:
        vm.start()
    elif args['configure']:
        vm.configure(args['--playbook'])
    elif args['delete']:
        vm.delete()

if __name__ == '__main__':
    main()
