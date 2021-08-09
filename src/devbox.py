
import time
import subprocess
import logging
from pathlib import Path
from cloud_init import write_cloud_init
from utils import read_var
from multipass import Multipass


class DevBox:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def launch(self):
        config_path = Path(read_var('CONFIG_PATH'))
        write_cloud_init(config_path)

        Multipass.launch({
            'name': self.name,
            'config_path': config_path,
            'ram': '3G',
            'disk': '30G',
            'image': 'ubuntu'
        })

    def configure(self, ip: str, Configurator) -> None:
        """Configure the Multipass VM via external module."""

        conf = Configurator(self.name, ip)
        conf.run()

    def up(self, configurator) -> None:
        start_time = time.monotonic()
        info = Multipass.info(self.name)

        if not info or info['state'] != 'Running':
            self.launch()

        info = Multipass.info(self.name)
        if not info:
            logging.info(f'📦 {self.name}')
            return

        ipv4 = info['ipv4'][0]
        seconds_elapsed = round(time.monotonic() - start_time)

        logging.info(f'📦 {self.name} up at {ipv4} (+{seconds_elapsed}s)')

        logging.info(f'📦 configuring {self.name}...')
        self.configure(ipv4, configurator)

    def into(self, user: str) -> None:
        """SSH into the devbox"""

        user = user if user else read_var('USER')

        # add timeout
        Multipass.start(self.name)
        info = Multipass.info(self.name)
        if not info:
            logging.info(f'📦 {self.name}')
            return

        # todo polling in...

        ipv4 = info['ipv4'][0]
        subprocess.run(['ssh', f'{user}@{ipv4}'])

    def stop(self):
        Multipass.stop(self.name)

    def start(self):
        Multipass.start(self.name)
