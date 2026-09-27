# Distribution plan — PositionGuard AI integrations

Goal: make AI-assistant users aware they can get consent-gated family presence
in minutes — and make the *consent* part the story, not the location part.

## Shared listing copy (reuse everywhere)

- **One line:** Consent-gated family presence for AI assistants — area-level answers, never coordinates.
- **Two lines:** PositionGuard lets an AI assistant answer "where is Hanna?" or "who's at the lake house?" It sees only what each member chose to share, says "I don't know" otherwise, and never reports a stale position as current.
- **Repo (MCP):** https://github.com/positionguard/positionguard-mcp (MIT)
- **Repo (Muse skill):** https://github.com/positionguard/muse-skill (MIT, when published)
- **Category:** Privacy / Family / AI tools

## Launch sequence (in this order)

### 1. Assets first
- [ ] Publish `positionguard/muse-skill` (this repo's contents + LICENSE).
- [ ] 90-second demo video: hook ("I gave an AI my family's location without sharing a single coordinate"), setup montage, three questions (where-is → last-known, who-is-at → honest unknown, count → "at least N"), punchline (the consent toggle).
- [ ] Announcement post / LinkedIn follow-up: the SSL analogy — consent infrastructure is to AI assistants what SSL was to internet banking.
- [ ] Test server with simulators (in progress) so all demos use synthetic data.

### 2. Launch day (coordinate these)
- [ ] **LinkedIn** — follow-up post with the video. Audience: your network, tech folks. Angle: founder + thesis.
- [ ] **Show HN** — "PositionGuard: consent-gated location for AI assistants (open-source MCP + Muse skill)". Angle: open source + the `unknown`-means-unknown design. Be ready to answer in comments.

### 3. Sustained distribution
- [ ] **MCP registries** (for positionguard-mcp):
  - Official MCP Registry (`registry.modelcontextprotocol.io`) — `mcp-publisher` with a `server.json` at repo root.
  - PulseMCP — https://www.pulsemcp.com (Submit button).
  - Glama — https://glama.ai/mcp/servers (form, manually reviewed).
  - awesome-mcp-servers — PR to `punkpeye/awesome-mcp-servers`.
  - mcp.so — paid listing ($39 one-time); decide if worth it.
  - Smithery — needs a *hosted* HTTP endpoint (the Cloudflare Worker path from the README); revisit after hosting.
- [ ] **Reddit** — r/ClaudeAI (MCP angle), r/privacy (consent-infrastructure angle). Lead with the open source + demo; respect self-promo rules, answer questions.
- [ ] **Forums (existing momentum)** — update your Hubitat + Home Assistant threads with the AI-assistant angle and the video.
- [ ] **YouTube** — the demo video lives there permanently; title it for search ("Connect family location to Muse / Claude without sharing coordinates").

### 4. Convert
Every asset points to the same 2-minute path: install app → Assistant key at
dev.positionguardai.com → install skill / MCP server → ask. Track GitHub stars,
key creation, and forum/registry referral traffic.

## Notes
- The **Assistant vs Integration key** distinction is the whole story — every
  piece of copy should say the assistant only sees what members opted into.
- Never demo with real family data; use the simulator test server.
- The Muse skill path needs no MCP support in Muse — it's pure API, and that
  "took minutes" fact is itself a selling point.
