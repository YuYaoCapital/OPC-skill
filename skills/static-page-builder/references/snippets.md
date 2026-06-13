# 常用页面片段

直接复制到页面中修改文案即可。

## 导航栏

```html
<nav class="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur border-b border-slate-100">
  <div class="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
    <a href="#" class="font-bold text-lg text-primary">Logo</a>
    <div class="hidden md:flex gap-8 text-sm font-medium text-slate-600">
      <a href="#features" class="hover:text-accent transition">功能</a>
      <a href="#about" class="hover:text-accent transition">关于</a>
    </div>
  </div>
</nav>
```

## Hero 区域

```html
<section class="pt-32 pb-20 px-6 text-center">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight text-primary mb-6">主标题</h1>
    <p class="text-lg md:text-xl text-slate-600 mb-10 leading-relaxed">副标题描述</p>
    <div class="flex justify-center gap-4">
      <a href="#" class="px-6 py-3 rounded-lg bg-accent text-white font-medium hover:bg-blue-600 transition">主要按钮</a>
      <a href="#" class="px-6 py-3 rounded-lg border border-slate-200 text-slate-700 font-medium hover:border-slate-300 transition">次要按钮</a>
    </div>
  </div>
</section>
```

## 三列卡片

```html
<section class="py-20 bg-slate-50">
  <div class="max-w-5xl mx-auto px-6">
    <div class="grid md:grid-cols-3 gap-8">
      <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
        <h3 class="font-semibold text-lg mb-2">卡片标题</h3>
        <p class="text-slate-600 text-sm leading-relaxed">卡片内容</p>
      </div>
    </div>
  </div>
</section>
```

## 两列图文

```html
<section class="py-20">
  <div class="max-w-5xl mx-auto px-6 grid md:grid-cols-2 gap-12 items-center">
    <div>
      <h2 class="text-3xl font-bold text-primary mb-4">标题</h2>
      <p class="text-slate-600 leading-relaxed">内容</p>
    </div>
    <div class="bg-slate-100 rounded-2xl aspect-video"></div>
  </div>
</section>
```

## CTA 区域

```html
<section class="py-20 px-6 text-center bg-primary text-white">
  <div class="max-w-3xl mx-auto">
    <h2 class="text-3xl font-bold mb-4">准备好开始了吗？</h2>
    <p class="text-slate-300 mb-8">立即体验，无需注册。</p>
    <a href="#" class="inline-block px-8 py-3 rounded-lg bg-accent text-white font-medium hover:bg-blue-600 transition">开始使用</a>
  </div>
</section>
```

## Footer

```html
<footer class="py-10 border-t border-slate-100 text-center text-sm text-slate-500">
  <p>&copy; 2026 Site Name. All rights reserved.</p>
</footer>
```
