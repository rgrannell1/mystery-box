
import os
from typing import Optional
from pathlib import Path


class BoxConfig:
    def __init__(self, user: str, ssh_public_path: str, memory: str, disk: str, playbook: str, copy: Optional[list[dict]]) -> None:
        self.user = user
        self.ssh_public_path = ssh_public_path
        self.memory = memory
        self.disk = disk
        self.playbook = playbook
        self.copy = copy

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        if value is None:
            raise ValueError('user is required')

        self._user = value

    @property
    def ssh_public_path(self):
        return self._ssh_public_path

    @ssh_public_path.setter
    def ssh_public_path(self, value):
        if value is None:
            raise ValueError('ssh_public_path is required')

        self._ssh_public_path = value

    @property
    def memory(self):
        return self._memory

    @memory.setter
    def memory(self, value):
        self._memory = value

    @property
    def disk(self):
        return self._disk

    @disk.setter
    def disk(self, value):
        self._disk = value

    @property
    def playbook(self):
        return self._playbook

    @playbook.setter
    def playbook(self, value):
        if value:
            if not os.path.exists(value):
                raise FileNotFoundError(f'file {value} does not exist')

            self._playbook = Path(value)

    @property
    def copy(self):
        return self._copy

    @copy.setter
    def copy(self, value):
        if value:
            if not isinstance(value, list):
                raise TypeError('copy value must be a list')

            processed = []
            for idx, entry in enumerate(value):
                if not isinstance(entry, dict):
                    raise TypeError(
                        f'copy entry #{str(idx)} must be a dictionary')

                if not 'src' in entry:
                    raise KeyError(f'dict entry #{idx} is missing "src" entry')
                elif not isinstance(entry['src'], str):
                    raise TypeError(
                        f'dict entry #{idx} src entry was not a string')
                elif not os.path.exists(entry['src']):
                    fpath = entry['src']
                    raise FileNotFoundError(f'file {fpath} does not exist')

                if not 'dest' in entry:
                    raise KeyError(
                        f'dict entry #{idx} is missing "dest" entry')
                elif not isinstance(entry['dest'], str):
                    raise TypeError(
                        f'dict entry #{idx} dest entry was not a string')

                processed.append({
                    'src': Path(entry['src']),
                    'dest': Path(entry['dest'])
                })

            self._copy = processed
