import { readJobs, authorize, json } from "./_shared.mjs";

export default async (req) => {
  const gate = authorize(req);
  if (!gate.ok) return gate.res;
  const jobs = await readJobs();
  return json({ jobs: Object.values(jobs) });
};
