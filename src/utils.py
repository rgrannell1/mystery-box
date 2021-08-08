
import os

def read_var(name: str) -> str:
  """Read environmental variables and assert they are present."""

  value = os.environ.get(name)

  if not value:
    raise Exception(f"name '{name}' not available.")

  return value
