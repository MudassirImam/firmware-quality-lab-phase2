"""Run the layered suite and emit JUnit XML plus a concise summary."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

def main() -> int:
    artifacts = Path("artifacts/phase2")
    artifacts.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable, "-m", "pytest", "-v",
        f"--junitxml={artifacts / 'junit.xml'}",
    ]
    return subprocess.call(command)

if __name__ == "__main__":
    raise SystemExit(main())
