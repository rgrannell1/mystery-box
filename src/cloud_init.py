#!/usr/bin/env python3

import yaml
from dotenv import load_dotenv
from pathlib import Path
from utils import read_var

load_dotenv()

def read_public_keys(fpaths: list[Path]) -> list[str]:
  """Read public SSH keys from a provided path"""

  results = []

  for fpath in fpaths:
    with open(fpath) as conn:
      content = conn.read()
      results.append(content)

  return results

def cloud_init() -> str:
  """Generate cloud-init file"""

  SSH_PUBLIC_PATH = Path(read_var('SSH_PUBLIC_PATH'))
  USER = read_var('USER')

  return yaml.dump({
    'users': [
      {
        'name': USER,
        'ssh-authorized-keys': read_public_keys([SSH_PUBLIC_PATH])
      }
    ],
    'package_upgrade': True,
    'packages': [
      'git'
    ]
  })

def write_cloud_init(fpath: Path):
  """Write cloud-init configuration to a temporary file"""

  with open(fpath, 'w') as conn:
    conn.write(cloud_init())

def main():
  CONFIG_PATH = Path(read_var('CONFIG_PATH'))

  write_cloud_init(CONFIG_PATH)
  print(CONFIG_PATH)

if __name__ == '__main__':
  main()
