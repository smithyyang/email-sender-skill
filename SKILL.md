---
name: email-sender
description: Use this skill whenever the user wants to send emails programmatically via SMTP. This includes sending test emails, sending automated notifications, sending reports or attachments via email, or configuring email clients for school/corporate/enterprise mail servers. Trigger when the user mentions "send email", "发邮件", "SMTP", "邮箱发送", or asks to configure email sending with Python. This skill covers common email servers (Gmail, Outlook, QQ, 163, school mail systems like Coremail) and handles authentication details including regular passwords, app-specific passwords, and alternative passwords for 2FA-enabled accounts.
license: Proprietary. LICENSE.txt has complete terms
---

# Email Sender Skill Guide

## Overview

This skill enables programmatic email sending via SMTP using Python. It handles various authentication scenarios including standard passwords, app-specific passwords, and alternative passwords for accounts with two-factor authentication (2FA).

## Ready-to-Use Scripts

This skill includes pre-configured scripts in the `scripts/` directory:

### `scripts/send_csu_email.py`
A fully configured command-line email sender for **中南大学 (CSU) mail system**. Already authenticated with saved credentials.

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

**Or use short flags:**
```bash
python scripts/send_csu_email.py -t someone@qq.com -s "Meeting" -b "See you there!"
```

**With attachments:**
```bash
# Single attachment
python scripts/send_csu_email.py -t someone@qq.com -a report.pdf

# Multiple attachments
python scripts/send_csu_email.py -t someone@qq.com -a file1.docx file2.xlsx photo.jpg
```

**Pre-configured settings (saved in script):**
- Sender: `8208230611@csu.edu.cn`
- SMTP Server: `mail.csu.edu.cn:465` (SSL)
- Uses alternative password for 2FA
- Auto-BCC to sender for record keeping

## Quick Start

### Basic Email Sending

```python
import smtplib
import ssl
from email.mime.text import MIMEText
from email.header import Header

# Configuration
SMTP_SERVER = "mail.example.com"      # Your SMTP server
SMTP_PORT = 465                        # SSL port (usually 465 or 587)
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

## Authentication Guide

### Standard Password (Simple Mail Servers)

Some servers use the same password as web login:
- Personal mailboxes on basic hosting
- Some corporate mail servers

```python
SENDER_PASSWORD = "your_regular_password"
```

### App-Specific Password (Gmail, Outlook, Yahoo)

For accounts with 2FA enabled, generate an app-specific password:

**Gmail:**
1. Google Account → Security → 2-Step Verification → App passwords
2. Generate password for "Mail"
3. Use the 16-character password

**Outlook/Hotmail:**
1. Account settings → Security → Advanced security options
2. Create app password

```python
SENDER_PASSWORD = "xxxx xxxx xxxx xxxx"  # App-specific password
```

### Alternative Password (Coremail School/Corporate Systems)

For Coremail-based systems (中南大学, many Chinese universities, some enterprises):

**When account has Two-Factor Authentication (2FA) enabled:**

1. Log into webmail (e.g., https://mail.csu.edu.cn)
2. Go to **Settings** → **Two-Factor Authentication**
3. Find **[Configure Alternative Password]** link
4. Generate an alternative password (usually 16 characters)
5. Use this password for SMTP/IMAP

```python
SENDER_PASSWORD = "AlternativePasswordHere"  # Not the CAS/web login password
```

## Common SMTP Configurations

| Provider | SMTP Server | Port | Encryption | Notes |
|----------|-------------|------|------------|-------|
| Gmail | smtp.gmail.com | 587 | STARTTLS | Use app-specific password with 2FA |
| Outlook/Hotmail | smtp.office365.com | 587 | STARTTLS | Use app-specific password with 2FA |
| QQ Mail | smtp.qq.com | 465/587 | SSL/TLS | Use authorization code, not QQ password |
| 163 Mail | smtp.163.com | 465/994 | SSL | Use authorization code |
| 中南大学 (CSU) | mail.csu.edu.cn | 465/25 | SSL | Use alternative password with 2FA |
| Generic Coremail | mail.domain.com | 465 | SSL | Check if alternative password needed |

## Advanced Examples

### Sending HTML Email

```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

msg = MIMEMultipart("alternative")
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg["Subject"] = "HTML Email"

# Plain text version
text_part = MIMEText("Plain text content", "plain", "utf-8")

# HTML version
html_content = """
<html>
<body>
    <h1>Hello</h1>
    <p>This is an <b>HTML</b> email.</p>
</body>
</html>
"""
html_part = MIMEText(html_content, "html", "utf-8")

msg.attach(text_part)
msg.attach(html_part)
```

### Sending with Attachment

```python
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

msg = MIMEMultipart()
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg["Subject"] = "Email with Attachment"

# Attach file
filename = "document.pdf"
filepath = "/path/to/document.pdf"

with open(filepath, "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

encoders.encode_base64(part)
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {os.path.basename(filename)}",
)
msg.attach(part)
```

### BCC to Self (Keep Record in Webmail)

SMTP clients don't automatically save to "Sent" folder. BCC yourself:

```python
msg["Bcc"] = SENDER_EMAIL  # Blind carbon copy to yourself
server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL, SENDER_EMAIL], msg.as_string())
```

### STARTTLS (Port 587)

For servers using STARTTLS instead of SSL:

```python
server = smtplib.SMTP(SMTP_SERVER, 587, timeout=10)
server.starttls(context=context)
server.login(SENDER_EMAIL, SENDER_PASSWORD)
server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
server.quit()
```

## Security Best Practices

- **Never hardcode passwords** in scripts that will be committed to version control
- **Use environment variables** for credentials:
  ```python
  import os
  SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD")
  ```
- **Alternative/app passwords** are safer than main passwords for automation
- **Delete scripts** containing passwords after use
- **Regenerate passwords** if accidentally exposed

## Troubleshooting

### "Authentication failed" (535 Error)
- Wrong password type (using web login instead of app/alternative password)
- Account has 2FA but using regular password
- Username format incorrect (try with/without @domain)

### Connection timeout
- Firewall blocking port 25/465/587
- Not on campus network (school mail may require VPN)
- Wrong server address

### SMTP server not responding
- Verify SMTP server address with your email provider
- Some providers require enabling SMTP/IMAP in settings first

### Email sent but recipient didn't receive
- Check recipient's spam/junk folder
- Sender domain may have poor reputation
- Attachment too large

## Important Limitations

- **Sent emails cannot be modified** after sending (same as physical mail)
- **"Recall" rarely works** across different mail systems
- **SMTP sends don't appear in webmail "Sent" folder** unless BCC'd or IMAP-save is used
- **Rate limits** apply: most providers limit emails per hour/day

## School/Corporate Mail Specific Notes

For Coremail-based systems (common in Chinese universities):
- Username is usually full email: `student_id@school.edu.cn`
- Password is NOT the CAS/unified authentication password
- If 2FA enabled, must use **Alternative Password** configured in webmail settings
- May require campus network or VPN for SMTP access
- Check https://mail.school.edu.cn/coremail/help/ for official client settings
