"""Execute the reusable workflow's Bash blocks with deterministic tool doubles.

Only Python's standard library and Bash are required. No scanners or network
access are needed; the pinned tools' exit contracts are linked in README.md.
"""

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest


WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "reusable-security.yml"
).read_text(encoding="utf-8")


def step(name):
    """Read one known, fixed-indent step, not arbitrary YAML."""
    match = re.search(
        rf"^      - name: {re.escape(name)}\n(.*?)(?=^      - name:|^  \S|\Z)",
        WORKFLOW.split("  actions-audit:\n", 1)[1].split("  gitleaks:\n", 1)[0],
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"Missing workflow step: {name}")
    return match.group(1)


def run_block(name):
    return textwrap.dedent(step(name).split("        run: |\n", 1)[1])


class WorkflowTests(unittest.TestCase):
    def run_step(self, name, *, config=False, **env):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # These commands stand in for setup only, not the scanner exit logic.
            stubs = r"""
                curl() { return "${DOWNLOAD_RC:-0}"; }
                sha256sum() { read -r line; return "${CHECKSUM_RC:-0}"; }
                tar() { return 0; }
                python3() { return "${INSTALL_RC:-0}"; }
                function ./actionlint() { return "$TOOL_RC"; }
                zizmor() {
                    printf "%s\n" "$@" > args.txt
                    local rc="$TOOL_RC"
                    if [[ " $* " == *" --no-exit-codes "* ]]; then
                        case "$rc" in 11|12|13|14) rc=0 ;; esac
                    fi
                    return "$rc"
                }
            """
            if config:
                (root / ".github").mkdir()
                (root / ".github" / "zizmor.yml").write_text("rules: {}\n", encoding="utf-8")
            environment = {
                **os.environ,
                "ACTIONLINT_VERSION": "test",
                "ACTIONLINT_SHA256": "test",
                "ZIZMOR_MIN_SEVERITY": "low",
                **{key: str(value) for key, value in env.items()},
            }
            result = subprocess.run(
                [
                    shutil.which("bash"),
                    "-e",
                    "-o",
                    "pipefail",
                    "-c",
                    textwrap.dedent(stubs) + run_block(name),
                ],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=10,
            )
            args_file = root / "args.txt"
            args = args_file.read_text().splitlines() if args_file.exists() else []
            return result, args

    def test_actionlint_exit_policy(self):
        for blocking in ("true", "false"):
            for code in (0, 1, 2, 3, 127, 130):
                with self.subTest(blocking=blocking, code=code):
                    result, _ = self.run_step(
                        "actionlint", FAIL_ON_FINDINGS=blocking, TOOL_RC=code
                    )
                    expected = 0 if code == 1 and blocking == "false" else code
                    self.assertEqual(result.returncode, expected, result.stderr)

    def test_zizmor_exit_policy(self):
        for blocking in ("true", "false"):
            for code in (0, 1, 2, 3, 10, 11, 12, 13, 14, 127, 130):
                with self.subTest(blocking=blocking, code=code):
                    result, args = self.run_step(
                        "Run zizmor", FAIL_ON_FINDINGS=blocking, TOOL_RC=code
                    )
                    expected = 0 if code in (11, 12, 13, 14) and blocking == "false" else code
                    self.assertEqual(result.returncode, expected, result.stderr)
                    self.assertIn("--strict-collection", args)
                    self.assertEqual("--no-exit-codes" in args, blocking == "false")
                    self.assertEqual(args[-1], ".github/workflows")
                    self.assertEqual(args[args.index("--min-severity") + 1], "low")

    def test_setup_errors_are_never_findings(self):
        for name, failures in (
            ("actionlint", ("DOWNLOAD_RC", "CHECKSUM_RC")),
            ("Run zizmor", ("INSTALL_RC",)),
        ):
            for failure in failures:
                for blocking in ("true", "false"):
                    with self.subTest(step=name, failure=failure, blocking=blocking):
                        result, _ = self.run_step(
                            name, FAIL_ON_FINDINGS=blocking, TOOL_RC=0, **{failure: 7}
                        )
                        self.assertEqual(result.returncode, 7, result.stderr)

    def test_local_zizmor_configuration(self):
        for config in (False, True):
            with self.subTest(config=config):
                result, args = self.run_step(
                    "Run zizmor", config=config, FAIL_ON_FINDINGS="false", TOOL_RC=0
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual("--config" in args, config)
                if config:
                    self.assertEqual(args[args.index("--config") + 1], ".github/zizmor.yml")

    def test_zizmor_runs_after_actionlint_failure_but_not_failed_checkout(self):
        self.assertIn("        id: checkout\n", step("Checkout"))
        # The explicit status function overrides Actions' implicit success().
        self.assertIn(
            "        if: ${{ !cancelled() && steps.checkout.outcome == 'success' }}\n",
            step("Run zizmor"),
        )
        self.assertNotIn("continue-on-error:", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
