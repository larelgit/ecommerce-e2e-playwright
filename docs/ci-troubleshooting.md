# CI failure analysis

The failed [main run 27691865635](https://github.com/larelgit/ecommerce-e2e-playwright/actions/runs/27691865635)
ran commit `9d42b04` on 2026-06-17. Dependency/browser installation succeeded.
Chromium and Firefox each finished with **9 failed, 5 errors, 24 reruns**; WebKit passed.

## Evidence and diagnosis

The [Chromium job](https://github.com/larelgit/ecommerce-e2e-playwright/actions/runs/27691865635/job/81904703950)
reported the following home-page assertion:

```text
Page title expected to be 'Automation Exercise'
Actual value: One moment, please...
```

Both failed engines then timed out looking for normal shop controls. Account creation
and deletion failed with `Max redirect count exceeded`. Their request logs showed
HTTP 302 responses with `Location: /`, followed by repeated redirects at `/`.

These observations show a target access challenge and redirect loop, rather than
nine independent selector regressions. The logs do not establish exactly which
site-side rule triggered the challenge. An IP, browser, traffic or regional rule is
possible, but unverified. WebKit's passing job does not prove the engine itself caused
the difference, because each job ran on a separate runner.

## Changes in this repository

- The preflight checks the catalog API and, for UI jobs, the selected browser's home
  page. It writes `reports/preflight-*.json` and exits nonzero on failure.
- API requests disable redirects. HTTP status is checked before JSON, so the first
  unexpected redirect is visible instead of a long redirect-loop traceback.
- Page navigation waits for DOM readiness, rejects HTTP errors, and waits up to
  15 seconds for recognized challenge titles to clear. Persistent challenges raise
  `TargetUnavailableError` before tests start locating form controls.
- PRs run smoke checks; the full browser matrix runs on main/scheduled/manual runs.
  Browser jobs are serialized and each uses two workers instead of four. API tests
  run once in their own job. This reduces load; it cannot guarantee site access.
- Blanket test reruns and fixed navigation delays were removed. A failed environment
  check still fails CI; it is never converted into a pass or a skip.
- The base URL fixture now preserves CLI/environment overrides on xdist workers.
  Cleanup is registered before account creation and validates deletion responses.

## Diagnose a new failure

Inside the project's activated virtual environment:

```bash
python scripts/check_target.py --browser chromium
pytest tests/ui/test_smoke.py --browser chromium --tracing retain-on-failure
```

Expected: preflight reports `"status": "passed"`; the home-page test passes. If a
compatible target is selected with pytest's `--base-url`, pass the same URL to
the preflight's `--base-url` option. Both commands also read `PYTEST_BASE_URL`.

If the report shows 302, 403, 5xx or a challenge title, check access to the target
from the runner's network. A persistent site-side block requires a permitted runner
or a target instance you control. Increasing locator timeouts will not restore access.
If preflight passes but a UI assertion fails, inspect its screenshot and trace:

```bash
playwright show-trace test-results/<failed-test-directory>/trace.zip
```

If the error instead names a missing shared library, the browser cannot start on
that machine. `playwright install --with-deps <browser>` installs system packages on
Ubuntu and may require sudo. CI already includes this installation step.

## Verification scope

Local verification on 2026-09-08:

| Check | Result |
|---|---|
| Full default suite, `pytest -n 2`, without reruns | 32 passed in 42.79 s: 15 API, 12 Chromium UI, 5 offline |
| Firefox UI, two workers | 12 passed in 40.05 s |
| WebKit UI, two workers with temporary library setup | 12 passed in 49.12 s |
| Ruff lint/format, Pyright, actionlint, pip dependency consistency | Passed |
| Preflight against local HTTP 302 loop, HTTP 503 and HTML challenge responses | Each exited 1 with diagnostics; redirects were not followed |
| Preflight against healthy local API, including environment URL override | Passed |

The development machine lacked WebKit's GStreamer/AVIF libraries and passwordless
sudo. For verification only, the Ubuntu `libgstreamer-plugins-bad1.0-0`, `libavif16`,
`libgav1-1` and `libyuv0` packages were downloaded and extracted under
`/tmp/ecommerce-webkit-deps`. A temporary launcher added those library paths to the
same Playwright WebKit binary. No system packages were installed. Normal WebKit
execution on this PC still needs the documented browser system dependencies.
The standard Chromium and Firefox commands needed no such adjustment.

Local results establish that the scenarios work from the development machine.
The updated workflow must still run on GitHub-hosted runners after publication;
local passes cannot establish that their network will be accepted by the live site.
