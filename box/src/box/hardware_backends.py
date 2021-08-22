
import os
import time
import yaml
from yaml.parser import ParserError

from .utils import logging
from typing import Optional
from .cloud_init import BootstrappingCloudInit
from .ssh import SSH
from .multipass import Multipass
from abc import ABC, abstractmethod
from .software_backends import VMConfigurators
from .box_config import BoxConfig


class DevBox(ABC):
    """An abstract class for each hardware backend"""
    @abstractmethod
    def __init__(self, name: str) -> None:
        pass

    @abstractmethod
    def up(self) -> None:
        pass

    @abstractmethod
    def into(self, opts: dict) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def configure(self, cfg: BoxConfig) -> None:
        pass

    @abstractmethod
    def ip(self) -> Optional[str]:
        pass


class DevBoxMultipass(DevBox):
    """Set up a devbox using multipass as a VM middle-layer, and
    ansible as a configurator"""
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def configure(self, cfg: BoxConfig) -> None:
        """configure the multipass VM"""
        if not cfg.playbooks:
            return

        # -- configure via ansible, otherwise just exit.

        logging.info(f'📦 configuring {self.name}...')

        ipv4 = self.ip()

        if not ipv4:
            logging.error(f'📦 ipv4 not present')
            exit(1)

        configurator = VMConfigurators.ansible(self.name, ipv4)
        configurator.configure(cfg)
        configurator.run()

    def ip(self) -> Optional[str]:
        """Fetch an IP address for a multipass vm"""
        info = Multipass.info(self.name)
        return info['ipv4'][0] if info else None

    def load_config(self, fpath: Optional[str]) -> BoxConfig:
        """Load configuration from a file"""
        default_cfg = os.path.join(os.getcwd(), 'box.yaml')

        if fpath and not os.path.exists(fpath):
            logging.error(f'file "{fpath}" does not exist.')
            exit(1)
        elif default_cfg and not os.path.exists(default_cfg):
            logging.error(f'file "{default_cfg}" does not exist.')
            exit(1)

        tgt = fpath if fpath else default_cfg

        with open(tgt) as conn:
            try:
                opts = yaml.load(conn.read(), Loader=yaml.SafeLoader)

                return BoxConfig(
                    user=opts['user'],
                    memory=opts['memory'],
                    disk=opts['disk'],
                    playbooks=opts['playbooks'],
                    copy=opts['copy'],
                    key_folder=opts['key_folder']
                )
            except:
                raise ParserError(f'failed to parse {tgt} as yaml')

    def up(self) -> None:
        """Initialise and configure a multipass VM"""
        cfg = self.load_config(None)

        start_time = time.monotonic()
        info = Multipass.info(self.name)

        if not info or info['state'] != 'Running':
            # -- we shouldn't assume Ansible is present on the machine; let's copy any ansible
            # -- content to the VM, and have the VM configure itself! One restriction is we can only really
            # -- work within a single directory

            cloud_init = BootstrappingCloudInit(
                cfg.user, cfg.key_folder).to_yaml()

            Multipass.launch({
                'name': self.name,
                'config': cloud_init,
                'ram': cfg.memory,
                'disk': cfg.disk,
                'image': 'ubuntu'
            })

        ipv4 = self.ip()

        if not ipv4:
            logging.error(f'📦 ipv4 not present')
            exit(1)

        seconds_elapsed = round(time.monotonic() - start_time)

        logging.info(f'📦 {self.name} hardware up at {ipv4} (+{seconds_elapsed}s)')
        start_time = time.monotonic()

        self.configure(cfg)

        seconds_elapsed = round(time.monotonic() - start_time)

        logging.info(
            f'📦 {self.name} fully configured and ready to use (+{seconds_elapsed}s)')


    def into(self, opts: dict) -> None:
        """SSH into the devbox"""

        cfg = self.load_config(opts.get('config'))

        user = opts['user'] if opts.get('user') else cfg.user

        Multipass.start(self.name)
        ipv4 = self.ip()

        if ipv4:
            with SSH(user, ipv4, cfg) as ssh:
                ssh.open(cfg.key_folder)
        else:
            logging.error(f'📦 cannot access instance, no IP found.')

    def stop(self):
        """Stop a multipass devbox"""
        Multipass.stop(self.name)

    def start(self):
        """Start a multipass devbox"""
        Multipass.start(self.name)

    def delete(self):
        """Delete a multipass devbox"""
        Multipass.delete(self.name)


class DevBoxProvisioner():
    multipass = DevBoxMultipass
