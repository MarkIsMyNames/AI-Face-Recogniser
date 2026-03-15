import os
import pickle
import sys
from pathlib import Path

import face_recognition

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def encode_known_faces(known_faces_dir: Path, output_path: Path) -> None:
    """
    Scan known_faces_dir for images, generate face encodings, save to output_path atomically.

    Raises:
        FileNotFoundError: if known_faces_dir does not exist.
        ValueError: if no valid face encodings are found across all images.
    """
    known_faces_dir = Path(known_faces_dir)
    output_path = Path(output_path)

    if not known_faces_dir.is_dir():
        raise FileNotFoundError(
            f"known_faces/ directory not found at '{known_faces_dir}'.\n"
            "Create it and add photos of your face, then run again."
        )

    image_paths = sorted(
        p for p in known_faces_dir.iterdir()
        if p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    encodings = []
    for image_path in image_paths:
        image = face_recognition.load_image_file(str(image_path))
        found = face_recognition.face_encodings(image)

        if not found:
            print(
                f"Warning: no face detected in '{image_path.name}', skipping.",
                file=sys.stderr,
            )
            continue

        if len(found) > 1:
            print(
                f"Warning: {len(found)} faces detected in '{image_path.name}', "
                "using only the first detected.",
                file=sys.stderr,
            )

        encodings.append(found[0])

    if not encodings:
        raise ValueError(
            "No valid face encodings found in known_faces/.\n"
            "Ensure your photos each contain exactly one clearly visible face."
        )

    # Atomic write: temp file in same directory prevents cross-filesystem rename failure
    tmp_path = output_path.parent / f".tmp_{output_path.name}"
    try:
        with open(tmp_path, "wb") as f:
            pickle.dump(encodings, f)
        os.replace(tmp_path, output_path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise
