# SEU Library / IEEE Access Capability Assessment

This note checks whether the local machine already has evidence of using Southeast University Library access to search and download IEEE papers, and records the implementation route for repeatable Paper A source-level verification.

## Revised Conclusion

- **The dedicated skill exists locally:** `C:\Users\LaneLiang\.claude\skills\seu-ieee-downloader\SKILL.md`.
- **The intended MCP dependency is Playwright:** the skill is written for `mcp__playwright__*` browser tools, especially `mcp__playwright__browser_tabs`.
- **The blocker is credentials/session, not workflow design:** the skill expects `SEU_USERNAME` and `SEU_PASSWORD`, or an already-authenticated Playwright browser session.
- **Direct command-line PDF download is not the correct route:** IEEE PDF delivery uses browser-bound signed cookies, so `curl`/`Invoke-WebRequest` outside the authenticated browser can fail even when SEU access is valid.

## Local Reference Project Checked

Path checked:

```text
G:\blog\claude_code_useage\PROJECT\creative_find
```

## Evidence Found

The folder contains:

- Dedicated Claude skill:
  - `C:\Users\LaneLiang\.claude\skills\seu-ieee-downloader\SKILL.md`
- SEU login and library snapshots:
  - `seu-auth-login.md`
  - `seu-auth-login.png`
  - `seu-library-home.md`
  - `seu-library-home.png`
  - `seu-login-page.png`
  - `smoke-test-01-login-form.md`
- Playwright MCP session cache:
  - `.playwright-mcp\console-*.log`
  - `.playwright-mcp\page-*.yml`
- Downloaded IEEE PDFs:
  - `.playwright-mcp\paper-9521987-buck-drl.pdf`
  - `.playwright-mcp\paper-9817114-boost-drl.pdf`
  - `.playwright-mcp\paper-10006016-predictive-drl.pdf`

## What the Snapshots Show

- The SEU library home snapshot contains a database tab and an IEEE database link pointing to `https://ieeexplore.ieee.org/`.
- The IEEE page snapshot for document `9521987` shows:
  - `Access provided by:`
  - `Southeast University`
  - a PDF link of the form `/stamp/stamp.jsp?tp=&arnumber=9521987`
  - DOI `10.1109/TCSII.2021.3107535`
- The presence of downloaded PDFs in `.playwright-mcp` confirms that a prior Playwright MCP session could access and save IEEE full text.

## Implementation Mechanism

The local `seu-ieee-downloader` skill implements the IEEE download flow as follows:

1. **CARSI entry:** open the IEEE Xplore CARSI/Shibboleth URL:

   ```text
   https://ieeexplore.ieee.org/servlet/wayf.jsp?entityId=https://idp.seu.edu.cn/idp/shibboleth&url=https%3A%2F%2Fieeexplore.ieee.org
   ```

2. **Redirect chain:** IEEE Xplore Shibboleth service provider redirects to SEU IdP and then to the SEU CAS login page at `auth.seu.edu.cn`.

3. **CAS login page handling:** the SEU login page is an Ant Design Vue SPA. Plain JavaScript assignment such as `input.value = ...` may not update Vue state. The skill therefore uses the native input setter:

   ```javascript
   const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
     window.HTMLInputElement.prototype, 'value'
   ).set;

   nativeInputValueSetter.call(userInput, process.env.SEU_USERNAME);
   userInput.dispatchEvent(new Event('input', { bubbles: true }));
   ```

4. **Institutional session check:** after redirecting back to IEEE Xplore, verify that the page shows institutional access, e.g., `Access provided by: Southeast University`.

5. **Paper location:** prefer DOI lookup or direct `/document/{arnumber}` navigation; otherwise use IEEE title search.

6. **Browser-context PDF download:** compute the `ref` parameter from the paper URL and run PDF retrieval inside the authenticated browser context:

   ```javascript
   const ref = btoa(`https://ieeexplore.ieee.org/document/${arnumber}`);
   const pdfUrl = `https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber=${arnumber}&ref=${ref}`;
   const resp = await fetch(pdfUrl);
   const blob = await resp.blob();
   const url = URL.createObjectURL(blob);
   const a = document.createElement('a');
   a.href = url;
   a.download = `paper_${arnumber}.pdf`;
   document.body.appendChild(a);
   a.click();
   ```

7. **Save location:** downloaded files land in the working directory's `.playwright-mcp\` folder, then should be moved into Paper A's source PDF folder.

## Current Codex Session Limitation

In this Codex session, the local filesystem confirms the skill and prior Playwright artifacts, but the active tool surface does not expose callable `mcp__playwright__*` tools. A non-browser `Invoke-WebRequest` attempt to download the five target IEEE PDFs through the same `stamp.jsp` pattern returned HTTP 418 for all five articles. This confirms why the skill correctly uses browser-context `fetch` instead of command-line download.

## Current Operational Conclusion

- **Capability exists on this machine:** yes, via the `seu-ieee-downloader` skill and Playwright browser workflow.
- **Authentication route is known:** CARSI + Shibboleth + SEU CAS.
- **Required credentials:** `SEU_USERNAME` and `SEU_PASSWORD`, unless an authenticated browser session already exists.
- **Correct PDF route:** use browser-context `fetch` and blob download from `stampPDF/getPDF.jsp`; do not rely on external `curl`/PowerShell HTTP download.
- **Current Codex-callable status:** local evidence is confirmed; active `mcp__playwright__*` tools must be available in the running agent session before I can execute the skill directly here.

## Execution Checklist for Paper A PDF Verification

1. Confirm `SEU_USERNAME` and `SEU_PASSWORD` are available to the agent environment, or open an already-authenticated Playwright session.
2. Run `mcp__playwright__browser_tabs` with `action: "list"`.
3. If no IEEE institutional session exists, navigate through the CARSI entry URL and complete CAS login.
4. Verify `Access provided by: Southeast University` on IEEE Xplore.
5. For each target paper, navigate by DOI or arnumber.
6. Download with browser-context `fetch` and blob anchor click.
7. Move each PDF into:

   ```text
   G:\blog\claude_code_useage\project_paper\overleaf\ACM_computing_Surverys\paper_a_control_deployment\source_pdfs
   ```

8. Open each PDF and record method-section and experiment-section evidence in `reading_notes_red_yellow_batch1.md`.

## Five Target Articles and IEEE Arnumbers

| Key | DOI | IEEE arnumber | Direct CLI PDF attempt |
|---|---|---:|---|
| `hajihosseini2020dc` | `10.1109/TPEL.2020.2977765` | 9020169 | Failed with HTTP 418 |
| `meng2022novel` | `10.1109/TIE.2022.3170608` | 9767707 | Failed with HTTP 418 |
| `fathollahi2023robust` | `10.1109/TCSII.2023.3270751` | 10109206 | Failed with HTTP 418 |
| `gheisarnejad2022reducing` | `10.1109/TCSII.2022.3194271` | 9843888 | Failed with HTTP 418 |
| `khooban2022smartenance` | `10.1109/TCSII.2022.3206230` | 9888784 | Failed with HTTP 418 |
