---
name: report-wechat-push
description: 将生成的报告（PDF、HTML 等）通过企业微信群机器人 webhook 推送到指定企微群。支持发送 Markdown 消息（报告标题、日期、在线 HTML 链接）和上传 PDF/文件附件。可被 fund-weekly-review、fund-weekly-hybrid、portfolio-week-companion 等生成报告的 skill 调用，作为报告分发的最后一步。
triggers:
  - 推送到企业微信
  - 发送到企微群
  - 报告推送
  - 企微机器人
  - 微信群发报告
  - webhook 推送报告
  - 发送 PDF 到企微
inputs:
  - webhook: 企业微信机器人 webhook URL（必填）
  - title: 报告标题（必填）
  - fund_code: 基金代码（可选）
  - fund_name: 基金名称（可选）
  - date: 报告日期（可选）
  - pdf: PDF 报告本地文件路径（可选）
  - html: HTML 在线链接或本地文件路径（可选）
  - html_as_file: 是否同时将 HTML 作为文件附件上传（可选，默认 false）
  - extra: 附加说明文本（可选）
outputs:
  - 企业微信群 Markdown 消息
  - 企业微信群文件消息（PDF / HTML）
---

# 报告推送至企业微信

本 skill 负责将已生成的报告（PDF、HTML 等）通过企业微信群机器人 webhook 推送到指定企微群，作为报告生成的最后一步分发动作。

## 能力定位

- **独立分发能力**：不生成报告内容，只负责把已生成的报告文件/链接推送到企微群。
- **可被其他 skill 调用**：如 `fund-weekly-review`、`fund-weekly-hybrid`、`portfolio-week-companion` 等生成报告的 skill，在输出 PDF + HTML 后可调用本 skill 完成推送。
- **支持两种消息**：
  1. **Markdown 消息**：报告标题、基金代码/名称、报告日期、摘要、HTML 在线链接。
  2. **文件消息**：通过企业微信 `upload_media` 接口上传 PDF（或 HTML），再作为文件附件发送到群里。

## 触发条件

| 触发词 | 示例 |
|---|---|
| 推送到企业微信 | "把这份报告推到企业微信群" |
| 发送到企微群 | "发送到企微群的 webhook" |
| 报告推送 | "推报告到企微" |
| 企微机器人 | "用企微机器人发报告" |
| 微信群发报告 | "把 PDF 发到微信群" |
| webhook 推送报告 | "通过 webhook 推送报告" |
| 发送 PDF 到企微 | "把 PDF 文件发到企业微信" |

## 输入变量

```
webhook = 企业微信机器人 webhook URL（必填，如 https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx）
title = 报告标题（必填，作为 markdown 消息首行）
fund_code = 基金代码（可选）
fund_name = 基金名称（可选）
date = 报告日期（可选）
pdf = PDF 报告本地文件路径（可选）
html = HTML 在线链接或本地文件路径（可选）
html_as_file = 是否同时将 HTML 作为文件附件上传（可选，默认 false）
extra = 附加说明文本（可选）
```

## 输出结果

- 企业微信群收到一条 Markdown 消息
- 若提供了 `--pdf`，群中会再收到一个 PDF 文件附件
- 若提供了 `--html-as-file`，群中会再收到一个 HTML 文件附件

## 使用方式

### 1. 命令行直接调用

```bash
python skills/report-wechat-push/scripts/send_wechat_work.py \
  --webhook "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY" \
  --title "007119 周度陪伴报告" \
  --fund-code "007119" \
  --fund-name "睿远成长价值混合A" \
  --date "2026-07-03" \
  --pdf "reports/20260703_睿远成长价值_周度回顾.pdf" \
  --html "https://fundadvisor.pages.dev/reports/20260703_睿远成长价值_周度回顾.html"
```

### 2. 被其他 skill 调用

在生成报告的 skill（如 `fund-weekly-review`）末尾追加一步：

> 若用户提供了 `wechat_webhook`，调用 `report-wechat-push` 将生成的 PDF 与 HTML 推送到企微群。

调用脚本路径：`skills/report-wechat-push/scripts/send_wechat_work.py`

## 参数说明

| 参数 | 必填 | 说明 |
|---|---|---|
| `--webhook` | 是 | 企业微信机器人 webhook URL |
| `--title` | 是 | 报告标题，会作为 markdown 消息首行 |
| `--fund-code` | 否 | 基金代码 |
| `--fund-name` | 否 | 基金名称 |
| `--date` | 否 | 报告日期 |
| `--pdf` | 否 | PDF 报告本地文件路径 |
| `--html` | 否 | HTML 在线链接或本地文件路径 |
| `--html-as-file` | 否 | 同时将 HTML 作为文件附件上传 |
| `--extra` | 否 | 附加说明文本 |
| `--dry-run` | 否 | 仅打印待发送内容，不实际推送 |

## 消息格式示例

发送的 Markdown 消息内容示例：

```markdown
**007119 周度陪伴报告**
> 基金代码：007119
> 基金名称：睿远成长价值混合A
> 报告日期：2026-07-03
> 在线 HTML 报告：[点击访问](https://fundadvisor.pages.dev/reports/20260703_睿远成长价值_周度回顾.html)

PDF 报告请见下方附件。
```

## 企业微信机器人接口说明

### 发送 Markdown 消息

```http
POST https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
Content-Type: application/json

{
  "msgtype": "markdown",
  "markdown": {
    "content": "**报告标题**\n> 在线 HTML 报告：[点击访问](https://example.com/report.html)"
  }
}
```

### 上传文件获取 media_id

```http
POST https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=YOUR_KEY&type=file
Content-Type: multipart/form-data

media=@report.pdf
```

响应示例：

```json
{
  "errcode": 0,
  "errmsg": "ok",
  "type": "file",
  "media_id": "MEDIA_ID",
  "created_at": "123456789"
}
```

### 发送文件消息

```http
POST https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
Content-Type: application/json

{
  "msgtype": "file",
  "file": {
    "media_id": "MEDIA_ID"
  }
}
```

## 注意事项

- **文件大小限制**：企业微信群机器人对文件大小通常限制在 20MB 以内，超大 PDF 需先压缩。
- **凭证安全**：webhook URL 中的 `key` 是群机器人唯一凭证，不要硬编码在公开仓库中，建议通过环境变量或运行时参数传入。
- **网络要求**：调用企业微信 API 需要能访问 `qyapi.weixin.qq.com`。
- **HTML 处理方式**：默认将 HTML 作为在线链接发送；如需发送 HTML 文件本身，使用 `--html-as-file`。
- **幂等性**：企业微信 API 不支持自动去重，重复调用会导致重复发送，调用方需自行控制重试逻辑。
