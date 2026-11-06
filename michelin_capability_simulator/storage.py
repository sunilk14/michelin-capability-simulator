"""Google Sheets persistence in production; local CSV for offline testing."""
import csv
import os
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import streamlit as st
from model import CAPABILITIES, calculate_outcomes

HEADERS = ['timestamp_utc', 'section', 'group', 'round', *CAPABILITIES.keys(),
           'Ready capabilities', 'Predictive insight', 'Actionable service', 'Commercial readiness']
LOCAL_FILE = Path('local_submissions.csv')


def secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except (FileNotFoundError, OSError):
        return default


def use_google_sheets():
    return bool(secret('spreadsheet_id', '')) and secret('gcp_service_account') is not None


def worksheet():
    import gspread
    creds = dict(st.secrets['gcp_service_account'])
    client = gspread.service_account_from_dict(creds)
    sh = client.open_by_key(st.secrets['spreadsheet_id'])
    try:
        ws = sh.worksheet('Submissions')
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title='Submissions', rows=1000, cols=len(HEADERS))
    if ws.row_values(1) != HEADERS:
        if not ws.row_values(1):
            ws.update('A1', [HEADERS])
        else:
            raise ValueError('Existing Submissions tab has unexpected column headings.')
    return ws


def get_submissions():
    if use_google_sheets():
        records = worksheet().get_all_records()
        return pd.DataFrame(records, columns=HEADERS)
    if LOCAL_FILE.exists():
        return pd.read_csv(LOCAL_FILE, dtype={'group':str, 'section':str, 'round':str})
    return pd.DataFrame(columns=HEADERS)


def save_submission(section, group, round_name, allocation):
    existing = get_submissions()
    if not existing.empty:
        match = (existing['section'].astype(str).str.casefold() == section.casefold()) & \
                (existing['group'].astype(str).str.casefold() == group.casefold()) & \
                (existing['round'].astype(str).str.casefold() == round_name.casefold())
        if match.any():
            return False, 'This group has already submitted for the selected round. Ask the instructor to resolve duplicates.'
    metrics = calculate_outcomes(allocation)
    record = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'section': section, 'group': group, 'round': round_name,
        **allocation, **metrics,
    }
    if use_google_sheets():
        worksheet().append_row([record[h] for h in HEADERS], value_input_option='RAW')
    else:
        with LOCAL_FILE.open('a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(record)
    return True, 'Submission saved.'
