"""Require native outputs from every declared build matrix artifact."""

import sys
from pathlib import Path


def verify(root):
    versions = ["3.10", "3.11", "3.12", "3.13", "3.14"]
    platforms = {
        "ubuntu-latest": ".cpython-{abi}-x86_64-linux-gnu.so",
        "macos-latest": ".cpython-{abi}-darwin.so",
        "windows-latest": ".cp{abi}-win_amd64.pyd",
    }
    expected = {f"mypyc-{os}-py{version}" for os in platforms for version in versions}
    if {entry.name for entry in root.iterdir()} != expected:
        raise ValueError("Native matrix artifacts are missing or unexpected")
    for os, suffix in platforms.items():
        for version in versions:
            folder = root / f"mypyc-{os}-py{version}"
            pattern = "*" + suffix.format(abi=version.replace(".", ""))
            if not any(path.is_file() for path in folder.rglob(pattern)):
                raise ValueError(f"No matching native extension in {folder.name}")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
