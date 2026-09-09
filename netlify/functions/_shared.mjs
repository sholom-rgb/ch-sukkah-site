import { getStore } from "@netlify/blobs";

export const CAP = 2;
export const KEY = "jobs";

// The public form sends a human time; the ledger works in day-slot keys.
export const SLOT_LABELS = [
  "8:00 AM – 12:00 PM",
  "12:00 PM – 4:00 PM",
  "4:00 PM – 8:00 PM",
];
const DAY_BY_LABEL = {
  "Tue Sep 15": 15, "Wed Sep 16": 16, "Thu Sep 17": 17, "Fri Sep 18": 18,
  "Tue Sep 22": 22, "Wed Sep 23": 23, "Thu Sep 24": 24,
};

/** "Tue Sep 15, 8:00 AM – 12:00 PM" -> "15-0", or null if it doesn't parse. */
export function slotKeyFromLabel(label) {
  if (!label) return null;
  const at = String(label).indexOf(",");
  if (at < 0) return null;
  const day = DAY_BY_LABEL[String(label).slice(0, at).trim()];
  // The site uses an en-dash; be forgiving about hyphens and spacing.
  const time = String(label).slice(at + 1).trim().replace(/[-–—]/g, "–").replace(/\s+/g, " ");
  const idx = SLOT_LABELS.indexOf(time);
  if (day == null || idx < 0) return null;
  return day + "-" + idx;
}

// Strong consistency: a read must see writes that already happened, or a
// booking can act on a stale picture.
export function store() {
  return getStore({ name: "bookings", consistency: "strong" });
}

const PREFIX = "job/";

/**
 * Each job is its own blob. Nothing does read-modify-write on a shared list,
 * so two bookings landing at once cannot erase each other — which is exactly
 * what a single "all the jobs" blob allowed.
 */
export async function readJobs() {
  const s = store();
  const out = {};

  // Anything left in the old single-blob format still counts.
  try {
    const legacy = await s.get(KEY, { type: "json" });
    if (legacy && typeof legacy === "object") Object.assign(out, legacy);
  } catch { /* nothing to migrate */ }

  try {
    const { blobs } = await s.list({ prefix: PREFIX });
    const loaded = await Promise.all(
      (blobs || []).map((b) =>
        s.get(b.key, { type: "json" }).catch(() => null)
      )
    );
    loaded.forEach((j) => { if (j && j.id) out[j.id] = j; });
  } catch { /* fall back to whatever the legacy blob held */ }

  return out;
}

/** Write one job. Touches only that job's key. */
export async function writeJob(job) {
  await store().setJSON(PREFIX + job.id, job);
}

/** Remove one job, from both the new layout and any legacy leftovers. */
export async function deleteJob(id) {
  const s = store();
  await s.delete(PREFIX + id).catch(() => {});
  try {
    const legacy = await s.get(KEY, { type: "json" });
    if (legacy && legacy[id]) {
      delete legacy[id];
      await s.setJSON(KEY, legacy);
    }
  } catch { /* no legacy blob */ }
}

/** How many of a window's slots are used. A job can hold both. */
export function countsFrom(jobs) {
  const out = {};
  Object.values(jobs || {}).forEach((j) => {
    if (!j || !j.slot) return;
    const n = Number(j.slots) === 2 ? 2 : 1;
    out[j.slot] = Math.min(CAP, (out[j.slot] || 0) + n);
  });
  return out;
}

/** Counts keyed by the label the public page uses. */
export function publicCounts(jobs) {
  const byKey = countsFrom(jobs);
  const out = {};
  Object.keys(byKey).forEach((k) => {
    const [d, i] = k.split("-");
    const label = Object.keys(DAY_BY_LABEL).find((L) => DAY_BY_LABEL[L] === Number(d));
    if (label) out[label + ", " + SLOT_LABELS[Number(i)]] = byKey[k];
  });
  return out;
}

/** Shared-secret gate. Set LEDGER_TOKEN in Netlify's environment variables. */
export function authorize(req) {
  const expected = process.env.LEDGER_TOKEN;
  if (!expected) {
    return { ok: false, res: json({ error: "not_configured",
      message: "LEDGER_TOKEN is not set in this site's environment variables." }, 503) };
  }
  const got = req.headers.get("x-ledger-token") || "";
  if (got !== expected) {
    return { ok: false, res: json({ error: "unauthorized" }, 401) };
  }
  return { ok: true };
}

export function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

export function newId() {
  return "j" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}
