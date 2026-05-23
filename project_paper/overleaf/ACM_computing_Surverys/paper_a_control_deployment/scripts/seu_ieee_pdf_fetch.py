from __future__ import annotations

import argparse
import base64
import os
import sys
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


PAPERS = [
    {
        "key": "hajihosseini2020dc",
        "doi": "10.1109/TPEL.2020.2977765",
        "arnumber": "9020169",
    },
    {
        "key": "meng2022novel",
        "doi": "10.1109/TIE.2022.3170608",
        "arnumber": "9767707",
    },
    {
        "key": "fathollahi2023robust",
        "doi": "10.1109/TCSII.2023.3270751",
        "arnumber": "10109206",
    },
    {
        "key": "gheisarnejad2022reducing",
        "doi": "10.1109/TCSII.2022.3194271",
        "arnumber": "9843888",
    },
    {
        "key": "khooban2022smartenance",
        "doi": "10.1109/TCSII.2022.3206230",
        "arnumber": "9888784",
    },
]


CARSI_URL = (
    "https://ieeexplore.ieee.org/servlet/wayf.jsp?"
    "entityId=https://idp.seu.edu.cn/idp/shibboleth&"
    "url=https%3A%2F%2Fieeexplore.ieee.org"
)


def log(message: str) -> None:
    print(message, flush=True)


def has_seu_access(page) -> bool:
    try:
        text = page.locator("body").inner_text(timeout=8000)
    except PlaywrightTimeoutError:
        return False
    return "Southeast University" in text or "Access provided by" in text


def maybe_fill_seu_credentials(page) -> bool:
    username = os.environ.get("SEU_USERNAME")
    password = os.environ.get("SEU_PASSWORD")
    if not username or not password:
        return False

    if "auth.seu.edu.cn" not in page.url:
        return False

    script = """
    ({ username, password }) => {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 'value'
      ).set;

      const inputs = Array.from(document.querySelectorAll('input'));
      const userInput =
        document.querySelector('input[placeholder*="一卡通"]') ||
        document.querySelector('input[placeholder*="ID"]') ||
        inputs.find((el) => el.type === 'text') ||
        inputs[0];
      const passInput =
        document.querySelector('input[type="password"]') ||
        inputs.find((el) => el.placeholder && el.placeholder.includes('密码'));

      if (!userInput || !passInput) return false;

      nativeInputValueSetter.call(userInput, username);
      userInput.dispatchEvent(new Event('input', { bubbles: true }));
      nativeInputValueSetter.call(passInput, password);
      passInput.dispatchEvent(new Event('input', { bubbles: true }));

      const checkbox = document.querySelector('input[type="checkbox"]');
      if (checkbox && !checkbox.checked) checkbox.click();

      const buttons = Array.from(document.querySelectorAll('button'));
      const loginButton =
        buttons.find((button) => button.textContent.includes('登录')) ||
        buttons.find((button) => button.textContent.includes('登') && button.textContent.includes('录')) ||
        buttons.find((button) => button.type === 'submit');
      if (!loginButton) return false;
      loginButton.click();
      return true;
    }
    """
    return bool(page.evaluate(script, {"username": username, "password": password}))


def ensure_login(page, manual_timeout_s: int) -> None:
    log("Checking IEEE institutional access...")
    page.goto("https://ieeexplore.ieee.org", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2500)
    if has_seu_access(page):
        log("SEU access detected on IEEE Xplore.")
        return

    log("SEU access not detected. Opening CARSI login route...")
    page.goto(CARSI_URL, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(4000)
    maybe_fill_seu_credentials(page)

    deadline = time.time() + manual_timeout_s
    log(
        "If a browser login page is visible, please complete SEU/CAS login there. "
        f"Waiting up to {manual_timeout_s} seconds..."
    )
    while time.time() < deadline:
        try:
            if "ieeexplore.ieee.org" in page.url and has_seu_access(page):
                log("SEU access detected after login.")
                return
            if "auth.seu.edu.cn" in page.url:
                maybe_fill_seu_credentials(page)
        except Exception:
            pass
        page.wait_for_timeout(3000)

    raise RuntimeError("SEU/IEEE institutional access was not established before timeout.")


def download_pdf(page, key: str, arnumber: str, out_dir: Path) -> Path:
    doc_url = f"https://ieeexplore.ieee.org/document/{arnumber}/"
    log(f"[{key}] Opening {doc_url}")
    page.goto(doc_url, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(3500)

    result = page.evaluate(
        """
        async ({ arnumber }) => {
          const ref = btoa(`https://ieeexplore.ieee.org/document/${arnumber}`);
          const pdfUrl = `https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=${arnumber}&ref=${ref}`;
          const resp = await fetch(pdfUrl, { credentials: 'include' });
          const contentType = resp.headers.get('content-type') || '';
          const arrayBuffer = await resp.arrayBuffer();
          const bytes = new Uint8Array(arrayBuffer);
          let binary = '';
          const chunkSize = 0x8000;
          for (let i = 0; i < bytes.length; i += chunkSize) {
            binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
          }
          return {
            status: resp.status,
            contentType,
            size: bytes.length,
            base64: btoa(binary),
          };
        }
        """,
        {"arnumber": arnumber},
    )

    data = base64.b64decode(result["base64"])
    if result["status"] != 200 or not data.startswith(b"%PDF"):
        preview = data[:200].decode("utf-8", errors="replace")
        raise RuntimeError(
            f"{key}: PDF fetch failed. status={result['status']}, "
            f"contentType={result['contentType']}, size={result['size']}, preview={preview!r}"
        )

    out_path = out_dir / f"{key}_{arnumber}.pdf"
    out_path.write_bytes(data)
    log(f"[{key}] Saved {out_path} ({len(data)} bytes)")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        default=(
            r"G:\blog\claude_code_useage\project_paper\overleaf"
            r"\ACM_computing_Surverys\paper_a_control_deployment\source_pdfs"
        ),
    )
    parser.add_argument(
        "--profile-dir",
        default=(
            r"G:\blog\claude_code_useage\project_paper\overleaf"
            r"\ACM_computing_Surverys\paper_a_control_deployment\.browser_profile"
        ),
    )
    parser.add_argument("--manual-timeout", type=int, default=240)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    profile_dir = Path(args.profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            channel="chrome",
            headless=args.headless,
            accept_downloads=True,
            viewport={"width": 1440, "height": 960},
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        try:
            ensure_login(page, args.manual_timeout)
            failures: list[str] = []
            for paper in PAPERS:
                try:
                    download_pdf(page, paper["key"], paper["arnumber"], out_dir)
                except Exception as exc:
                    log(f"[{paper['key']}] ERROR: {exc}")
                    failures.append(f"{paper['key']}: {exc}")
            if failures:
                log("Failures:")
                for failure in failures:
                    log(f"  - {failure}")
                return 1
            return 0
        finally:
            browser.close()


if __name__ == "__main__":
    sys.exit(main())
