# Contributing to Adaptive Privacy Orchestrator

Thank you for contributing to our research platform! To ensure a high standard of quality, reproducibility, and academic rigor, please adhere to these guidelines.

## Code of Conduct
We are committed to providing a welcoming, inclusive, and professional environment for everyone. Please be respectful and constructive in all communication.

## Development Setup
1. Fork and clone the repository.
2. Initialize virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   ```
3. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Guidelines
* **Code Style:** Black is our default formatter (line length 88).
* **Lints:** Ruff is used for lint checks and import sorting.
* **Type Safety:** Mypy is run with strict configuration.
* **Tests:** Every change must include unit tests and keep codebase coverage at or above 80%.

## Pull Request Process
1. Open a Draft PR referencing the issue ID you are working on.
2. Ensure CI tests and formatting validations pass cleanly.
3. Obtain approval from at least one core maintainer before squash-merging.
