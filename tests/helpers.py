import os
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE_ENCODINGS = FIXTURES / "encodings_test.pkl"
RECOGNIZE = Path(__file__).parent.parent / "recognize.py"


def run_recognize(
    image_path: str,
    encodings_path: Path = FIXTURE_ENCODINGS,
    known_faces_dir: Path = None,
):
    """Run recognize.py as a subprocess. Returns (stdout, stderr, returncode)."""
    env = {
        **os.environ,
        "FACE_RECOGNIZER_ENCODINGS_PATH": str(encodings_path),
    }
    if known_faces_dir is not None:
        env["FACE_RECOGNIZER_KNOWN_FACES_DIR"] = str(known_faces_dir)

    result = subprocess.run(
        [sys.executable, str(RECOGNIZE), image_path],
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode
