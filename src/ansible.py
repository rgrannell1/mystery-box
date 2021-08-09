
import subprocess
import json
import time
import yaml
from pathlib import Path
from utils import read_var
import logging

logging.basicConfig(level=logging.INFO)


def apt_install(name: str) -> dict:
    return {
        'name': f'Install apt-package {name}',
        'apt': {
            'name': name
        }
    }


def snap_install(name: str, classic = False) -> dict:
    return {
        'name': f'Install snap-package {name}',
        'snap': {
            'name': name,
            'classic': classic
        }
    }


def classic_snap_install(name: str):
  return snap_install(name, True)

APT_PACKAGES = [
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
]

user = read_var('USER')


def setup_apt_packages() -> list[dict]:
    return [apt_install(pkg) for pkg in APT_PACKAGES]


def setup_carp() -> list[dict]:
    return [
        {
            'name': 'Clone Carp',
            'git': {
                'repo': 'https://github.com/rgrannell1/carp.git',
                'dest': f'/home/{user}/carp',
                'clone': 'yes'
            },
            'become_user': user
        },
        {
            'name': 'Install Carp',
            'shell': f'cd /home/{user}/carp && go build && cp /home/{user}/carp/carp /usr/bin/carp',
        }
    ]


def setup_gecko() -> list[dict]:
    return [
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


def setup_fzf() -> list[dict]:
    return [
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
        }
    ]


def setup_ssh() -> list[dict]:
    return [
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
            'file': {
                'path': f'/home/{user}/.ssh',
                'mode': '0700',
                'owner': user
            }
        },
        {
            'name': 'Save Github to known hosts',
            'shell': f'ssh-keyscan github.com >> /etc/ssh/ssh_known_hosts'
        }
    ]


def setup_antigen() -> list[dict]:
    return [{
        "name": "Clone Antigen",
        "shell": f"curl -L git.io/antigen > /home/{user}/antigen.zsh"
    }]


def setup_zoxide() -> list[dict]:
    return [{
        'name': 'Install Zoxide',
        'shell': 'wget "http://ftp.uk.debian.org/debian/pool/main/r/rust-zoxide/zoxide_0.4.3-2+b1_amd64.deb" && dpkg -i zoxide_0.4.3-2+b1_amd64.deb'
    }]


def setup_dotfiles() -> list[dict]:
    return [{
        "name": "Clone dotfiles",
        "shell": f'eval "$(ssh-agent -s)" && ssh-add /home/{user}/.ssh/id_rsa && yadm clone -f git@github.com:rgrannell1/dotfiles.git',
        'remote_user': user
    }]


def setup_env_locale() -> list[dict]:
    # -- this bricks the machine

    return [
        {
            'lineinfile': {
                'path': '/etc/environment',
                'line': 'LANG=en_US.utf-8'
            }
        },
        {
            'lineinfile': {
                'path': '/etc/environment',
                'line': 'LC_ALL=en_US.utf-8'
            }
        }
    ]


def setup_nodejs() -> list[dict]:
    return [{
        'name': 'Add NVM',
        'shell': 'curl -sL https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.0/install.sh -o install_nvm.sh && bash install_nvm.sh',
        'remote_user': user
    }]


def set_user_shell() -> list[dict]:
    return [{
        'name': 'Set ZSH as a default shell',
        'user': {
            'name': user,
            'shell': '/bin/zsh'
        }
    }]


CLASSIC_SNAP_PACKAGES = [
    'bashtop',
    'go',
    'hotline',
    'kale',
    'kohl',
    'rpgen',
    'polonium',
    'duf-utility',
    'gron'
]


def setup_snap_packages() -> list[dict]:
    return [classic_snap_install(name) for name in CLASSIC_SNAP_PACKAGES]


def disable_motd() -> list[dict]:
    return [{
        'name': 'Disable Motd',
        'shell': 'chmod -x /etc/update-motd.d/*'
    }]

def test_reboot() -> list[dict]:
    return [{
        'name': 'Test that rebooted instances come back up',
        'reboot': {
            'reboot_timeout': 60
        }
    }]


def test_carp() -> list[dict]:
    return [{
        'name': 'Test that rebooted instances come back up',
        'shell': f'carp /home/{user}/carpfile.py --group devbox'
    }]


def ansible_config(name: str, ip: str) -> str:
    setup_tasks = (
        setup_apt_packages() +
        set_user_shell() +
        setup_fzf() +
        setup_ssh() +
        setup_antigen() +
        setup_zoxide() +
        setup_dotfiles() +
        setup_nodejs() +
        setup_snap_packages() +
        disable_motd() +
        setup_env_locale() +
        setup_gecko() +
        setup_carp())

    test_tasks = (
        test_reboot() + test_carp()
    )

    # -- add tests

    return yaml.dump([
        {
            'name': f'Configure {name}',
            'hosts': ip,
            'remote_user': 'root',
            'tasks': setup_tasks + test_tasks
        }
    ])


def inventory_config(ip: str) -> str:
    return yaml.dump({
        'all': {'hosts': ip}
    })


class AnsibleConfiguration:
    name: str
    ip: str

    def __init__(self, name: str, ip: str) -> None:
        self.name = name
        self.ip = ip

    def generate(self):
        playbook_path = Path(read_var('ANSIBLE_PATH'))

        with open(playbook_path, 'w') as conn:
            conn.write(ansible_config(self.name, self.ip))

        inventory_path = Path(read_var('INVENTORY_PATH'))
        with open(inventory_path, 'w') as conn:
            conn.write(inventory_config(self.ip))

        return inventory_path, playbook_path

    def run(self) -> None:
        start_time = time.monotonic()

        inventory_path, playbook_path = self.generate()
        subprocess.run(['ansible-playbook', '-i',
                       inventory_path, playbook_path])

        seconds_elapsed = round(time.monotonic() - start_time)
        logging.info(
            f'📦 devbox configured and ready to use at {self.ip} (+{seconds_elapsed}s)')
