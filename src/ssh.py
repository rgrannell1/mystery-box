
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
