from pathlib import Path
from zipfile import ZipFile

import requests

BASE = "https://samples.scif.io/"
FILES = [
    "2chZT.zip",  # zeiss
    "mouse-kidney.zip",  # Leica LIF
    "leica_stack.zip",  # Leica
    "10-31_E1.zip",  # Olympus Fluoview TIFF
    "wtembryo.zip",  # quicktime
]
DEST_DIR = "sample_data"


def download_url(url, target_dir=".", chunk_size=128):
    Path(target_dir).mkdir(exist_ok=True)
    r = requests.get(url, stream=True)
    print("downloading", Path(url).name)
    dest = Path(target_dir) / Path(url).name
    with open(dest, "wb") as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
    with ZipFile(dest) as zf:
        zf.extractall(target_dir)
    Path(dest).unlink()


if __name__ == "__main__":
    import sys

    dest = sys.argv[1] if len(sys.argv) > 1 else DEST_DIR
    for f in FILES:
        download_url(BASE + f, dest)
    for p in Path(dest).glob("*.txt"):
        p.unlink()
