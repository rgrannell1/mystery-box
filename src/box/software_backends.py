
from abc import abstractmethod
from pathlib import Path
import tempfile
import time
import yaml

from box.box_config import BoxConfig
from box.ssh import SSH
from box.scp import SCP
from .utils import logging
from abc import ABC, abstractmethod


def inventory_config(ip: str) -> str:
    return yaml.dump({
        'all': {'hosts': ip}
    })


class VMConfigurator(ABC):
    @abstractmethod
    def __init__(self, name: str, ip: str) -> None:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    @abstractmethod
    def configure(self, cfg: BoxConfig) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass


class AnsibleConfiguration(VMConfigurator):
    name: str
    ip: str
    cfg: BoxConfig

    def __init__(self, name: str, ip: str) -> None:
        self.name = name
        self.ip = ip

    def configure(self, cfg: BoxConfig) -> None:
        self.cfg = cfg

    def test_connection(self) -> bool:
        return True  # todo

    def create_config(self) -> str:
        raise NotImplementedError(
            'no default ansible configuration, extend and provide your own')

    def run(self) -> None:
        start_time = time.monotonic()

        # -- first, copy all required resources over.
        with SCP(user='root', ip=self.ip) as scp:
            for entry in self.cfg.copy:
                scp.copy(entry['src'], entry['dest'])

            scp.copy(self.cfg.playbook, Path('/mystery-box-playbook.yaml'))

            # -- use ssh to call ansible on the remote host, to configure its own host on localhost
            with SSH(user='root', ip=self.ip) as ssh:
                ssh.run(
                    f'ansible-playbook -i "localhost, " -c local /mystery-box-playbook.yaml')

                seconds_elapsed = round(time.monotonic() - start_time)
                logging.info(
                    f'📦 devbox configured and ready to use at {self.ip} (+{seconds_elapsed}s)')


class VMConfigurators():
    ansible = AnsibleConfiguration
