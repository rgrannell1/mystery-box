
import os
import time
import yaml
from yaml.parser import ParserError
from .utils import logging
from pathlib import Path
from typing import Optional
from .cloud_init import MinimalCloudInit
from .ssh import SSH
from .utils import read_var
from .multipass import Multipass
from abc import ABC, abstractmethod
from .software_backends import VMConfiguratorProvisioner


class DevBox(ABC):
    @abstractmethod
    def __init__(self, name: str) -> None:
        pass

    @abstractmethod
    def launch(self, opts: dict[str, str]) -> None:
        pass

    @abstractmethod
    def up(self, opts: dict[str, str]) -> None:
        pass

    @abstractmethod
    def into(self, user: str) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def test(self) -> None:
        pass

    @abstractmethod
    def configure(self, playbook: Optional[str]) -> None:
        pass

    @abstractmethod
    def ip(self) -> Optional[str]:
        pass


class DevBoxMultipass(DevBox):
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def launch(self, opts: dict[str, str]) -> None:
        config_path = Path(read_var('CONFIG_PATH'))

        MinimalCloudInit().write(config_path)

        Multipass.launch({
            'name': self.name,
            'config_path': config_path,
            'ram': opts['memory'],
            'disk': opts['disk'],
            'image': 'ubuntu'
        })

    def configure(self, playbook: Optional[str]) -> None:
        if playbook:
            # -- configure via ansible, otherwise just exit.

            logging.info(f'📦 configuring {self.name}...')

            ipv4 = self.ip()

            if not ipv4:
                logging.error(f'📦 ipv4 not present')
                exit(1)

            configurator = VMConfiguratorProvisioner.create(
                'ansible', self.name, ipv4)

            configurator.playbook_path = Path(playbook).resolve()
            configurator.run()

    def ip(self) -> Optional[str]:
        info = Multipass.info(self.name)
        return info['ipv4'][0] if info else None

    def load_config(self, fpath: Optional[str]) -> dict[str, str]:
        default_cfg = os.path.join(os.getcwd(), 'box.yaml')

        if fpath and not os.path.exists(fpath):
            logging.error(f'file "{fpath}" does not exist.')
            exit(1)
        elif default_cfg and not os.path.exists(default_cfg):
            return {}

        tgt = fpath if fpath else default_cfg

        with open(tgt) as conn:
            cfg = conn.read()

            try:
                return yaml.load(cfg, Loader=yaml.SafeLoader)
            except:
                raise ParserError(f'failed to parse {tgt} as yaml')


    def up(self, opts: dict[str, str]) -> None:
        cfg = self.load_config(opts.get('config'))

        default_opts = cfg

        start_time = time.monotonic()
        info = Multipass.info(self.name)

        if not info or info['state'] != 'Running':
            self.launch({
                'disk': default_opts['disk'],
                'memory': default_opts['memory']
            })

        ipv4 = self.ip()

        if not ipv4:
            logging.error(f'📦 ipv4 not present')
            exit(1)

        seconds_elapsed = round(time.monotonic() - start_time)

        logging.info(f'📦 {self.name} up at {ipv4} (+{seconds_elapsed}s)')

        self.configure(default_opts['playbook'])


    def launch(self, opts: dict[str, str]) -> None:
        start_time = time.monotonic()
        info = Multipass.info(self.name)

        if not info or info['state'] != 'Running':
            self.launch({
                'disk': opts['disk'],
                'memory': opts['memory']
            })

        ipv4 = self.ip()

        if not ipv4:
            logging.error(f'📦 ipv4 not present')
            exit(1)

        seconds_elapsed = round(time.monotonic() - start_time)

        logging.info(f'📦 {self.name} up at {ipv4} (+{seconds_elapsed}s)')

        self.configure(opts['playbook'])


    def into(self, user: str) -> None:
        """SSH into the devbox"""

        user = user if user else read_var('USER')

        Multipass.start(self.name)
        ipv4 = self.ip()

        if ipv4:
            SSH(user, ipv4).open()
        else:
            logging.error(f'📦 cannot access instance, no IP found.')

    def stop(self):
        Multipass.stop(self.name)

    def start(self):
        Multipass.start(self.name)

    def test(self):
        raise NotImplementedError('test is not implemented yet')


class DevBoxProvisioner():
    backends: dict[str, type[DevBox]] = {
        'multipass': DevBoxMultipass
    }

    @staticmethod
    def create(backend: str, name: str) -> DevBox:
        """Create a DevBox instance with the requested backend service."""

        DevBoxBackend = DevBoxProvisioner.backends.get(backend)

        if DevBoxBackend is None:
            raise Exception(f'backend "{backend}" not supported')
        else:
            return DevBoxBackend(name)
