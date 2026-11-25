// Runs every 15 minutes. Sends each day's door once, at that day's random time inside your window.
// Does nothing before 1 December. A small record of what was sent means a late run can never skip or repeat a door.
import { getStore } from "@netlify/blobs";
import { configured, CHAT_ID, YEAR, localNow, slotFor, sendDoor, LAST_SLOT } from "../lib/advent.mjs";

export default async () => {
  if (!configured() || !CHAT_ID) return new Response("not configured");
  const n = localNow();
  if (n.y !== YEAR || n.m !== 12 || n.d < 1 || n.d > 24) return new Response("not advent");
  const due = slotFor(n.d);
  if (n.slot < due || n.slot >= LAST_SLOT) return new Response("not yet");

  let store = null;
  try { store = getStore("advent"); } catch (e) { store = null; }
  const key = `sent-${YEAR}-${n.d}`;
  if (store) {
    if (await store.get(key)) return new Response("already sent");
    await store.set(key, "claimed");
  } else if (n.slot !== due) {
    return new Response("no record store, waiting for exact slot");
  }

  const res = await sendDoor(n.d);
  if (!res.ok) {
    if (store) await store.delete(key);
    console.log("Door", n.d, "failed:", res.description || "unknown");
    return new Response("failed");
  }
  console.log("Delivered door", n.d);
  return new Response("sent");
};

export const config = { schedule: "*/15 * * * *" };
