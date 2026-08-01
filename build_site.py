"""Assemble the league site: site_templates/*.html + site_data.json -> docs/."""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
TPL = os.path.join(HERE, "site_templates")
OUT = os.path.join(HERE, "docs")
os.makedirs(OUT, exist_ok=True)


def load(n):
    with open(os.path.join(DATA, n), encoding="utf-8") as f:
        return json.load(f)


site = load("site_data.json")
fonts = json.load(open(os.path.join(HERE, "poppins_b64.json"), encoding="utf-8"))
users25 = load("users_2025.json")
commish_uid = next(u["user_id"] for u in users25 if u["display_name"] == "Strubes")

# ---------------- shared CSS ----------------
CSS = """
@font-face{font-family:'Poppins';font-style:normal;font-weight:400;font-display:swap;src:url(data:font/woff2;base64,F400) format('woff2');}
@font-face{font-family:'Poppins';font-style:normal;font-weight:600;font-display:swap;src:url(data:font/woff2;base64,F600) format('woff2');}
@font-face{font-family:'Poppins';font-style:normal;font-weight:800;font-display:swap;src:url(data:font/woff2;base64,F800) format('woff2');}
:root{--bg:#0B2B26;--surface:#0E332E;--card:#103A34;--card2:#0D3630;--line:#1D4A42;--line2:#2A5A50;
--ink:#EDF7F2;--ink2:#9DC3B7;--ink3:#6E958A;--mint:#2FE6A6;--mint-ink:#062019;--mark:#17AD7A;
--coral:#E84B3F;--coral-soft:rgba(232,75,63,.14);--gold:#D9A93C;--navy:#131C4D;--navy-line:#2FE6A6;}
@media (prefers-color-scheme: light){:root{--bg:#F1F7F4;--surface:#F8FCFA;--card:#FFFFFF;--card2:#F4FAF7;
--line:#D8E7E0;--line2:#C2D8CF;--ink:#0F2F29;--ink2:#48685F;--ink3:#7A968D;--mint:#0A9B6C;--mint-ink:#FFFFFF;
--mark:#0A9B6C;--coral:#CC3D2F;--coral-soft:rgba(204,61,47,.10);--gold:#8C6A10;--navy:#1A2560;--navy-line:#0A9B6C;}}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:'Poppins',system-ui,sans-serif;line-height:1.55;margin:0}
.wrap{max-width:980px;margin:0 auto;padding:28px 16px 80px}
h1,h2,h3{text-wrap:balance;margin:0}p{margin:0}a{color:var(--mint)}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.13em;text-transform:uppercase;color:var(--mint)}
.hero{margin:18px 0 6px}
h1{font-size:clamp(30px,5.5vw,46px);font-weight:800;line-height:1.08;margin:8px 0 12px}
.lede{color:var(--ink2);font-size:15.5px;max-width:64ch}
section{margin-top:52px}
.sec-head{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
h2{font-size:22px;font-weight:800}
.sec-note{color:var(--ink2);font-size:14px;max-width:65ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.scroll{overflow-x:auto}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 16px 13px}
.tile .num{font-size:30px;font-weight:800;line-height:1.1;font-variant-numeric:tabular-nums}
.tile .num.bad{color:var(--coral)}.tile .num.good{color:var(--mint)}
.tile .lbl{font-size:12.5px;color:var(--ink2);margin-top:6px;line-height:1.45}
.chip{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:2px 10px;font-size:11.5px;font-weight:600;white-space:nowrap}
.chip.gold{color:var(--gold);border:1px solid var(--gold)}
.chip.fire{color:var(--coral);border:1px solid var(--coral)}
.chip.flag{background:var(--coral);color:#fff;letter-spacing:.04em}
.chip.even{color:var(--ink3);border:1px solid var(--line2)}
.chip.wk{background:var(--navy);color:#EDF7F2;border:1px solid var(--navy-line);letter-spacing:.06em}
.chip.mini{color:var(--mint);border:1px solid var(--mint);padding:0 7px}
.tbl{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
.tbl th{font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink3);font-weight:600;text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--line2)}
.tbl td{padding:6px 10px 6px 0;border-bottom:1px solid var(--line)}
.tbl tr:last-child td{border-bottom:none}
.mut{color:var(--ink3)}.small{font-size:11px}
.good{color:var(--mint)}.bad{color:var(--coral)}
.departed td{opacity:.55}
.duo-cards{display:grid;gap:12px}
@media(min-width:640px){.duo-cards{grid-template-columns:1fr 1fr}}
.bigcard{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;text-decoration:none;color:var(--ink);transition:border-color .12s}
.bigcard:hover{border-color:var(--mint)}
.bigcard h3{font-size:18px;font-weight:800;margin:6px 0 8px}
.bigcard p{color:var(--ink2);font-size:13.5px}
.hof,.shame{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.banner{background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid var(--gold);border-radius:12px 12px 4px 4px;padding:16px 14px;text-align:center}
.banner .byear{font-size:12px;font-weight:600;letter-spacing:.12em;color:var(--gold)}
.banner .bname{font-weight:800;font-size:15px;margin-top:6px}
.banner .bsub{font-size:11px;color:var(--ink3);margin-top:4px}
.shamecard{background:var(--card2);border:1px dashed var(--coral);border-radius:12px;padding:14px;text-align:center}
.shamecard .byear{font-size:12px;font-weight:600;letter-spacing:.12em;color:var(--coral)}
.shamecard .bname{font-weight:800;font-size:14px;margin-top:5px}
.matrix th.rot{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;padding:4px 2px;font-size:10px}
.matrix td{text-align:center;padding:5px 6px}
.matrix td.winrec{color:var(--mint);font-weight:600}
.matrix td.loserec{color:var(--coral)}
.matrix td.self{color:var(--ink3)}
.matrix th{padding-right:8px}
.seasonbox{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin-bottom:10px}
.seasonbox summary{cursor:pointer;font-size:14px}
.seasonbox summary b{font-weight:800}
.seasonbox .tbl{margin-top:10px}
.reclist{margin:0;padding-left:22px;font-size:13.5px;display:grid;gap:7px;font-variant-numeric:tabular-nums}
.reclist b{font-weight:800}
.recgrid{display:grid;gap:0}
@media(min-width:760px){.recgrid{grid-template-columns:1fr 1fr;gap:0 16px}}
.luckrow{display:grid;grid-template-columns:130px 1fr 52px;align-items:center;gap:10px;min-height:30px}
.lname{font-size:12.5px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lucktrack{position:relative;height:14px;background:var(--card2);border:1px solid var(--line);border-radius:7px}
.luckbar{position:absolute;top:2px;bottom:2px}
.luckbar.pos{background:var(--mark);border-radius:0 5px 5px 0}
.luckbar.neg{background:var(--coral);border-radius:5px 0 0 5px}
.luckmid{position:absolute;left:50%;top:-2px;bottom:-2px;width:1px;background:var(--line2)}
.lval{font-size:12px;font-weight:600;text-align:right;font-variant-numeric:tabular-nums}
.filterrow{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.tpill{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:6px 14px;font-size:13px;font-weight:600;color:var(--ink2);cursor:pointer;font-family:inherit}
.tpill.active{background:var(--mint);color:var(--mint-ink);border-color:var(--mint)}
.trades{display:grid;gap:12px}
.trade{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 16px 15px}
.trade-head{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.trade-sides{display:grid;gap:10px}
@media(min-width:640px){.trade-sides{grid-template-columns:1fr 1fr}}
.side{background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:11px 13px}
.side.losing{border-color:var(--coral)}
.side-head{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;margin-bottom:7px}
.side-team{font-weight:600;font-size:13.5px}
.side-cap{font-size:12px;color:var(--ink2);font-variant-numeric:tabular-nums}
.gets{display:flex;flex-wrap:wrap;gap:6px}
.pchip{display:inline-flex;align-items:baseline;gap:6px;background:var(--surface);border:1px solid var(--line2);border-radius:8px;padding:3px 9px;font-size:12px;font-weight:600}
.pchip .s{font-weight:400;color:var(--ink2);font-size:11px;font-variant-numeric:tabular-nums}
.pchip.pick{border-style:dashed;font-weight:400;color:var(--ink2)}
.pchip.none{border:none;background:transparent;color:var(--ink3);font-weight:400}
nav.ggg{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
nav.ggg .in{max-width:980px;margin:0 auto;display:flex;align-items:center;gap:4px;padding:10px 16px;flex-wrap:wrap}
nav.ggg .logo{width:34px;height:34px;background:var(--mint);color:var(--mint-ink);border-radius:8px;display:grid;place-items:center;font-weight:800;font-size:13px;margin-right:10px}
nav.ggg a{color:var(--ink2);text-decoration:none;font-size:13px;font-weight:600;padding:6px 11px;border-radius:8px}
nav.ggg a:hover{color:var(--ink)}
nav.ggg a.on{background:var(--card);color:var(--mint)}
footer.ggg{border-top:1px solid var(--line);margin-top:60px}
footer.ggg .in{max-width:980px;margin:0 auto;padding:18px 16px;font-size:12px;color:var(--ink3)}
.teambar{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.chiprow{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.timeline{display:grid;grid-template-columns:repeat(auto-fit,minmax(64px,1fr));gap:8px}
.tcell{background:var(--card2);border:1px solid var(--line);border-radius:10px;text-align:center;padding:8px 4px}
.tcell.gold{border-color:var(--gold)}.tcell.fire{border-color:var(--coral)}
.tyear{font-size:10.5px;color:var(--ink3);font-weight:600;letter-spacing:.08em}
.tplace{font-weight:800;font-size:15px;margin-top:3px}
.cardh{font-size:12px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--ink2);margin-bottom:10px}
.bignum{font-size:32px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.05}
.bignum small{font-size:15px;font-weight:600;color:var(--ink3)}
.bignum.over{color:var(--coral)}
.subnum{font-size:12.5px;color:var(--ink2);margin-top:4px}
.meter{height:12px;border-radius:6px;background:var(--card2);border:1px solid var(--line);margin-top:12px;position:relative;overflow:hidden}
.meter .fillbar{position:absolute;inset:0 auto 0 0;background:var(--mark);border-radius:6px 0 0 6px;transition:width .18s}
.meter .fillbar.over{background:var(--coral)}
.rostercard{margin-top:12px}
.roster{display:grid;gap:6px}
.prow{display:grid;grid-template-columns:auto 1fr auto auto auto;gap:10px;align-items:center;background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:8px 13px;cursor:pointer}
.prow.on{border-color:var(--mint)}
.prow.inel{cursor:default;opacity:.55}
.prow:focus-visible{outline:2px solid var(--mint);outline-offset:2px}
.tick{width:17px;height:17px;border-radius:5px;border:2px solid var(--line2);display:grid;place-items:center;font-size:11px;color:var(--mint-ink);flex:none}
.prow.on .tick{background:var(--mint);border-color:var(--mint)}
.pname{font-weight:600;font-size:13px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pname .meta{font-weight:400;color:var(--ink3);font-size:11px;margin-left:6px}
.rnd{font-size:11px;color:var(--ink3);font-variant-numeric:tabular-nums}
.cost{font-weight:800;font-size:13.5px;text-align:right;min-width:34px;font-variant-numeric:tabular-nums}
.next{font-size:11px;color:var(--ink3);text-align:right;min-width:48px;white-space:nowrap;font-variant-numeric:tabular-nums}
.grudges{display:grid;grid-template-columns:repeat(auto-fill,minmax(108px,1fr));gap:8px}
.gcell{background:var(--card2);border:1px solid var(--line);border-radius:10px;text-align:center;padding:9px 6px}
.gname{font-size:11px;font-weight:600;color:var(--ink2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.grec{font-weight:800;font-size:15px;margin-top:2px;font-variant-numeric:tabular-nums}
.grec.winrec{color:var(--mint)}.grec.loserec{color:var(--coral)}
.wrap.wide{max-width:1400px}
.dashhero{display:flex;flex-direction:column;gap:14px}
.idband{display:flex;gap:16px;align-items:stretch;margin-top:26px;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 20px;flex-wrap:wrap}
.archbadge{flex:none;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:var(--card2);border:1px solid var(--line2);border-radius:14px;padding:14px 22px}
.archemoji{font-size:34px;line-height:1}
.archname{font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--mint);white-space:nowrap}
.idmid{flex:1;min-width:260px;display:flex;flex-direction:column;gap:12px;justify-content:center}
.idmid .chiprow{margin-bottom:0}
.dash{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;margin-top:14px}
.dcard{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px;display:flex;flex-direction:column;gap:10px;min-width:0}
.dcard.c3{grid-column:span 3}.dcard.c4{grid-column:span 4}.dcard.c5{grid-column:span 5}
.dcard.c6{grid-column:span 6}.dcard.c7{grid-column:span 7}.dcard.c12{grid-column:span 12}
@media(max-width:1100px){.dcard.c3,.dcard.c4{grid-column:span 6}.dcard.c5,.dcard.c6,.dcard.c7{grid-column:span 12}}
@media(max-width:680px){.dcard{grid-column:span 12 !important}.wrap{padding-left:12px;padding-right:12px}}
.dcard-head{display:flex;align-items:center;justify-content:space-between;gap:8px}
.dcard-head .cardh{margin-bottom:0}
.chip.soon{background:transparent;color:var(--gold);border:1px dashed var(--gold);letter-spacing:.08em;font-size:10px}
.cardnote{font-size:11.5px;color:var(--ink3);line-height:1.5;margin-top:auto}
.kmeters{display:grid;gap:12px}
.mlabel{font-size:12px;font-weight:600;color:var(--ink2);margin-bottom:5px}
.kmeters .meter{margin-top:0}
.tallroster{max-height:430px;overflow-y:auto;padding-right:4px}
.skel{height:13px;border-radius:7px;background:var(--card2);border:1px solid var(--line)}
@media(prefers-reduced-motion:no-preference){
.skel{background:linear-gradient(90deg,var(--card2) 25%,var(--line) 50%,var(--card2) 75%);background-size:200% 100%;animation:shimmer 1.8s infinite}
@keyframes shimmer{to{background-position:-200% 0}}}
.gauge{width:120px;height:120px;border-radius:50%;margin:6px auto;display:grid;place-items:center;background:conic-gradient(var(--line2) 0deg,var(--card2) 0deg);border:1px solid var(--line);position:relative}
.gauge::before{content:'';position:absolute;inset:12px;border-radius:50%;background:var(--card)}
.gaugev{position:relative;font-weight:800;font-size:22px;color:var(--ink3);font-variant-numeric:tabular-nums}
.vsrow{display:flex;align-items:center;gap:14px;justify-content:space-between}
.vsteam{font-weight:800;font-size:16px}
.vsmark{font-size:11px;font-weight:800;color:var(--ink3);letter-spacing:.14em}
.vitals,.vrow{display:flex;flex-direction:column;gap:0}
.vrow{flex-direction:row;justify-content:space-between;gap:10px;padding:6px 0;border-bottom:1px solid var(--line);font-size:12.5px;font-variant-numeric:tabular-nums}
.vrow:last-of-type{border-bottom:none}
.vrow .tn{text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%}
.vrow.wire{font-size:12.5px;line-height:1.5}
.nemduo{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.nemcard{border-radius:12px;padding:12px 14px;background:var(--card2);border:1px solid var(--line)}
.nemcard.good2{border-color:var(--mark)}.nemcard.bad2{border-color:var(--coral)}
.nemname{font-weight:800;font-size:15px;margin-top:2px}
.nemrec{font-weight:800;font-size:19px;font-variant-numeric:tabular-nums}
.pickchips{display:flex;flex-wrap:wrap;gap:6px}
.pk{background:var(--card2);border:1px solid var(--line2);border-radius:8px;padding:3px 10px;font-size:12px;font-weight:600;font-variant-numeric:tabular-nums}
.pk .frm{font-weight:400;color:var(--ink3);font-size:11px}
.cardnote2{font-size:11.5px;color:var(--ink3);line-height:1.5}
.cbrow{display:grid;grid-template-columns:minmax(120px,150px) 1fr 92px;align-items:center;gap:10px;min-height:38px}
.cbname{display:flex;align-items:center;gap:6px;min-width:0}
.cbteam{font-size:12.5px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cbname.good .cbteam{color:var(--mint)}
.cbtrack{position:relative;height:18px;background:var(--card2);border:1px solid var(--line);border-radius:9px;overflow:hidden}
.cbseg{position:absolute;top:2px;bottom:2px;transition:width .18s,left .18s}
.cbseg.k{background:var(--mark);border-radius:7px 0 0 7px}
.cbseg.d{background:var(--mark);opacity:.4}
.cbseg.f{background:var(--mark);opacity:.15}
.cbcap{position:absolute;top:-2px;bottom:-2px;width:0;border-left:2px dashed var(--coral)}
.cbval{display:flex;flex-direction:column;align-items:flex-end;line-height:1.25;font-variant-numeric:tabular-nums}
.cbval b{font-weight:800;font-size:13.5px}
.cbval b.bad{color:var(--coral)}
.chk{display:flex;gap:12px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--line)}
.chk:last-of-type{border-bottom:none}
.chkbox{flex:none;width:20px;height:20px;border-radius:6px;border:2px solid var(--line2);display:grid;place-items:center;font-size:12px;color:var(--mint-ink);margin-top:1px}
.chk.done .chkbox{background:var(--mint);border-color:var(--mint)}
.chk.done .chktxt{text-decoration:line-through;color:var(--ink2)}
.chktxt{font-size:13.5px;font-weight:600}
.idname{font-size:19px;font-weight:800;line-height:1.25;text-align:center;max-width:260px;text-wrap:balance}
.filterrow.tight{margin-bottom:4px;gap:6px}
.tpill.sm{padding:4px 11px;font-size:11.5px}
.mcrow{display:flex;gap:18px;align-items:center}
.mcl{flex:1;display:flex;flex-direction:column;gap:10px;min-width:0}
.mcrow .gauge{flex:none;margin:0}
details.histbox{grid-column:1 / -1;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px 18px;margin-top:6px}
details.histbox summary{cursor:pointer;font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--ink2)}
details.histbox summary:hover{color:var(--mint)}
details.histbox .dash{margin-top:14px}
.ctl{padding:10px 0;border-bottom:1px solid var(--line)}
.ctl:last-of-type{border-bottom:none}
.ctlrow{display:grid;grid-template-columns:110px 1fr 84px;align-items:center;gap:10px}
.ctlname{font-size:12.5px;font-weight:600;color:var(--ink2)}
.ctlval{font-size:12.5px;font-weight:800;text-align:right;font-variant-numeric:tabular-nums}
input[type=range]{width:100%;accent-color:var(--mint);background:transparent}
input[type=range]:disabled{opacity:.35}
.salary-mini{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
.tmini{display:flex;flex-direction:column;align-items:center;background:var(--card2);border:1px solid var(--line);border-radius:6px;padding:3px 6px;min-width:34px}
.tmini b{font-size:11.5px;font-weight:800;font-variant-numeric:tabular-nums}
.tmini i{font-style:normal;font-size:9px;color:var(--ink3);letter-spacing:.04em}
"""
CSS = CSS.replace("F400", fonts["400"]).replace("F600", fonts["600"]).replace("F800", fonts["800"])
with open(os.path.join(OUT, "ggg.css"), "w", encoding="utf-8") as f:
    f.write(CSS)
