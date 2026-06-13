#!/usr/bin/env python3
"""
微博热点财经情报板生成器
用法: python generate_board.py --data data.json --output board.png
"""

import argparse
import json
import os
from PIL import Image, ImageDraw, ImageFont


def load_fonts():
    """加载系统中文字体，按优先级尝试"""
    candidates = [
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2),  # macOS Bold
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ("/System/Library/Fonts/PingFang.ttc", 0),
    ]
    for path, idx in candidates:
        if os.path.exists(path):
            try:
                return {
                    "title": ImageFont.truetype(path, 52, index=idx),
                    "mod": ImageFont.truetype(path, 26, index=idx),
                    "item": ImageFont.truetype(path, 22, index=idx),
                    "body": ImageFont.truetype(path, 16, index=idx),
                    "num": ImageFont.truetype(path, 24, index=idx),
                    "tag": ImageFont.truetype(path, 15, index=idx),
                    "foot": ImageFont.truetype(path, 12, index=idx),
                }
            except Exception:
                continue
    # fallback
    f = ImageFont.load_default()
    return {k: f for k in ["title", "mod", "item", "body", "num", "tag", "foot"]}


# ============ 配色 ============
BG = (254, 249, 231)       # 淡黄背景 #FEF9E7
CARD_BG = (255, 255, 255)  # 纯白卡片
DARK = (30, 25, 15)
DARK_BODY = (60, 55, 45)
MUTED = (120, 110, 90)
LIGHT_BORDER = (230, 220, 195)

BLUE = (37, 99, 235)
ORANGE = (234, 88, 12)
GREEN = (22, 163, 74)
RED = (220, 38, 38)
PURPLE = (124, 58, 237)

COLOR_MAP = {
    "red": RED, "orange": ORANGE, "blue": BLUE,
    "purple": PURPLE, "green": GREEN,
}


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_card(draw, x, y, w, h, fill=CARD_BG, border=LIGHT_BORDER, radius=12):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=border, width=1)


