import { readJobsDetailed, publicCounts, json, readNote, whereAmI } from "./_shared.mjs";

// Public: which times are gone. `debug` carries no customer details — only
// counts and error text — and comes out once this is diagnosed.
export default async (req) => {
  const url = new URL(req.url);

  const { jobs, errors, listed, indexed } = await readJobsDetailed();
  const out = { taken: publicCounts(jobs), v: 3 };
  if (url.searchParams.get("debug") === "1") {
    out.debug = {
      jobCount: Object.keys(jobs).length,
      blobsListed: listed,
      indexed,
      errors,
      lastSubmission: await readNote(),
      readingFrom: whereAmI(),
    };
  }
  return json(out);
};
