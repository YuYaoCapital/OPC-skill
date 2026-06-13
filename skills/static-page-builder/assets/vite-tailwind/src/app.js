export function renderApp(container) {
  container.innerHTML = `
    <nav class="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur border-b border-slate-100">
      <div class="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#" class="font-bold text-lg text-primary">{{SITE_NAME}}</a>
        <div class="hidden md:flex gap-8 text-sm font-medium text-slate-600">
          <a href="#features" class="hover:text-accent transition">功能</a>
          <a href="#about" class="hover:text-accent transition">关于</a>
        </div>
      </div>
    </nav>

    <section class="pt-32 pb-20 px-6 text-center">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight text-primary mb-6">
          {{HERO_TITLE}}
        </h1>
        <p class="text-lg md:text-xl text-slate-600 mb-10 leading-relaxed">
          {{HERO_SUBTITLE}}
        </p>
        <div class="flex justify-center gap-4">
          <button class="px-6 py-3 rounded-lg bg-accent text-white font-medium hover:bg-blue-600 transition">
            {{CTA_PRIMARY}}
          </button>
          <button class="px-6 py-3 rounded-lg border border-slate-200 text-slate-700 font-medium hover:border-slate-300 transition">
            {{CTA_SECONDARY}}
          </button>
        </div>
      </div>
    </section>

    <section id="features" class="py-20 bg-slate-50">
      <div class="max-w-5xl mx-auto px-6">
        <div class="grid md:grid-cols-3 gap-8">
          <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
            <h3 class="font-semibold text-lg mb-2">{{FEATURE_1_TITLE}}</h3>
            <p class="text-slate-600 text-sm leading-relaxed">{{FEATURE_1_DESC}}</p>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
            <h3 class="font-semibold text-lg mb-2">{{FEATURE_2_TITLE}}</h3>
            <p class="text-slate-600 text-sm leading-relaxed">{{FEATURE_2_DESC}}</p>
          </div>
          <div class="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
            <h3 class="font-semibold text-lg mb-2">{{FEATURE_3_TITLE}}</h3>
            <p class="text-slate-600 text-sm leading-relaxed">{{FEATURE_3_DESC}}</p>
          </div>
        </div>
      </div>
    </section>

    <footer class="py-10 border-t border-slate-100 text-center text-sm text-slate-500">
      <p>&copy; ${new Date().getFullYear()} {{SITE_NAME}}. All rights reserved.</p>
    </footer>
  `
}
