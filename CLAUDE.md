# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is the **organisation-level `.github` repository** for the GitHub org
`Advans-IT-Solutions-GmbH`. It holds community-health / default files for the
organisation, not application code. There is no application build or test
step; CI runs workflow regression tests and security scans (Semgrep SAST,
`zizmor` and `actionlint` for GitHub Actions, and Gitleaks for secrets).
See `README.md` for the reusable workflow's contract and limitations.

GitHub treats this special repo as the source of org-wide defaults: files placed
here (the profile README, SECURITY policy, and other supported community-health
files) are **shown on the org page or inherited by every other repo in the org**
that does not provide its own copy.

## Tracked files and folders

- `profile/README.md` — the **organisation profile README** rendered on the
  org's public GitHub landing page (https://github.com/Advans-IT-Solutions-GmbH).
  Company description, services, label overview, and contact details. English.
- `.github/assets/labels/` — the swiss made software label logos the profile
  shows: unchanged originals, plus copies with a white margin for the dark
  theme. The profile loads them by absolute URL from `main`.
- `SECURITY.md` — the **org-wide security policy** (vulnerability reporting via
  GitHub Private Vulnerability Reporting or `info@advans.ch` with subject
  `SECURITY`). Inherited by repos without their own `SECURITY.md`.
- `README.md` — public repository map, reusable workflow usage and maintenance.
- `.github/workflows/` — reusable CI:
  - `reusable-security.yml` — a `workflow_call` reusable security scan
    (Semgrep SAST, `zizmor` + `actionlint` for GitHub Actions auditing, and Gitleaks).
    Other org repos call this via `uses: Advans-IT-Solutions-GmbH/.github/.github/workflows/reusable-security.yml@<ref>`.
  - `security.yml` — runs regression tests and the reusable workflow for this repo
    on push / PR to `main` and `workflow_dispatch`.
- `tests/` — standard-library Python tests of the workflow's Bash execution contract.
- `.devcontainer/` — a minimal GitHub Codespaces / dev-container config
  (`devcontainer.json` only). It intentionally does **not** hardcode a committing
  identity; each developer configures their own (see below).

## Conventions observed

- Markdown body language for public-facing files (`profile/README.md`,
  `SECURITY.md`) is **English**; the `.devcontainer` comments are German.
- **Git / commit / PR conventions:** commit under your **own** GitHub account
  (Model B — use your personal GitHub no-reply address
  (e.g. `<id>+<username>@users.noreply.github.com`) and your real name; never use an
  `@advans.ch` email address, i.e. any address in that domain, as the commit
  email). The full Git/branch/commit/PR conventions **and** the Copilot
  code-review Definition of Done live in `AGENTS.md` — that file is authoritative
  here, so the full rules and the DoD are **not** restated here; only this
  short identity summary is kept as a convenience pointer. (The org-wide SSOT
  is the private repo `Advans-IT-Solutions-GmbH/org` → `README.md`, section "Git and
  Commit Conventions".)
- Workflows pin third-party actions by **commit SHA** (with a version comment)
  and pin tool versions (e.g. `semgrep==1.167.0`) with checksum verification
  for downloaded binaries; keep this pattern when editing workflows.
- The security workflow is intended to be **reusable across the org** — changes
  here affect every repo that calls `reusable-security.yml`.
