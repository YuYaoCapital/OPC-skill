# -*- coding: utf-8 -*-
"""
企微群机器人报告推送脚本
用法: python send_wechat_work.py --webhook xxx --title xxx --pdf xxx
"""
import argparse
import json
import os
import requests
import sys

# 修复 Windows 终端 GBK 编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def send_markdown(webhook, content):
    """发送 Markdown 消息"""
    resp = requests.post(
        webhook,
        json={
            "msgtype": "markdown",
            "markdown": {"content": content}
        },
        timeout=30
    )
    return resp.json()


def upload_file(webhook, file_path):
    """上传文件获取 media_id"""
    upload_url = webhook.replace("/send?", "/upload_media?") + "&type=file"
    with open(file_path, "rb") as f:
        resp = requests.post(upload_url, files={"media": f}, timeout=60)
    data = resp.json()
    if data.get("errcode") != 0:
        raise RuntimeError(f"Upload failed: {data}")
    return data["media_id"]


def send_file(webhook, media_id):
    """发送文件消息"""
    resp = requests.post(
        webhook,
        json={"msgtype": "file", "file": {"media_id": media_id}},
        timeout=30
    )
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="企微报告推送")
    parser.add_argument("--webhook", required=True, help="企微机器人 webhook URL")
    parser.add_argument("--title", default="基金周报", help="消息标题")
    parser.add_argument("--fund-code", default="", help="基金代码")
    parser.add_argument("--fund-name", default="", help="基金名称")
    parser.add_argument("--nav", default="", help="最新净值")
    parser.add_argument("--weekly-return", default="", help="本周收益")
    parser.add_argument("--total-return", default="", help="成立以来收益")
    parser.add_argument("--date", default="", help="报告日期")
    parser.add_argument("--pdf", default="", help="PDF 文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不推送")
    args = parser.parse_args()

    # Markdown 消息内容
    markdown = f"""☕ {args.title}

📊 最新净值：{args.nav}
📊 本周收益：{args.weekly_return}
📊 成立以来：{args.total_return}

PDF 报告请见下方附件。"""

    print("=" * 50)
    print("企微推送消息预览:")
    print("=" * 50)
    print(markdown)
    print("=" * 50)

    if args.dry_run:
        print("\n[Dry Run] 已跳过实际推送")
        return

    # 1. 发送 Markdown 消息
    print("\n[1/3] 发送 Markdown 消息...")
    result = send_markdown(args.webhook, markdown)
    print(f"Markdown 发送结果: {result}")

    # 2. 上传 PDF 文件
    if args.pdf and os.path.exists(args.pdf):
        print(f"\n[2/3] 上传 PDF 文件: {args.pdf} ({os.path.getsize(args.pdf)} bytes)")
        media_id = upload_file(args.webhook, args.pdf)
        print(f"media_id: {media_id}")

        # 3. 发送文件消息
        print("\n[3/3] 发送文件消息...")
        result = send_file(args.webhook, media_id)
        print(f"File 发送结果: {result}")
    elif args.pdf:
        print(f"\n[Warning] PDF 文件不存在: {args.pdf}")
    else:
        print("\n[Info] 未提供 PDF 文件，跳过文件发送")

    print("\n✅ 推送完成!")


if __name__ == "__main__":
    main()
