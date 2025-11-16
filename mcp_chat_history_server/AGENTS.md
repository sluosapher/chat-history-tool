# Repository Guidelines

## Project Structure & Modules
- Core server code lives in `server.py`.
- Tests are in `test_server.py`.
- Build artifacts are in `build/` and `dist/`; do not edit them directly.
- Python virtual environment lives in `venv/` and should not be committed.

## Build, Test, and Run
- Create/refresh the venv and install deps: `.\setup.ps1` or `setup.bat`.
- Run the server locally: `.\run.ps1` or `python server.py`.
- Run tests: `python -m pytest test_server.py` (from the repo root).
- Build standalone executables: `.\build.ps1` or `build.bat` (uses PyInstaller spec `chat_history_server_server.spec`).

## Coding Style & Naming
- Use Python 3.11+ and type hints where practical.
- Follow PEP 8: 4-space indentation, snake_case for functions/variables, PascalCase for classes.
- Keep modules small and focused; prefer helper functions in `server.py` over ad-hoc inline logic.
- Keep user-facing strings and protocol details centralized near the top of `server.py` when possible.

## Testing Guidelines
- Add tests to `test_server.py` mirroring function or endpoint names.
- Name tests `test_<behavior>` (e.g., `test_get_history_for_channel`).
- Ensure new features include at least one happy-path and one error-path test.
- Run the full test suite before opening a PR.

## Commit & PR Practices
- Use concise, imperative commit messages (e.g., “Add chat history filter by user”).
- Reference related issues in the description when applicable.
- For PRs, include: purpose/summary, key changes, testing performed (with commands), and any breaking behavior.
