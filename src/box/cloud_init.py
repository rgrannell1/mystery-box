#!/usr/bin/env python3

from abc import ABC, abstractmethod
import yaml
from pathlib import Path


class CloudInit(ABC):

    @abstractmethod
    def create_config(self) -> dict:
        pass

    def read_public_keys(self, fpaths: list[Path]) -> list[str]:
        results = []

        for fpath in fpaths:
            with open(fpath) as conn:
                content = conn.read()
                results.append(content)

        return results

    @abstractmethod
    def to_yaml(self) -> str:
        pass


class MinimalCloudInit(CloudInit):
    """Set up minimal cloud-init configuration that will allow SSH connections
    into an instance, and configures sone user"""

    def __init__(self, user: str, ssh_public_path: Path) -> None:
        self.user = user
        self.ssh_public_path = ssh_public_path

    def create_config(self) -> dict:
        ssh_keys = self.read_public_keys([self.ssh_public_path])

        return {
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
        }

    def to_yaml(self) -> str:
        return yaml.dump(self.create_config())


class BootstrappingCloudInit(CloudInit):
    """Windows doesn't support Ansible. That's ok; we'll set up a Multipass instance, and bootstrap b
    installling Ansible from cloud-init and calling Ansible over SSH. This has limitations; system-specific configuration
    and auxilarily ansible files won't be easily bundled up and sent to the remote instance"""

    def __init__(self, user: str, ssh_public_path: Path) -> None:
        self.user = user
        self.ssh_public_path = ssh_public_path

    def create_config(self) -> dict:
        ssh_keys = self.read_public_keys([self.ssh_public_path])

        return {
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
            ],
            'packages': [
                'python3-pip'
            ],
            'runcmd': [
                'sudo pip3 install ansible'
            ]
        }

    def to_yaml(self) -> str:
        return yaml.dump(self.create_config())
