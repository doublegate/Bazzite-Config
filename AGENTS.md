# Repository Guidelines

## Project Structure & Module Organization
- Master: `bazzite-optimizer.py` (primary entrypoint)
- Tools: `gaming-manager-suite.py` (control), `gaming-monitor-suite.py` (metrics), `gaming-maintenance-suite.sh` (bench), `undo_bazzite-optimizer.py` (restore)
- Docs/refs: `README.md`, `CHANGELOG.md`, `docs/`, `ref_docs/`, `ref_scripts/`, `images/`, `to-dos/`
- Config/build: `pyproject.toml`, `VERSION`
- Tests: `tests/` (e.g., `tests/test_kernel_param_fix.py`)
 - See: `README.md` (overview), `docs/TECHNICAL_ARCHITECTURE.md` (architecture)

## Build, Test, and Development Commands
- Prereqs (Bazzite): `sudo dnf install python3-psutil stress-ng sysbench`
- Create env: `python -m venv .venv && source .venv/bin/activate`; install dev: `pip install -e .[dev]`
- Make executable: `chmod +x bazzite-optimizer.py gaming-manager-suite.py gaming-monitor-suite.py gaming-maintenance-suite.sh`
- Format/lint: `black . && isort . && flake8`
- Tests: `pytest -q` (add tests under `tests/test_*.py`)
- Build pkg: `python -m build`; Binary: `pyinstaller --name bazzite-optimizer --onefile bazzite-optimizer.py`
 - See: `WARP.md` (Essential/Running/Dev commands), `docs/INSTALLATION_SETUP.md`, `CONTRIBUTING.md` (dev setup)

## Coding Style & Naming Conventions
- Python: PEP 8 with Black (88); isort (profile=black); Flake8 ignores `E203,W503`.
- Type hints on public functions; module/class/method docstrings.
- Shell: bash with `set -euo pipefail`; run `shellcheck` for scripts.
- Names: scripts hyphenated; modules/functions snake_case; Classes PascalCase; CONSTANTS UPPER_SNAKE.
 - See: `CONTRIBUTING.md` (Code Guidelines), `CLAUDE.md` (logging/colors patterns)

## Testing Guidelines
- Use pytest; name tests `tests/test_*.py`; mirror targets.
- Focus on critical paths: optimizer actions, rollback, validation, kernel param handling (deduplication).
- Quick integration checks: `./gaming-manager-suite.py --status`, `./gaming-monitor-suite.py --mode simple`, `sudo ./bazzite-optimizer.py --validate`.
- Include regression tests for reported issues and profile transitions.
 - See: `WARP.md` (Testing/Smoke tests), `docs/TROUBLESHOOTING.md` (diagnostics)

## Commit & Pull Request Guidelines
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Message body: rationale, risks, and Bazzite version/hardware used; link issues (`Closes #123`).
- PRs: description, affected components, test evidence (logs/commands), screenshots if UI-like output; update `CHANGELOG.md`/`README.md` when user-facing.
 - See: `CONTRIBUTING.md` (PR process), `WARP.md` (Git workflow)

## Security & Configuration Tips
- Target: Bazzite Linux (immutable). Prefer idempotent changes and explicit rollback paths.
- Boot params: use rpm-ostree kargs batching; avoid duplicates; provide `--verify` (dry-run) and `--rollback` flows.
- Integrations: respect `ujust`, `system76-scheduler`, GameMode; validate service state before changes.
- Minimize `sudo`; validate inputs; avoid shell injection; prefer `subprocess.run([...], check=True)`.
 - See: `WARP.md` (Security/Safety), `docs/BOOT_INFRASTRUCTURE_IMPLEMENTATION.md` (boot), `README.md` (kernel param dedup notes)

## Agent-Specific Instructions
- Always read before write: verify file existence, read, plan, then edit.
- Keep changes minimal and aligned with architecture (immutable FS, rpm-ostree, profile-aware validation).
- When in doubt, prefer dry-run/validation modes and include safety/rollback notes in PRs.
 - See: `CLAUDE.md` (ALWAYS READ BEFORE WRITE), `CLAUDE.local.md` (current project state/context)

## References
- `WARP.md` — quick commands, workflow, and ops context
- `CONTRIBUTING.md` — contribution, setup, and PR process
- `docs/TECHNICAL_ARCHITECTURE.md` — system architecture details
- `docs/INSTALLATION_SETUP.md` — installation and verification steps
- `docs/TROUBLESHOOTING.md` — diagnostics and common fixes
- `README.md` — overview, usage, and component descriptions
- `CLAUDE.md` / `CLAUDE.local.md` — agent rules and local context

---

## Agent Workflow (Codex CLI)
- Use a brief preamble before tool calls to state the next action.
- Maintain a lightweight plan via `update_plan` for multi-step tasks; keep one step `in_progress`.
- Always read before write: locate file(s), read relevant chunks, then patch.
- Prefer minimal, surgical changes aligned with current architecture and style.

## Editing & Patching Rules
- Use `apply_patch` with focused hunks and 3 lines of stable context.
- Do not immediately re-read files after a successful patch.
- Avoid adding copyright/license headers unless explicitly requested.
- Avoid drive-by changes unrelated to the task; keep diffs small.
- No inline code comments unless asked; keep naming descriptive (no 1-letter vars).

## Shell Usage Conventions
- Prefer `rg` for searching files/content; it’s faster and available.
- When previewing files, read in chunks ≤ 250 lines per command.
- Keep command output concise; large outputs are truncated in the CLI.

## Formatting of Assistant Responses
- Be concise and scannable. Use short section headers and bullets when helpful.
- Wrap commands, paths, and code identifiers in backticks.
- Avoid heavy formatting beyond simple headers/bullets/monospace.

## Safety, Sandbox, and Approvals
- Default environment: `workspace-write`, network `restricted`, approvals `on-request`.
- Request approval before commands that write outside the workspace or need network.
- Avoid destructive actions (`rm`, `git reset`) unless explicitly requested.
- Prefer dry-run/validation flows (`--verify`, `--status`) when available.

## Validation & Testing Philosophy
- Validate changes as narrowly as possible first (unit/targeted tests), then broaden.
- Use `pytest -q` for tests; don’t add new frameworks. Add tests only where patterns exist.
- For formatting/lint, use project tools: `black`, `isort`, `flake8` (respect ignores).
- Don’t “fix” unrelated failing tests; call them out separately if encountered.

## Project-Specific Operational Notes
- Bazzite is immutable: ensure idempotent actions and explicit rollback paths.
- Kernel params: batch with `rpm-ostree kargs`, avoid duplicates, provide `--verify`/`--rollback`.
- Respect integrations (`ujust`, `system76-scheduler`, GameMode); verify service state first.
- Use `subprocess.run([...], check=True)` for shell calls; validate inputs to avoid injection.

## Quick Commands Cheatsheet (for agents)
- Search files: `rg -n "pattern"` / list files: `rg --files`.
- Run tests: `pytest -q`.
- Lint/format: `black . && isort . && flake8`.
- Build: `python -m build`.
- Package binary: `pyinstaller --name bazzite-optimizer --onefile bazzite-optimizer.py`.
