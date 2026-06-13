# 部署到 pages.dev

## 方案 A：Wrangler CLI 命令行（推荐）

```bash
# 1. 登录 Cloudflare
npx wrangler login

# 2. 进入项目目录，构建
npm run build

# 3. 部署
cd dist && npx wrangler pages deploy . --project-name=你的项目名
# 或者如果 package.json 里配了 deploy 脚本：
npm run deploy
```

## 方案 B：Git 连接 Cloudflare Pages

1. 在 Cloudflare Dashboard 进入 Pages
2. 点击 "Create a project" → "Connect to Git"
3. 选择 GitHub/GitLab 仓库
4. 构建设置：
   - Build command: `npm run build`
   - Build output directory: `dist`
5. 保存并部署

## 方案 C：Drag & Drop

直接把 `dist/` 文件夹拖到 Cloudflare Pages Dashboard 的 "Upload assets" 里。

## 常见配置

### `_routes.json`（函数/重定向规则）

放在 `dist/` 或 `public/` 里：

```json
{
  "version": 1,
  "include": ["/*"],
  "exclude": ["/assets/*"]
}
```

### `_headers`（自定义响应头）

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
```

### `_redirects`

```
/old /new 301
```
