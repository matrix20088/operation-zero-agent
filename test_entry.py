"""Offline, dependency-free regression checks for Operation Zero entry."""
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent

class TestMakeFunEntry(unittest.TestCase):
    def test_entry_runs_twice_deterministically(self):
        outputs=[]
        for _ in range(2):
            with tempfile.TemporaryDirectory() as d:
                env={**os.environ,"MAKEFUN_OUTPUT_DIR":d}
                subprocess.run([sys.executable,str(ROOT/"main.py")],env=env,cwd=d,check=True,timeout=60)
                outputs.append((Path(d)/"entry.png").read_bytes())
        self.assertEqual(outputs[0],outputs[1])
        self.assertTrue(outputs[0].startswith(b'\x89PNG\r\n\x1a\n'))
        self.assertEqual(struct.unpack(">II",outputs[0][16:24]),(640,640))
        self.assertLessEqual(len(outputs[0]),1048576)
        self.assertEqual(hashlib.sha256(outputs[0]).hexdigest(),"91c38983d18f04fa88dd2b60948ac0b7879ff9f85fee4a9d5e7ca203e3ec767b")

if __name__=="__main__":
    unittest.main()
