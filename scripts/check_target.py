"""Read-only CI preflight with an optional check from the selected browser."""

import argparse
import json
import os
import tomllib
from pathlib import Path

from playwright.sync_api import Error, sync_playwright

from pages.home_page import HomePage
from utils.api import assert_api_response
from utils.target import TargetUnavailableError


def main() -> int:
    config = tomllib.loads(
        (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text()
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.getenv("PYTEST_BASE_URL")
        or config["tool"]["pytest"]["ini_options"]["base_url"],
    )
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"])
    parser.add_argument("--output", type=Path, default=Path("reports/preflight.json"))
    args = parser.parse_args()
    report = {"base_url": args.base_url, "browser": args.browser, "status": "failed"}
    try:
        with sync_playwright() as playwright:
            api = playwright.request.new_context(base_url=args.base_url)
            try:
                body = assert_api_response(
                    api.get("/api/productsList", max_redirects=0), 200
                )
                assert isinstance(body.get("products"), list) and body["products"], (
                    "Catalog API returned no products"
                )
            finally:
                api.dispose()
            if args.browser:
                browser = getattr(playwright, args.browser).launch()
                try:
                    page = browser.new_page(base_url=args.base_url)
                    home = HomePage(page)
                    home.open()
                    home.featured_items.first.wait_for(state="visible", timeout=15_000)
                finally:
                    browser.close()
        report["status"] = "passed"
    except (AssertionError, Error, TargetUnavailableError) as error:
        report["error"] = str(error).split("Call log:")[0].strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
