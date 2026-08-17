# Engineering Standards

This document establishes the architectural principles, design guidelines, coding standards, Git workflow, testing conventions, and the Definition of Done (DoD) for the Resource-Aware Tiered Clustering (RATC) project.

---

## 1. Directory & Folder Naming Conventions
*   **Case Style:** Lowercase with underscores (`snake_case`) for directories and Python modules.
*   **Root Structure:**
    *   `src/`: Main source tree (e.g., `src/client/`, `src/server/`).
    *   `docs/`: Design, specifications, and research notes.
    *   `tests/`: Unit, integration, and performance benchmarks.
    *   `config/`: Template and profiles configurations.

---

## 2. Python Coding Standards
*   **PEP8 Compliance:** Strict adherence to PEP8 for code style. Linting enforced via automated pipelines (`flake8` / `black`).
*   **Typing:** Mandatory type hints for all public functions, classes, and method signatures using Python's `typing` module.
*   **Class & Variable naming:**
    *   Class names: PascalCase (e.g., `PrivacyEngine`).
    *   Functions/Methods: snake_case (e.g., `apply_dp_noise`).
    *   Interfaces: Prefix with a capital `I` (e.g., `IScheduler`, `IPrivacyEngine`).

---

## 3. Logging & Monitoring Standards
*   **Structured Logs:** Use JSON logging layouts in staging and production modes.
*   **Log Ingestion:** Log levels must map to actual server states:
    *   `DEBUG`: Low-level system trace metrics.
    *   `INFO`: High-level operations (e.g., round starts, updates received).
    *   `WARNING`: Recoverable errors (e.g., fallback scheduler triggered).
    *   `ERROR`: Local execution failures.
    *   `CRITICAL`: Total system halts.
*   **No Print Statements:** Python's standard `print` function must not be used for logging; use the `ILogger` abstraction.

---

## 4. Error & Exception Handling
*   **Custom Exceptions:** All expected runtime errors must inherit from a base `RATCError` exception.
*   **Clean Failures:** Throw early, catch late. Never silence exceptions without logging their cause.
*   **Resource Protection:** Use `try-finally` blocks or context managers (`with` statements) to clean up hardware, sockets, and memory allocations.

---

## 5. Dependency Injection
*   **Inversion of Control:** Classes must declare external dependencies through constructor injections (`__init__`) instead of instantiating dependencies directly.
*   **Testing Hooks:** Inject interfaces/protocols to allow easy mocking during tests.

---

## 6. Configuration & Secrets Management
*   **Stateless Code:** Code must not contain hardcoded credentials, IP addresses, or path configurations.
*   **Secrets Ingestion:** Secret keys, database passwords, and API credentials must be fetched from environment variables at execution time.
*   **Config Validation:** All config formats must be validated at launch via `IConfigurationLoader`.

---

## 7. Git Workflow & Commit Conventions
*   **Branch Strategy:** GitHub Flow configuration.
    *   `main`: High stability deployment branch.
    *   `feature/*`: Topic branches for new feature stories.
    *   `hotfix/*`: Quick patch updates.
*   **Commit Conventions:** Traditional conventional commit formats:
    *   `feat: <description>` (new capabilities)
    *   `fix: <description>` (patches)
    *   `docs: <description>` (updates)
    *   `test: <description>` (verification)
*   **Rebases:** Squash-merge features to keep history linear.

---

## 8. Code Review Checklist
*   Does the code compile and pass lints?
*   Are all class methods type-hinted and documented?
*   Are exceptions caught, handled, or raised cleanly?
*   Are dependencies injected instead of instantiated directly?
*   Are there unit tests covering normal and error execution paths?
*   Does it conform to the architecture guidelines?

---

## 9. Testing Conventions
*   **Coverage Goals:** Minimum of `80%` code coverage on new codebase packages.
*   **Test Naming:** Prefix test files with `test_` and methods with `test_` (e.g. `test_scheduler_evaluates_correctly`).
*   **Isolation:** Mock database, hardware, and network bindings.

---

## 10. Documentation Standards
*   **Docstrings:** All methods, functions, and classes must include Python docstrings describing:
    *   **Responsibilities:** Core behavior.
    *   **Inputs:** Type and purpose of each parameter.
    *   **Outputs:** Expected returns.
    *   **Exceptions:** Potential errors thrown.
*   **System Specs:** Architectural edits must be reflected in `docs/design/` documents.

---

## 11. Definition of Done (DoD)
*   Code passes black/flake8 checks.
*   Documentation exists inside codebase docstrings and `docs/design/`.
*   All unit and integration tests run successfully.
*   The system builds successfully in Docker containers.
*   No secrets are committed to version control.
*   Approved by at least one peer reviewer.

---

## 12. Design Principles

### SOLID
*   **Single Responsibility:** A class should have one reason to change.
*   **Open/Closed:** Open for extension, closed for modification.
*   **Liskov Substitution:** Derived types must be substitutable for their base types.
*   **Interface Segregation:** Clients should not depend on methods they do not use.
*   **Dependency Inversion:** Depend on abstractions, not concretes.

### DRY (Don't Repeat Yourself)
*   Extract duplicated logic into helper functions, utilities, or subclasses.

### KISS (Keep It Simple, Stupid)
*   Avoid over-engineering. Write code that is easy to read, refactor, and verify.
