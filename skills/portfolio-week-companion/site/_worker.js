/**
 * Cloudflare Pages Functions - Yahoo Finance 代理
 * 
 * 用途：解决浏览器端 Yahoo Finance API 的 CORS 跨域问题
 * 路径：/api/yahoo?symbol=<symbol>
 * 
 * 支持的 symbol：
 *   ^GSPC  (标普500)
 *   ^HSI   (恒生指数)
 *   GC=F   (COMEX黄金)
 *   ^DJI   (道琼斯)
 *   ^IXIC  (纳斯达克)
 * 
 * 优先级：P4（Yahoo Finance 公开数据）
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // 只允许 /api/yahoo 路径
    if (!path.startsWith('/api/yahoo')) {
      return new Response(JSON.stringify({ error: 'Not Found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const symbol = url.searchParams.get('symbol');
    if (!symbol) {
      return new Response(JSON.stringify({ error: 'Missing symbol parameter' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 构建 Yahoo Finance 查询 URL
    // 使用 Yahoo Finance 的 query1 接口（无需认证，公开数据）
    const yahooUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=1d&range=1d`;

    try {
      const response = await fetch(yahooUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      if (!response.ok) {
        return new Response(JSON.stringify({
          error: 'Yahoo Finance API error',
          status: response.status
        }), {
          status: 502,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
      }

      const data = await response.json();

      // 解析 Yahoo Finance 响应
      const result = data.chart?.result?.[0];
      if (!result) {
        return new Response(JSON.stringify({ error: 'No data available' }), {
          status: 404,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
      }

      const meta = result.meta;
      const quote = result.indicators?.quote?.[0];
      const timestamps = result.timestamp;

      // 提取最新价格数据
      const lastIndex = timestamps ? timestamps.length - 1 : 0;
      const price = meta.regularMarketPrice || meta.previousClose || quote?.close?.[lastIndex] || null;
      const prevClose = meta.chartPreviousClose || meta.previousClose || null;
      const change = price && prevClose ? price - prevClose : null;
      const changePct = price && prevClose ? ((change / prevClose) * 100).toFixed(2) : null;

      const output = {
        symbol: symbol,
        name: meta.shortName || meta.longName || symbol,
        currency: meta.currency || 'USD',
        price: price ? price.toFixed(2) : null,
        previousClose: prevClose ? prevClose.toFixed(2) : null,
        change: change ? change.toFixed(2) : null,
        changePct: changePct ? (change >= 0 ? '+' : '') + changePct + '%' : null,
        rawChange: changePct ? parseFloat(changePct) : null,
        timestamp: meta.regularMarketTime
          ? new Date(meta.regularMarketTime * 1000).toISOString()
          : new Date().toISOString(),
        source: 'Yahoo Finance',
        priority: 'P4'
      };

      return new Response(JSON.stringify(output), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Cache-Control': 'public, max-age=60' // 1分钟缓存
        }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        error: 'Proxy request failed',
        message: error.message
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }
  }
};
