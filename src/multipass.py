
import json
import subprocess


class Multipass:
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
    def launch(cls, launchArgs: dict):
        name = launchArgs['name']
        config_path = launchArgs['config_path']
        ram = launchArgs['ram']
        disk = launchArgs['disk']
        image = launchArgs['image']

        subprocess.run(['multipass', 'launch', '-n', name,
                       '--cloud-init', config_path,
                        '-d', disk, '-m', ram, image])
