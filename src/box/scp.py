
import os
import logging
from pathlib import Path
import paramiko

from .ssh import SSH


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

    def copy(self, folder: Path, src: Path, dest: Path) -> None:
        """Copy a file or folder from a local source to a remote destination"""

        _, ssh_private_path = SSH.save_keypair(folder)

        key = paramiko.RSAKey.from_private_key_file(
            str(ssh_private_path), password='')

        self.client.connect(self.ip, username=self.user,
                            pkey=key)

        sftp = self.client.open_sftp()

        if os.path.isdir(src):
            raise NotImplementedError(f'cannot copy {src}, as directory copies are not yet implemented')

        # -- update to support directories
        sftp.put(str(src), str(dest))
