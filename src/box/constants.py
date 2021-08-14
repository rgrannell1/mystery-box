
import os
from pathlib import Path

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))

BUILD_FOLDER = (dir_path / '../../build').resolve()
