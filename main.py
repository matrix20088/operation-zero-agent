"""Make the cutest picture: Moonlight in a Teacup.

Entrypoint for make.fun. Uses Python standard library only and no network.
The illustration is pre-rendered in entry.png in this repository.
"""
from pathlib import Path
import os
import shutil
import struct

HERE = Path(__file__).resolve().parent
IMAGE = HERE / "entry.png"

def main():
    data = IMAGE.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Missing or invalid PNG")
    w, h = struct.unpack(">II", data[16:24])
    if (w, h) != (1024, 1024) or len(data) > 1024 * 1024:
        raise RuntimeError("Image dimensions or size are not permitted")
    outdir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "entry.png").write_bytes(data)

if __name__ == "__main__":
    main()
