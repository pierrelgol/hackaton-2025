# Pierre Backend

## Project Structure

```
Pierrebackend/
├── LICENSE
├── README.md          (this file)
├── .gitignore
├── base/              # Raccoon face filter project
│   ├── *.py          # Python scripts
│   ├── *.md          # Documentation
│   ├── *.json        # Mesh data
│   ├── *.png/.jpg    # Images
│   ├── requirements.txt
│   ├── web/          # Web app
│   └── ...
├── POCgoogleface/    # Original project reference
└── working_example_for_face_stealing/
```

## Raccoon Filter (base/)

3D Snapchat-style raccoon face filter using MediaPipe face tracking.

### Quick Start

```bash
cd base
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
python server.py
```

Then open `http://localhost:8000` in your browser.

### Documentation

See `base/README.md` for full documentation.

