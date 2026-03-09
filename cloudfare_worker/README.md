# Cantus Cloudflare Worker Proxy

This folder contains a safe template proxy for Claude Vision requests.

No secret keys are committed here.

## Why this exists

GitHub Pages is static hosting, so browser-to-Claude direct calls are not a reliable or secure production path.
This Worker stores your Claude key server-side and forwards scan requests.

## Quick setup

1. Install Wrangler:
   `npm i -g wrangler`
2. Login:
   `wrangler login`
3. Copy config template:
   `cp wrangler.toml.example wrangler.toml`
4. Set `CORS_ALLOW_ORIGIN` in `wrangler.toml` to your exact site origin.
   Example: `https://kennyg91846.github.io`
5. Set your Claude key as a Worker secret:
   `wrangler secret put ANTHROPIC_API_KEY`
6. Deploy:
   `wrangler deploy`

After deploy, Wrangler prints your Worker URL, for example:
`https://cantus-claude-proxy.your-subdomain.workers.dev`

## Connect Cantus frontend

Set endpoint override before Cantus app script runs:

```html
<script>
  window.CANTUS_CLAUDE_ENDPOINT = "https://cantus-claude-proxy.your-subdomain.workers.dev/api/claude/messages";
</script>
```

The app will POST scans to that URL.

## Security notes

- Keep `ANTHROPIC_API_KEY` only in Worker secrets.
- Do not commit real keys into any file.
- Set `CORS_ALLOW_ORIGIN` to your real site origin in production.
- Worker now hard-blocks requests if `CORS_ALLOW_ORIGIN` is blank or `*`.
- Worker also blocks requests with no `Origin` header (for example plain curl without `Origin`).

## Local fallback

For local development without Cloudflare deploy, use:
`python3 proxy_server.py 8080 --bind 0.0.0.0`
