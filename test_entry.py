"""Deterministic, offline entry tests; stdlib only."""
from pathlib import Path
import hashlib
import os
import subprocess
import struct
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent

class TestEntrypoint(unittest.TestCase):
    def test_two_offline_runs_are_identical(self):
        pngs=[]
        for _ in range(2):
            with tempfile.TemporaryDirectory() as directory:
                subprocess.run(
                    [sys.executable, str(HERE/"main.py")],
                    cwd=directory,
                    env={**os.environ, "MAKEFUN_OUTPUT_DIR": directory},
                    check=True, timeout=45,
                )
                pngs.append((Path(directory)/"entry.png").read_bytes())
        self.assertEqual(pngs[0],pngs[1])
        self.assertEqual(pngs[0],(HERE/"entry.png").read_bytes())
        self.assertTrue(pngs[0].startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual(struct.unpack(">II",pngs[0][16:24]),(1024,1024))
        self.assertLessEqual(len(pngs[0]),1024*1024)
        print("PNG SHA-256:",hashlib.sha256(pngs[0]).hexdigest())
        print("PNG size:",len(pngs[0]))

if __name__ == "__main__":
    unittest.main()
