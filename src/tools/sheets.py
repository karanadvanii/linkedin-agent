import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import settings
from rich import print as rprint

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        settings.GOOGLE_CREDENTIALS_PATH, SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1
    return sheet

def get_pending_topics():
    """Fetch all rows where Status is empty or 'pending'"""
    sheet = get_sheet()
    rows = sheet.get_all_records()
    pending = []
    for i, row in enumerate(rows, start=2):  # start=2 because row 1 is header
        status = str(row.get("Status", "")).strip().lower()
        if status in ("", "pending"):
            pending.append({
                "row_index": i,
                "topic": row.get("Topic", "").strip(),
                "target_accounts": row.get("Target Accounts", "").strip(),
            })
    rprint(f"[green]📋 Found {len(pending)} pending topics[/green]")
    return pending

def update_row_status(row_index: int, status: str):
    """Update the Status column for a given row"""
    sheet = get_sheet()
    # Status is column C = 3
    sheet.update_cell(row_index, 3, status)
    rprint(f"[blue]📝 Row {row_index} status → {status}[/blue]")

def save_draft(row_index: int, draft: str):
    """Save the generated draft into column D"""
    sheet = get_sheet()
    sheet.update_cell(row_index, 4, draft)
    rprint(f"[blue]💾 Draft saved to row {row_index}[/blue]")

def mark_posted(row_index: int, timestamp: str):
    """Mark as posted with timestamp in column E"""
    sheet = get_sheet()
    sheet.update_cell(row_index, 3, "posted")
    sheet.update_cell(row_index, 5, timestamp)
    rprint(f"[green]✅ Row {row_index} marked as posted at {timestamp}[/green]")

def add_suggested_topics(topics: list[str]):
    """Write AI-suggested topics into the sheet as pending rows"""
    sheet = get_sheet()
    rows_added = 0
    for topic in topics:
        sheet.append_row([topic, "", "pending", "", ""])
        rows_added += 1
    rprint(f"[green]✅ Added {rows_added} suggested topics to Google Sheets[/green]")