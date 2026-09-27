---
name: "positionguard"
description: "Ask about PositionGuard presence: where members are, who is at an area, how many. Consent-gated, area-level only, never coordinates. Unknown means unknown, stale is never current."
---

# Positionguard

## Purpose
Answer presence questions against the PositionGuard API using the user's stored API key (collected once via the secure connect flow). Read-only. Area-level answers only: this skill never requests coordinates and the API never returns them here.

## Tooling
One CLI: `bin/pg.py` in this skill's own directory (resolve it relative to this SKILL.md, not to any absolute path; executable as `pg`).

- `pg list-groups` — groups (id, name)
- `pg list-areas [--group NAME]` — area names/ids only; no counts, no geometry
- `pg where-is NICKNAME [--group NAME]` — one member's presence
- `pg who-is-at AREA [--group NAME]` — confirmed / last_known / undisclosed breakdown
- `pg count-at AREA [--group NAME]` — member_count floor plus stale/undisclosed counts

Every command prints JSON with a `status` field. Nickname and area matching are case-insensitive; an area name found in several groups needs `--group`.

## Auth
No credential is assumed. On first use — or whenever calls fail for lack of one — set it up with `credentials.request_api_access`: `provider: "positionguard"`, `api_hosts: ["api.positionguardai.com"]`, `auth_scheme: "api_key"`, `placement: "bearer_header"`. The user enters the key on the secure card it returns; it lands in the vault as `custom.positionguard` and is never visible to you. Never ask the user to paste a raw key in chat, set a secret environment variable, pass a secret flag, or write an auth file.

The key must be an **Assistant** key: type Assistant, scopes `presence:read`, `counts:read`, `groups:read` — never `areas:read`. An Integration key, or a key with `areas:read`, breaks the consent story and the least-privilege contract; refuse to proceed with one and say why.

A 401 or 403 is a question about the request before it is a question about the key. Check that the credential was attached at all: a request built without the helpers named under Tooling carries nothing, and that looks exactly like a wrong or under-scoped token. Only once a request that did carry the credential is still rejected, call `credentials.request_api_access` again with `reconnect: true` and the same parameters to replace it. Replacing is destructive.

Base URL is `https://api.positionguardai.com/api/v1`. The API sits behind Cloudflare, which bans Python-urllib's default User-Agent (HTTP 403, error 1010): every request must send a browser-like User-Agent header.

## Presence semantics (mirrors positionguard-mcp's mapping)
- `at_area` — member is inside the area with a fresh position.
- `last_known_at_area` — inside the area but the position is stale (`position_fresh: false`). Always reported with its age, never as current presence.
- `not_at_area` — member is actively sharing but inside no defined area.
- `unknown` — the skill does not know. Reasons: `not_disclosed` (not opted in, paused, ghost, or the withheld wire shape), `stale` (server marked the row stale), `no_such_member`, `no_such_area`, `count_unavailable`.
- `unknown` is never "away". A stale last-known position is never presented as a current location.
- Counts: `member_count` is a floor when `stale_count` or `undisclosed_count` is non-zero — report "at least N". A real 0 from the counts endpoint is a normal state; a missing count is `unknown`, never zero.
- One person can own several member rows (e.g. one per device). Don't double-count people.

## Operating Rules
1. Use this skill when the user asks for Positionguard or this provider's API.
2. Restrict authenticated requests to: api.positionguardai.com.
3. Do not print, log, or persist raw credentials.
4. If auth is missing or rejected, follow the Auth section rather than asking for a key.
5. Relay statuses with their notes and ages; never upgrade `last_known_at_area` or `unknown` into a confident location claim.
6. For the consent story to hold, the key behind the connector should be an Assistant key (members visible only if they opted into AI visibility), not an Integration key.

