
from abc import abstractmethod
from pathlib import Path
import time
import yaml

from .box_config import BoxConfig
from .ssh import SSH
from .scp import SCP
from .utils import logging
from abc import ABC, abstractmethod


def inventory_config(ip: str) -> str:
    return yaml.dump({
        'all': {'hosts': ip}
    })


class VMConfigurator(ABC):
    """An abstract-class describing ways of configuring a VM"""
    @abstractmethod
    def __init__(self, name: str, ip: str) -> None:
        pass

    @abstractmethod
    def configure(self, cfg: BoxConfig) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass


class AnsibleConfiguration(VMConfigurator):
    """Describes how to configure a VM using Ansible."""
    name: str
    ip: str
    cfg: BoxConfig

    def __init__(self, name: str, ip: str) -> None:
        self.name = name
        self.ip = ip

    def configure(self, cfg: BoxConfig) -> None:
        self.cfg = cfg

    def create_config(self) -> str:
        raise NotImplementedError(
            'no default ansible configuration, extend and provide your own')

    def run(self) -> None:
        """Run an ansible playbook on the remote host."""
        start_time = time.monotonic()

        # -- first, copy all required resources over.
        with SCP(user='root', ip=self.ip) as scp:
            for entry in self.cfg.copy:
                try:
                    scp.copy(self.cfg.key_folder, entry['src'], entry['dest'])
                except:
                    raise IOError(
                        f"failed copying {entry['src']} to {entry['dest']}")

            for playbook in self.cfg.playbooks:
                scp.copy(self.cfg.key_folder, playbook,
                         Path(Path(playbook).name))

                # -- use ssh to call ansible on the remote host, to configure its own host on localhost.
                with SSH(user='root', ip=self.ip, cfg=self.cfg) as ssh:
                    ssh.run(self.cfg.key_folder,
                        f'ansible-playbook -i "localhost, " -c local {Path(Path(playbook).name)}')

            seconds_elapsed = round(time.monotonic() - start_time)
            logging.info(
                f'📦 devbox configured and ready to use at {self.ip} (+{seconds_elapsed}s)')


class VMConfigurators():
    ansible = AnsibleConfiguration
