#!/usr/bin/env python3
"""
邮件发送脚本 (Email Sender)
支持命令行参数 --target, --subject, --body, --attach
用法示例：
  python send_csu_email.py --target recipient@example.com
  python send_csu_email.py -t recipient@example.com -s "会议通知" -b "周五下午3点开会"
  python send_csu_email.py -t recipient@example.com -a resume.pdf photo.jpg
"""

import argparse
import mimetypes
import os
import smtplib
import ssl
import sys
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

# ============== 配置区域（填入你自己的邮箱信息） ==============
SENDER_EMAIL = "your_student_id@csu.edu.cn"     # 发件人：邮箱地址
CLIENT_PASSWORD = "YOUR_ALTERNATIVE_PASSWORD"    # 客户端备用密码（非CAS密码）
SMTP_SERVER = "mail.csu.edu.cn"                  # SMTP服务器（中南大学示例）
SMTP_PORT = 465                                  # SSL端口
DEFAULT_RECEIVER = "recipient@example.com"       # 默认收件人
# ==============================================================


def send_email(receiver, subject, body, attachments=None):
    """发送邮件的核心函数。"""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver
    msg["Subject"] = Header(subject, "utf-8")
    msg["Bcc"] = SENDER_EMAIL  # 密送给自己，方便在网页邮箱中查找记录

    # 添加正文
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # 添加附件
    if attachments:
        for filepath in attachments:
            if not os.path.isfile(filepath):
                print(f"⚠️  跳过不存在的附件: {filepath}")
                continue

            filename = os.path.basename(filepath)

            # 根据文件扩展名自动识别 MIME 类型
            mimetype, _ = mimetypes.guess_type(filepath)
            if mimetype:
                maintype, subtype = mimetype.split("/", 1)
            else:
                maintype, subtype = "application", "octet-stream"

            with open(filepath, "rb") as f:
                part = MIMEBase(maintype, subtype)
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{filename}"',
            )
            msg.attach(part)
            print(f"📎 已附加文件: {filename} ({maintype}/{subtype})")

    try:
        context = ssl.create_default_context()
        print(f"正在连接 {SMTP_SERVER}:{SMTP_PORT} ...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=10)
        print("✅ SSL 连接成功")

        print(f"正在登录 {SENDER_EMAIL} ...")
        server.login(SENDER_EMAIL, CLIENT_PASSWORD)
        print("✅ 登录成功")

        print(f"正在发送邮件到 {receiver} ...")
        server.sendmail(SENDER_EMAIL, [receiver, SENDER_EMAIL], msg.as_string())
        print("✅ 邮件发送成功！")
        print("⚠️ 提示：SMTP 客户端发送默认不会保存到网页邮箱的 'Sent' 文件夹，")
        print("   但已密送到你的收件箱，可在收件箱中查看。")

        server.quit()
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ 登录失败：请检查备用密码是否正确，或是否在网络限制环境。")
        return False
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="使用 SMTP 发送邮件（Coremail/School Mail Compatible）",
        epilog="示例: python send_csu_email.py --target xxx@qq.com -s '主题' -b '正文' -a file.pdf"
    )
    parser.add_argument(
        "--target", "-t",
        default=DEFAULT_RECEIVER,
        help=f"收件人邮箱地址（默认: {DEFAULT_RECEIVER}）"
    )
    parser.add_argument(
        "--subject", "-s",
        default="邮箱邮件",
        help="邮件主题"
    )
    parser.add_argument(
        "--body", "-b",
        default="这是一封邮件。",
        help="邮件正文内容"
    )
    parser.add_argument(
        "--attach", "-a",
        nargs="*",
        default=[],
        help="附件文件路径，可指定多个（示例: -a file1.pdf file2.jpg）"
    )

    args = parser.parse_args()

    print("=" * 50)
    print(f"发件人: {SENDER_EMAIL}")
    print(f"收件人: {args.target}")
    print(f"主题:   {args.subject}")
    print(f"正文:   {args.body[:50]}{'...' if len(args.body) > 50 else ''}")
    if args.attach:
        print(f"附件:   {', '.join(args.attach)}")
    print("=" * 50)

    success = send_email(args.target, args.subject, args.body, attachments=args.attach)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