import hashlib
css_v = hashlib.md5(CSS.encode()).hexdigest()[:8]

NAV_LINKS = [("index.html", "Home"), ("history.html", "History"), ("records.html", "Records"),
             ("drafts.html", "Drafts"), ("trades.html", "Trades"),
             ("cap-planner.html", "Planner"), ("cap-report.html", "The Case")]


def nav(active):
    links = "".join(f'<a href="{h}" class="{"on" if h == active else ""}">{t}</a>' for h, t in NAV_LINKS)
    return f'<nav class="ggg"><div class="in"><span class="logo">GGG</span>{links}</div></nav>'


FOOT = ('<footer class="ggg"><div class="in">GGG League · data from the Sleeper API · '
        f'stats computed {site["generated"]} · regular-season records unless noted · '
        'grudges update automatically</div></footer>')

# ---------------- keeper-planner team data (same order/sort as cap-planner) ----------------
CFG = {"cap": 220, "budget": 45, "maxKeep": 5, "waiver": 0, "franchise": True,
       "table": {1: 30, 2: 26, 3: 22, 4: 19, 5: 16, 6: 14, 7: 12, 8: 10,
                 9: 8, 10: 7, 11: 6, 12: 5, 13: 4, 14: 3, 15: 2, 16: 2}}
STEEP_TABLE = {1: 34, 2: 28, 3: 23, 4: 19, 5: 16, 6: 13, 7: 11, 8: 9,
               9: 7, 10: 5, 11: 4, 12: 3, 13: 2, 14: 2, 15: 1, 16: 1}


