# Bug Report

**Title:** An ini-configured `base_url` becomes `None` on pytest-xdist workers

**Environment:** Ubuntu 24.04, Python 3.12.3, pytest 9.1.0,
pytest-base-url 2.1.0, pytest-xdist 3.8.0. Verified on 2026-09-08.

**Preconditions:** The three pytest packages are installed in the active virtual
environment. Run the reproduction in a temporary directory outside this repository,
because this repository's `conftest.py` contains a workaround. No browser, network
request, account or running application is required.

**Steps to Reproduce:**

1. Create an isolated directory and configuration. These commands create only
   temporary files and use packages from the already activated environment:

   ```bash
   QA_REPRO_DIR=$(mktemp -d /tmp/base-url-repro.XXXXXX)
   cd "$QA_REPRO_DIR"
   cat > pytest.ini <<'INI'
   [pytest]
   base_url = http://example.test
   INI
   cat > test_base_url.py <<'PY'
   def test_base_url_from_ini(base_url):
       assert base_url == "http://example.test"
   PY
   ```

2. Run the serial control, with inherited URL/pytest options removed:

   ```bash
   env -u PYTEST_BASE_URL -u PYTEST_ADDOPTS -u VERIFY_BASE_URL python -m pytest -q
   ```

3. Run the same test on xdist workers:

   ```bash
   env -u PYTEST_BASE_URL -u PYTEST_ADDOPTS -u VERIFY_BASE_URL python -m pytest -q -n 2
   ```

4. Confirm the CLI workaround:

   ```bash
   env -u PYTEST_BASE_URL -u PYTEST_ADDOPTS -u VERIFY_BASE_URL \
     python -m pytest -q -n 2 --base-url http://example.test
   ```

**Actual Result:** Serial execution passes. Parallel execution fails with
`assert None == 'http://example.test'`. Parallel execution with `--base-url` passes.

**Expected Result:** The configured URL is available through the `base_url` fixture
in both serial and parallel execution without requiring a CLI workaround.

**Reproducibility:** 2/2 isolated parallel reproductions failed; the serial and
explicit-CLI controls passed in both reproductions.

**Severity:** Medium — breaks parallel tests that rely on ini configuration;
serial execution and explicit CLI configuration remain available.

**Priority:** Suggested P2; upstream maintainers determine their own priority.

**Attachments / Evidence:** [Captured command output](evidence/base-url-xdist.txt).
The `.test` hostname is a reserved example value; the test only compares strings.

**Additional Notes:**

- This is a reproduced existing open-source defect, not a claim of first discovery.
  Duplicate review found [pytest-xdist issue #800](https://github.com/pytest-dev/pytest-xdist/issues/800)
  and the earlier [pytest-base-url issue #34](https://github.com/pytest-dev/pytest-base-url/issues/34).
  No duplicate issue has been submitted from this project.
- The installed `pytest-base-url` plugin reads its fixture value from
  `config.getoption("base_url")`. Its controller configuration hook resolves the ini
  value but returns early on workers. This agrees with the observed missing value;
  the upstream discussion covers the broader option propagation problem.
- Our fixture uses `getoption("base_url") or getini("base_url")`. Five offline
  [infrastructure checks](../../tests/unit/test_fixtures.py) cover serial/parallel ini
  configuration, environment/CLI precedence and browser-free API setup.
- This defect is separate from the historical CI access challenge. The old suite
  already had an ini fallback, but that fallback ignored CLI/environment overrides.
