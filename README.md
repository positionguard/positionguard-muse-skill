# PositionGuard skill for Muse

Gives [Muse](https://muse.ai) (Meta's AI assistant) consent-gated access to your
PositionGuard family presence — via the API, no MCP needed.

Ask things like *"where is Hanna?"*, *"who is at the lake house?"*,
*"how many people are at home?"* — and get answers that respect what each
member chose to share.

## What the assistant can and cannot do

- **Area-level presence only.** It sees *Home*, *Lake House* — never coordinates.
- **`unknown` means "I don't know."** A member who hasn't opted in, paused sharing,
  or gone stale looks identical: the assistant says it doesn't know, and never guesses.
- **Stale is never current.** A last-known position is always reported with its age,
  never as where someone is now.
- **Honest counts.** "At least N" when some readings are stale or undisclosed.
- **Read-only.** No writes, no history, no messages.

The mapping rules live in `SKILL.md` and mirror
[positionguard-mcp](https://github.com/positionguard/positionguard-mcp)'s semantics.

## Setup (about 2 minutes)

1. **Get the app.** Install PositionGuard ([positionguardai.com](https://positionguardai.com)),
   set up your family group.
2. **Create an Assistant API key.** Go to [dev.positionguardai.com](https://dev.positionguardai.com),
   sign in with the same phone number, and create a key of type **Assistant**
   (not Integration). Members are visible to the assistant only if they turned on
   *Let AI agents see whether I'm at an area* — that toggle is the consent gate,
   and this whole integration is pointless without it. The key starts with `pg_live_`;
   copy it (shown once).
3. **Install this skill.** In Muse, say:
   > Install the PositionGuard skill from https://github.com/positionguard/muse-skill
4. **Connect your account.** Then say:
   > Connect my PositionGuard account
   Muse shows a secure link — paste your API key there. It goes straight to
   secure storage; nobody (not even Muse) can read it back.
5. **Try it.** *"Where is Chris?"* / *"Who is at the lake house?"*

## Contents

- `SKILL.md` — what the skill does, auth, and the presence-semantics contract
- `bin/pg.py` — the CLI the assistant calls (`list-groups`, `list-areas`,
  `where-is`, `who-is-at`, `count-at`; all JSON with a `status` field)

## License

MIT, like the rest of the PositionGuard integrations — add your LICENSE file on publish.
