#!/usr/bin/env python3
"""PositionGuard presence CLI with MCP-grade semantics.

Subcommands:
  list-groups            list groups (id, name)
  list-areas             list area names/ids only (no counts, no geometry)
  where-is NICKNAME      at_area | last_known_at_area | not_at_area | unknown
  who-is-at AREA         confirmed / last_known / undisclosed breakdown
  count-at AREA          member_count floor + stale/undisclosed counts

Every command prints JSON with a `status` field. `unknown` means the skill
does not know -- never "away". A stale position is never reported as current
presence. Mirrors the mapping in positionguard-mcp (src/core/mapping.ts).
"""
import sys
sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
import argparse
import json
import urllib.request
import urllib.error
from dynamic_credentials import add_surrogate_to_request, read_json_response, DynamicCredentialError

BASE = "https://api.positionguardai.com/api/v1"
ALLOWED = ["api.positionguardai.com"]
CRED = "custom.positionguard"
# Cloudflare bans Python-urllib's default User-Agent on this API (HTTP 403/1010)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

IDENTITY_KEYS = {"nickname", "user_id", "avatar_url", "name", "display_name"}
# fields proving the member's device is actively reporting (vs a withheld row)
REPORTING_KEYS = {"position_fresh", "position_age_seconds", "last_update", "safety_status", "safety_area"}


class ApiError(RuntimeError):
    pass


