import { getStore } from "@netlify/blobs";

const CAP = 2;

export default async (req) => {
  let body;
  try {
    body = await req.json();
  } catch {
    return new Response("bad payload", { status: 400 });
  }

  const payload = body?.payload || {};
  // Only real bookings claim a slot; a "different time" request claims nothing.
  if (payload.form_name !== "sukkah-booking") {
    return new Response("not a booking", { status: 200 });
  }

  const slot = (payload.data?.time || "").trim();
  if (!slot) return new Response("no time on submission", { status: 200 });

  const store = getStore("bookings");
  const taken = (await store.get("taken", { type: "json" })) || {};
  taken[slot] = Math.min(CAP, (taken[slot] || 0) + 1);
  await store.setJSON("taken", taken);

  return new Response(JSON.stringify({ slot, now: taken[slot] }), {
    status: 200,
    headers: { "content-type": "application/json" },
  });
};
