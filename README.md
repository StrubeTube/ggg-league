# GGG Cap Keeper

Companion tooling for the GGG League (10-team, 0.5 PPR keeper league on Sleeper) — a
salary-cap layer that prices trades and keepers without leaving Sleeper.

**Sleeper league ID:** `1256797701320753152` (2025 season; chain goes back to 2020 via
`previous_league_id`). No auth needed — the Sleeper API is public and read-only.

## The ruleset (locked 2026-07-26)

- **Salary by draft round:** R1=$34, R2=$28, R3=$23, R4=$19, R5=$16, R6=$13, R7=$11,
  R8=$9, R9=$7, R10=$5, R11=$4, R12=$3, R13=$2, R14=$2, R15=$1, R16=$1. Waiver/FA adds $1.
  Draft picks carry $0.
- **$220 season cap**, checked on trades only. Drafting over is legal ("cap jail"): while
  over, every trade must end ≤$220 or reduce your salary.
- **Keepers:** up to 5, total keeper salary ≤ $45. Keepers are OFF the draft board — each
  keep removes your latest-round held pick. Immediate escalation: +1 round-step per year
  kept (past R1: +$6/step). Drafted-only (undrafted pickups are rental-only). No rental tax.
- Pre-draft keeper-rights trades are exempt; the cap sheet is born on draft night.

## Pipeline

All scripts are stdlib-only Python (no deps). Run from this directory.

1. `fetch_league.py` — pulls the full league chain (leagues, users, rosters, drafts,
   picks, transactions, traded picks, player DB) into `data/`. Re-run any time to refresh;
   delete `data/players_nfl.json` first to refresh the player DB.
2. `analyze.py` — replays 2024–2025 transactions under the cap → `data/retro_analysis.json`.
3. `build_report.py` — retro-analysis page → `report.html`
   (published: https://claude.ai/code/artifact/af1abd38-47ff-4a79-9306-315246aa4984).
4. `build_planner.py` — interactive 2026 keeper planner → `planner.html`
   (published: https://claude.ai/code/artifact/1611ed75-a5e7-44a6-884a-e015fe64a1f2).
   Rule numbers live in `CFG` at the top of this script.

`poppins_b64.json` holds the inlined webfont subsets; `*_template.html` are the page
sources with `__FONT*__` / `/*__DATA__*/{}` placeholders the build scripts fill.

## When the 2026 league renews on Sleeper

Look up the new league ID (`GET /v1/user/<user_id>/leagues/nfl/2026`, must have
`previous_league_id == 1256797701320753152`), pull its rosters/traded picks, and point
`build_planner.py` at them (it currently reads final 2025 rosters + the 2026 pick ledger
derived from `tradedpicks_2024/2025.json`).

## Roadmap (v1 in-season, ~draft time late Aug 2026)

- Live cap sheets for all 10 teams, auto-refreshed from Sleeper transactions
- Trade validator ("this deal puts Team X $12 over / is legal from cap jail")
- Draft-night salary ingestion the moment picks come in
- Longer-term: multi-league micro-SaaS ("cap layer for Sleeper") — validate via 2027
  offseason retention before charging. Reference price point: League Tycoon charges
  $11.99/team/yr for its contract layer.
