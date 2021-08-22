
from setuptools import setup, find_packages

requirements = [
    'docopt',
    'paramiko'
]

setup(
  name="Mystery Box",
  version="0.1",
  python_requires=">=3.9",
  install_requires=requirements,
  packages=find_packages(),
  entry_points = {
    'console_scripts': {
      'box=box.main:main'
    }
  }
)
