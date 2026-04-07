"""
gmail.py — Fetch and manage emails via Gmail API
"""

import base64
from googleapiclient.discovery import build
from auth import get_credentials


def get_service():
    """Build and return Gmail API service."""
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def fetch_unread_emails(count=50):
    """Fetch unread emails from inbox, one per thread. Returns list of email dicts."""
    service = get_service()

    # Fetch more than needed to account for thread deduplication
    result = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=count * 2
    ).execute()

    messages = result.get("messages", [])

    # Deduplicate: keep only the first (newest) message per thread
    seen_threads = set()
    unique_messages = []
    for msg in messages:
        tid = msg.get("threadId", msg["id"])
        if tid not in seen_threads:
            seen_threads.add(tid)
            unique_messages.append(msg)
        if len(unique_messages) >= count:
            break

    emails = []
    for msg in unique_messages:
        full = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = {h["name"]: h["value"]
                   for h in full["payload"]["headers"]}

        body = extract_body(full["payload"])
        if not body:
            body = full.get("snippet", "")

        emails.append({
            "id": msg["id"],
            "subject": headers.get("Subject", "(no subject)"),
            "from": headers.get("From", "unknown"),
            "date": headers.get("Date", ""),
            "body": body,
            "label_ids": full.get("labelIds", [])
        })

    return emails


def extract_body(payload):
    """Extract plain text body from email payload."""
    # Direct body
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(
            payload["body"]["data"]
        ).decode("utf-8", errors="ignore")

    # Multipart — look for text/plain part
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(
                    data
                ).decode("utf-8", errors="ignore")

    # Fallback: try first part recursively
    for part in payload.get("parts", []):
        result = extract_body(part)
        if result:
            return result

    return ""


def move_to_label(email_id, label_name):
    """Move email to a Gmail label (creates label if it doesn't exist)."""
    service = get_service()

    # Get or create label
    label_id = get_or_create_label(service, label_name)

    # Apply label and remove from inbox
    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={
            "addLabelIds": [label_id],
            "removeLabelIds": ["INBOX"]
        }
    ).execute()


def get_or_create_label(service, label_name):
    """Return label ID, creating the label if it doesn't exist."""
    # List existing labels
    labels = service.users().labels().list(userId="me").execute()
    for label in labels.get("labels", []):
        if label["name"].lower() == label_name.lower():
            return label["id"]

    # Create new label
    new_label = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }
    ).execute()
    return new_label["id"]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    # Quick test — print first 5 unread emails
    emails = fetch_unread_emails(count=5)
    print(f"Found {len(emails)} unread emails:\n")
    for e in emails:
        print(f"From: {e['from']}")
        print(f"Subject: {e['subject']}")
        print(f"Preview: {e['body'][:100].strip()}")
        print("---")
