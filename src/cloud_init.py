#!/usr/bin/env python3

from abc import ABC, abstractmethod
import yaml
from dotenv import load_dotenv
from pathlib import Path
from utils import read_var

load_dotenv()


class CloudInit(ABC):

    @abstractmethod
    def create_config(self) -> dict:
        pass

    @abstractmethod
    def write(self, fpath: Path) -> None:
        pass


class MinimalCloudInit:
    """Set up minimal cloud-init configuration that will allow SSH connections
    into an instance, and configures sone user"""

    def read_public_keys(self, fpaths: list[Path]) -> list[str]:
        results = []

        for fpath in fpaths:
            with open(fpath) as conn:
                content = conn.read()
                results.append(content)

        return results

    def create_config(self):
        USER = read_var('USER')
        SSH_PUBLIC_PATH = Path(read_var('SSH_PUBLIC_PATH'))

        ssh_keys = self.read_public_keys([SSH_PUBLIC_PATH])

        return {
            'users': [
                {
                    'name': 'root',
                    'ssh-authorized-keys': ssh_keys
                },
                {
                    'name': USER,
                    'ssh-authorized-keys': ssh_keys,
                    'groups': 'sudo',
                    'sudo': ['ALL=(ALL) NOPASSWD: ALL']
                }
            ]
        }

    def write(self, fpath: Path):
        """Write cloud-init configuration to a temporary file"""

        with open(fpath, 'w') as conn:
            config = self.create_config()
            conn.write(yaml.dump(config))
