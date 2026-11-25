// Your private control page: /api/setup?secret=YOUR_SECRET
//   (no extras)  -> status, who has started the bot, and this year's delivery times
//   &hello=1     -> the character sends the welcome message
//   &send=5      -> sends door 5 right now (for testing; opens only if it is already that day)
import { configured, CHAT_ID, SITE, YEAR, NAME, slotFor, slotLabel, telegram, sendDoor, sendWelcome } from "../lib/advent.mjs";

const page = (body) => new Response(`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Control room</title>
<body style="font:15px/1.5 system-ui;background:#0b0710;color:#f7eedc;padding:20px;max-width:560px;margin:auto">
<h2 style="color:#ff9a2e">Control room</h2>${body}</body>`, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });

export default async (req) => {
  const url = new URL(req.url);
  if (!configured()) return page("<p>Add TELEGRAM_TOKEN and SECRET in Netlify environment variables, then redeploy.</p>");
  if (url.searchParams.get("secret") !== process.env.SECRET) return new Response("Not found", { status: 404 });
  const s = encodeURIComponent(process.env.SECRET);
  let out = "";

  if (!CHAT_ID) {
    const me = await telegram("getMe", {});
    if (!me.ok) return page(`<p>Telegram rejected the bot token (${me.description || "no reason given"}).</p><p>Open Netlify, Environment variables, and check TELEGRAM_TOKEN: no spaces before or after, nothing missing, then deploy again.</p>`);
    out += `<p>Connected to the bot <b>@${me.result.username}</b>. The person must press Start on this exact bot.</p>`;
    const upd = await telegram("getUpdates", {});
    if (!upd.ok) return page(out + `<p>Telegram would not hand over messages: ${upd.description || "unknown error"}.</p>`);
    const chats = new Map();
    (upd.result || []).forEach(u => { const c = (u.message || {}).chat; if (c && c.type === "private") chats.set(c.id, c.first_name || c.username || "someone"); });
    out += chats.size
      ? "<p>People who pressed Start:</p><ul>" + [...chats].map(([id, n]) => `<li>${n}: <b>${id}</b></li>`).join("") +
        "</ul><p>Copy the number into a Netlify environment variable called CHAT_ID, then redeploy.</p>"
      : "<p>Nobody has pressed Start yet. Send them the bot link, ask them to tap Start, then reload this page (within 24 hours).</p>";
    return page(out);
  }

  if (url.searchParams.get("hello")) {
    const r = await sendWelcome(); if (!r.ok) out += `<p>Welcome failed: ${r.description || ""}</p>`;
    out += "<p>Welcome message sent.</p>";
  }
  const send = parseInt(url.searchParams.get("send"), 10);
  if (send >= 1 && send <= 24) { const r = await sendDoor(send); out += `<p>Door ${send}: ${r.ok ? "sent" : "failed: " + (r.description || "")}</p>`; }

  out += `<p>Connected to chat <b>${CHAT_ID}</b>. Site: ${SITE}</p>
  <p><a style="color:#ff4f8b" href="?secret=${s}&hello=1">Send ${NAME}'s welcome message</a></p>
  <h3>Delivery times ${YEAR} (only you can see these)</h3><ol>` +
  Array.from({ length: 24 }, (_, i) => `<li>${i + 1} Dec, ${slotLabel(slotFor(i + 1))} <a style="color:#14c7b1" href="?secret=${s}&send=${i + 1}">send now</a></li>`).join("") + "</ol>";
  return page(out);
};

export const config = { path: "/api/setup" };
