# Email Skill

English | [中文](README.md)

> 🎯 A skill that lets AI Agents send emails and read inbox messages in read-only mode, compatible with Coremail campus/enterprise email systems.

## ✨ Features

- ✅ **SMTP Email Sending** with SSL encryption
- ✅ **IMAP Read-Only Inbox Reading**: read latest/unread messages using `BODY.PEEK[]`; does not mark messages as read, send, delete, or move mail
- ✅ **Command Line Arguments**: specify recipient, subject, body, attachments, read limit, unread-only mode, etc.
- ✅ **Multi-attachment Support**: auto-detects MIME types for PDFs, images, Office documents, etc.
- ✅ **BCC (Blind Carbon Copy)**: automatically BCCs a copy to your own inbox for easy record tracking in the web client
- ✅ **Coremail Compatible**: supports campus/enterprise mailboxes with Two-Factor Authentication (2FA) using an Alternative Password

## 📁 Repository Structure

```
email/
├── SKILL.md                       # Skill metadata and detailed documentation
├── README.md                      # Chinese version
├── README.en.md                   # English version (this file)
├── LICENSE.txt
└── scripts/
    ├── send_csu_email.py          # Ready-to-run email sender
    └── read_csu_email.py          # Read-only inbox reader
```

## ⚡ Quick Start

### 1. Configure the Script

Edit `scripts/send_csu_email.py` and fill in your own email information:

```python
# ============== Config Area ==============
SENDER_EMAIL = "your_id@edu.cn"               # Your email address
CLIENT_PASSWORD = "YOUR_ALTERNATIVE_PASSWORD" # Client / Alternative Password
SMTP_SERVER = "mail.edu.cn"                   # Your school's SMTP server
SMTP_PORT = 465                               # SSL port
# =========================================
```

> **About the Alternative Password**
> If your mailbox has Two-Factor Authentication (2FA) enabled, generate a client/alternative password in the webmail settings for SMTP/IMAP login.
> The usual path is: Mailbox Settings → Two-Factor Authentication → Configure Alternative Password.

### 2. Send Emails

```bash
# Basic send
python scripts/send_csu_email.py

# Specify recipient
python scripts/send_csu_email.py --target recipient@example.com

# Full customization
python scripts/send_csu_email.py \
  --target boss@company.com \
  --subject "Weekly Report" \
  --body "Please find this week's work report attached."

# With attachments
python scripts/send_csu_email.py \
  --target team@example.com \
  --attach report.pdf photo.jpg data.xlsx
```

You can also use short arguments:

```bash
python scripts/send_csu_email.py -t boss@company.com -s "Weekly Report" -b "Please review." -a report.pdf
```

### 3. Read Inbox Messages in Read-Only Mode

`read_csu_email.py` reuses `SENDER_EMAIL` and `CLIENT_PASSWORD` from `send_csu_email.py` by default. Environment variables can override them.

```bash
# Read the latest 5 email bodies
python scripts/read_csu_email.py -n 5

# Read unread messages only
python scripts/read_csu_email.py --unread -n 10

# Show headers only, without body content
python scripts/read_csu_email.py --summary-only -n 10
```

The script uses IMAP read-only mode and `BODY.PEEK[]`; it does not send, delete, move, or mark messages as read.

## 🛠️ Installing for Other Agents / CLI

### OpenCode Agent

Clone this repository into the skills directory:

```bash
git clone https://github.com/smithyyang/email-skill.git \
  ~/.config/opencode/skills/email
```

After that, when any of the following keywords appear in a conversation, OpenCode will automatically load this skill:

> "send email", "发邮件", "SMTP", "邮箱发送", "read email", "读邮箱", "查看邮件", "收件箱", "IMAP"

### Claude Code

```bash
git clone https://github.com/smithyyang/email-skill.git \
  ~/.claude/skills/email
```

After that, Claude Code can load this skill when the same keywords appear.

### CLI / Shell Script

This repository includes ready-to-run Python scripts that can be used independently without any AI Agent:

```bash
python scripts/send_csu_email.py --help
python scripts/read_csu_email.py --help
```

## 📚 Common SMTP / IMAP Configurations

| Email Provider | SMTP Server | SMTP Port | IMAP Server | IMAP Port | Password Note |
|----------------|-------------|-----------|-------------|-----------|---------------|
| CSU (中南大学) | `mail.csu.edu.cn` | 465 | `mail.csu.edu.cn` | 993 | Alternative Password with 2FA |
| Gmail | `smtp.gmail.com` | 587 | `imap.gmail.com` | 993 | App Password |
| Outlook | `smtp.office365.com` | 587 | `outlook.office365.com` | 993 | App Password / OAuth |
| QQ Mail | `smtp.qq.com` | 465 | `imap.qq.com` | 993 | Authorization Code, not QQ password |
| 163 Mail | `smtp.163.com` | 465 | `imap.163.com` | 993 | Authorization Code |

## 🤝 Contributing

Pull Requests and Issues are welcome! For example:
- Support for more mailbox providers with ready-to-use scripts
- Add HTML email templates
- Add `--config` multi-mailbox configuration file support

## 📄 License

MIT License — see [LICENSE.txt](LICENSE.txt)
