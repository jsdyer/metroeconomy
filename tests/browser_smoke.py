"""Exercise the built starter at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/")
                page.locator("#cards h3").first.wait_for()
                assert page.locator("#cards h3").all_text_contents() == ["Halifax", "Vancouver"]
                page.select_option("#right", "932")
                page.select_option("#month", "2025-10")
                page.select_option("#metric", "3")
                page.locator("#cards h3").filter(has_text="Abbotsford-Mission").wait_for()
                page.wait_for_function("document.querySelector('#definition').textContent.includes('employed people')")
                assert "month=2025-10" in page.locator("#share").get_attribute("href")
                with page.expect_download() as captured:
                    page.locator("#download").click()
                assert "932" in captured.value.suggested_filename
                assert page.locator("#history tr").count() == 60
                assert page.get_by_text("Report an issue").count() == 1
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                assert not errors, errors
                browser.close()
            print("Browser checks passed: project subpath, city and month change, indicator, sharing, CSV and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
