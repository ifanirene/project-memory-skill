"""A deleted private file must still be detected in reachable history."""
from pathlib import Path
import subprocess
import sys


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_public_package.py"


def test_current_files_and_historical_exposure(tmp_path):
    def git(*args):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)

    def scan(*args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(tmp_path), *args],
            capture_output=True, text=True,
        )

    git("init")
    git("config", "user.name", "Example")
    git("config", "user.email", "example@example.invalid")
    private = tmp_path / "audits/private.md"
    private.parent.mkdir()
    private.write_text("/" + "Users/example/private-project\n")
    git("add", ".")
    git("commit", "-m", "Add a fixture")
    current = scan()
    assert current.returncode == 1
    assert "private artifact: audits/private.md" in current.stdout
    assert "personal machine path" in current.stdout
    assert scan("--history").returncode == 1

    git("rm", "audits/private.md")
    (tmp_path / "README.md").write_text("Generic package documentation.\n")
    git("add", ".")
    git("commit", "-m", "Remove fixture from current tree")
    assert scan().returncode == 0
    historical = scan("--history")
    assert historical.returncode == 1
    assert "audits/private.md" in historical.stdout
