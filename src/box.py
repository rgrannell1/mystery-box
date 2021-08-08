#!/usr/bin/env python3

"""Box

Usage:
  box up

Description:
   Run
"""

import json
import logging
import subprocess
from typing import Optional
from docopt import docopt
from pathlib import Path
from dotenv import load_dotenv
from cloud_init import read_var, write_cloud_init

logging.basicConfig(level=logging.INFO)

load_dotenv()

class Multipass:
  @classmethod
  def list(cls):
    output = subprocess.check_output(
        ['multipass', 'ls', '--format', 'json'])
    info = json.loads(output)

    return info['list']

  @classmethod
  def running_vms(cls):
    info = Multipass.list()

    running = set()

    for inst in info:
      if inst['state'] == 'Running':
        running.add(inst['name'])

    return running

  @classmethod
  def info(cls, name: str):
    running = Multipass.running_vms()
    if not name in running:
      return None

    output = subprocess.check_output(['multipass', 'info', name, '--format', 'json'])
    info = json.loads(output)

    for error in info['errors']:
      raise Exception(f'an error {error}')

    return info['info'][name]

  @classmethod
  def launch(cls, name: str, config_path: Path):
    subprocess.run(['multipass', 'launch', '-n', name,
                   '--cloud-init', config_path, 'ubuntu'])

class DevBox:
  name: str

  def __init__(self, name: str) -> None:
    self.name = name

  def info(self):
    return Multipass.info(self.name)

  def launch(self):
    config_path = Path(read_var('CONFIG_PATH'))
    write_cloud_init(config_path)

    subprocess.run(['multipass', 'launch', '-n', 'devbox',
                  '--cloud-init', config_path, 'ubuntu'])

    Multipass.launch(self.name, config_path)

  def up(self) -> None:
    info = self.info()

    if not info or info['state'] != 'Running':
      self.launch()

    info = self.info()
    if not info:
      logging.info(f'📦 {self.name}')
      return

    ipv4 = info['ipv4'][0]
    logging.info(f'📦 {self.name} up at {ipv4}!')

def box_up():
  """Bring an instance up"""

  vm = DevBox('devbox')
  vm.up()

def main():
  """Call the correct CLI command"""

  if args['up']:
    box_up()

if __name__ == '__main__':
  args = docopt(__doc__, version='Box 1.0')
  main()