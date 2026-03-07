Cantus Cloudflare Worker Proxy
This folder contains a safe template proxy for Claude Vision requests.

No secret keys are committed here.

Why this exists
GitHub Pages is static hosting, so browser-to-Claude direct calls are not a reliable or secure production path. This Worker stores your Claude key server-side and forwards scan requests.

Quick setup
Install Wrangler: npm i -g wrangler
Login: wrangler login
Copy config template: cp wrangler.toml.example wrangler.toml
Set your Claude key as a Worker secret: wrangler secret put ANTHROPIC_API_KEY
Deploy: wrangler deploy
After deploy, Wrangler prints your Worker URL, for example: https://cantus-claude-proxy.your-subdomain.workers.dev

Connect Cantus frontend
Set endpoint override before Cantus app script runs:

<script>
  window.CANTUS_CLAUDE_ENDPOINT = "https://cantus-claude-proxy.your-subdomain.workers.dev/api/claude/messages";
</script>
The app will POST scans to that URL.

Security notes
Keep ANTHROPIC_API_KEY only in Worker secrets.
Do not commit real keys into any file.
Set CORS_ALLOW_ORIGIN to your real site origin in production.
Local fallback
For local development without Cloudflare depl
