import os
import pickle
import sys
from pathlib import Path

import face_recognition

BASE_DIR = Path(__file__).parent

_env_encodings = os.environ.get("FACE_RECOGNIZER_ENCODINGS_PATH")
ENCODINGS_PATH = Path(_env_encodings) if _env_encodings else BASE_DIR / "encodings.pkl"

_env_known = os.environ.get("FACE_RECOGNIZER_KNOWN_FACES_DIR")
KNOWN_FACES_DIR = Path(_env_known) if _env_known else BASE_DIR / "known_faces"

FACE_MATCH_TOLERANCE = 0.6  # Lower = stricter; adjust here if needed


def _enroll() -> None:
    from encoder import encode_known_faces
    encode_known_faces(KNOWN_FACES_DIR, ENCODINGS_PATH)


def _load_encodings() -> list:
    with open(ENCODINGS_PATH, "rb") as f:
        return pickle.load(f)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python recognize.py <image_path>", file=sys.stderr)
        print("false")
        return

    image_path = sys.argv[1]

    try:
        # Auto-enroll if encodings file is absent
        if not ENCODINGS_PATH.exists():
            _enroll()

        # Load encodings — handle corrupt file by re-enrolling
        try:
            known_encodings = _load_encodings()
            if not isinstance(known_encodings, list):
                raise ValueError("encodings.pkl contains unexpected data type")
        except Exception as load_err:
            print(
                f"Warning: could not load encodings ({load_err}). Re-enrolling...",
                file=sys.stderr,
            )
            ENCODINGS_PATH.unlink(missing_ok=True)
            _enroll()
            known_encodings = _load_encodings()

        # Encode faces in the input image
        image = face_recognition.load_image_file(image_path)
        input_encodings = face_recognition.face_encodings(image)

        # Check each detected face against known encodings
        for enc in input_encodings:
            results = face_recognition.compare_faces(
                known_encodings, enc, tolerance=FACE_MATCH_TOLERANCE
            )
            if any(results):
                print("true")
                return

        print("false")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("false")


if __name__ == "__main__":
    main()
