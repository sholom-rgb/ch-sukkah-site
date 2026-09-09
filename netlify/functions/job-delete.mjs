import { readJobs, writeJobs, authorize, json } from "./_shared.mjs";

export default async (req) => {
  const gate = authorize(req);
  if (!gate.ok) return gate.res;
  let body;
  try { body = await req.json(); } catch { return json({ error: "bad json" }, 400); }
  const jobs = await readJobs();
  if (!jobs[body.id]) return json({ error: "not_found" }, 404);
  delete jobs[body.id];
  await writeJobs(jobs);
  return json({ ok: true });
};
