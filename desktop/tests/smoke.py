"""Check the reader served by the Python runtime and files that will ship."""
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

runtime, resources = sys.argv[1:]
with subprocess.Popen([runtime, "-E", "-s", "-B", str(Path(resources) / "backend/desktop.py")],
                      stdout=subprocess.PIPE, text=True) as reader:
    try:
        assert reader.stdout.readline().strip() == "ready"
        with urlopen("http://127.0.0.1:18371/", timeout=5) as response:
            assert b"SOS My Feed" in response.read()
    finally:
        reader.terminate()
