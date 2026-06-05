---
name: email
description: Use this skill whenever the user wants to send emails via SMTP or read received mailbox messages via IMAP. Includes sending test emails, automated notifications, reports/attachments, configuring school/corporate mail clients, and checking latest/unread inbox emails. Trigger on "send email", "发邮件", "SMTP", "邮箱发送", "read email", "读邮箱", "查看邮件", "收件箱", or "IMAP". Supports Gmail, Outlook, QQ, 163, and Coremail systems such as 中南大学 using app/alternative passwords.
license: Proprietary. LICENSE.txt has complete terms
---

# Email Skill Guide

## Overview

This skill enables programmatic email operations in Python:

- **Send emails** via SMTP, including attachments and BCC-to-self record keeping.
- **Read received emails** via IMAP in read-only mode, including latest/unread inbox messages.

It supports common authentication scenarios: standard passwords, app-specific passwords, and Coremail alternative passwords for accounts with two-factor authentication (2FA).

## Safety Rules

### Reading email

- Only read mailbox content when the user explicitly asks to read/check emails or otherwise grants permission.
- Use `scripts/read_csu_email.py` for received mail. It is designed to be **read-only**:
  - opens the mailbox with `readonly=True`;
  - uses `BODY.PEEK[]` so messages are not marked as read;
  - does not send, delete, move, append, expunge, or modify messages.
- When the user asks to read emails, do **not** send any email unless the user separately and explicitly asks for sending.

### Sending email

- Only send an email when the user explicitly asks to send one.
- Confirm or infer the recipient, subject, body, and attachments from the user's request before sending.
- Do not commit real mailbox credentials to public repositories. Keep credentials only in the user's private local configuration or environment variables.

## Ready-to-Use Scripts

This skill includes pre-configured scripts in the `scripts/` directory.

### `scripts/send_csu_email.py`

A command-line email sender for SMTP/Coremail systems. The public repository contains placeholders; a user's private installed copy may already have real credentials configured.

**Basic usage:**
```bash
python scripts/send_csu_email.py
```

**Specify recipient:**
```bash
python scripts/send_csu_email.py --target recipient@example.com
python scripts/send_csu_email.py -t recipient@example.com
```

**Full customization:**
```bash
python scripts/send_csu_email.py \
  --target someone@qq.com \
  --subject "Meeting Reminder" \
  --body "The meeting starts at 3 PM tomorrow."
```

**With attachments:**
```bash
# Single attachment
python scripts/send_csu_email.py -t someone@qq.com -a report.pdf

# Multiple attachments
python scripts/send_csu_email.py -t someone@qq.com -a file1.docx file2.xlsx photo.jpg
```

### `scripts/read_csu_email.py`

A command-line inbox reader for CSU/Coremail IMAP. It reuses `SENDER_EMAIL` and `CLIENT_PASSWORD` from `scripts/send_csu_email.py` by default, or reads credentials from environment variables.

**Read latest received emails:**
```bash
python scripts/read_csu_email.py -n 5
```

**Read latest unread emails only:**
```bash
python scripts/read_csu_email.py --unread -n 10
```

**Read headers only, without body content:**
```bash
python scripts/read_csu_email.py --summary-only -n 10
```

**Override credentials/server with environment variables:**
```bash
EMAIL_ADDRESS="your_id@csu.edu.cn" \
EMAIL_PASSWORD="YOUR_ALTERNATIVE_PASSWORD" \
IMAP_SERVER="mail.csu.edu.cn" \
IMAP_PORT="993" \
python scripts/read_csu_email.py -n 5
```

**What it prints:**
- account and IMAP server;
- mailbox folder and read-only mode notice;
- for each message: From, To, Date, Subject, attachment names, and body text unless `--summary-only` is used.

**Default CSU/Coremail read settings:**
- IMAP Server: `mail.csu.edu.cn`
- IMAP Port: `993` SSL
- Mailbox: `INBOX`
- Authentication: same client/alternative password used for SMTP/IMAP

## Quick Start: Basic Email Sending

