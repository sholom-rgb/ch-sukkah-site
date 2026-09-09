import { readJobs, writeJobs, slotKeyFromLabel, newId, json, countsFrom, CAP } from "./_shared.mjs";

export default async (req) => {
  let body;
  try { body = await req.json(); } catch { return json({ error: "bad payload" }, 400); }

  const payload = body?.payload || {};
  const data = payload.data || {};

  // A "different time" request books nothing — it becomes a job with no slot,
  // so it still shows up for you instead of being lost.
  const isBooking = payload.form_name === "sukkah-booking";
  const slot = isBooking ? slotKeyFromLabel(data.time) : null;

  const jobs = await readJobs();

  if (isBooking && slot) {
    const used = countsFrom(jobs)[slot] || 0;
    if (used >= CAP) {
      // Someone got in first. Keep the request, but unslotted, so you can call them.
      return await add(jobs, { slot: null, note: "Asked for " + (data.time || "") +
        " but it was already full. " + (data.notes || "") });
    }
  }

  return await add(jobs, {
    slot,
    note: isBooking ? (data.notes || "") : ("Wants: " + (data.when_works || "")),
  });

  async function add(all, extra) {
    const id = newId();
    all[id] = {
      id,
      slot: extra.slot,
      name: (data.name || "").trim() || "No name given",
      phone: (data.phone || "").trim(),
      addr: (data.address || "").trim(),
      type: "", size: "", hrs: "",
      status: extra.slot ? "Booked" : "Needs a time",
      charged: 0, materials: 0, helper: 0, gas: 0,
      slots: 1,
      note: (extra.note || "").trim(),
      createdAt: new Date().toISOString(),
      source: payload.form_name || "website",
    };
    await writeJobs(all);
    return json({ ok: true, id, slot: all[id].slot });
  }
};
