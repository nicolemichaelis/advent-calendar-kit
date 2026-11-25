// Shared logic for the sender, the door list and the control page.
// Everything personal comes from config.json (copied here by tools/build.py). Nothing is hard-coded.
import { createHmac } from "node:crypto";
import cfg from "./config.json";

const SECRET = process.env.SECRET || "";
const TOKEN = process.env.TELEGRAM_TOKEN || "";
export const CHAT_ID = process.env.CHAT_ID || "";
export const SITE = (process.env.URL || "").replace(/\/$/, "");

export const YEAR = Number(process.env.ADVENT_YEAR || cfg.year);
export const TZ = cfg.timezone || "Europe/Stockholm";
export const SPECIAL = cfg.special_days || [];
export const NAME = cfg.character.name;
const FROM_H = (cfg.send_window && cfg.send_window.from_hour) ?? 8;
const TO_H = (cfg.send_window && cfg.send_window.to_hour) ?? 20;
const SLOTS = Math.max(1, (TO_H - FROM_H) * 4);          // quarter-hour slots inside the window
export const LAST_SLOT = TO_H * 4;                       // nothing is sent at or after this

const h = (s) => createHmac("sha256", SECRET).update(s).digest("hex");
export const configured = () => Boolean(SECRET && TOKEN);
export const keyFor = (day) => h(`key-${YEAR}-${day}`).slice(0, 16);

/* Each day gets its own random 15-minute slot inside the window, fixed by your SECRET. */
export function slotFor(day) {
  const n = parseInt(h(`slot-${YEAR}-${day}`).slice(0, 8), 16);
  return FROM_H * 4 + (n % SLOTS);
}
export const slotLabel = (s) => `${String(Math.floor(s / 4)).padStart(2, "0")}:${String((s % 4) * 15).padStart(2, "0")}`;

export function localNow() {
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en-GB", {
    timeZone: TZ, year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric", hourCycle: "h23"
  }).formatToParts(new Date()).map(p => [p.type, p.value]));
  return { y: +parts.year, m: +parts.month, d: +parts.day, slot: +parts.hour * 4 + Math.floor(+parts.minute / 15) };
}

/* A door counts as delivered from its slot on that day, and for good after that. Never before 1 December. */
export function isDelivered(day) {
  const n = localNow();
  if (n.y > YEAR) return true;
  if (n.y < YEAR || n.m !== 12) return false;
  return day < n.d || (day === n.d && n.slot >= slotFor(day));
}

export const doorLink = (day) => `${SITE}/?door=${day}&k=${keyFor(day)}`;
const note = (day) => ((cfg.days[String(day)] || {}).note || "");
const pad = (d) => String(d).padStart(2, "0");

export async function telegram(method, body) {
  const r = await fetch(`https://api.telegram.org/bot${TOKEN}/${method}`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body || {})
  });
  return r.json();
}

function deliver(chatId, media, caption, button) {
  const markup = button ? { inline_keyboard: [[button]] } : undefined;
  if (cfg.cards) return telegram("sendAnimation", { chat_id: chatId, animation: `${SITE}/cards/${media}.mp4`, caption, reply_markup: markup });
  return telegram("sendMessage", { chat_id: chatId, text: caption, reply_markup: markup });   // plain fallback when no cards were built
}

export function sendDoor(day, chatId = CHAT_ID) {
  const special = SPECIAL.includes(day);
  return deliver(chatId, pad(day), `${note(day)}\n\n${cfg.character.sign_off}`,
    { text: special ? `Open special door ${day}` : `Open door ${day}`, url: doorLink(day) });
}

export function sendWelcome(chatId = CHAT_ID) {
  return deliver(chatId, "welcome", cfg.welcome_message || `${NAME} here. One delivery a day, 1 to 24 December.`, null);
}
