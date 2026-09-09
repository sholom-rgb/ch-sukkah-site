import { getStore } from "@netlify/blobs";

export default async () => {
  let taken = {};
  try {
    const store = getStore("bookings");
    taken = (await store.get("taken", { type: "json" })) || {};
  } catch {
    taken = {};                     // never hide a time because the store hiccuped
  }
  return new Response(JSON.stringify({ taken }), {
    status: 200,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store, max-age=0",
    },
  });
};
