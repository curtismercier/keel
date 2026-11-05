"""Smoke tests: the two export scripts must pass their own controls, and each public layer must stay partitioned.

Why this file exists: `pytest` exits 5 when it collects nothing, so a template with only an empty
`packages/_template/tests/` shipped a CI that failed on every PR — forever, on every project laid on it.
A template's CI must test the template's own guarantees, not wait for the project to have some.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          cwd=ROOT, capture_output=True, text=True)


def test_gate_self_test_passes():
    r = run("orchestrator-export-check.py", "--self-test")
    assert r.returncode == 0, f"gate self-test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"


def test_generator_self_test_passes():
    r = run("orchestrator-export.py", "--self-test")
    assert r.returncode == 0, f"generator self-test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"


def test_every_layer_exports_clean():
    """Each target must find its units and pass the gate. Empty is legal (a fresh project has no rings yet)."""
    for target in ("public", "process", "private"):
        r = run("orchestrator-export.py", "--target", target)
        assert r.returncode == 0, f"--target {target} failed:\n{r.stderr[-2000:]}"


def test_the_gate_can_fail():
    """The control: a core unit must be refused when it rides the shown-work export."""
    core = next(iter((ROOT / "packages").rglob("*.py")), None)
    assert core is not None, "no python file under packages/ to test with"
    rel = core.relative_to(ROOT).as_posix()
    r = run("orchestrator-export-check.py", "--target", "process", "--files", rel)
    assert r.returncode == 1, f"the gate ACCEPTED a core file in the process export ({rel})"
    assert "EXPORT BLOCKED" in r.stderr
