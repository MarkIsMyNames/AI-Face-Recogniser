# AI Face Recogniser

A Python CLI tool that checks whether a specific person's face appears in an image. Returns `true` if the enrolled face is found, `false` in all other cases. Designed to be called from any language via subprocess.

---

## Prerequisites

- Python 3.8–3.11
- CMake (required to build `dlib`)
- A C++ compiler

### Installing CMake

**Ubuntu / Debian:**
```bash
sudo apt-get install cmake build-essential
```

**macOS:**
```bash
brew install cmake
```

**Windows:**
Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022) with the C++ workload, then install CMake from [cmake.org](https://cmake.org/download/).

---

## Installation

```bash
pip install -r requirements.txt
```

> If `dlib` fails to install, ensure CMake and a C++ compiler are installed first. Python 3.12+ users may need to build dlib from source.

---

## Setup: Enrolling Your Face

1. Create a `known_faces/` directory in the project root:

   ```bash
   mkdir known_faces
   ```

2. Add 3–10 clear photos of your face to `known_faces/`. Use `.jpg` or `.png` files. Each photo should show exactly one face (yours), well-lit and forward-facing.

3. Run the tool once — enrollment happens automatically:

   ```bash
   python recognize.py some_image.jpg
   ```

   The first run generates `encodings.pkl` from your photos. Subsequent runs load this file directly — `known_faces/` is no longer needed after enrollment.

---

## Re-enrolling

To re-enroll (e.g. after adding better photos):

```bash
rm encodings.pkl
python recognize.py some_image.jpg
```

---

## Usage

```bash
python recognize.py <path_to_image>
```

**Output:** `true` or `false` on stdout. Exit code is always `0`.

| Situation | Output |
|-----------|--------|
| Your face is in the image | `true` |
| A different face is in the image | `false` |
| No face in the image | `false` |
| Any error | `false` |

Errors and warnings are printed to stderr only — they never appear on stdout.

---

## Calling from Another Language

Read stdout from the subprocess:

**Node.js:**
```javascript
const { execSync } = require("child_process");
const result = execSync(`python recognize.py ${imagePath}`).toString().trim();
const isMyFace = result === "true";
```

**Go:**
```go
out, _ := exec.Command("python", "recognize.py", imagePath).Output()
isMyFace := strings.TrimSpace(string(out)) == "true"
```

**C# / .NET:**
```csharp
var proc = Process.Start(new ProcessStartInfo("python", $"recognize.py {imagePath}") {
    RedirectStandardOutput = true, UseShellExecute = false
});
bool isMyFace = proc.StandardOutput.ReadToEnd().Trim() == "true";
```

---

## Privacy

`known_faces/` and `encodings.pkl` are listed in `.gitignore` and must never be committed to version control. `encodings.pkl` contains your biometric face data and should be kept private. If you need to share the project, share only the code — not these files.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use public-domain fixture images committed to `tests/fixtures/`. A fixture `encodings.pkl` is generated automatically before the tests run — no personal photos are needed.

### Setting up test fixture images

The test suite requires three public-domain face photos:

| File | Description |
|------|-------------|
| `tests/fixtures/person_a_1.jpg` | Photo of Person A (enrolled test face) |
| `tests/fixtures/person_a_2.jpg` | Second photo of Person A |
| `tests/fixtures/person_b.jpg` | Photo of a different person |

Suitable sources: [Wikimedia Commons](https://commons.wikimedia.org) (filter by "Public Domain").
Each photo must contain exactly one clearly visible, forward-facing face.

The no-face image is generated automatically when you first run the tests.

---

## Troubleshooting

**`dlib` build fails:**
- Ensure CMake is installed: `cmake --version`
- Ensure a C++ compiler is available: `g++ --version` (Linux/macOS)
- Python 3.12+: try `pip install dlib --no-binary dlib` or switch to Python 3.11

**`encodings.pkl` is corrupt:**
Delete it — the tool re-enrolls automatically on the next run:
```bash
rm encodings.pkl && python recognize.py some_image.jpg
```

**Your face is not recognised:**
- Add more varied photos (different lighting, angles) to `known_faces/`
- Delete `encodings.pkl` and re-enroll
- Lower the matching tolerance by editing `FACE_MATCH_TOLERANCE` in `recognize.py` (default `0.6`; lower = stricter, higher = more lenient)
