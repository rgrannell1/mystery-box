
from setuptools import setup, find_packages

requirements = [
    'docopt',
    'paramiko'
]

setup(
  name="Mystery Box",
  python_requires=">=3.9",
  install_requires=requirements,
  packages=find_packages(),
  entry_points = {
    'console_scripts': {
      'box=src.cli:main'
    }
  }
)
