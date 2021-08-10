
from abc import abstractmethod
import subprocess
import time
import yaml
from pathlib import Path
from .utils import read_var
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
    def run(self) -> None:
        pass


class AnsibleConfiguration(VMConfigurator):
    name: str
    ip: str
    playbook_path: str

    def __init__(self, name: str, ip: str) -> None:
        self.name = name
        self.ip = ip

    def test_connection(self) -> bool:
        return True  # todo

    def create_config(self) -> str:
        raise NotImplementedError(
            'no default ansible configuration, extend and provide your own')

    def generate(self, playbook_path: str):
        inventory_path = Path(read_var('INVENTORY_PATH'))

        with open(inventory_path, 'w') as conn:
            conn.write(inventory_config(self.ip))

        return inventory_path, playbook_path

    def run(self) -> None:
        start_time = time.monotonic()

        inventory_path, playbook_path = self.generate(self.playbook_path)
        subprocess.run(['ansible-playbook', '-i',
                       inventory_path, playbook_path])

        seconds_elapsed = round(time.monotonic() - start_time)
        logging.info(
            f'📦 devbox configured and ready to use at {self.ip} (+{seconds_elapsed}s)')


class VMConfiguratorProvisioner():
    backends: dict[str, type[VMConfigurator]] = {
        'ansible': AnsibleConfiguration
    }

    @staticmethod
    def create(backend: str, name: str, ip: str) -> VMConfigurator:
        """Create a DevBox instance with the requested backend service."""

        configurator = VMConfiguratorProvisioner.backends.get(backend)

        if configurator is None:
            raise Exception(
                f'software-configuration backend "{backend}" not supported')
        else:
            return configurator(name, ip)
