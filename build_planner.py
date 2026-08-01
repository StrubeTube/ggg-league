"""Assemble planner.html — keeper planner data from final 2025 rosters + 2026 traded picks."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

CFG = {"cap": 220, "budget": 45, "maxKeep": 5, "waiver": 0, "franchise": True,
       "table": {1: 30, 2: 26, 3: 22, 4: 19, 5: 16, 6: 14, 7: 12, 8: 10,
                 9: 8, 10: 7, 11: 6, 12: 5, 13: 4, 14: 3, 15: 2, 16: 2}}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def escalate(round_2025, steps):
    """Salary after moving up `steps` round-steps; past R1 climbs +$6/step."""
    r = round_2025 - steps
    if r >= 1:
        return CFG["table"][r]
    return CFG["table"][1] + 6 * (1 - r)


players_db = load("players_nfl.json")
users = {u["user_id"]: u for u in load("users_2025.json")}
rosters = load("rosters_2025.json")
draft_round = {}  # player_id -> 2025 draft round
for p in load("draftpicks_2025_1256797701333319680.json"):
    draft_round[str(p["player_id"])] = p["round"]

# ---- 2026 pick ownership: original grid minus/plus trades ----
name_of = {}
for r in rosters:
    u = users.get(r["owner_id"])
    name_of[r["roster_id"]] = u["display_name"] if u else "Former manager"

owner = {}  # (round, original_roster_id) -> current roster_id
for rnd in range(1, 17):
    for rid in name_of:
        owner[(rnd, rid)] = rid
for fname in ("tradedpicks_2024.json", "tradedpicks_2025.json"):
    path = os.path.join(DATA, fname)
    if not os.path.exists(path):
        continue
    for tp in load(fname):
        if tp["season"] == "2026" and (tp["round"], tp["roster_id"]) in owner:
            owner[(tp["round"], tp["roster_id"])] = tp["owner_id"]

picks_of = {rid: [] for rid in name_of}
for (rnd, orig), cur in owner.items():
    entry = {"r": rnd}
    if orig != cur:
        entry["from"] = name_of[orig]
    picks_of[cur].append(entry)
for rid in picks_of:
    picks_of[rid].sort(key=lambda p: (p["r"], "from" in p))

# ---- teams ----
teams = []
for r in sorted(rosters, key=lambda x: x["roster_id"]):
    rid = r["roster_id"]
    plist = []
    for pid in (r.get("players") or []):
        pdb = players_db.get(str(pid), {})
        rnd = draft_round.get(str(pid))
        entry = {"n": pdb.get("name") or f"?{pid}", "pos": pdb.get("pos") or "?",
                 "t": pdb.get("team") or ""}
        if rnd is not None:
            entry.update({"el": True, "r": rnd,
                          "k26": escalate(rnd, 1), "k27": escalate(rnd, 2)})
        else:
            entry["el"] = False
        plist.append(entry)
    plist.sort(key=lambda p: (not p["el"], p.get("k26", 999), p["n"]))

    gained = [p for p in picks_of[rid] if "from" in p]
    lost = [f"R{rnd}" for (rnd, orig), cur in owner.items() if orig == rid and cur != rid]
    note_bits = []
    if gained:
        note_bits.append("acquired: " + ", ".join(f"R{p['r']} from {p['from']}" for p in gained))
    if lost:
        note_bits.append("traded away: " + ", ".join(sorted(lost, key=lambda s: int(s[1:]))))
    s = r["settings"]
    teams.append({"name": name_of[rid], "rec": f"{s['wins']}-{s['losses']}",
                  "picks": picks_of[rid], "players": plist,
                  "picksNote": "; ".join(note_bits) if note_bits else ""})

fonts = load2 = json.load(open(os.path.join(HERE, "poppins_b64.json"), encoding="utf-8"))
page = {"cfg": CFG, "teams": teams}

with open(os.path.join(HERE, "planner_template.html"), encoding="utf-8") as f:
    html = f.read()
html = html.replace("__FONT400__", fonts["400"])
html = html.replace("__FONT600__", fonts["600"])
html = html.replace("__FONT800__", fonts["800"])
html = html.replace("/*__DATA__*/{}", json.dumps(page, ensure_ascii=False))
out = os.path.join(HERE, "planner.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

for t in teams:
    el = sum(1 for p in t["players"] if p["el"])
    print(f"{t['name']:<16} roster {len(t['players']):>2}  eligible {el:>2}  picks {len(t['picks']):>2}  {t['picksNote'][:70]}")
print(f"wrote {out} ({len(html)//1024} KB)")
