"""Exercise actual pytest sessions so fixture regressions fail without the site."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[2]


def run_probe(
    directory: Path,
    source: str,
    options: list[str],
    environment_url: str | None = None,
) -> None:
    (directory / "conftest.py").write_text((ROOT / "conftest.py").read_text())
    (directory / "pytest.ini").write_text(
        "[pytest]\nbase_url = http://configured.example.test\n"
    )
    (directory / "test_probe.py").write_text(source)
    environment = os.environ.copy()
    for key in ("PYTEST_BASE_URL", "PYTEST_ADDOPTS", "VERIFY_BASE_URL"):
        environment.pop(key, None)
    if environment_url:
        environment["PYTEST_BASE_URL"] = environment_url
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *options],
        cwd=directory,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("options", "environment_url", "expected"),
    [
        ([], None, "http://configured.example.test"),
        (["-n", "2"], None, "http://configured.example.test"),
        (
            ["-n", "2"],
            "http://environment.example.test",
            "http://environment.example.test",
        ),
        (
            ["-n", "2", "--base-url", "http://cli.example.test"],
            "http://environment.example.test",
            "http://cli.example.test",
        ),
    ],
    ids=["serial-ini", "parallel-ini", "parallel-env", "cli-over-env"],
)
def test_base_url_precedence_in_real_pytest_sessions(
    tmp_path: Path, options: list[str], environment_url: str | None, expected: str
) -> None:
    run_probe(
        tmp_path,
        f"def test_url(base_url):\n    assert base_url == {expected!r}\n",
        options,
        environment_url,
    )


def test_api_fixture_does_not_request_a_browser(tmp_path: Path) -> None:
    run_probe(
        tmp_path,
        "import pytest\n"
        "@pytest.fixture(scope='session')\n"
        "def browser():\n"
        "    raise AssertionError('API test requested a browser')\n"
        "def test_request_context(api):\n"
        "    assert api.storage_state() == {'cookies': [], 'origins': []}\n",
        [],
    )
