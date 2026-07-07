# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is the **organisation-level `.github` repository** for the GitHub org
`Advans-IT-Solutions-GmbH`. It holds community-health / default files for the
organisation, not application code. There is no application build or test
step; the only CI is a security-scan workflow (Semgrep SAST plus `zizmor` and
`actionlint` for GitHub Actions auditing) — see `.github/workflows/`.

GitHub treats this special repo as the source of org-wide defaults: files placed
here (the profile README, SECURITY policy, and other supported community-health
files) are **shown on the org page or inherited by every other repo in the org**
that does not provide its own copy.

## Tracked files and folders

- `profile/README.md` — the **organisation profile README** rendered on the
  org's public GitHub landing page (https://github.com/Advans-IT-Solutions-GmbH).
  Company description, services, and contact details. English.
- `SECURITY.md` — the **org-wide security policy** (vulnerability reporting via
  GitHub Private Vulnerability Reporting or `info@advans.ch` with subject
  `SECURITY`). Inherited by repos without their own `SECURITY.md`.
- `README.md` — repository README (currently empty).
- `.github/workflows/` — reusable CI:
  - `reusable-security.yml` — a `workflow_call` reusable security scan
    (Semgrep SAST, plus `zizmor` + `actionlint` for GitHub Actions auditing).
    Other org repos call this via `uses: Advans-IT-Solutions-GmbH/.github/.github/workflows/reusable-security.yml@<ref>`.
  - `security.yml` — runs the reusable workflow for this repo on push / PR to
    `main` and `workflow_dispatch`.
- `.devcontainer/` — a minimal GitHub Codespaces / dev-container config
  (`devcontainer.json` only). It intentionally does **not** hardcode a committing
  identity; each developer configures their own (see below).

## Conventions observed

- Markdown body language for public-facing files (`profile/README.md`,
  `SECURITY.md`) is **English**; the `.devcontainer` comments are German.
- **Git / commit / PR conventions:** commit under your **own** GitHub account
  (Model B — use its personal GitHub no-reply address
  `<id>+<username>@users.noreply.github.com` and your real name; never use an
  `@advans.ch` email address, i.e. any address in that domain, as the commit
  email). The full Git/branch/commit/PR conventions **and** the Copilot
  code-review Definition of Done live in `AGENTS.md` — that file is authoritative
  here, so they are **not** duplicated in this file. (The org-wide SSOT is the
  private repo `Advans-IT-Solutions-GmbH/org` → `README.md`, section "Git and
  Commit Conventions".)
- Workflows pin third-party actions by **commit SHA** (with a version comment)
  and pin tool versions (e.g. `semgrep==1.167.0`) with checksum verification
  for downloaded binaries; keep this pattern when editing workflows.
- The security workflow is intended to be **reusable across the org** — changes
  here affect every repo that calls `reusable-security.yml`.
