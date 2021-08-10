
from setuptools import setup, find_packages

requirements = [
    'docopt',
    'python-dotenv'
]

setup(
  name="Mystery Box",
  python_requires=">=3.9",
  install_requires=requirements,
  packages=find_packages(),
  entry_points = """
      [console_scripts]
      box=box.cli:main
  """
)
