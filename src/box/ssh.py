
import os
import pathlib
import subprocess
import paramiko

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

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

        _, ssh_private_path = SSH.generate_keypair()

        subprocess.run(
            ['ssh', f'{self.user}@{self.ip}', '-i ', ssh_private_path])

    def run(self, cmd: str) -> None:
        _, ssh_private_path = self.save_keypair(
            constants.BUILD_FOLDER)

        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.ip, username=self.user,
                            key_filename=str(ssh_private_path))

        self.client.exec_command(cmd)

    @staticmethod
    def generate_keypair():
        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            # -- not a choice by me; this is a mandatory constant
            public_exponent=65537,
            # -- big key secure key
            key_size=4096
        )

        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption())

        public_key = key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH
        )

        return public_key, private_key

    @staticmethod
    def save_keypair(build_folder: pathlib.Path):
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
                os. remove(private_key_path)

        # -- neither exists; save newly generated credentials
        public_key, private_key = SSH.generate_keypair()

        with open(public_key_path, 'w') as conn:
            conn.write(public_key.decode('utf8'))

        public_key_path.chmod(0o600)

        with open(private_key_path, 'w') as conn:
            conn.write(private_key.decode('utf8'))

        private_key_path.chmod(0o600)

        return public_key_path, private_key_path
