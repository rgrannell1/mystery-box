
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

  tasks = [apt_install(pkg) for pkg in [
    'build-essential',
    'libev-dev',
    'libpcre3-dev',
    'asciinema',
    'bpfcc-tools',
    'fzf',
    'python3-pip',
    'smem',
    'upower',
    'zsh',
    'yadm'
  ]] + [
    {
      'name': 'Set ZSH as a default shell',
      'user': {
        'name': user,
        'shell': '/bin/zsh'
      }
    },
    {
      'name': 'clone fzf',
      'git': {
        'repo': 'https://github.com/junegunn/fzf.git',
        'dest': f'/home/{user}/.fzf',
        'clone': 'yes'
      },
      'become_user': user
    },
    {
      'name': 'Install fzf',
      'shell': f'yes | /home/{user}/.fzf/install'
    }
  ]

  return yaml.dump([
    {
      'name': f'Configure {name}',
      'hosts': ip,
      'remote_user': 'root',
      'tasks': tasks
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
