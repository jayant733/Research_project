# GitHub Workflow Specifications

This document defines the guidelines for repository management, branching, issue tracking, code reviews, and release processes for the RATC project.

---

## 1. Issue Management, Labels & Milestones

### Issue Templates
*   **Feature Request Template:** Contains sections for: *User Story*, *Proposed Solution*, *Alternative Implementations*, and *Task Breakdown*.
*   **Bug Report Template:** Contains sections for: *Steps to Reproduce*, *Expected vs. Actual Behavior*, *Device/OS Details*, and *Relevant Log Dumps*.

### Standard Label Schema
*   `type: feature` (Green): Introduce new system behavior.
*   `type: bug` (Red): Fix existing code errors.
*   `type: documentation` (Blue): Edits to design documents, markdown files, or docstrings.
*   `scope: crypto` / `scope: telemetry` / `scope: flower` (Purple): Tagged module boundaries.
*   `priority: blocker` / `priority: high` / `priority: low` (Yellow/Orange): Operational urgency indicators.

### Projects & Milestones
*   **Jira/GitHub Board:** Kanban column tracking (`Backlog` -> `To Do` -> `In Progress` -> `In Review` -> `Done`).
*   **Milestones:** Mapped to 1-month Sprints (e.g. `Sprint 1 - Foundations`, `Sprint 2 - Cryptographic Core`).

---

## 2. Pull Request (PR) & Review Workflow

### PR Creation Guidelines
1.  **Branch Name:** Must follow conventional prefixes: `feature/<issue-id>-summary` or `bugfix/<issue-id>-summary` (e.g., `feature/RATC-201-fhe-setup`).
2.  **PR Description:** Must describe the *Rationale*, *Key Changes*, *Verification Steps*, and reference the matching issue ID (`Closes #123`).
3.  **Draft Status:** PRs must be opened as "Draft" if they are still actively being worked on.

### Review Workflow
1.  **Self-Review:** Author reviews their own diff to remove debug logging or temporary changes.
2.  **Automated Checks:** The PR must pass all CI checks (linting, testing) before peer review.
3.  **Peer Review:** At least one other student must review and explicitly approve the PR.
4.  **Merge Rule:** PRs must be merged using a squash-merge strategy to keep the git history clean and linear.

---

## 3. Release Workflow, Semantic Versioning & Tags

### Semantic Versioning (SemVer 2.0.0)
Releases are named using the `MAJOR.MINOR.PATCH` format:
*   `MAJOR`: Breaking changes or major architectural redesigns.
*   `MINOR`: New features added in a backwards-compatible manner (e.g., adding a new scheduling policy).
*   `PATCH`: Backwards-compatible bug fixes.

### Release Process
1.  Create a release candidate branch `release/vX.Y.Z` from `main`.
2.  Run full integration, stress, and performance tests on the release branch.
3.  Merge the release branch back into `main` and tag the merge commit with the version tag.
4.  **Git Tag Format:** `vX.Y.Z` (e.g. `git tag -a v1.0.0 -m "Release v1.0.0"`).
5.  Generate release notes automatically from conventional commit messages.

---

## 4. Branch Protections & CI/CD Triggers

### Branch Protections on `main`
*   **Require Pull Request Reviews:** Minimum of 1 approving review before merging.
*   **Require Status Checks:** Mandatory pass for all CI workflows (linting, test runners).
*   **Restrict Deletions:** Prevent direct deletion of the `main` branch.
*   **Block Direct Commits:** Commits cannot be pushed directly to `main`; all changes must go through PRs.

### CI/CD Workflow Triggers
*   **Pull Request Workflow:**
    *   *Trigger:* On opening or pushing updates to a PR targeting `main`.
    *   *Steps:* Installs requirements, runs `black --check` and `flake8` lints, and executes the unit/integration test suite.
*   **Merge/Release Workflow:**
    *   *Trigger:* On push/merge of code to the `main` branch.
    *   *Steps:* Build Docker images for server/client services and push tags to the container registry.