def escalate(round_2025, steps):
    r = round_2025 - steps
    return CFG["table"][r] if r >= 1 else CFG["table"][1] + 6 * (1 - r)


def planner_teams():
    players_db = load("players_nfl.json")
    users = {u["user_id"]: u for u in load("users_2025.json")}
    rosters = load("rosters_2025.json")
    draft_round = {str(p["player_id"]): p["round"]
                   for p in load("draftpicks_2025_1256797701333319680.json")}
    name_of = {r["roster_id"]: (users.get(r["owner_id"]) or {}).get("display_name", "Former manager")
               for r in rosters}
    owner = {(rnd, rid): rid for rnd in range(1, 17) for rid in name_of}
    for fname in ("tradedpicks_2024.json", "tradedpicks_2025.json"):
        for tp in load(fname):
            if tp["season"] == "2026" and (tp["round"], tp["roster_id"]) in owner:
                owner[(tp["round"], tp["roster_id"])] = tp["owner_id"]
    picks_of = {rid: [] for rid in name_of}
    for (rnd, orig), cur in owner.items():
        e = {"r": rnd}
        if orig != cur:
            e["from"] = name_of[orig]
        picks_of[cur].append(e)
    for rid in picks_of:
        picks_of[rid].sort(key=lambda p: (p["r"], "from" in p))
    teams = []
    for r in sorted(rosters, key=lambda x: x["roster_id"]):
        plist = []
        for pid in (r.get("players") or []):
            pdb = players_db.get(str(pid), {})
            rnd = draft_round.get(str(pid))
            e = {"n": pdb.get("name") or f"?{pid}", "pos": pdb.get("pos") or "?",
                 "t": pdb.get("team") or ""}
            if rnd is not None:
                e.update({"el": True, "r": rnd, "k26": escalate(rnd, 1), "k27": escalate(rnd, 2)})
            else:
                e["el"] = False
            plist.append(e)
        plist.sort(key=lambda p: (not p["el"], p.get("k26", 999), p["n"]))
        teams.append({"name": name_of[r["roster_id"]], "picks": picks_of[r["roster_id"]],
                      "players": plist})
    return teams