```python
import smtplib
import ssl
from email.mime.text import MIMEText
from email.header import Header

# Configuration
SMTP_SERVER = "mail.example.com"      # Your SMTP server
SMTP_PORT = 465                        # SSL port, usually 465 or 587
SENDER_EMAIL = "your_email@example.com"
SENDER_PASSWORD = "your_password"      # See authentication section below
RECEIVER_EMAIL = "recipient@example.com"

# Create message
msg = MIMEText("Hello, this is a test email.", "plain", "utf-8")
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg["Subject"] = Header("Test Email", "utf-8")

# Send
context = ssl.create_default_context()
with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=10) as server:
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
print("Email sent successfully!")
```

## Quick Start: Basic Read-Only IMAP Reading

```python
import imaplib
from email import policy
from email.parser import BytesParser

IMAP_SERVER = "mail.example.com"
IMAP_PORT = 993
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_password"

with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as imap:
    imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    imap.select("INBOX", readonly=True)
    status, data = imap.search(None, "ALL")
    latest_id = data[0].split()[-1]
    status, fetched = imap.fetch(latest_id, "(BODY.PEEK[])")
    raw = next(item[1] for item in fetched if isinstance(item, tuple))
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    print(msg["From"], msg["Subject"])
    imap.close()
    imap.logout()
```

## Authentication Guide

### Standard Password

Some servers use the same password as web login:
- Personal mailboxes on basic hosting
- Some corporate mail servers

```python
SENDER_PASSWORD = "your_regular_password"
```

### App-Specific Password

For accounts with 2FA enabled, generate an app-specific password:

**Gmail:** Google Account → Security → 2-Step Verification → App passwords

**Outlook/Hotmail:** Account settings → Security → Advanced security options → Create app password

```python
SENDER_PASSWORD = "xxxx xxxx xxxx xxxx"
```

### Alternative Password for Coremail School/Corporate Systems

For Coremail-based systems such as 中南大学:

1. Log into webmail, for example `https://mail.csu.edu.cn`.
2. Go to Settings → Two-Factor Authentication.
3. Find **Configure Alternative Password**.
4. Generate an alternative/client password.
5. Use this password for SMTP and IMAP.

```python
SENDER_PASSWORD = "AlternativePasswordHere"  # Not the CAS/web login password
```

## Common SMTP and IMAP Configurations

| Provider | SMTP Server | SMTP Port | IMAP Server | IMAP Port | Notes |
|----------|-------------|-----------|-------------|-----------|-------|
| Gmail | `smtp.gmail.com` | 587 STARTTLS | `imap.gmail.com` | 993 SSL | Use app-specific password with 2FA |
| Outlook/Hotmail | `smtp.office365.com` | 587 STARTTLS | `outlook.office365.com` | 993 SSL | Use app-specific password/OAuth depending on account policy |
| QQ Mail | `smtp.qq.com` | 465/587 | `imap.qq.com` | 993 SSL | Use authorization code, not QQ password |
| 163 Mail | `smtp.163.com` | 465 | `imap.163.com` | 993 SSL | Use authorization code |
| 中南大学 (CSU) | `mail.csu.edu.cn` | 465 SSL | `mail.csu.edu.cn` | 993 SSL | Use Coremail alternative password with 2FA |
| Generic Coremail | `mail.domain.com` | 465 SSL | `mail.domain.com` | 993 SSL | Check if alternative password is required |

## Troubleshooting

### Authentication failed

- Wrong password type: using web/CAS password instead of app/alternative password.
- Account has 2FA but no client password was generated.
- Username format is wrong; try the full email address.

### Connection timeout

- Firewall blocks port 465/587/993.
- School mail may require campus network or VPN.
- Server address or encryption mode is wrong.

### Reading marks messages as read

Use `scripts/read_csu_email.py`; it fetches with `BODY.PEEK[]` and opens the mailbox as read-only. Avoid raw `BODY[]` fetches if you do not want to set the Seen flag.

### Email sent but recipient did not receive it

- Check spam/junk folder.
- Sender domain reputation or SPF/DKIM/DMARC may affect delivery.
- Attachment may be too large.

## Important Limitations

- Sent emails cannot be modified after sending.
- SMTP sends usually do not appear in webmail "Sent" unless BCC-to-self or IMAP-save is used.
- Reading via IMAP depends on server support and access permissions.
- Rate limits apply for sending; mail providers may limit messages per hour/day.
