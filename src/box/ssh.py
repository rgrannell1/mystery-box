
import os
import pathlib
import subprocess
import paramiko
from paramiko.rsakey import RSAKey

from box import constants


class SSH:
    """Manage SSH connections"""
    ip: str
    user: str
    client: paramiko.SSHClient

    def __init__(self, user: str, ip: str) -> None:
        self.user = user
        self.ip = ip
        self.client = paramiko.SSHClient()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.client.close()

    def open(self) -> None:
        """Open an SSH connection into a provided host, using native SSH"""

        _, ssh_private_path = SSH.save_keypair(constants.BUILD_FOLDER)
        subprocess.run(
            f'ssh {self.user}@{self.ip} -i {ssh_private_path}', shell=True)

    def run(self, cmd: str) -> None:
        """Run an SSH command, and print the output"""

        _, ssh_private_path = self.save_keypair(
            constants.BUILD_FOLDER)

        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.ip, username=self.user,
                            key_filename=str(ssh_private_path))

        _, stdout, _ = self.client.exec_command(cmd, get_pty=True)
        for line in iter(stdout.readline, ''):
            print(line, end='')

    @staticmethod
    def save_keypair(build_folder: pathlib.Path):
        """Save RSA public, private keys to a file"""

        # -- do the credentials exist?

        build_folder.chmod(0o700)

        if not os.path.isdir(build_folder):
            raise FileNotFoundError(f'{build_folder} does not exist')

        public_key_path = build_folder / 'mystery_box.pub'
        private_key_path = build_folder / 'mystery_box'

        public_key_exists = os.path.isfile(public_key_path)
        private_key_exists = os.path.isfile(private_key_path)

        if public_key_exists and private_key_exists:
            return public_key_path, private_key_path

        # -- if one, but not both exists, wipe the keys
        if public_key_exists or private_key_exists:
            if public_key_exists:
                os. remove(public_key_path)

            if private_key_exists:
                os.remove(private_key_path)

        # -- neither exists; save newly generated credentials

        # -- save a private-key
        priv_key = RSAKey.generate(bits=4096)
        priv_key.write_private_key_file(str(private_key_path), password=None)

        # -- save a public-key
        pub_key = RSAKey(filename=str(private_key_path), password=None)

        with open(public_key_path, 'w') as conn:
            conn.write('{0} {1}'.format(
                pub_key.get_name(), pub_key.get_base64()))

        return public_key_path, private_key_path
