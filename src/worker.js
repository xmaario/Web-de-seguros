/* UnpackInsurance Worker.
 * Static pages are served straight from the assets. Only /api/* runs this code.
 * POST /api/contact: validates the contact form and emails it to the site owner
 * through Cloudflare Email Routing (send_email binding, fixed verified destination). */

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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/contact") return handleContact(request, env);
    if (url.pathname.startsWith("/api/")) return json(404, { ok: false, error: "not_found" });
    return env.ASSETS.fetch(request);
  },
};
