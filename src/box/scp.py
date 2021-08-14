
import logging
import pathlib
import paramiko

from box import constants
from box.ssh import SSH


class SCP:
    """Manage SSH connections"""
    ip: str
    user: str
    client: paramiko.SSHClient

    def __init__(self, user: str, ip: str) -> None:
        self.user = user
        self.ip = ip

        logging.getLogger("paramiko").setLevel(logging.WARNING)

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.client.close()

    def copy(self, src: pathlib.Path, dest: pathlib.Path) -> None:
        _, ssh_private_path = SSH.save_keypair(
            constants.BUILD_FOLDER)

        key = paramiko.RSAKey.from_private_key_file(str(ssh_private_path))

        self.client.connect(self.ip, username=self.user,
                            pkey=key)

        sftp = self.client.open_sftp()

        # -- update to support directories
        sftp.put(str(src), str(dest))

        sftp.close()
