import pickle
import shutil
from pathlib import Path

import numpy as np
import pytest

from encoder import encode_known_faces

FIXTURES = Path(__file__).parent / "fixtures"


def test_encodes_single_person(tmp_path):
    """Two images of the same person produce a list with 2 encodings."""
    known_dir = tmp_path / "known"
    known_dir.mkdir()
    shutil.copy(FIXTURES / "person_a_1.jpg", known_dir / "a1.jpg")
    shutil.copy(FIXTURES / "person_a_2.jpg", known_dir / "a2.jpg")

    output = tmp_path / "encodings.pkl"
    encode_known_faces(known_dir, output)

    with open(output, "rb") as f:
        encodings = pickle.load(f)

    assert len(encodings) == 2
    assert all(isinstance(e, np.ndarray) for e in encodings)
    assert all(e.shape == (128,) for e in encodings)


def test_raises_if_known_faces_dir_missing(tmp_path):
    """FileNotFoundError if known_faces/ does not exist."""
    output = tmp_path / "encodings.pkl"
    with pytest.raises(FileNotFoundError):
        encode_known_faces(tmp_path / "nonexistent", output)


def test_raises_if_no_valid_faces(tmp_path):
    """ValueError if known_faces/ exists but contains no recognisable faces."""
    known_dir = tmp_path / "known"
    known_dir.mkdir()
    shutil.copy(FIXTURES / "no_face.png", known_dir / "blank.png")

    output = tmp_path / "encodings.pkl"
    with pytest.raises(ValueError):
        encode_known_faces(known_dir, output)


def test_skips_image_with_no_face_and_continues(tmp_path, capsys):
    """Image with no face is skipped with a warning; valid images are still encoded."""
    known_dir = tmp_path / "known"
    known_dir.mkdir()
    shutil.copy(FIXTURES / "no_face.png", known_dir / "blank.png")
    shutil.copy(FIXTURES / "person_a_1.jpg", known_dir / "a1.jpg")

    output = tmp_path / "encodings.pkl"
    encode_known_faces(known_dir, output)

    captured = capsys.readouterr()
    assert "warning" in captured.err.lower() or "skipping" in captured.err.lower()

    with open(output, "rb") as f:
        encodings = pickle.load(f)
    assert len(encodings) == 1


def test_no_temp_files_left_after_write(tmp_path):
    """No leftover temp files after a successful write."""
    known_dir = tmp_path / "known"
    known_dir.mkdir()
    shutil.copy(FIXTURES / "person_a_1.jpg", known_dir / "a1.jpg")

    output = tmp_path / "encodings.pkl"
    encode_known_faces(known_dir, output)

    leftover_tmp = [f for f in tmp_path.iterdir() if f.name.startswith(".tmp_")]
    assert leftover_tmp == []
