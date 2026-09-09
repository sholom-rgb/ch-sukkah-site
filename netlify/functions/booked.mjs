import { readJobsDetailed, publicCounts, json, readNote, whereAmI, store } from "./_shared.mjs";

// Public: which times are gone. `debug` carries no customer details — only
// counts and error text — and comes out once this is diagnosed.
export default async (req) => {
  const url = new URL(req.url);

  // Temporary: fetch one job by its exact key, to compare a direct read
  // against what listing returns.
  const probe = url.searchParams.get("probe");
  if (probe) {
    const out = { probe };
    try {
      out.direct = await store().get("job/" + probe, { type: "json" });
    } catch (e) { out.directError = e?.message || String(e); }
    try {
      const res = await store().list({ prefix: "job/" });
      out.listKeys = (res?.blobs || []).map((b) => b.key);
    } catch (e) { out.listError = e?.message || String(e); }
    try {
      const all = await store().list();
      out.allKeys = (all?.blobs || []).map((b) => b.key);
    } catch (e) { out.allError = e?.message || String(e); }
    return json(out);
  }

  const { jobs, errors, listed } = await readJobsDetailed();
  const out = { taken: publicCounts(jobs), v: 3 };
  if (url.searchParams.get("debug") === "1") {
    out.debug = {
      jobCount: Object.keys(jobs).length,
      blobsListed: listed,
      errors,
      lastSubmission: await readNote(),
      readingFrom: whereAmI(),
    };
  }
  return json(out);
};