career = site["career"]
finishes = {}
for sn in site["seasons"]:
    for i, t in enumerate(sn["standings"]):
        finishes.setdefault(t["name"], []).append(
            {"s": sn["season"], "place": i + 1,
             "champ": t["name"] == sn["champ"], "toilet": t["name"] == sn["toilet"]})
slices = {
    "index.html": {"cfg": CFG, "teams": planner_teams(), "career": career,
                   "h2h": site["h2h"], "finishes": finishes,
                   "commishUserId": commish_uid, "leagueId2025": "1256797701320753152"},
    "history.html": {"seasons": site["seasons"], "career": career, "h2h": site["h2h"]},
    "records.html": {"records": site["records"], "career": career},
    "drafts.html": {"drafts": site["drafts"]},
    "trades.html": {"trades": site["trades"]},
    "lab.html": {"teams": planner_teams(), "steep": STEEP_TABLE, "adopted": CFG["table"],
                 "defaults": {"cap": CFG["cap"], "budget": CFG["budget"], "maxKeep": CFG["maxKeep"]}},
}

for page, data in slices.items():
    with open(os.path.join(TPL, page), encoding="utf-8") as f:
        html = f.read()
    html = html.replace("__NAV__", nav(page)).replace("__FOOT__", FOOT)
    html = html.replace('href="ggg.css"', f'href="ggg.css?v={css_v}"')
    html = html.replace("/*__DATA__*/{}", json.dumps(data, ensure_ascii=False))
    with open(os.path.join(OUT, page), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"built {page} ({os.path.getsize(os.path.join(OUT, page))//1024} KB)")

# cap tools: copy the built artifacts in (generated in this directory by
# build_planner.py / build_report.py)
for src, dst in (("planner.html", "cap-planner.html"), ("report.html", "cap-report.html")):
    sp = os.path.join(HERE, src)
    if os.path.exists(sp):
        shutil.copy(sp, os.path.join(OUT, dst))
        print(f"copied {dst}")

open(os.path.join(OUT, ".nojekyll"), "w").close()
print("site assembled ->", OUT)
