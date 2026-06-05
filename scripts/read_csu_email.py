#!/usr/bin/env python3
"""Read CSU/Coremail inbox messages via IMAP in read-only mode.

Safety guarantees:
- Does not send emails.
- Opens the mailbox with readonly=True.
- Uses BODY.PEEK[] so fetched messages are not marked as read.
- Does not delete, move, expunge, append, or modify messages.

By default this script reuses SENDER_EMAIL and CLIENT_PASSWORD from
scripts/send_csu_email.py. You can override values with environment variables:
EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_SERVER, IMAP_PORT.
"""

import argparse
import html
import imaplib
import importlib.util
import os
import re
import sys
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_SCRIPT = os.path.join(SCRIPT_DIR, "send_csu_email.py")
DEFAULT_IMAP_SERVER = "mail.csu.edu.cn"
DEFAULT_IMAP_PORT = 993
PLACEHOLDER_VALUES = {
    "",
    "your_student_id@csu.edu.cn",
    "your_email@example.com",
    "YOUR_ALTERNATIVE_PASSWORD",
    "your_password",
}


def load_send_config(config_script):
    if not os.path.isfile(config_script):
        return None
    spec = importlib.util.spec_from_file_location("send_csu_email_config", config_script)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def choose_value(*values):
    for value in values:
        if value is None:
            continue
        value = str(value).strip()
        if value and value not in PLACEHOLDER_VALUES:
            return value
    return ""


def load_connection_settings(config_script):
    mod = load_send_config(config_script)
    email_addr = choose_value(
        os.environ.get("EMAIL_ADDRESS"),
        getattr(mod, "SENDER_EMAIL", "") if mod else "",
    )
    password = choose_value(
        os.environ.get("EMAIL_PASSWORD"),
        getattr(mod, "CLIENT_PASSWORD", "") if mod else "",
    )
    imap_server = choose_value(
        os.environ.get("IMAP_SERVER"),
        getattr(mod, "IMAP_SERVER", "") if mod else "",
        DEFAULT_IMAP_SERVER,
    )
    imap_port = int(choose_value(
        os.environ.get("IMAP_PORT"),
        getattr(mod, "IMAP_PORT", "") if mod else "",
        DEFAULT_IMAP_PORT,
    ))

    if not email_addr or not password:
        raise RuntimeError(
            "Missing mailbox credentials. Configure scripts/send_csu_email.py "
            "or set EMAIL_ADDRESS and EMAIL_PASSWORD."
        )
    return email_addr, password, imap_server, imap_port


def clean_text(text, limit):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    if len(text) > limit:
        return text[:limit].rstrip() + f"\n...[正文截断，仅显示前 {limit} 字符]"
    return text


def html_to_text(content):
    content = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", content)
    content = re.sub(r"(?i)<br\s*/?>", "\n", content)
    content = re.sub(r"(?i)</p\s*>", "\n", content)
    content = re.sub(r"<[^>]+>", " ", content)
    return html.unescape(content)


def get_part_content(part):
    try:
        content = part.get_content()
        return content if isinstance(content, str) else str(content)
    except Exception:
        payload = part.get_payload(decode=True) or b""
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")


def extract_body(message, body_limit):
    plain_parts = []
    html_parts = []

    if message.is_multipart():
        parts = message.walk()
    else:
        parts = [message]

    for part in parts:
        if part.is_multipart():
            continue
        filename = part.get_filename()
        disposition = (part.get_content_disposition() or "").lower()
        if filename or disposition == "attachment":
            continue

        content_type = part.get_content_type()
        content = get_part_content(part)
        if content_type == "text/plain":
            plain_parts.append(content)
        elif content_type == "text/html":
            html_parts.append(html_to_text(content))

    body = "\n\n".join(part for part in plain_parts if part.strip())
    if not body.strip():
        body = "\n\n".join(part for part in html_parts if part.strip())
    if not body.strip():
        return "[无可提取的文本正文，可能是纯附件或加密邮件]"
    return clean_text(body, body_limit)


def attachment_names(message):
    if not message.is_multipart():
        return []
    names = []
    for part in message.walk():
        filename = part.get_filename()
        if filename:
            names.append(filename)
    return names


def format_date(value):
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).isoformat(sep=" ")
    except Exception:
        return str(value)


def fetch_raw_message(imap, message_id):
    status, fetched = imap.fetch(message_id, "(BODY.PEEK[])")
    if status != "OK":
        raise RuntimeError(f"Cannot fetch message {message_id!r}")
    for item in fetched:
        if isinstance(item, tuple):
            return item[1]
    raise RuntimeError(f"Message {message_id!r} has no fetchable body")


def print_message(index, message, body_limit, summary_only):
    attachments = attachment_names(message)
    print(f"#{index}")
    print(f"From: {message.get('From', '')}")
    print(f"To: {message.get('To', '')}")
    print(f"Date: {format_date(message.get('Date', ''))}")
    print(f"Subject: {message.get('Subject', '')}")
    if attachments:
        print("Attachments: " + ", ".join(attachments))
    if not summary_only:
        print("Body:")
        print(extract_body(message, body_limit))
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Read latest CSU/Coremail inbox messages via IMAP in read-only mode."
    )
    parser.add_argument("-n", "--limit", type=int, default=5, help="number of latest messages to read")
    parser.add_argument("--mailbox", default="INBOX", help="mailbox/folder name, default: INBOX")
    parser.add_argument("--unread", action="store_true", help="read latest unread messages only")
    parser.add_argument("--summary-only", action="store_true", help="print headers only, without message body")
    parser.add_argument("--body-limit", type=int, default=4000, help="max body characters per message")
    parser.add_argument(
        "--config-script",
        default=DEFAULT_CONFIG_SCRIPT,
        help="Python config script containing SENDER_EMAIL and CLIENT_PASSWORD",
    )
    args = parser.parse_args()

    if args.limit < 1:
        raise RuntimeError("--limit must be >= 1")
    if args.body_limit < 1:
        raise RuntimeError("--body-limit must be >= 1")

    email_addr, password, imap_server, imap_port = load_connection_settings(args.config_script)

    with imaplib.IMAP4_SSL(imap_server, imap_port) as imap:
        imap.login(email_addr, password)
        status, _ = imap.select(args.mailbox, readonly=True)
        if status != "OK":
            raise RuntimeError(f"Cannot select mailbox: {args.mailbox}")

        search_query = "UNSEEN" if args.unread else "ALL"
        status, data = imap.search(None, search_query)
        if status != "OK":
            raise RuntimeError("Cannot search mailbox")

        message_ids = data[0].split()
        latest_ids = message_ids[-args.limit:]

        print(f"账号: {email_addr}")
        print(f"服务器: {imap_server}:{imap_port}")
        print(f"邮箱目录: {args.mailbox}")
        print(f"读取范围: 最新 {len(latest_ids)} 封{'未读' if args.unread else ''}邮件")
        print("模式: 只读；BODY.PEEK[]；不标记已读；不发送、不删除、不移动邮件")
        print("=" * 80)

        if not latest_ids:
            print("没有匹配的邮件。")
            return

        for index, message_id in enumerate(reversed(latest_ids), 1):
            raw_message = fetch_raw_message(imap, message_id)
            message = BytesParser(policy=policy.default).parsebytes(raw_message)
            print_message(index, message, args.body_limit, args.summary_only)

        imap.close()
        imap.logout()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
