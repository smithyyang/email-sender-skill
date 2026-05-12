# Email Sender Skill

English | [中文](README.md)

> 🎯 A skill that lets AI Agents send emails with one command, fully compatible with the Coremail campus/enterprise email system.

## ✨ Features

- ✅ **SMTP Email Sending** (SSL encrypted)
- ✅ **Command Line Arguments**: specify recipient, subject, and body
- ✅ **Multi-attachment Support**: auto-detects MIME types for PDFs, images, Office documents, etc.
- ✅ **BCC (Blind Carbon Copy)**: automatically BCCs a copy to your own inbox for easy record tracking in the web client; the primary recipient cannot see the BCC
- ✅ **Coremail Compatible**: supports campus/enterprise mailboxes with Two-Factor Authentication (2FA) using an Alternative Password

## 📁 Repository Structure

```
email-sender/
├── SKILL.md                       # Skill metadata and detailed documentation
├── README.md                      # Chinese version
├── README.en.md                   # English version (this file)
├── LICENSE.txt
└── scripts/
    └── send_csu_email.py          # Ready-to-run email script
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
> If your mailbox has Two-Factor Authentication (2FA) enabled, you need to generate a "Client/Alternative Password" in the webmail settings for SMTP login.  
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

# With attachments (auto-detects MIME types for PDF, images, Office, etc.)
python scripts/send_csu_email.py \
  --target team@example.com \
  --attach report.pdf photo.jpg data.xlsx
```

You can also use short arguments:

```bash
python scripts/send_csu_email.py -t boss@company.com -s "Weekly Report" -b "Please review." -a report.pdf
```

## 🛠️ Installing for Other Agents / CLI

### OpenCode Agent

Clone this repository into the skills directory:

```bash
# Clone into the OpenCode skills directory
git clone https://github.com/smithyyang/email-sender-skill.git \
  ~/.config/opencode/skills/email-sender
```

After that, when any of the following keywords appear in a conversation, OpenCode will automatically load this skill:

> "send email", "发邮件", "SMTP", "邮箱发送"

### Claude Code

```bash
# Clone into the Claude Code skills directory
git clone https://github.com/smithyyang/email-sender-skill.git \
  ~/.claude/skills/email-sender
```

After that, when any of the following keywords appear in a conversation, Claude Code will automatically load this skill:

> "send email", "发邮件", "SMTP", "邮箱发送"

### CLI / Shell Script

This repository includes a ready-to-run Python script that can be used independently without any AI Agent:

```bash
python scripts/send_csu_email.py --help
```

## 📚 Common SMTP Configurations

| Email Provider | SMTP Server        | Port | Password Note                  |
|----------------|--------------------|------|--------------------------------|
| CSU (中南大学) | `mail.csu.edu.cn`  | 465  | Alternative Password (with 2FA)|
| Gmail          | `smtp.gmail.com`   | 587  | App Password                   |
| Outlook        | `smtp.office365.com`| 587 | App Password                   |
| QQ Mail        | `smtp.qq.com`      | 465  | Authorization Code (not QQ pwd)|
| 163 Mail       | `smtp.163.com`     | 465  | Authorization Code             |

## 🤝 Contributing

Pull Requests and Issues are welcome! For example:
- Support for more mailbox providers with ready-to-use scripts
- Add HTML email templates
- Add `--config` multi-mailbox configuration file support

## 📄 License

MIT License — see [LICENSE.txt](LICENSE.txt)
