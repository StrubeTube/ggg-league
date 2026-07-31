"""Cap Keeper retro-analysis v2 — pre-draft trades excluded, clean summary JSON.

Rules simulated:
  - Salary by draft round (keepers included; their escalated round = their salary)
  - Waiver/FA adds: $1
  - Picks carry $0 salary
  - Cap $200, checked on trades only, from draft day onward
"""
import json
import os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CAP = 200
SALARY = {1: 34, 2: 28, 3: 23, 4: 19, 5: 16, 6: 13, 7: 11, 8: 9,
          9: 7, 10: 5, 11: 4, 12: 3, 13: 2, 14: 2, 15: 1, 16: 1}
WAIVER_SALARY = 1


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


players = load("players_nfl.json")


def pname(pid):
    p = players.get(str(pid))
    return p["name"] if p else f"?{pid}"


def records_through(matchups, week):
    rec = {}
    for wk_s, items in matchups.items():
        if int(wk_s) >= week:
            continue
        by_m = {}
        for m in items:
            if m.get("matchup_id") is not None:
                by_m.setdefault(m["matchup_id"], []).append(m)
        for pair in by_m.values():
            if len(pair) != 2:
                continue
            a, b = pair
            if (a.get("points") or 0) == (b.get("points") or 0) == 0:
                continue
            win, lose = (a, b) if a["points"] > b["points"] else (b, a)
            rec.setdefault(win["roster_id"], [0, 0])[0] += 1
            rec.setdefault(lose["roster_id"], [0, 0])[1] += 1
    return rec


def simulate(season):
    users = {u["user_id"]: u for u in load(f"users_{season}.json")}
    rosters = load(f"rosters_{season}.json")
    label, finals = {}, {}
    for r in rosters:
        u = users.get(r["owner_id"])
        label[r["roster_id"]] = u["display_name"] if u else "departed-manager"
        s = r["settings"]
        finals[r["roster_id"]] = {"w": s["wins"], "l": s["losses"], "pf": s.get("fpts", 0)}

    matchups = load(f"matchups_{season}.json")
    drafts = load(f"drafts_{season}.json")
    draft = drafts[0]
    draft_end = draft.get("last_picked") or draft.get("start_time")
    picks = load(f"draftpicks_{season}_{draft['draft_id']}.json")

    sal = {r["roster_id"]: {} for r in rosters}
    for p in picks:
        if p.get("roster_id") is not None:
            sal[p["roster_id"]][str(p["player_id"])] = SALARY[p["round"]]
    opening = {rid: sum(v.values()) for rid, v in sal.items()}
    peak = dict(opening)

    tx_all = []
    for wk, items in load(f"transactions_{season}.json").items():
        for t in items:
            if t["status"] == "complete":
                tx_all.append((int(wk), t))
    tx_all.sort(key=lambda x: x[1]["status_updated"])

    predraft_trades, events = [], []
    for wk, t in tx_all:
        adds = t.get("adds") or {}
        drops = t.get("drops") or {}
        if t["type"] == "trade" and t["status_updated"] < draft_end:
            sides = {}
            for rid in t["roster_ids"]:
                got_p = [pname(p) for p, r2 in adds.items() if r2 == rid]
                got_k = sum(1 for dp in t.get("draft_picks") or [] if dp["owner_id"] == rid)
                sides[label[rid]] = {"players": got_p, "picks": got_k}
            predraft_trades.append(sides)
            continue
        if t["type"] in ("waiver", "free_agent"):
            for pid, rid in drops.items():
                sal[rid].pop(str(pid), None)
            for pid, rid in adds.items():
                sal[rid][str(pid)] = WAIVER_SALARY
                tot = sum(sal[rid].values())
                peak[rid] = max(peak[rid], tot)
        elif t["type"] == "trade":
            rec = records_through(matchups, wk)
            before = {rid: sum(sal[rid].values()) for rid in t["roster_ids"]}
            moved = {rid: {"in": [], "out": []} for rid in t["roster_ids"]}
            for pid, rid in adds.items():
                pid = str(pid)
                src = drops.get(pid)
                s = sal.get(src, {}).pop(pid, WAIVER_SALARY) if src is not None else WAIVER_SALARY
                sal[rid][pid] = s
                moved[rid]["in"].append({"name": pname(pid), "sal": s})
                if src is not None:
                    moved[src]["out"].append({"name": pname(pid), "sal": s})
            npicks = {rid: [] for rid in t["roster_ids"]}
            for dp in t.get("draft_picks") or []:
                if dp["owner_id"] in npicks:
                    npicks[dp["owner_id"]].append(f"{dp['season']} R{dp['round']}")
            after = {rid: sum(sal[rid].values()) for rid in t["roster_ids"]}
            for rid in t["roster_ids"]:
                peak[rid] = max(peak[rid], after[rid])

            # fire-sale classification: a side that sheds >=$15 net salary and
            # receives only picks and/or players worth <= $5 each
            fire_seller = None
            for rid in t["roster_ids"]:
                net = sum(x["sal"] for x in moved[rid]["out"]) - sum(x["sal"] for x in moved[rid]["in"])
                cheap_in = all(x["sal"] <= 5 for x in moved[rid]["in"]) if moved[rid]["in"] else True
                if net >= 15 and cheap_in:
                    fire_seller = rid
            events.append({
                "week": wk,
                "sides": [{
                    "team": label[rid],
                    "record": "-".join(map(str, rec.get(rid, [0, 0]))),
                    "before": before[rid], "after": after[rid],
                    "over": after[rid] > CAP,
                    "in": moved[rid]["in"], "out": moved[rid]["out"],
                    "picks_in": npicks[rid],
                    "is_fire_seller": rid == fire_seller,
                } for rid in t["roster_ids"]],
                "fire_sale": fire_seller is not None,
                "violation": any(after[rid] > CAP for rid in t["roster_ids"]),
            })

    return {
        "season": season,
        "teams": [{"team": label[rid], "final": finals[rid],
                   "opening": opening[rid], "peak": peak[rid]}
                  for rid in sorted(opening)],
        "predraft_trades": predraft_trades,
        "trades": events,
    }


out = {"cap": CAP, "salary_table": SALARY, "seasons": [simulate("2025"), simulate("2024")]}
with open(os.path.join(DATA, "retro_analysis.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)

for s in out["seasons"]:
    print(f"\n=== {s['season']} ===")
    print(f"pre-draft keeper-rights trades excluded: {len(s['predraft_trades'])}")
    print("opening / peak cap sheets:")
    for tm in s["teams"]:
        f_ = tm["final"]
        star = " <-- over cap at peak" if tm["peak"] > CAP else ""
        print(f"  {tm['team']:<18} open ${tm['opening']:>3}  peak ${tm['peak']:>3}  ({f_['w']}-{f_['l']}){star}")
    print("in-season trades:")
    for e in s["trades"]:
        tags = []
        if e["violation"]:
            tags.append("OVER CAP")
        if e["fire_sale"]:
            tags.append("FIRE SALE")
        tag = f"  [{' + '.join(tags)}]" if tags else ""
        print(f"  Week {e['week']}:{tag}")
        for side in e["sides"]:
            ins = ", ".join(f"{x['name']} ${x['sal']}" for x in side["in"]) or "-"
            pk = (" + " + ", ".join(side["picks_in"])) if side["picks_in"] else ""
            print(f"    {side['team']:<18}({side['record']}) ${side['before']}->${side['after']}"
                  f"{' OVER' if side['over'] else ''}: {ins}{pk}")