def emit(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def api_get(path):
    req = urllib.request.Request(
        BASE + path, headers={"Accept": "application/json", "User-Agent": UA})
    add_surrogate_to_request(req, CRED, allowed_hosts=ALLOWED)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return read_json_response(resp)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            body = ""
        raise ApiError(f"HTTP {e.code}: {body}")


def as_list(d):
    if isinstance(d, dict):
        for k in ("groups", "members"):
            if k in d:
                return d[k]
        return [d]
    return d


def nickname_of(m):
    return m.get("nickname") or m.get("name") or m.get("display_name") or "?"


def area_name_of(area):
    if isinstance(area, dict):
        return (area.get("name") or "").strip()
    return (area or "").strip()


def member_status(m):
    """Map a member row to a status dict, per positionguard-mcp semantics.

    - inside + current_area, fresh            -> at_area
    - inside + current_area, position stale   -> last_known_at_area (with age)
    - safety_status == "stale"                -> unknown/stale (never a location)
    - not inside, actively reporting          -> not_at_area
    - withheld shape / sharing off           -> unknown/not_disclosed
    """
    nick = nickname_of(m)
    inside = bool(m.get("inside"))
    area = area_name_of(m.get("current_area"))
    fresh = m.get("position_fresh")
    safety = m.get("safety_status")
    age = m.get("position_age_seconds")
    updated = m.get("last_update")
    reporting = [k for k in REPORTING_KEYS if m.get(k) is not None]

    if m.get("sharing_disabled"):
        return {"status": "unknown", "reason": "not_disclosed",
                "note": f"{nick} has sharing disabled"}
    if not inside and not area and not reporting:
        extra = set(m.keys()) - IDENTITY_KEYS - {"inside"}
        if not extra:
            # the withheld shape: identity + inside:false and nothing else.
            # consent-off, ghost, paused and lapsed all render like this.
            return {"status": "unknown", "reason": "not_disclosed",
                    "note": f"{nick} has not disclosed a position"}
    if safety == "stale":
        return {"status": "unknown", "reason": "stale",
                "note": f"{nick}'s last position is stale; not reporting it as a location",
                "area": area or None, "last_confirmed_seconds_ago": age}
    if inside and area:
        if fresh is False:
            return {"status": "last_known_at_area", "area": area,
                    "last_confirmed_seconds_ago": age, "last_update": updated,
                    "note": f"Last confirmed at {area} {age}s ago; no newer position"}
        return {"status": "at_area", "area": area,
                "last_confirmed_seconds_ago": age, "last_update": updated}
    if not inside:
        if reporting:
            return {"status": "not_at_area",
                    "note": f"{nick} is sharing but inside no defined area",
                    "last_update": updated}
        return {"status": "unknown", "reason": "not_disclosed",
                "note": f"{nick} has not disclosed a position"}
    return {"status": "unknown", "reason": "not_disclosed",
            "note": f"{nick}: no area reported"}


def resolve_groups(name=None):
    groups = [g for g in as_list(api_get("/groups")) if isinstance(g, dict)]
    if name:
        q = name.strip().lower()
        hits = [g for g in groups if (g.get("name") or "").strip().lower() == q]
        if not hits:
            raise ApiError(f"no_such_group: {name}")
        return hits
    return groups


def group_members(gid):
    return [m for m in as_list(api_get(f"/groups/{gid}/members")) if isinstance(m, dict)]


def group_area_counts(gid):
    return [a for a in as_list(api_get(f"/groups/{gid}/area-counts")) if isinstance(a, dict)]


def resolve_area(name, group_name=None):
    """Find an area by name. Returns (group, counts_row)."""
    q = name.strip().lower()
    hits = []
    for g in resolve_groups(group_name):
        for a in group_area_counts(g["id"]):
            if (a.get("area_name") or "").strip().lower() == q:
                hits.append((g, a))
    if not hits:
        raise ApiError(f"no_such_area: {name}")
    if len(hits) > 1 and not group_name:
        where = ", ".join(f"{a['area_name'].strip()} ({g['name']})" for g, a in hits)
        raise ApiError(f"ambiguous_area: '{name}' exists in several groups: {where}. Use --group.")
    return hits[0]


def cmd_list_groups(_args):
    groups = resolve_groups()
    emit({"status": "ok", "groups": [
        {"group_id": g.get("id"), "name": g.get("name")} for g in groups]})


def cmd_list_areas(args):
    out = []
    for g in resolve_groups(args.group):
        for a in group_area_counts(g["id"]):
            out.append({"area_id": a.get("area_id"),
                        "name": (a.get("area_name") or "").strip(),
                        "group_id": g.get("id"), "group_name": g.get("name")})
    emit({"status": "ok", "areas": out})


def find_members(query, groups):
    q = query.strip().lower()
    exact, partial = [], []
    for g in groups:
        for m in group_members(g["id"]):
            nick = nickname_of(m)
            rec = {"group": g.get("name"), "nickname": nick, **member_status(m)}
            nl = nick.lower()
            if nl == q:
                exact.append(rec)
            elif q in nl:
                partial.append(rec)
    return exact or partial


PRECEDENCE = {"at_area": 0, "last_known_at_area": 1, "not_at_area": 2, "unknown": 3}


def cmd_where_is(args):
    groups = resolve_groups(args.group)
    matches = find_members(args.nickname, groups)
    if not matches:
        emit({"status": "unknown", "reason": "no_such_member",
              "note": f"No member matching '{args.nickname}'"})
        return
    best = sorted(matches, key=lambda r: PRECEDENCE.get(r["status"], 9))[0]
    out = {"status": best["status"], "nickname": best["nickname"], "group": best["group"]}
    out.update({k: v for k, v in best.items() if k not in ("status", "nickname", "group")})
    if len(matches) > 1:
        out["all_matches"] = matches
    emit(out)


def cmd_who_is_at(args):
    g, counts_row = resolve_area(args.area, args.group)
    area = (counts_row.get("area_name") or "").strip()
    q = area.lower()
    confirmed, last_known = [], []
    for m in group_members(g["id"]):
        st = member_status(m)
        if (st.get("area") or "").lower() != q:
            continue
        nick = nickname_of(m)
        if st["status"] == "at_area":
            confirmed.append(nick)
        elif st["status"] == "last_known_at_area":
            last_known.append({"nickname": nick,
                               "last_confirmed_seconds_ago": st.get("last_confirmed_seconds_ago")})
    stale = counts_row.get("stale_count") or 0
    undisclosed = counts_row.get("undisclosed_count") or 0
    out = {"status": "ok", "area": area, "group": g.get("name"),
           "confirmed": confirmed}
    if last_known:
        out["last_known"] = last_known
        out["last_known_note"] = ("These are last-known positions, not current presence; "
                                  "ages are in seconds.")
    if undisclosed or stale:
        out["undisclosed_note"] = (f"{undisclosed} member(s) have not disclosed a position "
                                   f"and {stale} reading(s) are stale; the confirmed list is "
                                   f"not complete.")
    emit(out)


def cmd_count_at(args):
    g, counts_row = resolve_area(args.area, args.group)
    area = (counts_row.get("area_name") or "").strip()
    n = counts_row.get("member_count")
    stale = counts_row.get("stale_count") or 0
    undisclosed = counts_row.get("undisclosed_count") or 0
    if n is None:
        # archived area with no count: unknown, never zero
        emit({"status": "unknown", "reason": "count_unavailable",
              "area": area, "group": g.get("name"),
              "note": f"No count available for {area}; not reporting zero"})
        return
    out = {"status": "ok", "area": area, "group": g.get("name"),
           "member_count": n, "stale_count": stale, "undisclosed_count": undisclosed}
    if stale or undisclosed:
        out["note"] = (f"At least {n} at {area} "
                       f"({stale} stale, {undisclosed} undisclosed)")
    else:
        out["note"] = f"{n} at {area}"
    emit(out)


def main():
    p = argparse.ArgumentParser(prog="pg", description="PositionGuard presence (consent-gated)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-groups", help="list groups")

    a = sub.add_parser("list-areas", help="list area names (no counts, no geometry)")
    a.add_argument("--group", default=None)

    w = sub.add_parser("where-is", help="where is a member")
    w.add_argument("nickname")
    w.add_argument("--group", default=None)

    h = sub.add_parser("who-is-at", help="who is at an area")
    h.add_argument("area")
    h.add_argument("--group", default=None)

    c = sub.add_parser("count-at", help="how many at an area")
    c.add_argument("area")
    c.add_argument("--group", default=None)

    args = p.parse_args()
    try:
        {"list-groups": cmd_list_groups, "list-areas": cmd_list_areas,
         "where-is": cmd_where_is, "who-is-at": cmd_who_is_at,
         "count-at": cmd_count_at}[args.cmd](args)
    except DynamicCredentialError as e:
        emit({"status": "error", "message": f"credential error: {e}"})
        sys.exit(2)
    except ApiError as e:
        emit({"status": "error", "message": str(e)})
        sys.exit(1)
    except Exception as e:
        emit({"status": "error", "message": f"request failed: {e}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
