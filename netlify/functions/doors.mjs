// GET /api/doors            -> which doors have been delivered so far
// GET /api/doors?door=5&k=… -> checks a Telegram link; only valid links open a door
import { keyFor, isDelivered } from "../lib/advent.mjs";

export default async (req) => {
  const url = new URL(req.url);
  const headers = { "content-type": "application/json", "cache-control": "no-store" };
  const door = parseInt(url.searchParams.get("door"), 10);
  if (door) {
    const ok = door >= 1 && door <= 24 && url.searchParams.get("k") === keyFor(door) && isDelivered(door);
    return new Response(JSON.stringify({ ok }), { headers });
  }
  const delivered = [];
  for (let d = 1; d <= 24; d++) if (isDelivered(d)) delivered.push(d);
  return new Response(JSON.stringify({ delivered }), { headers });
};

export const config = { path: "/api/doors" };
