import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from helpers import FIXTURES, FIXTURE_ENCODINGS, RECOGNIZE, run_recognize


def test_enrolled_face_returns_true():
    """Image of enrolled person → stdout is 'true'."""
    stdout, _, code = run_recognize(str(FIXTURES / "person_a_1.jpg"))
    assert stdout == "true"
    assert code == 0


def test_different_person_returns_false():
    """Image of a different person → stdout is 'false'."""
    stdout, _, code = run_recognize(str(FIXTURES / "person_b.jpg"))
    assert stdout == "false"
    assert code == 0


def test_no_face_returns_false():
    """Image with no face → stdout is 'false'."""
    stdout, _, code = run_recognize(str(FIXTURES / "no_face.png"))
    assert stdout == "false"
    assert code == 0


def test_missing_file_returns_false():
    """Non-existent file path → stdout is 'false'."""
    stdout, _, code = run_recognize("/nonexistent/path/image.jpg")
    assert stdout == "false"
    assert code == 0


def test_corrupt_image_returns_false(tmp_path):
    """Corrupt image bytes → stdout is 'false'."""
    corrupt = tmp_path / "corrupt.jpg"
    corrupt.write_bytes(b"this is not an image")
    stdout, _, code = run_recognize(str(corrupt))
    assert stdout == "false"
    assert code == 0


def test_no_arguments_returns_false():
    """No arguments → stdout 'false', exit 0, usage in stderr."""
    result = subprocess.run(
        [sys.executable, str(RECOGNIZE)],
        capture_output=True,
        text=True,
        env={**os.environ, "FACE_RECOGNIZER_ENCODINGS_PATH": str(FIXTURE_ENCODINGS)},
    )
    assert result.stdout.strip() == "false"
    assert result.returncode == 0
    assert "Usage" in result.stderr


def test_too_many_arguments_returns_false():
    """Too many arguments → stdout 'false', exit 0."""
    result = subprocess.run(
        [sys.executable, str(RECOGNIZE), "a.jpg", "b.jpg"],
        capture_output=True,
        text=True,
        env={**os.environ, "FACE_RECOGNIZER_ENCODINGS_PATH": str(FIXTURE_ENCODINGS)},
    )
    assert result.stdout.strip() == "false"
    assert result.returncode == 0


def test_missing_known_faces_at_enrollment_returns_false(tmp_path):
    """No encodings.pkl and no known_faces/ → stdout 'false', error in stderr."""
    missing_encodings = tmp_path / "no_encodings.pkl"
    missing_known = tmp_path / "no_known_faces"
    stdout, stderr, code = run_recognize(
        str(FIXTURES / "no_face.png"),
        encodings_path=missing_encodings,
        known_faces_dir=missing_known,
    )
    assert stdout == "false"
    assert code == 0
    # stderr should contain guidance about creating known_faces/
    assert "known_faces" in stderr.lower() or "error" in stderr.lower()


def test_corrupt_encodings_re_enroll_succeeds(tmp_path):
    """Corrupt encodings.pkl → re-enroll from valid known_faces/ → recognition proceeds."""
    # Write a corrupt pkl file
    corrupt_pkl = tmp_path / "corrupt.pkl"
    corrupt_pkl.write_bytes(b"not a pickle")

    # Provide a valid known_faces/ dir with Person A images
    known_dir = tmp_path / "known"
    known_dir.mkdir()
    shutil.copy(FIXTURES / "person_a_1.jpg", known_dir / "a1.jpg")

    stdout, stderr, code = run_recognize(
        str(FIXTURES / "person_a_1.jpg"),
        encodings_path=corrupt_pkl,
        known_faces_dir=known_dir,
    )
    assert stdout == "true"
    assert code == 0
    assert "re-enroll" in stderr.lower() or "warning" in stderr.lower()


def test_corrupt_encodings_re_enroll_fails_returns_false(tmp_path):
    """Corrupt encodings.pkl and no known_faces/ → stdout 'false'."""
    corrupt_pkl = tmp_path / "corrupt.pkl"
    corrupt_pkl.write_bytes(b"not a pickle")
    missing_known = tmp_path / "no_known_faces"

    stdout, _, code = run_recognize(
        str(FIXTURES / "no_face.png"),
        encodings_path=corrupt_pkl,
        known_faces_dir=missing_known,
    )
    assert stdout == "false"
    assert code == 0


def test_stdout_contains_only_true_or_false():
    """stdout is exactly 'true' or 'false' — nothing else."""
    stdout, _, _ = run_recognize(str(FIXTURES / "no_face.png"))
    assert stdout in ("true", "false")
