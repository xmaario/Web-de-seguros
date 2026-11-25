/* UnpackInsurance Worker.
 * Static pages are served straight from the assets. Only /api/* runs this code.
 * POST /api/contact: validates the contact form and emails it to the site owner
 * through Cloudflare Email Routing (send_email binding, fixed verified destination).
 * POST /api/gsc: private, read-only Search Console report for the site owner.
 *   Needs secrets GSC_KEY (Google service account JSON with Restricted access in
 *   Search Console) and STATS_TOKEN (sent by the caller in the X-Stats-Token header). */

const FROM = { email: "contact@unpackinsurance.com", name: "UnpackInsurance contact form" };
const TOPICS = { general: "General question", correction: "Content correction", privacy: "Privacy request", advertising: "Advertising inquiry" };

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

async function handleContact(request, env) {
  if (request.method !== "POST") return json(405, { ok: false, error: "method" });
  if (!env.EMAIL) return json(503, { ok: false, error: "disabled" });

  // Only accept posts from our own pages (same origin as the request).
  const origin = request.headers.get("Origin") || "";
  if (origin !== new URL(request.url).origin) return json(403, { ok: false, error: "origin" });

  // Basic abuse limit per visitor IP (Workers rate limiting binding).
  if (env.LIMITER) {
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const { success } = await env.LIMITER.limit({ key: ip });
    if (!success) return json(429, { ok: false, error: "rate" });
  }

  let form;
  try {
    form = await request.formData();
  } catch (e) {
    return json(400, { ok: false, error: "form" });
  }
  const get = (k) => String(form.get(k) || "").trim();
  const name = get("name").slice(0, 100);
  const email = get("email").slice(0, 200);
  const message = get("message").slice(0, 5000);
  const topic = TOPICS[get("topic")] || TOPICS.general;

  // Spam traps: hidden field must stay empty, and the form must not be sent instantly.
  const started = parseInt(get("started"), 10);
  if (get("website") || !started || Date.now() - started < 3000) {
    return json(200, { ok: true }); // pretend success so bots learn nothing
  }
  if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || message.length < 5 || get("privacy_consent") !== "yes") {
    return json(400, { ok: false, error: "invalid" });
  }

  const text = [
    `Name: ${name}`,
    `Email: ${email}`,
    `Topic: ${topic}`,
    `Consent to privacy policy: yes`,
    `Sent: ${new Date().toISOString()}`,
    "",
    message,
  ].join("\n");

  try {
    await env.EMAIL.send({
      from: FROM,
      to: env.CONTACT_TO,
      replyTo: { email, name },
      subject: `[UnpackInsurance] ${topic}: ${name.replace(/[\r\n]+/g, " ")}`,
      text,
    });
  } catch (e) {
    console.error("contact send failed", e && e.code, e && e.message);
    return json(502, { ok: false, error: "send" });
  }
  return json(200, { ok: true });
}

const GSC_SITE = "sc-domain:unpackinsurance.com";
let gscToken = { value: "", exp: 0 };

function b64url(data) {
  const bytes = typeof data === "string" ? new TextEncoder().encode(data) : new Uint8Array(data);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function sameSecret(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

async function googleAccessToken(env) {
  const now = Math.floor(Date.now() / 1000);
  if (gscToken.value && gscToken.exp - 60 > now) return gscToken.value;
  const key = JSON.parse(env.GSC_KEY);
  const pem = key.private_key.replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
  const der = Uint8Array.from(atob(pem), (c) => c.charCodeAt(0));
  const cryptoKey = await crypto.subtle.importKey("pkcs8", der, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const unsigned = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" })) + "." + b64url(JSON.stringify({
    iss: key.client_email,
    scope: "https://www.googleapis.com/auth/webmasters.readonly",
    aud: "https://oauth2.googleapis.com/token",
    iat: now,
    exp: now + 3600,
  }));
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", cryptoKey, new TextEncoder().encode(unsigned));
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer", assertion: unsigned + "." + b64url(sig) }),
  });
  const data = await res.json();
  if (!data.access_token) throw new Error("token: " + (data.error_description || data.error || res.status));
  gscToken = { value: data.access_token, exp: now + (data.expires_in || 3600) };
  return gscToken.value;
}

async function handleGsc(request, env) {
  if (request.method !== "POST") return json(405, { ok: false, error: "method" });
  if (!env.GSC_KEY || !env.STATS_TOKEN) return json(503, { ok: false, error: "not_configured" });
  if (!sameSecret(request.headers.get("X-Stats-Token") || "", env.STATS_TOKEN)) return json(401, { ok: false, error: "auth" });
  let query;
  try {
    query = await request.json();
  } catch (e) {
    return json(400, { ok: false, error: "json" });
  }
  try {
    const token = await googleAccessToken(env);
    const res = await fetch(`https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(GSC_SITE)}/searchAnalytics/query`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify(query),
    });
    return json(res.status, await res.json());
  } catch (e) {
    return json(502, { ok: false, error: String(e && e.message || e).slice(0, 200) });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/contact") return handleContact(request, env);
    if (url.pathname === "/api/gsc") return handleGsc(request, env);
    if (url.pathname.startsWith("/api/")) return json(404, { ok: false, error: "not_found" });
    return env.ASSETS.fetch(request);
  },
};