def generate_board(data, output_path, width=1000):
    """生成情报板图片"""
    fonts = load_fonts()
    f_title = fonts["title"]
    f_mod = fonts["mod"]
    f_item = fonts["item"]
    f_body = fonts["body"]
    f_num = fonts["num"]
    f_tag = fonts["tag"]
    f_foot = fonts["foot"]

    W = width
    MARGIN_X = 50
    GAP_S = 16
    GAP_M = 20

    # 估算高度
    H = 1600
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    def ts(text, font):
        return text_size(draw, text, font)

    y = 55

    # 1. 标题
    title = data.get("title", "财经热点情报板")
    tw, th = ts(title, f_title)
    draw.text((W // 2 - tw // 2, y), title, fill=DARK, font=f_title)
    y += th + 12

    subtitle = data.get("subtitle", "")
    if subtitle:
        tw, th = ts(subtitle, f_body)
        draw.text((W // 2 - tw // 2, y), subtitle, fill=MUTED, font=f_body)
        y += th + 35

    draw.line([(MARGIN_X, y), (W - MARGIN_X, y)], fill=LIGHT_BORDER, width=1)
    y += GAP_M

    # 2. 微博热搜 TOP5
    hot_topics = data.get("hot_topics", [])
    if hot_topics:
        draw.text((MARGIN_X, y), "微博热搜财经话题", fill=DARK, font=f_mod)
        y += 36

        ITEM_H = 66
        for item in hot_topics:
            rank = str(item.get("rank", ""))
            topic = item.get("topic", "")
            heat = item.get("heat", "")
            color = COLOR_MAP.get(item.get("color", "blue"), BLUE)

            draw_card(draw, MARGIN_X, y, W - MARGIN_X * 2, ITEM_H)
            r = 14
            cx, cy = MARGIN_X + 16 + r, y + ITEM_H // 2
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
            draw.text((cx - 5, cy - 7), rank, fill=(255, 255, 255), font=f_tag)
            draw.text((MARGIN_X + 56, y + 18), topic, fill=DARK, font=f_item)
            hw, hh = ts(heat, f_num)
            draw.text((W - MARGIN_X - 16 - hw, y + 16), heat, fill=color, font=f_num)
            y += ITEM_H + 10
        y += GAP_M

    # 3. 核心投资热点
    hotspots = data.get("hotspots", [])
    if hotspots:
        draw.text((MARGIN_X, y), "核心投资热点解析", fill=DARK, font=f_mod)
        y += 36

        col_w = (W - MARGIN_X * 2 - 12) // 2
        CARD_H = 100
        for i, item in enumerate(hotspots):
            col = i % 2
            row = i // 2
            x = MARGIN_X + col * (col_w + 12)
            vy = y + row * (CARD_H + 12)

            name = item.get("name", "")
            desc = item.get("desc", "")
            focus = item.get("focus", "")
            color = COLOR_MAP.get(item.get("color", "blue"), BLUE)

            draw_card(draw, x, vy, col_w, CARD_H)
            draw.rounded_rectangle([x, vy, x + col_w, vy + 5], radius=2, fill=color)

            tw, th = ts(name, f_tag)
            draw.rounded_rectangle([x + 14, vy + 18, x + 14 + tw + 16, vy + 18 + th + 8], radius=4, fill=color)
            draw.text((x + 14 + 8, vy + 22), name, fill=(255, 255, 255), font=f_tag)
            draw.text((x + 14, vy + 52), desc, fill=DARK, font=f_item)
            draw.text((x + 14, vy + 78), focus, fill=MUTED, font=f_body)

        rows = (len(hotspots) + 1) // 2
        y += rows * (CARD_H + 12) + GAP_M

    # 4. 风险警示
    risks = data.get("risks", [])
    if risks:
        RISK_H = 145
        draw_card(draw, MARGIN_X, y, W - MARGIN_X * 2, RISK_H, fill=(254, 242, 242), border=(254, 202, 202))
        draw.rounded_rectangle([MARGIN_X, y, MARGIN_X + 5, y + RISK_H], radius=2, fill=RED)
        draw.text((MARGIN_X + 22, y + 16), "风险警示", fill=RED, font=f_mod)
        ry = y + 48
        for r in risks:
            draw.text((MARGIN_X + 22, ry), "· " + r, fill=DARK_BODY, font=f_body)
            ry += 26
        y += RISK_H + GAP_M

    # 5. 机构动向
    insts = data.get("institutions", [])
    if insts:
        INST_H = 145
        draw_card(draw, MARGIN_X, y, W - MARGIN_X * 2, INST_H, fill=(240, 253, 244), border=(187, 247, 208))
        draw.rounded_rectangle([MARGIN_X, y, MARGIN_X + 5, y + INST_H], radius=2, fill=GREEN)
        draw.text((MARGIN_X + 22, y + 16), "机构动向", fill=GREEN, font=f_mod)
        iy = y + 48
        for inst in insts:
            draw.text((MARGIN_X + 22, iy), "· " + inst, fill=DARK_BODY, font=f_body)
            iy += 26
        y += INST_H + GAP_M

    # 6. 投资观点速查
    views = data.get("views", [])
    if views:
        draw.text((MARGIN_X, y), "当日投资观点速查", fill=DARK, font=f_mod)
        y += 36

        PILL_H = 54
        col_w = (W - MARGIN_X * 2 - 24) // 3
        for i, item in enumerate(views):
            col = i % 3
            row = i // 3
            x = MARGIN_X + col * (col_w + 12)
            vy = y + row * (PILL_H + 12)

            name = item.get("name", "")
            view = item.get("view", "")
            color = COLOR_MAP.get(item.get("color", "green"), GREEN)

            draw.rounded_rectangle([x, vy, x + col_w, vy + PILL_H], radius=PILL_H // 2, fill=CARD_BG, outline=LIGHT_BORDER, width=1)
            nw, nh = ts(name, f_body)
            draw.text((x + 18, vy + PILL_H // 2 - nh // 2), name, fill=DARK, font=f_body)

            vw, vh = ts(view, f_tag)
            tag_w = vw + 20
            tx = x + col_w - tag_w - 16
            ty = vy + PILL_H // 2 - (vh + 8) // 2
            draw.rounded_rectangle([tx, ty, tx + tag_w, ty + vh + 8], radius=4, fill=color)
            draw.text((tx + 10, ty + 4), view, fill=(255, 255, 255), font=f_tag)

        rows = (len(views) + 1) // 3
        y += rows * (PILL_H + 12) + GAP_M

    # 7. 底部
    draw.line([(MARGIN_X, y), (W - MARGIN_X, y)], fill=LIGHT_BORDER, width=1)
    y += GAP_S
    footer = data.get("footer", "数据来源: 微博热搜 + 全网财经资讯  ·  投资有风险，理财需谨慎")
    tw, th = ts(footer, f_foot)
    draw.text((W // 2 - tw // 2, y), footer, fill=MUTED, font=f_foot)

    img.save(output_path, "PNG")
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="生成微博热点财经情报板")
    parser.add_argument("--data", required=True, help="JSON数据文件路径")
    parser.add_argument("--output", default="board.png", help="输出图片路径")
    parser.add_argument("--width", type=int, default=1000, help="画布宽度")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    generate_board(data, args.output, args.width)


if __name__ == "__main__":
    main()
