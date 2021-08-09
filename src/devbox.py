
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
        info = Multipass.info(self.name)

        if not info or info['state'] != 'Running':
            self.launch()

        info = Multipass.info(self.name)
        if not info:
            logging.info(f'📦 {self.name}')
            return

        ipv4 = info['ipv4'][0]
        logging.info(f'📦 {self.name} up at {ipv4}')

        self.configure(ipv4, configurator)
