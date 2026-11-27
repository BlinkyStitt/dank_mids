import tempfile
import unittest
from pathlib import Path

from verify_native_artifacts import verify


class NativeArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for os, suffix in [
            ("ubuntu-latest", ".cpython-{abi}-x86_64-linux-gnu.so"),
            ("macos-latest", ".cpython-{abi}-darwin.so"),
            ("windows-latest", ".cp{abi}-win_amd64.pyd"),
        ]:
            for version in ["3.10", "3.11", "3.12", "3.13", "3.14"]:
                folder = self.root / f"mypyc-{os}-py{version}"
                folder.mkdir()
                (folder / ("module" + suffix.format(abi=version.replace(".", "")))).touch()

    def test_complete_native_matrix(self):
        verify(self.root)

    def test_missing_artifact(self):
        folder = self.root / "mypyc-windows-latest-py3.10"
        for path in folder.iterdir():
            path.unlink()
        folder.rmdir()
        with self.assertRaises(ValueError):
            verify(self.root)

    def test_python_source_is_not_native_evidence(self):
        folder = self.root / "mypyc-macos-latest-py3.14"
        for path in folder.iterdir():
            path.unlink()
        (folder / "module.py").touch()
        with self.assertRaises(ValueError):
            verify(self.root)

    def test_wrong_windows_abi(self):
        folder = self.root / "mypyc-windows-latest-py3.10"
        path = next(folder.iterdir())
        path.rename(folder / "module.cp311-win_amd64.pyd")
        with self.assertRaises(ValueError):
            verify(self.root)
