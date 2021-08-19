
import os
from typing import Optional
from pathlib import Path


class BoxConfig:
    """A dataclass for box-configuration, that validates each provided argument."""

    def __init__(self, user: str, memory: str, disk: str, playbooks: list[str], copy: Optional[list[dict]], key_folder: Path) -> None:
        self.user = user
        self.memory = memory
        self.disk = disk
        self.playbooks = playbooks
        self.copy = copy
        self.key_folder = key_folder

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        if value is None:
            raise ValueError('user is required')

        self._user = value

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
    def playbooks(self):
        return self._playbooks

    @playbooks.setter
    def playbooks(self, value):
        if value:
            if not isinstance(value, list):
                raise ValueError('expected playbooks to be a list')

            playbooks = []
            for playbook in value:
                if not os.path.exists(playbook):
                    raise FileNotFoundError(f'file {playbook} does not exist')

                playbooks.append(Path(playbook))

            self._playbooks = playbooks

    @property
    def key_folder(self):
        return self._key_folder

    @key_folder.setter
    def key_folder(self, value):
        if not value:
            raise ValueError('key_folder must be provided')

        if not os.path.exists(value):
            raise FileNotFoundError(f'folder {value} does not exist')

        self._key_folder = Path(value)

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
