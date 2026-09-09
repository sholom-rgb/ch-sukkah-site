import { readJobs, writeJob, deleteJob, slotKeyFromLabel, newId, json, countsFrom, CAP, noteRun }
  from "./_shared.mjs";

const DUPLICATE_WINDOW_MS = 15 * 60 * 1000;

const norm = (v) => String(v || "").toLowerCase().replace(/[^a-z0-9]/g, "");

/** Same person, same time, submitted moments ago — a back-button resubmit. */
function findDuplicate(jobs, { name, phone, slot }) {
  const now = Date.now();
  return Object.values(jobs).find((j) => {
    if (j.slot !== slot) return false;
    if (norm(j.name) !== norm(name)) return false;
    if (norm(j.phone) !== norm(phone)) return false;
    const age = now - Date.parse(j.createdAt || 0);
    return isFinite(age) && age >= 0 && age < DUPLICATE_WINDOW_MS;
  });
}

export default async (req) => {
  let stage = "start";
  try {
    let body;
    stage = "parse";
    try { body = await req.json(); }
    catch (e) {
      await noteRun({ stage, ok: false, error: "body not json: " + (e?.message || e) });
      return json({ error: "bad payload" }, 400);
    }

    const payload = body?.payload || {};
    const data = payload.data || {};
    const isBooking = payload.form_name === "sukkah-booking";
    const rawTime = data.time || "";
    const slot = isBooking ? slotKeyFromLabel(rawTime) : null;
    const name = (data.name || "").trim() || "No name given";
    const phone = (data.phone || "").trim();

    stage = "read";
    const jobs = await readJobs();

    stage = "duplicate";
    if (isBooking && slot) {
      const dup = findDuplicate(jobs, { name, phone, slot });
      if (dup) {
        await noteRun({ stage: "duplicate", ok: true, form: payload.form_name,
          rawTime, parsedSlot: slot, ignoredAsDuplicateOf: dup.id });
        return json({ ok: true, duplicate: true, id: dup.id });
      }
    }

    stage = "capacity";
    let finalSlot = slot;
    let note = isBooking ? (data.notes || "") : ("Wants: " + (data.when_works || ""));
    if (isBooking && slot && (countsFrom(jobs)[slot] || 0) >= CAP) {
      finalSlot = null;
      note = "Asked for " + rawTime + " but it was already full. " + note;
    }

    stage = "write";
    const id = newId();
    const job = {
      id, slot: finalSlot, name, phone,
      addr: (data.address || "").trim(),
      type: "", size: "", hrs: "",
      status: finalSlot ? "Booked" : "Needs a time",
      charged: 0, materials: 0, helper: 0, gas: 0,
      slots: 1,
      note: note.trim(),
      createdAt: new Date().toISOString(),
      source: payload.form_name || "website",
    };
    await writeJob(job);

    // The list read above can be a moment out of date, so a window could be
    // pushed past its capacity. Re-read and, if this job is the one that broke
    // it, move it out of the slot rather than quietly overbooking.
    stage = "reconcile";
    let demoted = false;
    if (finalSlot) {
      const after = await readJobs();
      const inSlot = Object.values(after)
        .filter((j) => j.slot === finalSlot)
        .sort((a, b) => String(a.createdAt).localeCompare(String(b.createdAt)));
      const used = inSlot.reduce((n, j) => n + (Number(j.slots) === 2 ? 2 : 1), 0);
      if (used > CAP && inSlot.length && inSlot[inSlot.length - 1].id === id) {
        job.slot = null;
        job.status = "Needs a time";
        job.note = ("Asked for " + rawTime + " but it filled up first. " + job.note).trim();
        await writeJob(job);
        demoted = true;
      }
    }

    await noteRun({
      stage: "done", ok: true, form: payload.form_name || null,
      rawTime, parsedSlot: slot, finalSlot: job.slot, demoted, id,
      jobsAfter: Object.keys(jobs).length + 1,
    });
    return json({ ok: true, id, slot: job.slot, demoted });
  } catch (e) {
    await noteRun({ stage, ok: false, error: (e?.message || String(e)),
      stack: String(e?.stack || "").slice(0, 500) });
    return json({ error: "failed", stage, message: e?.message || String(e) }, 500);
  }
};
