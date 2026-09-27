# 90-second demo script — PositionGuard × AI assistants

**Working title:** "I gave an AI my family's location without sharing a single coordinate"

All demo data is synthetic — the simulator "My Family" group (Alex, Peter, Sarah
at Los Angeles; Fred at Home; John, Marcus, Sally undisclosed). Never use real
family members or real areas on camera.

## 0:00–0:10 — Hook (to camera)

> "I connected my family's location to an AI assistant. It never saw a single
> GPS coordinate. Here's the proof."

## 0:10–0:25 — Setup montage (screen recording, sped up)

- PositionGuard app → dev.positionguardai.com → create an **Assistant** key
- In Muse: *"Install the PositionGuard skill"* → *"Connect my PositionGuard account"* → paste key
- Caption: **"2 minutes. Read-only. Revocable."**

## 0:25–0:45 — The three questions (chat on screen)

1. *"Where is Alex?"* → "Alex is at Los Angeles." (confirmed, current)
2. *"Who is at Los Angeles?"* → "Alex, Peter, and Sarah."
3. *"Where is John?"* → "I don't know — John hasn't disclosed a position."
- Caption: **"Unknown means unknown. It never guesses."**

## 0:45–1:05 — The consent beat (live, the killer moment)

- (hold up phone, Settings screen) *"Now watch this. I turn off 'Let AI agents
  see whether I'm at an area'…"* — toggle OFF
- Back to chat: *"Where is Christer?"* → "I don't know where Christer is."
- (to camera) *"My groups and home automations still see me exactly as before.
  Only the AI went blind. That's consent infrastructure — the same idea as SSL,
  but for AI assistants."*

## 1:05–1:20 — Close (to camera)

> "PositionGuard: share your presence, not your every move."
> Links on screen: the Muse skill repo, the open-source MCP server, positionguardai.com

## Production notes

- The stale rule is demoable too: a last-known position is always reported with
  its age ("last seen 12 hours ago"), never as where someone *is*.
- Counts are honest: "at least N" when readings are stale or undisclosed.
- If anyone asks "why not just share coordinates?" — that's the entire thesis:
  the assistant doesn't need them, so it never gets them.
