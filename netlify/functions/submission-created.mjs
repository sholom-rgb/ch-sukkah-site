import { readJobs, writeJob, slotKeyFromLabel, newId, json, countsFrom, CAP, noteRun }
  from "./_shared.mjs";

export default async (req) => {
  // Every path records what happened, so a silent failure becomes visible.
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

    stage = "read";
    const jobs = await readJobs();

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
      id,
      slot: finalSlot,
      name: (data.name || "").trim() || "No name given",
      phone: (data.phone || "").trim(),
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

    stage = "verify";
    const after = await readJobs();
    const visible = Boolean(after[id]);

    await noteRun({
      stage: "done", ok: true,
      form: payload.form_name || null,
      rawTime, parsedSlot: slot, finalSlot,
      id, jobsBefore: Object.keys(jobs).length,
      jobsAfter: Object.keys(after).length,
      writeVisibleImmediately: visible,
    });
    return json({ ok: true, id, slot: finalSlot, visible });
  } catch (e) {
    await noteRun({ stage, ok: false, error: (e?.message || String(e)), stack: String(e?.stack || "").slice(0, 500) });
    return json({ error: "failed", stage, message: e?.message || String(e) }, 500);
  }
};
