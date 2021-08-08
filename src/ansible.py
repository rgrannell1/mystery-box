
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
    'yadm',
    'zsh-antigen'
  ]] + [
    {
      'name': 'Set ZSH as a default shell',
      'user': {
        'name': user,
        'shell': '/bin/zsh'
      }
    },
    {
      'name': 'Clone Fzf',
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
    },
    {
      'name': 'Copy SSH Private Key',
      'copy': {
        'src': '~/.ssh/id_rsa',
        'dest': f'/home/{user}/.ssh/id_rsa',
        'mode': '0600',
        'owner': user
      }
    },
    {
      'name': 'Set SSH Configuration',
      'copy': {
        'content': 'Host github.com\n    StrictHostKeyChecking no\n',
        'dest': f'/etc/ssh/sshd_config',
        'mode': '0644'
      }
    },
    {
      'file': {
        'path': f'/home/{user}/.ssh',
        'mode': '0700',
        'owner': user
      }
    },
    {
      'name': 'Save Github to known hosts',
      'shell': f'ssh-keyscan github.com >> /etc/ssh/ssh_known_hosts'
    },
    {
      "name": "Clone Antigen",
      "shell": f"curl -L git.io/antigen > /home/{user}/antigen.zsh"
    },
    {
      'name': 'Install Zoxide',
      'shell': 'wget "http://ftp.uk.debian.org/debian/pool/main/r/rust-zoxide/zoxide_0.4.3-2+b1_amd64.deb" && dpkg -i zoxide_0.4.3-2+b1_amd64.deb'
    },
    {
      "name": "Clone dotfiles",
      "shell": f'eval "$(ssh-agent -s)" && ssh-add /home/{user}/.ssh/id_rsa && yadm clone -f git@github.com:rgrannell1/dotfiles.git',
      'remote_user': user
    },
    {
      'name': 'Install Go',
      'community.general.snap': {
        'name': 'go',
        'classic': 'yes'
      }
    },
    {
      'name': 'Clone Gecko',
      'git': {
        'repo': 'https://github.com/rgrannell1/gecko.git',
        'dest': f'/home/{user}/gecko',
        'clone': 'yes'
      },
      'become_user': user
    },
    {
      'name': 'Install Gecko',
      'shell': f'cd /home/{user}/gecko && go build && cp /home/{user}/gecko/gecko /usr/bin/gecko',
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
