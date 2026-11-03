"""Builds the runnable CoreSight tree in workspace/.

This repo holds only work done during the hackathon. The code written before
kickoff stays in its own public repo. This script fetches it at the pinned
commit, applies our changes to those files and adds the files from this repo.
Needs git and Python 3.11+.
"""

import pathlib
import shutil
import stat
import subprocess
import sys

BASE_REPO = "https://github.com/Raul99Alejandro/coresight.git"
BASE_COMMIT = "14bc545a8f0190f6ffeb452378406bf86e2ca1ee"
ROOT = pathlib.Path(__file__).resolve().parent
WORK = ROOT / "workspace"
PATCH = ROOT / "patches" / "changes-to-pre-event-files.patch"
# Removed during the hackathon.
DELETED = ["docs/PLAN.md"]
# Files that describe this repo, not the product.
NOT_COPIED = {".git", ".github", ".gitattributes", ".gitignore", ".venv", ".env", "install.py", "patches", "workspace"}


def git(*args: str) -> None:
    subprocess.run(["git", "-C", str(WORK), *args], check=True)


def writable(func, path, _exc) -> None:
    pathlib.Path(path).chmod(stat.S_IWRITE)
    func(path)


def main() -> None:
    if WORK.exists():
        if "--force" not in sys.argv:
            sys.exit("workspace/ already exists. Run with --force to rebuild it; that deletes its .env and .venv.")
        shutil.rmtree(WORK, onerror=writable)
    WORK.mkdir()
    git("init", "-q")
    git("config", "core.autocrlf", "false")
    git("fetch", "-q", "--depth", "1", BASE_REPO, BASE_COMMIT)
    git("checkout", "-q", "FETCH_HEAD")
    git("apply", "--whitespace=nowarn", str(PATCH))
    for name in DELETED:
        (WORK / name).unlink()
    for item in ROOT.iterdir():
        if item.name in NOT_COPIED:
            continue
        target = WORK / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(item, target)
    print(f"Ready: {WORK}")


if __name__ == "__main__":
    main()
