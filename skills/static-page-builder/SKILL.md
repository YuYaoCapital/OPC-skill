---
name: static-page-builder
description: 快速构建和部署 pages.dev 风格的现代静态网页。当用户需要"做个网页"、"搭个页面"、"写个静态网站"、"pages.dev"、"landing page"、"单页网站"、"前端页面"时触发。适用于落地页、数据展示页、产品介绍页、个人主页等轻量静态站点，输出可直接部署到 Cloudflare Pages。
---

# Static Page Builder

帮用户快速做出一个能直接部署到 pages.dev 的干净静态网页。

## 工作流

1. **确认需求**（快速问 1-2 个问题）：
   - 做什么类型的页面？（落地页 / Dashboard / 展示页 / 其他）
   - 简单单页还是复杂多页？是否需要交互数据？
2. **选择模板**：
   - 简单单页 → 复制 `assets/hello-world/`（HTML + Tailwind CDN）
   - 需要构建、多组件、JS 交互 → 复制 `assets/vite-tailwind/`（Vite + Tailwind）
3. **生成页面内容**：基于用户描述填充文案、结构和样式
4. **本地预览**：如果是 Vite 模板，运行 `npm install && npm run dev`
5. **部署**：按 `references/deploy.md` 指导用户部署到 pages.dev

## 设计规范（默认）

- 配色：白底（`bg-white`）+ 深蓝主色（`#0f172a`）+ 蓝色强调（`#3b82f6`）
- 字体：系统默认无衬线，不要引用 Google Fonts
- 布局：居中容器 `max-w-5xl mx-auto px-6`，响应式优先移动端
- 组件：圆角 `rounded-2xl` 或 `rounded-lg`，轻微阴影 `shadow-sm`
- 风格：简洁、留白、现代
- 如果用户有其他偏好，以用户为准

## 可用资源

- `assets/hello-world/index.html` — 单文件 HTML 模板，复制即改
- `assets/vite-tailwind/` — Vite + Tailwind 项目模板
- `references/snippets.md` — 常用组件片段（导航、Hero、卡片、Footer、CTA）
- `references/deploy.md` — pages.dev 部署指南

## 替换占位符

模板中用 `{{XXX}}` 标记的内容需要替换成实际文案，例如：
- `{{PAGE_TITLE}}` → 页面标题
- `{{SITE_NAME}}` → 网站/品牌名
- `{{HERO_TITLE}}` / `{{HERO_SUBTITLE}}` → Hero 区大标题和副标题
- `{{CTA_PRIMARY}}` / `{{CTA_SECONDARY}}` → 按钮文案
- `{{FEATURE_X_TITLE}}` / `{{FEATURE_X_DESC}}` → 功能卡片
- `{{PROJECT_NAME}}` → package.json 里的项目名
- `{{YEAR}}` → 当前年份

## 输出要求

- 代码整洁、语义化 HTML
- 所有页面必须响应式
- 如果需要图片，使用占位图或用户提供的资源
- 部署前确保 `dist/`（或根目录）下有 `index.html`
