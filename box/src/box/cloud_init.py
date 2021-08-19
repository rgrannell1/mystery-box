#!/usr/bin/env python3

from abc import ABC, abstractmethod
import yaml
from pathlib import Path

from .ssh import SSH


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


class BootstrappingCloudInit(CloudInit):
    """Windows doesn't support Ansible. That's ok; we'll set up a Multipass instance, and bootstrap b
    installling Ansible from cloud-init and calling Ansible over SSH. This has limitations; system-specific configuration
    and auxilarily ansible files won't be easily bundled up and sent to the remote instance"""

    cfg: dict

    def __init__(self, user: str, folder: Path) -> None:
        self.user = user
        self.cfg = self.create_config(folder)

    def create_config(self, folder: Path) -> dict:
        """Create minimal cloud-init configuration"""

        ssh_public_path, _ = SSH.save_keypair(folder)
        ssh_keys = self.read_public_keys([ssh_public_path])

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
            ],
            'write_files': [
                {
                    'path': '/etc/environment',
                    'content': 'LANG=en_US.utf-8\nLC_ALL=en_US.utf-8\n'
                }
            ]
        }

    def to_yaml(self) -> str:
        """Convert Cloud-Init configuration to YAML"""
        return yaml.dump(self.cfg)
