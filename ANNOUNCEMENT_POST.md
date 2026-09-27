# Announcement post (LinkedIn) — PositionGuard × AI assistants

I gave an AI assistant access to my family's location. It never saw a single coordinate.

That's the whole point of what we've been building with PositionGuard.

SSL didn't invent banking. It made people trust the internet *with* banking.
AI assistants are at the same inflection point: no one will trust them with
real personal context until there's consent infrastructure sitting *outside*
the model — controlled by the user, not the prompt.

So we built it, starting with the hardest signal: location.

Two things are live today:

**For Muse users** — a skill + connector that answers "where is Alex?" or
"who's at the lake house?" from area-level presence. It sees *Home*, never
47.6062° N. Two-minute setup, read-only, revocable.

**For everyone else** — an open-source MCP server (MIT):
github.com/positionguard/positionguard-mcp

And here's the part that matters: every member decides what the AI can see.
Turn off "Let AI agents see whether I'm at an area" and the assistant doesn't
get a stale location or a polite evasion — it gets *unknown*. It says
"I don't know," because the consent layer said so, not the model.

Three rules we refused to bend:
1. Unknown means unknown — never "away," never a guess.
2. A stale position is never reported as current.
3. Read-only. No messages, no history, no tracking.

Demo video to follow — the repos are live now. Would love feedback, especially
from the home-automation crowd that's been with us since the Hubitat days.

#AI #Privacy #SmartHome #MCP
