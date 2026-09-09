import { getStore } from "@netlify/blobs";

// TEMPORARY. Clears the booking counts once, then this file is deleted.
const TOKEN = "QcQqsRRQwMckU0obmYqqqTRigtX6YFv0N8CkDmjEEcQ";

export default async (req) => {
  const url = new URL(req.url);
  if (url.searchParams.get("token") !== TOKEN) {
    return new Response("no", { status: 404 });
  }
  const store = getStore("bookings");
  const before = (await store.get("taken", { type: "json" })) || {};
  await store.setJSON("taken", {});
  return new Response(JSON.stringify({ cleared: before }), {
    status: 200,
    headers: { "content-type": "application/json" },
  });
};
