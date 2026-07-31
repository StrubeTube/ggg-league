"""Assemble report.html from template + retro_analysis.json + fonts."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


retro = load(os.path.join(DATA, "retro_analysis.json"))
fonts = load(os.path.join(HERE, "poppins_b64.json"))

# champions: roster_id -> display name via league metadata
champs = {}
for season in ("2025", "2024"):
    lg = load(os.path.join(DATA, f"league_{season}.json"))
    rid = int(lg["metadata"]["latest_league_winner_roster_id"])
    users = {u["user_id"]: u for u in load(os.path.join(DATA, f"users_{season}.json"))}
    rosters = load(os.path.join(DATA, f"rosters_{season}.json"))
    owner = next(r["owner_id"] for r in rosters if r["roster_id"] == rid)
    champs[season] = users[owner]["display_name"] if owner in users else "Former manager"
print("champs:", champs)

COPY = {
    "2025": {
        "title": "Three contenders bought. Two of the buys break the cap.",
        "note": ("Hart started 0-4 and sold Saquon Barkley, Drake London, and Kenneth Walker inside two weeks. "
                 "lynnkm23, at 1-4, sent Amon-Ra St. Brown and Travis Etienne to the league's eventual points leader "
                 "for nothing but 2026 picks. Under the cap, the two biggest hauls don't fit — while the balanced "
                 "PrezNix–DaBlondest star swap and the week-11 Henry deal sail through untouched."),
    },
    "2024": {
        "title": "The week-7 frenzy, replayed",
        "note": ("Five trades cleared in week 7 alone — the pick-trade deadline doesn't stop fire sales, it schedules them. "
                 "VEROVILLIANZ, at 2-4, shipped out Josh Jacobs, Kyle Pitts, and Amon-Ra St. Brown and got back two $1 players. "
                 "TommyHolland's Jacobs-and-Pitts haul lands $14 over the cap. Note what stays legal: EvanDeFilippis bought "
                 "Christian McCaffrey and Josh Allen on the way to the title, but real players went back the other way each time."),
    },
}

seasons_out = []
total_viol = total_fs = total_dumped = 0
for s in retro["seasons"]:
    season = s["season"]
    teams = []
    for tm in s["teams"]:
        name = "Former manager" if tm["team"] == "departed-manager" else tm["team"]
        teams.append({
            "team": name, "w": tm["final"]["w"], "l": tm["final"]["l"],
            "opening": tm["opening"], "peak": tm["peak"],
            "champ": name == champs[season],
        })
    trades = []
    for e in s["trades"]:
        fire = False
        for side in e["sides"]:
            w, l = map(int, side["record"].split("-"))
            net = sum(x["sal"] for x in side["out"]) - sum(x["sal"] for x in side["in"])
            cheap_in = all(x["sal"] <= 5 for x in side["in"]) if side["in"] else True
            if w < l and net >= 15 and cheap_in:
                fire = True
                total_dumped += net
        if fire:
            total_fs += 1
        if e["violation"]:
            total_viol += 1
        trades.append({
            "week": e["week"], "violation": e["violation"], "fireSale": fire,
            "sides": [{
                "team": "Former manager" if sd["team"] == "departed-manager" else sd["team"],
                "record": sd["record"], "before": sd["before"], "after": sd["after"],
                "over": sd["over"], "in": sd["in"], "picks": sd["picks_in"],
            } for sd in e["sides"]],
        })
    seasons_out.append({
        "season": season, "title": COPY[season]["title"], "note": COPY[season]["note"],
        "teams": teams, "trades": trades,
    })

baseline = sum(retro["salary_table"].values())
page_data = {
    "cap": retro["cap"],
    "salary": retro["salary_table"],
    "stats": {
        "violations": total_viol,
        "fireSales": total_fs,
        "dumped": total_dumped,
        "headroom": retro["cap"] - baseline,
    },
    "seasons": seasons_out,
}
print(f"stats: violations={total_viol} fireSales={total_fs} dumped=${total_dumped} "
      f"baseline=${baseline} headroom=${retro['cap']-baseline}")

with open(os.path.join(HERE, "report_template.html"), encoding="utf-8") as f:
    html = f.read()
html = html.replace("__FONT400__", fonts["400"])
html = html.replace("__FONT600__", fonts["600"])
html = html.replace("__FONT800__", fonts["800"])
html = html.replace("/*__DATA__*/{}", json.dumps(page_data, ensure_ascii=False))

out = os.path.join(HERE, "report.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote {out} ({len(html)//1024} KB)")
