#!/usr/bin/env python3
"""
企业微信群机器人报告推送工具

用法示例:
    python send_wechat_work.py \
        --webhook "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY" \
        --title "007119 周度回顾报告" \
        --pdf "20260703_007119_周度回顾.pdf" \
        --html "https://fundadvisor.pages.dev/reports/20260703_007119_周度回顾.html" \
        --date "2026-07-03"

支持消息类型:
    - markdown: 发送报告标题、日期、HTML 在线链接等文本信息
    - file: 上传并发送 PDF 附件（如需发送 HTML 文件，同样走 file 类型）
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests


def extract_key_from_webhook(webhook_url: str) -> str:
    """从 webhook URL 中提取 key 参数。"""
    parsed = urlparse(webhook_url)
    query = parse_qs(parsed.query)
    if "key" not in query or not query["key"]:
        raise ValueError("webhook URL 中缺少 key 参数")
    return query["key"][0]


def send_markdown(webhook_url: str, content: str) -> dict:
    """发送 markdown 消息到企业微信群。"""
    payload = {"msgtype": "markdown", "markdown": {"content": content}}
    resp = requests.post(webhook_url, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    if result.get("errcode") != 0:
        raise RuntimeError(f"发送 markdown 失败: {result}")
    return result


def upload_media(webhook_url: str, file_path: str) -> str:
    """上传文件到企业微信，返回 media_id。"""
    key = extract_key_from_webhook(webhook_url)
    upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file"

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(path, "rb") as f:
        files = {"media": (path.name, f, "application/octet-stream")}
        resp = requests.post(upload_url, files=files, timeout=60)

    resp.raise_for_status()
    result = resp.json()
    if result.get("errcode") != 0:
        raise RuntimeError(f"上传文件失败: {result}")
    return result["media_id"]


def send_file(webhook_url: str, media_id: str) -> dict:
    """发送文件消息到企业微信群。"""
    payload = {"msgtype": "file", "file": {"media_id": media_id}}
    resp = requests.post(webhook_url, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    if result.get("errcode") != 0:
        raise RuntimeError(f"发送文件失败: {result}")
    return result


def build_markdown(title: str, date: str = None, html_url: str = None,
                   fund_code: str = None, fund_name: str = None,
                   extra: str = None) -> str:
    """构建 markdown 消息内容。"""
    lines = [f"**{title}**"]
    if fund_code:
        lines.append(f"> 基金代码：{fund_code}")
    if fund_name:
        lines.append(f"> 基金名称：{fund_name}")
    if date:
        lines.append(f"> 报告日期：{date}")
    if html_url:
        lines.append(f"> 在线 HTML 报告：[点击访问]({html_url})")
    if extra:
        lines.append("")
        lines.append(extra)
    lines.append("")
    lines.append("PDF 报告请见下方附件。")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="推送基金报告到企业微信群")
    parser.add_argument("--webhook", required=True, help="企业微信机器人 webhook URL")
    parser.add_argument("--title", required=True, help="报告标题")
    parser.add_argument("--fund-code", help="基金代码")
    parser.add_argument("--fund-name", help="基金名称")
    parser.add_argument("--date", help="报告日期")
    parser.add_argument("--pdf", help="PDF 报告文件路径")
    parser.add_argument("--html", help="HTML 在线访问地址或本地文件路径")
    parser.add_argument("--html-as-file", action="store_true",
                        help="同时将 HTML 文件作为附件上传（默认仅通过链接发送）")
    parser.add_argument("--extra", help="附加说明文本")
    parser.add_argument("--dry-run", action="store_true", help="仅打印将要发送的内容，不实际发送")

    args = parser.parse_args()

    # 区分 HTML 链接和本地 HTML 文件
    html_url = None
    html_file = None
    if args.html:
        if args.html.startswith("http://") or args.html.startswith("https://"):
            html_url = args.html
        elif os.path.exists(args.html):
            html_file = args.html
            if args.html_as_file:
                html_url = f"（HTML 文件已作为附件发送）"
        else:
            print(f"警告：HTML 路径不存在或不是有效链接：{args.html}", file=sys.stderr)

    content = build_markdown(
        title=args.title,
        date=args.date,
        html_url=html_url,
        fund_code=args.fund_code,
        fund_name=args.fund_name,
        extra=args.extra,
    )

    if args.dry_run:
        print("[DRY RUN] 将要发送的 markdown 内容：")
        print(content)
        if args.pdf:
            print(f"[DRY RUN] 将要上传 PDF: {args.pdf}")
        if html_file and args.html_as_file:
            print(f"[DRY RUN] 将要上传 HTML: {html_file}")
        return

    print("发送 markdown 消息...")
    send_markdown(args.webhook, content)
    print("markdown 消息发送成功")

    if args.pdf:
        print(f"上传 PDF: {args.pdf} ...")
        media_id = upload_media(args.webhook, args.pdf)
        print(f"发送 PDF 文件...")
        send_file(args.webhook, media_id)
        print("PDF 文件发送成功")

    if html_file and args.html_as_file:
        print(f"上传 HTML: {html_file} ...")
        media_id = upload_media(args.webhook, html_file)
        print(f"发送 HTML 文件...")
        send_file(args.webhook, media_id)
        print("HTML 文件发送成功")

    print("全部推送完成")


if __name__ == "__main__":
    main()
