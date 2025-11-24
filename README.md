# World Engine

[![CI](https://github.com/Colt45en/world-ide-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/Colt45en/world-ide-engine/actions/workflows/ci.yml) [![Coverage](https://codecov.io/gh/Colt45en/world-ide-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/Colt45en/world-ide-engine)

A lexicon processing and semantic analysis system with integrated recording, chat interface, and real-time analysis capabilities.

## Core Architecture

**Multi-Component Bridge System**: Three main controllers communicate via `StudioBridge`:
- `ChatController` - Command router and workflow coordinator
- `EngineController` - Lexicon analysis engine wrapper
- `RecorderController` - Audio/video capture with timeline markers

**Data Flow**: `Chat Controller ↔ Recorder ↔ World Engine ↔ External Store`

## Project Structure

- `api/`: FastAPI service endpoints
- `config/`: Configuration files
- `context/`: NLP processing modules (spaCy-based)
- `scales/`: Semantic scaling system (seeds and constraints)
- `web/`: Web interfaces
  - `studio.html` - Complete studio interface
  - `worldengine.html` - Engine-only view
  - `*-controller.js` - Component controllers
- `engine/`: Legacy engine components (deprecated)
- `tests/`: Unit and integration tests

## Setup

1. **Install Python 3.13+**

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## Running the System

### Quick Launch
```bash
python launch_studio.py
```
Opens browser to the studio interface automatically.

### API Server
```bash
# You can override the port with the PORT environment variable, e.g. on Windows PowerShell:
# $env:PORT=9000; python main.py
python main.py
```
By default the server runs on port 8001. Access at:
- Studio Interface: http://localhost:8001/web/studio.html
- Engine Only: http://localhost:8001/web/worldengine.html
- API Docs: http://localhost:8001/docs

The `launch_studio.py` helper will pick a free local port if PORT isn't set and will wait for the server to respond before opening the browser.

Health check endpoint: `GET /api/health` — returns {"status": "ok"} when the server is healthy.

Persistence: by default the service now uses an SQLite database at `config/seeds.db` for durability. You can override this location with the `SEEDS_FILE` environment variable to point to a different file (JSON or SQLite).

Notes on storage behavior:
- `config/seeds.db` — SQLite database (recommended for production). The DB stores `seeds` and `constraints` tables and all changes are persisted atomically.
- `config/seeds.json` — legacy JSON file format still supported and used when your `SEEDS_FILE` ends with `.json`.

The API will save newly added/modified seeds and constraints automatically when they are changed via the endpoints or the web UI.

CI: a GitHub Actions workflow is included at `.github/workflows/ci.yml` which runs the full test suite on push and pull requests.

CI details:
- The workflow runs on Python 3.11 / 3.12 / 3.13 and publishes coverage reports to Codecov (via the standard Codecov GitHub Action).
- If your repository is private, set a `CODECOV_TOKEN` secret in GitHub to allow the coverage upload step to succeed.

Codecov token (private repos):

- If your repository is private, create a Codecov token for the repository (Codecov settings) and add it to GitHub Secrets as `CODECOV_TOKEN`.
- The CI workflow will read `CODECOV_TOKEN` from GitHub Secrets and use it when uploading coverage reports.

Coverage policy:
- CI enforces a minimum total line-coverage threshold of 75% by default. If coverage drops below this threshold CI will fail.
- To adjust the threshold, update the `COVERAGE_THRESHOLD` environment variable in `.github/workflows/ci.yml` or modify the workflow step accordingly.

Status badges:

- The README contains placeholder status badges for CI and Codecov earlier near the top; replace `<OWNER>/<REPO>` with your GitHub org/repo name (e.g. `my-org/my-repo`) so they become active links in the README.

Badges:
- The README contains placeholder status badges for CI and Codecov. Replace `<OWNER>/<REPO>` with your GitHub org/repo to enable live badges.

### Interactive Demo
```bash
python demo.py
```
Command-line demo of semantic analysis capabilities.

## Key Features

### Semantic Scaling System
- **Hand-labeled Seeds**: Core truth values (`terrible: -0.8`, `excellent: 0.8`)
- **Constraint-based Scaling**: Explicit ordering relationships
- **Context-sensitive Scoring**: Same word scored differently by syntactic role

### NLP Pipeline
- spaCy-powered linguistic processing
- POS tagging, dependency parsing
- Named entity recognition
- Context-aware sentiment analysis

### Web Interface
- Real-time text analysis
- Timeline-based recording with markers
- Chat-based command system
- Component communication via message bridge

## API Usage

```python
from api.service import WorldEngineAPI
from scales.seeds import DEFAULT_SEEDS

api = WorldEngineAPI()
result = api.analyze_text("This is an excellent product!")
print(f"Sentiment: {result['sentiment_score']}")
```

## Development

- **Dependencies**: FastAPI, spaCy, NumPy, Pandas, scikit-learn
- **Architecture**: Component-based with event messaging
- **Focus**: Semantic scaling and constraint validation

## Contributing

Follow the semantic scaling approach - hand-labeled seeds, not ML-generated values.