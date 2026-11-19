"""Linux real flock/CLI tests with synthetic data only; no database or secrets."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mvp03_ingest_adapter import writer_lock, IngestBusy, LocalBackend

class LockTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.d = Path(self.t.name)
        self.p = self.d / "ingest.lock"
        self.p.touch(mode=0o600)
    def test_reacquire(self):
        with writer_lock(self.p):
            with self.assertRaises(IngestBusy):
                with writer_lock(self.p): pass
        with writer_lock(self.p): pass
    def test_missing_file(self):
        self.p.unlink()
        with self.assertRaises(FileNotFoundError):
            with writer_lock(self.p): pass
        self.assertFalse(self.p.exists())
    def test_permissive_file(self):
        self.p.chmod(0o644)
        with self.assertRaises(PermissionError):
            with writer_lock(self.p): pass
    def test_permissive_dir(self):
        self.d.chmod(0o755)
        with self.assertRaises(PermissionError):
            with writer_lock(self.p): pass
    def test_symlink_file(self):
        self.p.unlink(); self.p.symlink_to("/dev/null")
        with self.assertRaises(OSError):
            with writer_lock(self.p): pass
    def test_symlink_dir(self):
        p=self.d / "alias"; p.symlink_to(self.d,target_is_directory=True)
        with self.assertRaises(OSError):
            with writer_lock(p / self.p.name): pass
    def test_hardlink(self):
        os.link(self.p, self.d / "other")
        with self.assertRaises(PermissionError):
            with writer_lock(self.p): pass
    def test_fifo(self):
        self.p.unlink(); os.mkfifo(self.p,0o600)
        with self.assertRaises(PermissionError):
            with writer_lock(self.p): pass
    def test_cross_process_busy(self):
        script="from mvp03_ingest_adapter import writer_lock,IngestBusy; import sys\ntry:\n with writer_lock(sys.argv[1]): pass\nexcept IngestBusy: sys.exit(17)\n"
        with writer_lock(self.p):
            r=subprocess.run([sys.executable,"-c",script,str(self.p)],timeout=10)
            self.assertEqual(r.returncode,17)
        r=subprocess.run([sys.executable,"-c",script,str(self.p)],timeout=10)
        self.assertEqual(r.returncode,0)
    def test_inherited_lock_survives_parent_close(self):
        with writer_lock(self.p) as fd:
            p=subprocess.Popen([sys.executable,"-c","import sys,os; os.fstat(int(sys.argv[1])); sys.stdin.read()",str(fd)],
                               stdin=subprocess.PIPE,pass_fds=(fd,))
        try:
            with self.assertRaises(IngestBusy):
                with writer_lock(self.p): pass
        finally:
            p.communicate(timeout=10)
        self.assertEqual(p.returncode,0)
        with writer_lock(self.p): pass
    def test_worker_passes_lock_fd(self):
        with writer_lock(self.p) as fd:
            with patch("mvp03_ingest_adapter.subprocess.run") as run:
                run.return_value=subprocess.CompletedProcess([],0,b"INCREMENTAL_INGEST_PASS\n",b"")
                LocalBackend(fd).apply("metadata",[])
                self.assertEqual(run.call_args.kwargs["pass_fds"],(fd,))
    def test_exception_releases(self):
        with self.assertRaises(RuntimeError):
            with writer_lock(self.p): raise RuntimeError("fixture")
        with writer_lock(self.p): pass

if __name__=="__main__": unittest.main()
