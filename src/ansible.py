
import yaml
from pathlib import Path
from utils import read_var

def apt_install (name: str):
  return {
    'name': f'Install apt-package {name}',
    'apt': {
      'name': name
    }
  }

def ansible_config(name: str, ip: str) -> str:
  user = read_var('USER')

  return yaml.dump([
    {
      'name': f'Configure {name}',
      'hosts': ip,
      'remote_user': user,
      'tasks': [] + [apt_install(pkg) for pkg in [
        'build-essential',
        'libev-dev',
        'libpcre3-dev',
        'asciinema',
        'bpfcc-tools',
        'fzf',
        'python-pip',
        'python-pip3',
        'sensors',
        'smem',
        'upower'
      ]]
    }
  ])

def inventory_config(ip: str) -> str:
  return yaml.dump({
    'all': {
      'hosts': ip
    }
  })

def write_ansible_config(name: str, ip: str):
  with open(Path(read_var('ANSIBLE_PATH')), 'w') as conn:
    conn.write(ansible_config(name, ip))

  with open(Path(read_var('INVENTORY_PATH')), 'w') as conn:
    conn.write(inventory_config(ip))
