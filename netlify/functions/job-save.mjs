import { readJobs, writeJobs, authorize, json, newId, countsFrom, CAP } from "./_shared.mjs";

const NUM = ["charged", "materials", "helper", "gas"];
const STR = ["name", "phone", "addr", "type", "size", "hrs", "status", "note"];

export default async (req) => {
  const gate = authorize(req);
  if (!gate.ok) return gate.res;

  let body;
  try { body = await req.json(); } catch { return json({ error: "bad json" }, 400); }

  const jobs = await readJobs();
  const id = body.id && jobs[body.id] ? body.id : newId();
  const existing = jobs[id] || {};
  const slot = body.slot === null ? null : (body.slot || existing.slot || null);
  const wants = Number(body.slots) === 2 ? 2 : 1;

  // Don't let a save overbook a window.
  if (slot) {
    const others = { ...jobs };
    delete others[id];
    const used = countsFrom(others)[slot] || 0;
    if (used + wants > CAP) {
      return json({ error: "no_room",
        message: "That time doesn't have room for this job." }, 409);
    }
  }

  const job = { ...existing, id, slot, slots: wants };
  STR.forEach((k) => { if (k in body) job[k] = String(body[k] ?? "").trim(); });
  NUM.forEach((k) => { if (k in body) job[k] = Number(body[k]) || 0; });
  if (!job.createdAt) job.createdAt = new Date().toISOString();
  if (!job.name) job.name = "No name given";
  if (!job.status) job.status = slot ? "Booked" : "Needs a time";

  jobs[id] = job;
  await writeJobs(jobs);
  return json({ ok: true, job });
};
