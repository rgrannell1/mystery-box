#!/usr/bin/env python3

import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def read_var (name: str) -> str:
  """Read environmental variables and assert they are present."""

  value = os.environ.get(name)

  if not value:
    raise Exception(f"name '{name}' not available.")

  return value

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

  return yaml.dump({
    'users': [
      {
        'name': 'rg',
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
