
import os
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__))

BUILD_FOLDER = Path(os.path.join(dir_path, '../../build')).resolve()
