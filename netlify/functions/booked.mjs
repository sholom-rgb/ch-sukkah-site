import { readJobs, publicCounts, json } from "./_shared.mjs";

// Public: which times are gone. Derived from the jobs themselves, so a job you
// give a whole window to also disappears from the public site.
export default async () => {
  const jobs = await readJobs();
  return json({ taken: publicCounts(jobs), v: 2 });
};
