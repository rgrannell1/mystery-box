
import json
import subprocess
from .utils import logging


class Multipass:
    """Interact with Multipass."""
    @classmethod
    def list(cls):
        output = subprocess.check_output(
            ['multipass', 'ls', '--format', 'json'])
        info = json.loads(output)

        return info['list']

    @classmethod
    def running_vms(cls):
        info = Multipass.list()

        running = set()

        for inst in info:
            if inst['state'] == 'Running':
                running.add(inst['name'])

        return running

    @classmethod
    def info(cls, name: str):
        running = Multipass.running_vms()
        if not name in running:
            return None

        output = subprocess.check_output(
            ['multipass', 'info', name, '--format', 'json'])
        info = json.loads(output)

        for error in info['errors']:
            raise Exception(f'an error: {error}')

        return info['info'][name]

    @classmethod
    def launch(cls, opts: dict):
        name = opts['name']
        config = opts['config']
        ram = opts['ram']
        disk = opts['disk']
        image = opts['image']

        try:
            subprocess.check_output(['multipass', 'launch', '-n', name,
                                     '--cloud-init', '-',
                                     '-d', disk, '-m', ram, image], stderr=subprocess.STDOUT,
                                    input=config.encode())
        except subprocess.CalledProcessError as err:
            msg = err.output.decode('utf8')

            if 'Remote "" is unknown or unreachable.' in msg:
                logging.error(
                    'Cannot launch due to known issue with Multipass. Try running: sudo snap restart multipass')
                exit(1)
            elif "cannot connect to the multipass socket" in msg:
                logging.error(
                    'Cannot connect to multipass. Try running: sudo snap restart multipass')
                exit(1)
            else:
                logging.error(msg)
                exit(1)


    @classmethod
    def stop(cls, name: str):
        subprocess.run(['multipass', 'stop', name])

    @classmethod
    def start(cls, name: str):
        for vm in Multipass.list():
            if vm['name'] == name:
                if vm['state'] == 'Stopped':
                    subprocess.run(['multipass', 'start', name])
            return

        raise Exception(f'vm {name} does not exist')
