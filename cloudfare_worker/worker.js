export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Support both root and /api/claude/messages for flexibility.
    const validPath = url.pathname === "/" || url.pathname === "/api/claude/messages";
    if (!validPath) {
      return jsonResponse({ error: { message: "Not found" } }, 404, request, env);
    }

    if (request.method === "OPTIONS") {
      return corsPreflight(request, env);
    }

    if (request.method !== "POST") {
      return jsonResponse({ error: { message: "Method not allowed" } }, 405, request, env);
    }

    if (!env.ANTHROPIC_API_KEY) {
      return jsonResponse(
        { error: { message: "ANTHROPIC_API_KEY secret is not configured." } },
        500,
        request,
        env
      );
    }

    // Optional request size guard (bytes) to protect against abuse.
    const maxBytes = Number(env.MAX_REQUEST_BYTES || 12_000_000);
    const len = Number(request.headers.get("content-length") || 0);
    if (len && len > maxBytes) {
      return jsonResponse(
        { error: { message: `Payload too large (${len} bytes). Limit is ${maxBytes} bytes.` } },
        413,
        request,
        env
      );
    }

    const bodyText = await request.text();

    const upstream = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "anthropic-version": request.headers.get("anthropic-version") || "2023-06-01",
        "x-api-key": env.ANTHROPIC_API_KEY,
      },
      body: bodyText,
    });

    const upstreamBody = await upstream.text();
    return new Response(upstreamBody, {
      status: upstream.status,
      headers: withCors(
        {
          "content-type": upstream.headers.get("content-type") || "application/json; charset=utf-8",
        },
        request,
        env
      ),
    });
  },
};

function corsPreflight(request, env) {
  return new Response(null, {
    status: 204,
    headers: withCors(
      {
        "access-control-allow-methods": "POST, OPTIONS",
        "access-control-allow-headers": "content-type, anthropic-version",
        "access-control-max-age": "86400",
      },
      request,
      env
    ),
  });
}

function jsonResponse(payload, status, request, env) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: withCors({ "content-type": "application/json; charset=utf-8" }, request, env),
  });
}

function withCors(baseHeaders, request, env) {
  const headers = new Headers(baseHeaders);
  const allowOrigin = computeAllowedOrigin(request, env);
  headers.set("access-control-allow-origin", allowOrigin);
  if (allowOrigin !== "*") {
    headers.set("vary", "Origin");
  }
  return headers;
}

function computeAllowedOrigin(request, env) {
  const configured = (env.CORS_ALLOW_ORIGIN || "*").trim();
  if (!configured || configured === "*") {
    return "*";
  }

  const requestOrigin = request.headers.get("Origin") || "";
  if (!requestOrigin) {
    return configured;
  }

  const allowed = configured
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);

  if (allowed.includes(requestOrigin)) {
    return requestOrigin;
  }

  // Fallback to first configured origin.
  return allowed[0] || "*";
}
