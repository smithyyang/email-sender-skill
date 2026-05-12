# Email Sender Skill for OpenCode

> 🎯 让 AI Agent 一键发送邮件的 skill，完美兼容 Coremail 校园/企业邮箱系统。

## ✨ 功能

- ✅ **SMTP 邮件发送**（SSL 加密）
- ✅ **命令行参数**：指定收件人、主题、正文
- ✅ **多附件支持**：自动识别 PDF、图片、Office 文档等 MIME 类型
- ✅ **BCC 密送**：自动抄送一份到自己收件箱，方便网页端查看记录
- ✅ **Coremail 兼容**：支持开启了二次验证（2FA）的校园/企业邮箱，使用备用密码

## 📁 仓库结构

```
email-sender/
├── SKILL.md                       # Skill 元数据与详细文档
├── README.md                      # 本文件
├── LICENSE.txt
└── scripts/
    └── send_csu_email.py          # 现成可运行的邮件脚本
```

## ⚡ 快速开始

### 1. 配置脚本

编辑 `scripts/send_csu_email.py`，填入你自己的邮箱信息：

```python
# ============== 配置区域 ==============
SENDER_EMAIL = "your_id@edu.cn"               # 你的邮箱地址
CLIENT_PASSWORD = "YOUR_ALTERNATIVE_PASSWORD" # 客户端备用密码
SMTP_SERVER = "mail.edu.cn"                   # 你学校的 SMTP 服务器
SMTP_PORT = 465                               # SSL 端口
# =======================================
```

> **关于备用密码（Alternative Password）**  
> 如果你的邮箱开启了二次验证（2FA），需要在网页邮箱里生成“客户端专用密码”用于 SMTP 登录。  
> 路径通常为：邮箱设置 → Two-Factor Authentication → Configure Alternative Password。

### 2. 发送邮件

```bash
# 基础发送
python scripts/send_csu_email.py

# 指定收件人
python scripts/send_csu_email.py --target recipient@example.com

# 完整自定义
python scripts/send_csu_email.py \
  --target boss@company.com \
  --subject "周报" \
  --body "请查收本周工作报告。"

# 带附件（自动识别 PDF、图片、Office 等 MIME 类型）
python scripts/send_csu_email.py \
  --target team@example.com \
  --attach report.pdf photo.jpg data.xlsx
```

也可以使用短参数：

```bash
python scripts/send_csu_email.py -t boss@company.com -s "周报" -b "请查收" -a report.pdf
```

## 🛠️ 安装到其他 Agent / CLI

### OpenCode Agent

将本仓库克隆到 skills 目录即可：

```bash
# 克隆到 OpenCode skills 目录
git clone https://github.com/smithyyang/email-sender-skill.git \
  ~/.config/opencode/skills/email-sender
```

之后，当对话中出现以下关键词时，OpenCode 会自动加载此 skill：

> "send email", "发邮件", "SMTP", "邮箱发送"

### 通用 AI Agent（如 Claude Code、Cursor 等）

把 `SKILL.md` 的内容复制到项目根目录的 `AGENTS.md`（或 agent 的 system prompt）中，AI 就会遵循其中的工作流程和代码规范来发送邮件。

### CLI / Shell 脚本

此仓库自带可直接运行的 Python 脚本，无需 AI Agent 也可独立使用：

```bash
python scripts/send_csu_email.py --help
```

## 📚 常见 SMTP 配置参考

| 邮箱类型 | SMTP 服务器 | 端口 | 密码说明 |
|---------|------------|------|---------|
| 中南大学 | `mail.csu.edu.cn` | 465 | 备用密码（2FA 开启时） |
| Gmail | `smtp.gmail.com` | 587 | App Password |
| Outlook | `smtp.office365.com` | 587 | App Password |
| QQ 邮箱 | `smtp.qq.com` | 465 | 授权码（非 QQ 密码） |
| 163 | `smtp.163.com` | 465 | 授权码 |

## 🤝 贡献

欢迎 PR 和 Issue！例如：
- 支持更多邮箱的现成脚本
- 添加 HTML 邮件模板
- 添加 `--config` 多邮箱配置文件支持

## 📄 License

MIT License - 详见 [LICENSE.txt](LICENSE.txt)
