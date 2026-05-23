from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

import requests
import websocket


PAPERS = [
    ("hajihosseini2020dc", "9020169"),
    ("meng2022novel", "9767707"),
    ("fathollahi2023robust", "10109206"),
    ("gheisarnejad2022reducing", "9843888"),
    ("khooban2022smartenance", "9888784"),
]

CARSI_URL = (
    "https://ieeexplore.ieee.org/servlet/wayf.jsp?"
    "entityId=https://idp.seu.edu.cn/idp/shibboleth&"
    "url=https%3A%2F%2Fieeexplore.ieee.org%2FXplore%2Fhome.jsp"
)


def log(msg: str) -> None:
    print(msg, flush=True)


class CDPPage:
    def __init__(self, ws_url: str) -> None:
        self.ws = websocket.create_connection(ws_url, timeout=20)
        self.next_id = 1

    def close(self) -> None:
        self.ws.close()

    def call(self, method: str, params: dict | None = None, timeout: int = 60) -> dict:
        msg_id = self.next_id
        self.next_id += 1
        payload = {"id": msg_id, "method": method}
        if params is not None:
            payload["params"] = params
        self.ws.send(json.dumps(payload))
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = self.ws.recv()
            msg = json.loads(raw)
            if msg.get("id") != msg_id:
                continue
            if "error" in msg:
                raise RuntimeError(f"{method} failed: {msg['error']}")
            return msg.get("result", {})
        raise TimeoutError(f"{method} timed out")

    def eval(self, expression: str, timeout: int = 60) -> object:
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": True,
                "returnByValue": True,
                "timeout": timeout * 1000,
            },
            timeout=timeout + 5,
        )
        remote = result.get("result", {})
        if "value" in remote:
            return remote["value"]
        return remote.get("description")

    def navigate(self, url: str) -> None:
        self.call("Page.navigate", {"url": url}, timeout=30)
        time.sleep(4)


def chrome_path() -> str:
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError("Chrome or Edge executable was not found.")


def ensure_chrome(port: int, profile_dir: Path) -> None:
    try:
        requests.get(f"http://127.0.0.1:{port}/json/version", timeout=2)
        log(f"Reusing existing Chrome DevTools session on port {port}.")
        return
    except Exception:
        pass

    profile_dir.mkdir(parents=True, exist_ok=True)
    exe = chrome_path()
    args = [
        exe,
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--new-window",
        CARSI_URL,
    ]
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log(f"Started visible browser for SEU login: {exe}")
    for _ in range(60):
        try:
            requests.get(f"http://127.0.0.1:{port}/json/version", timeout=2)
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Chrome DevTools endpoint did not become available.")


def open_page(port: int, url: str) -> CDPPage:
    quoted = urllib.parse.quote(url, safe=":/?=&%")
    resp = requests.put(f"http://127.0.0.1:{port}/json/new?{quoted}", timeout=10)
    resp.raise_for_status()
    target = resp.json()
    page = CDPPage(target["webSocketDebuggerUrl"])
    page.call("Page.enable")
    page.call("Runtime.enable")
    return page


def has_access(page: CDPPage) -> bool:
    expr = """
    (() => {
      const text = document.body ? document.body.innerText : '';
      return {
        url: location.href,
        title: document.title,
        access: text.includes('Access provided by') || text.includes('Southeast University')
      };
    })()
    """
    try:
        state = page.eval(expr, timeout=10)
    except Exception:
        return False
    if isinstance(state, dict):
        log(f"Current page: {state.get('title')} | {state.get('url')}")
        return bool(state.get("access"))
    return False


def wait_for_manual_login(page: CDPPage, seconds: int) -> None:
    log("Please complete SEU/CARSI login in the visible browser window.")
    log(f"Waiting up to {seconds} seconds for IEEE to show Southeast University access...")
    deadline = time.time() + seconds
    while time.time() < deadline:
        if has_access(page):
            log("SEU institutional access detected.")
            return
        time.sleep(5)
    raise TimeoutError("SEU institutional access was not detected before timeout.")


def enable_downloads(page: CDPPage, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        page.call("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(out_dir)})
    except Exception:
        page.call("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(out_dir)})


def download_one(page: CDPPage, key: str, arnumber: str, out_dir: Path) -> Path:
    filename = f"{key}_{arnumber}.pdf"
    target = out_dir / filename
    if target.exists() and target.stat().st_size > 100_000:
        log(f"[{key}] Already exists: {target}")
        return target

    page.navigate(f"https://ieeexplore.ieee.org/document/{arnumber}/")
    enable_downloads(page, out_dir)
    expr = f"""
    (async () => {{
      const arnumber = {json.dumps(arnumber)};
      const filename = {json.dumps(filename)};
      const ref = btoa(`https://ieeexplore.ieee.org/document/${{arnumber}}`);
      const pdfUrl = `https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=${{arnumber}}&ref=${{ref}}`;
      const resp = await fetch(pdfUrl, {{ credentials: 'include' }});
      const contentType = resp.headers.get('content-type') || '';
      if (!resp.ok) {{
        const text = await resp.text();
        return {{ ok: false, status: resp.status, contentType, preview: text.slice(0, 300) }};
      }}
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {{ URL.revokeObjectURL(url); a.remove(); }}, 1000);
      return {{ ok: true, status: resp.status, contentType, size: blob.size }};
    }})()
    """
    result = page.eval(expr, timeout=90)
    log(f"[{key}] Fetch result: {result}")
    if not isinstance(result, dict) or not result.get("ok"):
        raise RuntimeError(f"{key} PDF fetch failed: {result}")

    deadline = time.time() + 90
    while time.time() < deadline:
        if target.exists() and target.stat().st_size >= int(result.get("size", 0) or 1):
            log(f"[{key}] Saved {target} ({target.stat().st_size} bytes)")
            return target
        # Chrome may still use .crdownload while finishing.
        time.sleep(1)

    candidates = sorted(out_dir.glob(f"*{arnumber}*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        log(f"[{key}] Saved as {candidates[0]} ({candidates[0].stat().st_size} bytes)")
        return candidates[0]
    raise TimeoutError(f"{key} download did not appear in {out_dir}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9333)
    parser.add_argument(
        "--profile-dir",
        default=(
            r"G:\blog\claude_code_useage\project_paper\overleaf"
            r"\ACM_computing_Surverys\paper_a_control_deployment\.cdp_profile"
        ),
    )
    parser.add_argument(
        "--out-dir",
        default=(
            r"G:\blog\claude_code_useage\project_paper\overleaf"
            r"\ACM_computing_Surverys\paper_a_control_deployment\source_pdfs"
        ),
    )
    parser.add_argument("--login-timeout", type=int, default=360)
    args = parser.parse_args()

    profile_dir = Path(args.profile_dir)
    out_dir = Path(args.out_dir)
    ensure_chrome(args.port, profile_dir)
    page = open_page(args.port, CARSI_URL)
    try:
        wait_for_manual_login(page, args.login_timeout)
        downloaded = []
        for key, arnumber in PAPERS:
            downloaded.append(download_one(page, key, arnumber, out_dir))
        log("Downloaded PDFs:")
        for path in downloaded:
            log(f"  {path}")
        return 0
    finally:
        page.close()


if __name__ == "__main__":
    sys.exit(main())
