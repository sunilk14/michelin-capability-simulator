# Michelin Connected-Tyre Capability Challenge

A ready-to-run **Streamlit classroom simulation**. Students allocate exactly 100 points among eight complementary capabilities; teachers compare submitted portfolios.

All budgets, thresholds and scores are **fictional classroom mechanics**; this is not an operational model of Michelin.

## Included
- `app.py` — student interface, running budget warning, outcome previews and faculty dashboard.
- `model.py` — capability definitions, validation, and transparent scoring.
- `storage.py` — optional Google Sheets storage; local CSV fallback for testing.
- `requirements.txt` — dependencies.
- `.streamlit/config.toml` — visual theme.
- `.streamlit/secrets.toml.example` — template, **not** a usable credential file.
- `tests/test_model.py` — validation tests.

## 1. Run locally (Windows PowerShell)

Open PowerShell inside this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The application opens in your web browser, usually at `http://localhost:8501`.

Without Google Sheets secrets it runs in **local demo mode** and writes `local_submissions.csv`. Do not use that storage mode for a cloud classroom session: a cloud instance can restart and its filesystem is not durable.

## 2. Configure durable Google Sheets storage (before deploying)

1. In Google Drive, create a new spreadsheet called `Michelin Classroom Responses`. Copy its **spreadsheet ID** from the URL between `/d/` and `/edit`.
2. In [Google Cloud Console](https://console.cloud.google.com/), create or select a project, and enable **Google Sheets API** and **Google Drive API**.
3. Under **IAM & Admin → Service Accounts**, create a service account, then under **Keys**, create a **JSON key**. Download the key file securely. Your institution may restrict key creation; follow your organisation's policies.
4. Share the spreadsheet with the service account's `client_email` (as **Editor**). **Do not** share the spreadsheet with students; they only need the Streamlit link.
5. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace placeholders. Copy field values from the JSON credential; TOML requires the private key string with literal `\n` escapes. Set a strong `faculty_password`.
6. Restart Streamlit. The first successful submission automatically creates a `Submissions` worksheet and headings if needed.

**Never upload the service-account JSON or `.streamlit/secrets.toml` to GitHub.** The provided `.gitignore` excludes secrets.toml. Check `git status` before pushing.

## 3. Deploy on Streamlit Community Cloud

1. Create a new GitHub repository (public is easiest) at [github.com](https://github.com/). **Upload contents of this folder**, preserving `app.py`, `requirements.txt`, `.streamlit/config.toml`, etc. The hidden `.streamlit` folder should also be included (not `secrets.toml`).
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) and connect GitHub.
3. Select **Create app**, choose the repository and branch (usually `main`), and set the main file path to `app.py`.
4. In **Advanced settings / Secrets**, paste your complete local `.streamlit/secrets.toml` content. Choose an app URL and deploy.
5. Open the hosted `https://...streamlit.app` link on a separate device. Make a test group submission, verify the corresponding row in the Google Sheet, then open the faculty dashboard using the password.
6. Share **only the app URL**, not the Google Sheet or faculty password, via LMS, email, or class QR code.

If you deploy first without credentials, the app enters **local demo mode** and submissions **will not reliably persist**. Configure secrets before live use.

## Suggested 25–30-minute classroom use

- 5 min — sell connected-tyre value proposition.
- 7 min — allocate points across capabilities, submit once per group.
- 5 min — discuss bottlenecks revealed in faculty dashboard.
- 5 min — announce fleet customer complaints: predictions do not lead to timely servicing.
- 5 min — discuss how outcome-based service contracts change which capabilities matter.

### How scoring works
Each slider is 0–50 points, in increments of 5. Full budget is 100 points. Readiness threshold is 15 per capability, deliberately impossible to meet across all eight simultaneously.

- `Predictive insight` = min(Data infrastructure, Analytics and AI, People and skills)
- `Actionable service` = min(Predictive insight, Customer IT integration, Service operations)
- `Commercial readiness` = min(Actionable service, Sales transformation, Partner ecosystem, Governance and incentives)

**These numbers are illustrative teaching scores, not a validated causal model.** Teachers may change the rules in `model.py`.

### Caveats
- Starter version supports **Round 1 only**. A later multi-round version could permit reinvestment, disruptions, and profit/loss scoring.
- Duplicate submissions for the same Section/Group/Round are rejected by checking existing records first. This is a classroom convenience, **not transaction-safe** against truly simultaneous submissions; use a database with uniqueness constraints for high-stakes use.
- The faculty dashboard has a shared-password gate; the app URL itself is public. Avoid entering real student personal data. Assign anonymous group IDs.
- Remote Google Sheets calls may occasionally fail; if so the app reports that the submission could not be confirmed. Check the sheet before retrying.
