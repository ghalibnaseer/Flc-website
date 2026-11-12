/**
 * Shared-password gate for the case law database on Cloudflare Pages.
 * Place at functions/_middleware.js in the flc-case-law repository.
 * Set two encrypted environment variables in the Pages project:
 *   DB_USER and DB_PASSWORD
 * The check runs on Cloudflare's server before any file (including data/cases.json) is sent.
 */
export async function onRequest({ request, env, next }) {
  const header = request.headers.get("Authorization") || "";
  const [scheme, encoded] = header.split(" ");
  if (scheme === "Basic" && encoded) {
    const [user, ...rest] = atob(encoded).split(":");
    const pass = rest.join(":");
    if (env.DB_USER && env.DB_PASSWORD && user === env.DB_USER && pass === env.DB_PASSWORD) {
      const res = await next();
      const out = new Response(res.body, res);
      out.headers.set("Cache-Control", "private, no-store");
      out.headers.set("X-Robots-Tag", "noindex, nofollow");
      return out;
    }
  }
  return new Response("Members only. Please sign in.", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="FLC case law database", charset="UTF-8"', "Cache-Control": "no-store" },
  });
}
