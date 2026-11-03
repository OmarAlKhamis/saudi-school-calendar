// Usage counter for the landing page: counts people who press a subscribe button.
// GET  /count -> {"total": n}
// POST /hit   (body: feed name, e.g. "main-ar") -> counts each visitor once, ever.
// Visitors are identified only by a salted hash of IP + user agent; nothing personal is stored.

const FEEDS = new Set(["main-ar", "main-en", "west-ar", "west-en"]);
const ORIGINS = new Set(["https://omaralkhamis.github.io", "http://localhost:8791"]);

function cors(req) {
  const origin = req.headers.get("Origin") || "";
  return {
    "Access-Control-Allow-Origin": ORIGINS.has(origin) ? origin : "https://omaralkhamis.github.io",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Vary": "Origin",
  };
}

async function visitorKey(req, salt) {
  const raw = (req.headers.get("CF-Connecting-IP") || "") + "|" + (req.headers.get("User-Agent") || "") + "|" + salt;
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(raw));
  return "seen:" + [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, "0")).join("");
}

async function num(kv, key) {
  return parseInt((await kv.get(key)) || "0", 10);
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const headers = { ...cors(req), "Content-Type": "application/json" };
    if (req.method === "OPTIONS") return new Response(null, { headers });

    if (url.pathname === "/count" && req.method === "GET") {
      const total = await num(env.COUNTS, "total");
      return new Response(JSON.stringify({ total }), { headers: { ...headers, "Cache-Control": "public, max-age=60" } });
    }

    if (url.pathname === "/hit" && req.method === "POST") {
      const feed = (await req.text()).trim();
      if (!FEEDS.has(feed)) return new Response('{"error":"unknown feed"}', { status: 400, headers });
      const key = await visitorKey(req, env.SALT || "");
      if (await env.COUNTS.get(key)) return new Response('{"counted":false}', { headers });
      await env.COUNTS.put(key, "1");
      await env.COUNTS.put("total", String((await num(env.COUNTS, "total")) + 1));
      await env.COUNTS.put("feed:" + feed, String((await num(env.COUNTS, "feed:" + feed)) + 1));
      return new Response('{"counted":true}', { headers });
    }

    return new Response('{"error":"not found"}', { status: 404, headers });
  },
};
