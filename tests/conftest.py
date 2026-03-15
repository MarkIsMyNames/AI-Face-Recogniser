import shutil

import pytest

from encoder import encode_known_faces
from helpers import FIXTURES, FIXTURE_ENCODINGS


@pytest.fixture(scope="session", autouse=True)
def generate_fixture_encodings(tmp_path_factory):
    """Pre-generate a fixture encodings file from Person A test images."""
    known_dir = tmp_path_factory.mktemp("known")
    shutil.copy(FIXTURES / "person_a_1.jpg", known_dir / "a1.jpg")
    shutil.copy(FIXTURES / "person_a_2.jpg", known_dir / "a2.jpg")
    encode_known_faces(known_dir, FIXTURE_ENCODINGS)
    yield
    # File is gitignored; leave it for local inspection
