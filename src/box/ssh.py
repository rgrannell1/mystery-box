
from pathlib import Path
import subprocess


class SSH:
    """Manage SSH connections"""
    ip: str
    user: str

    def __init__(self, user: str, ip: str) -> None:
        self.user = user
        self.ip = ip

    def open(self) -> None:
        """Open an SSH connection into a provided host."""

        subprocess.run(['ssh', f'{self.user}@{self.ip}'])

    def run(self, cmd: str) -> None:
        subprocess.run(
            ['ssh', f'{self.user}@{self.ip}', '-o StrictHostKeyChecking=no', cmd])


class SCP:
    """Manage SSH connections"""
    ip: str
    user: str

    def __init__(self, user: str, ip: str) -> None:
        self.user = user
        self.ip = ip

    def copy(self, src: Path, dest: Path) -> None:
        subprocess.run(['rsync', '-a', src, f'{self.user}@{self.ip}:{dest}'])
