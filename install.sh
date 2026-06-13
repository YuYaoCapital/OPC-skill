#!/bin/bash
set -e

TARGET_DIR="$HOME/.kimi/skills"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)/skills"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "错误：未找到 skills/ 目录，请确保在仓库根目录运行此脚本。"
    exit 1
fi

mkdir -p "$TARGET_DIR"

echo "正在安装 Skill 到 $TARGET_DIR ..."
cp -R "$SOURCE_DIR"/* "$TARGET_DIR/"

INSTALLED_COUNT=$(find "$SOURCE_DIR" -maxdepth 1 -type d ! -path "$SOURCE_DIR" | wc -l | tr -d ' ')
echo "安装完成！共安装 $INSTALLED_COUNT 个 Skill。"
echo ""
echo "你可以通过以下命令验证："
echo "  ls ~/.kimi/skills/ | wc -l"
