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
const INDEX = "job-index";

/**
 * Listing keys turned out to be unreliable here — it repeatedly returned only
 * part of what had been written, which silently broke capacity checks and
 * counts. So the set of job ids is kept in one record and read by exact key,
 * which is consistent. Listing is still consulted as a safety net in case the
 * index ever misses one.
 */
async function readIndex() {
  try {
    const ids = await store().get(INDEX, { type: "json" });
    return Array.isArray(ids) ? ids : [];
  } catch {
    return [];
  }
}

/** Add an id, then confirm it stuck. Two writes at once can clobber. */
export async function addToIndex(id) {
  for (let attempt = 0; attempt < 4; attempt++) {
    const ids = await readIndex();
    if (ids.includes(id)) return true;
    await store().setJSON(INDEX, ids.concat(id));
    const check = await readIndex();
    if (check.includes(id)) return true;
  }
  return false;
}

export async function removeFromIndex(id) {
  for (let attempt = 0; attempt < 4; attempt++) {
    const ids = await readIndex();
    if (!ids.includes(id)) return true;
    await store().setJSON(INDEX, ids.filter((x) => x !== id));
    const check = await readIndex();
    if (!check.includes(id)) return true;
  }
  return false;
}

export async function readJobsDetailed() {
  const s = store();
  const out = {};
  const errors = [];

  try {
    const legacy = await s.get(KEY, { type: "json" });
    if (legacy && typeof legacy === "object") Object.assign(out, legacy);
  } catch (e) {
    errors.push("legacy-get: " + (e?.message || String(e)));
  }

  const ids = await readIndex();

  // Listing is only a backstop now; anything it finds that the index missed
  // still counts, and anything it misses the index still covers.
  let listedKeys = [];
  try {
    const res = await s.list({ prefix: PREFIX });
    listedKeys = (res?.blobs || []).map((b) => b.key.slice(PREFIX.length));
  } catch (e) {
    errors.push("list: " + (e?.message || String(e)));
  }

  const wanted = Array.from(new Set(ids.concat(listedKeys)));
  const loaded = await Promise.all(
    wanted.map((id) =>
      s.get(PREFIX + id, { type: "json" }).catch((e) => {
        errors.push("get " + id + ": " + (e?.message || String(e)));
        return null;
      })
    )
  );
  loaded.forEach((j) => { if (j && j.id) out[j.id] = j; });

  return { jobs: out, errors, listed: listedKeys.length, indexed: ids.length };
}

export async function readJobs() {
  return (await readJobsDetailed()).jobs;
}

/** Write one job and make sure the index knows about it. */
export async function writeJob(job) {
  await store().setJSON(PREFIX + job.id, job);
  await addToIndex(job.id);
}

export async function deleteJob(id) {
  const s = store();
  await removeFromIndex(id);
  await s.delete(PREFIX + id).catch(() => {});
  try {
    const legacy = await s.get(KEY, { type: "json" });
    if (legacy && legacy[id]) {
      delete legacy[id];
      await s.setJSON(KEY, legacy);
    }
  } catch { /* no legacy blob */ }
}

/** Leaves a breadcrumb so a failed submission is visible instead of silent. */
export function whereAmI() {
  return {
    deployId: process.env.DEPLOY_ID || null,
    siteId: process.env.SITE_ID || null,
    context: process.env.CONTEXT || null,
    commit: (process.env.COMMIT_REF || "").slice(0, 7) || null,
  };
}

export async function noteRun(record) {
  try {
    await store().setJSON("diag/last", {
      at: new Date().toISOString(), ...whereAmI(), ...record,
    });
  } catch { /* if even this fails, its absence is the signal */ }
}

export async function readNote() {
  try {
    return await store().get("diag/last", { type: "json" });
  } catch (e) {
    return { error: "could not read diagnostic: " + (e?.message || String(e)) };
  }
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
