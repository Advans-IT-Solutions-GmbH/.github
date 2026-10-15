
# Organisation defaults and reusable security checks

This public repository provides community-health defaults for
[Advans IT Solutions](https://github.com/Advans-IT-Solutions-GmbH) and a reusable
GitHub Actions security workflow. It contains no application.

## File map

| Path | Purpose |
| --- | --- |
| `profile/README.md` | Public organisation profile. |
| `SECURITY.md` | Vulnerability reporting policy, inherited by repositories without their own policy. |
| `.github/workflows/reusable-security.yml` | Semgrep SAST, actionlint, zizmor and Gitleaks, exposed through `workflow_call`. |
| `.github/workflows/security.yml` | This repository's scans and regression tests on PRs/pushes to `main` and manual dispatch. |
| `tests/test_security_workflow.py` | Scanner execution-policy regression tests; Python standard library and Bash only. |
| `.devcontainer/devcontainer.json` | Minimal development container without a hardcoded commit identity. |
| `AGENTS.md`, `CLAUDE.md` | Contributor/agent conventions and repository guidance. |

Community-health inheritance and reusable workflow calls are separate: other
repositories must explicitly call the workflow to run these checks.

## Calling the workflow

Pin the reusable workflow to a reviewed **full commit SHA**, not a mutable branch
or tag. For example, save this as `.github/workflows/security.yml` in a caller:

```yaml
name: Security Scan
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  security:
    uses: Advans-IT-Solutions-GmbH/.github/.github/workflows/reusable-security.yml@fc2542e862def044ea16d81340624c1d69e9bdbb
    with:
      fail_on_findings: false
      gitleaks_fail: true
```

The example deliberately makes SAST/Actions findings report-only while keeping
secret findings blocking. It does **not** make tool failures report-only.
This repository's own caller omits these overrides, so both defaults are blocking.
Keep the caller's existing trigger and concurrency policy when adopting/upgrading;
the reusable workflow does not impose a concurrency group.

### Inputs and permissions

All inputs are optional:

| Input | Type | Default | Effect |
| --- | --- | --- | --- |
| `semgrep_config` | string | `p/security-audit p/secrets p/github-actions p/javascript p/php p/python` | Whitespace-separated Semgrep rule packs; the workflow passes each as a separate `--config`. |
| `fail_on_findings` | boolean | `true` | Blocks on Semgrep, actionlint and zizmor findings when true; reports findings without failing when false. |
| `zizmor_min_severity` | string | `low` | Minimum zizmor finding severity: `informational`, `low`, `medium` or `high`. |
| `gitleaks_fail` | boolean | `true` | Independently blocks on secrets in the scanned commits when true. |

Only `contents: read` is requested. No inherited secrets, write permissions or
`security-events: write` are required. zizmor receives the caller's `github.token`
for online audits. Checkouts disable persisted credentials. Semgrep rule packs
are fetched from the registry; pinning the tool does not freeze registry rules.

The three scan jobs are independent. Semgrep has a 20-minute timeout; Actions
auditing and Gitleaks each have 15 minutes. Semgrep and Gitleaks upload redacted
(Gitleaks) or tool-generated (Semgrep) SARIF artifacts for **three days**, even
after failures when a report exists. These are artifacts, not Code Scanning
uploads. actionlint and zizmor findings appear in step logs.

### Findings versus tool failures

`fail_on_findings: false` is not permission to ignore a broken scanner:

- **actionlint 1.7.12:** exit `0` means no findings, `1` means findings, `2` means
  invalid command options and `3` means fatal execution errors. Only `1` is
  tolerated in report-only mode; other nonzero statuses fail.
- **zizmor 1.26.1:** finding statuses are `11` through `14`; audit, argument and
  no-input errors are `1`, `2` and `3`. Report-only mode uses the documented
  `--no-exit-codes` option, which suppresses finding statuses but preserves tool
  errors. `--strict-collection` also makes input parsing failures fatal.
- **Semgrep:** blocking mode adds `--error`; report-only mode omits it. Nonzero
  tool exits still fail the step.
- **Gitleaks:** `gitleaks_fail` selects the findings exit code (`1` or `0`).
  Download, checksum, installation and scanner execution failures are not
  suppressed.

zizmor runs after actionlint findings **or failures**, provided checkout succeeded
and the job was not cancelled. A failed actionlint step still makes the job fail;
running zizmor does not erase that failure. A job timeout/cancellation can prevent
remaining steps from running.

Exit contracts:
[actionlint constants](https://github.com/rhysd/actionlint/blob/v1.7.12/command.go),
[zizmor exit codes](https://github.com/zizmorcore/zizmor/blob/v1.26.1/docs/usage.md#exit-codes),
[Gitleaks configuration and CLI](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md).

### Gitleaks coverage and local false positives

Checkout fetches full history, but scanning is deliberately **incremental**, not
a full-history audit:

| Caller event | `git log` selection |
| --- | --- |
| `pull_request` | `base.sha..head.sha` |
| `push` with a nonzero `before` | `before..github.sha` |
| Initial/new-branch push with missing or all-zero `before` | `-1` (latest commit only) |
| `workflow_dispatch` or any other event | `-1` (latest commit only) |

All selections also use `--no-merges`. Thus an initial push containing multiple
commits is **not** fully covered, and dispatch is **not** a full-history audit or
a way to rescan every file. A push does not detect secrets added outside its
selected range. Existing history findings are intentionally not turned into
blockers for unrelated incremental changes. Plan a separate, explicitly scoped
history audit when broader coverage is needed.

The workflow supplies a central `GITLEAKS_CONFIG_TOML` extending Gitleaks' default
rules. It takes precedence over a repository's `.gitleaks.toml`; changing that
local TOML does not replace or extend the central policy. The central baseline
currently excludes paths under `tests/logs/` and `tests/scripts/`, not Markdown or
documentation generally. Those broad fixture exclusions are deliberate existing
policy, not proof that every file in those directories is safe.

For a reviewed **false positive**, use the narrowest local mechanism:

- Add the exact finding fingerprint to root `.gitleaksignore` (supported by the
  pinned Gitleaks version, documented upstream as experimental).
- Use an inline `gitleaks:allow` comment on the affected dummy-secret line.

Record the reason in review and keep suppressions narrow. Both mechanisms remain
effective with the central TOML. Never suppress a live credential: revoke/rotate
it and follow `SECURITY.md`. Central rule/allowlist changes belong in a separate,
reviewed change here, not an arbitrary caller-supplied config.

For Actions false positives, zizmor uses `.github/zizmor.yml` when present and
also supports its documented inline ignore comments. Prefer specific findings
over disabling whole audits.

## Maintenance and validation

Run `python3 -m unittest discover -s tests -v` with Bash available. Tests execute
the actual workflow Bash blocks against deterministic tool doubles, covering
findings, runtime/config/no-input exits, setup failures, config arguments and
the independent-step condition. They do not replace real scanner runs; this
repository's CI runs both.

Upgrade through a reviewed PR: update tool versions with their verified release
checksums, keep actions pinned to full SHAs with version comments, recheck
upstream exit semantics and run regression tests plus actionlint/zizmor. Check
blocking and report-only behavior before rollout. After the change is merged,
update callers to the reviewed merge commit SHA in separate PRs; existing pins
do not automatically adopt changes here. Do not widen historical scan ranges or
make existing report-only findings blocking as an incidental dependency upgrade.
