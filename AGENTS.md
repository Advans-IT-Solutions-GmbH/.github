# Agent Instructions — .github

Git, commit, and PR conventions follow the org-wide rules: never commit directly to `main`,
feature branch + PR (`fix/…`, `feat/…`, `docs/…`, `chore/…`), squash merge by the maintainer,
commit under your **own** GitHub account with your personal no-reply address (never `@advans.ch`
in commits), no `Co-authored-by` trailer and no agent signature. Org members find the
authoritative version (SSOT) in the private org repo `Advans-IT-Solutions-GmbH/org`,
`README.md`, section "Git and Commit Conventions". This summary is sufficient for contributors
without access.

**Definition of Done — Copilot code review:** a PR with Copilot code review is only
**done** once every review comment has been addressed (commit and push a fix, or reject it
with a reasoned reply if the suggestion isn't sensible), all review threads are resolved, and
a re-requested Copilot round finds nothing new. This applies to developers and agents alike.
The loop: fetch the review and its threads (`gh api .../reviews` and the GraphQL
`reviewThreads` field), handle every open thread, push fixes, resolve each thread via the
GraphQL `resolveReviewThread` mutation, re-request Copilot
(`gh api --method POST .../requested_reviewers -f 'reviewers[]=copilot-pull-request-reviewer[bot]'`),
and repeat until nothing new comes back.

Repo-specific: this **public** repo holds the org profile/community-health files and provides
the reusable `reusable-security.yml` workflow used by every org repo — changes here affect all
repos. No internal details or secrets belong here. Further notes: `CLAUDE.md`.
