#!/usr/bin/env python3

from abc import ABC, abstractmethod
import yaml
from pathlib import Path


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

    def __init__(self, user: str, ssh_public_path: Path) -> None:
        self.user = user
        self.ssh_public_path = ssh_public_path

    def read_public_keys(self, fpaths: list[Path]) -> list[str]:
        results = []

        for fpath in fpaths:
            with open(fpath) as conn:
                content = conn.read()
                results.append(content)

        return results

    def create_config(self) -> str:
        ssh_keys = self.read_public_keys([self.ssh_public_path])

        return yaml.dump({
            'users': [
                {
                    'name': 'root',
                    'ssh-authorized-keys': ssh_keys
                },
                {
                    'name': self.user,
                    'ssh-authorized-keys': ssh_keys,
                    'groups': 'sudo',
                    'sudo': ['ALL=(ALL) NOPASSWD: ALL']
                }
            ]
        })
