#!/usr/bin/env python3
"""games.json → board.html (게임 공장 관리 보드). 표준 라이브러리만.

사용: python3 tools/build_board.py
board.html은 생성물이다. 내용은 games.json을 고친다. 규칙은 README.md.
기본 스타일은 tools/base.css (business 허브 스타일 사본).

games[]: id(G###), slug, title, one_liner, type, type2?, refs[], why, risk,
         scores{hook,clip,replay,scope,fresh} 1~5, scores_by(claude|user),
         stage(아이디어|프로토|플레이테스트|유지|보류|폐기), created, updated,
         started?, deadline?, parent?, extended?, playtests?[{date,testers,again,median_min}],
         decision?{date,result,reason}, lessons?[]
"""
import datetime, html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
G = ROOT
BIZ = "../../agents/business"
e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
STAGES = ["아이디어", "프로토", "플레이테스트", "유지", "보류", "폐기"]   # 보류: 진행 칸·오락실에서 빠지지만 다시 꺼낼 수 있음
ACTIVE = {"프로토", "플레이테스트"}
KEYS = ["hook", "clip", "replay", "scope", "fresh"]


def base_css():
    return (pathlib.Path(__file__).with_name("base.css")).read_text(encoding="utf-8")


def folder(g):
    return G / f"{g['id']}_{g['slug']}"


def total(g):
    s = g.get("scores", {})
    return sum(int(s.get(k, 0)) for k in KEYS)


def check(d):
    errs, ids = [], set()
    meta = d.get("meta", {})
    for g in d.get("games", []):
        gid = g.get("id", "")
        if not gid.startswith("G") or gid in ids:
            errs.append(f"id 없음/중복 {gid}")
        ids.add(gid)
        if g.get("stage") not in STAGES:
            errs.append(f"{gid}: 단계 {g.get('stage')}")
        for k in KEYS:
            v = g.get("scores", {}).get(k)
            if not isinstance(v, int) or not 1 <= v <= 5:
                errs.append(f"{gid}: 점수 {k}={v}")
        if g.get("stage") != "아이디어" and not folder(g).exists():
            errs.append(f"{gid}: 폴더 없음 {folder(g).name}")
        if g.get("stage") in ACTIVE and not (folder(g) / "brief.md").exists():
            errs.append(f"{gid}: brief.md 없음")
        if g.get("stage") in ("보류", "폐기") and not (g.get("decision") or {}).get("reason"):
            errs.append(f"{gid}: {g.get('stage')} 이유 없음")
        if g.get("parent") and g["parent"] not in {x.get("id") for x in d.get("games", [])}:
            errs.append(f"{gid}: parent {g['parent']} 없음")
    act = [g["id"] for g in d.get("games", []) if g.get("stage") in ACTIVE]
    if len(act) > meta.get("wip_limit", 1):
        errs.append(f"동시 진행 한도 초과: {', '.join(act)}")
    keep = [g["id"] for g in d.get("games", []) if g.get("stage") == "유지"]
    if len(keep) > meta.get("keep_limit", 1):
        errs.append(f"유지 한도 초과: {', '.join(keep)}")
    return errs


EXTRA_CSS = r"""
:root{ --grn:#2b7a4b; --grn-bg:#e2f2e8; }
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){ --grn:#6fcf97; --grn-bg:#1c3326; } }
:root[data-theme="dark"]{ --grn:#6fcf97; --grn-bg:#1c3326; }
section{margin-top:36px} section h2{margin:0 0 4px} .lead2{color:var(--sub);font-size:13.5px;margin:0 0 12px}
.crumb{font-size:13px;color:var(--sub)} .crumb a{margin-right:6px}
.flow{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:13px;margin:14px 0}
.flow span{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:4px 10px}
.flow span b{font-family:var(--font-mono);color:var(--acc);margin-left:6px}
.flow i{color:var(--sub);font-style:normal}
.rules{display:grid;gap:8px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.rules div{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:13px}
.rules b{display:block;font-size:14px;margin-bottom:2px}
.lanes{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.lane{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px;min-height:90px}
.lane h3{margin:0 0 8px;font-size:14px;color:var(--sub)}
.gcard{border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:8px;padding:8px 10px;font-size:13px;margin-top:6px;background:var(--bg)}
.gcard b{font-size:14.5px} .gcard .id{font-family:var(--font-mono);color:var(--sub);margin-right:6px}
.gcard .dl{color:var(--red);font-weight:700}
.none{color:var(--sub);font-size:13px}
.itable{width:100%;border-collapse:collapse;font-size:13.5px}
.itable th,.itable td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}
.itable th{font-size:12px;color:var(--sub);font-weight:700}
.itable td.n{font-family:var(--font-mono);text-align:center;white-space:nowrap}
.itable td.t{font-family:var(--font-mono);font-weight:700;text-align:center}
.itable tr.pass td.t{color:var(--grn)} .itable tr.fail{opacity:.62}
.itable .ol{display:block;margin-top:2px}
.itable details summary{cursor:pointer;color:var(--acc);font-size:12.5px}
.itable details p{margin:6px 0 0;font-size:12.5px;color:var(--sub)}
.chip{display:inline-block;background:var(--chip);border-radius:6px;padding:0 7px;font-size:12px;margin-right:4px}
.passline td{border-bottom:2px dashed var(--grn)!important;padding:0!important}
.grave{display:grid;gap:8px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.grave div{border:1px dashed var(--line);border-radius:8px;padding:8px 12px;font-size:13px}
@media (max-width:640px){ .itable thead{display:none} .itable tr{display:block;border-bottom:1px solid var(--line);padding:6px 0} .itable td{display:inline-block;border:0;padding:2px 4px} .itable td.idea{display:block} }
"""


def build():
    try:
        d = json.loads((G / "games.json").read_text(encoding="utf-8"))
    except Exception as ex:
        print(f"games.json 읽기 실패: {ex}")
        return
    errs = check(d)
    for x in errs:
        print("  -", x)
    meta, rub, games = d.get("meta", {}), d.get("rubric", []), d.get("games", [])
    pass_score = meta.get("pass_score", 18)
    by = {s: [g for g in games if g.get("stage") == s] for s in STAGES}
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    today = datetime.date.today().isoformat()

    flow = " <i>→</i> ".join(f"<span>{s}<b>{len(by[s])}</b></span>" for s in STAGES[:4]) + f" <i>·</i> <span>보류<b>{len(by['보류'])}</b></span> <i>·</i> <span>폐기<b>{len(by['폐기'])}</b></span>"

    def gcard(g):
        f = folder(g)
        links = []
        if (f / "game" / "index.html").exists():
            links.append(f'<a href="{e(f.name)}/game/index.html">▶ 플레이</a>')
        for nm, lb in (("brief.md", "기획"), ("playtest.md", "테스트"), ("result.md", "결과")):
            if (f / nm).exists():
                links.append(f'<a href="{e(f.name)}/{nm}">{lb}</a>')
        dl = g.get("deadline", "")
        late = dl and dl < today and g.get("stage") in ACTIVE
        pt = g.get("playtests") or []
        pts = ""
        if pt:
            t = sum(p.get("testers", 0) for p in pt); a = sum(p.get("again", 0) for p in pt)
            pts = f"<div>테스터 {t} · 다시 {a}</div>"
        return (f'<div class="gcard"><span class="id">{e(g["id"])}</span><b>{e(g["title"])}</b>'
                f'<div>{e(g.get("one_liner", ""))}</div>'
                f'<div>{"<span class=dl>기한 초과 </span>" if late else ""}{("기한 " + e(dl)) if dl else ""}</div>{pts}'
                f'<div>{" · ".join(links)}</div></div>')

    lanes = "".join(
        f'<div class="lane"><h3>{s}</h3>{"".join(gcard(g) for g in by[s]) or "<div class=none>비어 있음</div>"}</div>'
        for s in ("프로토", "플레이테스트", "유지"))

    ideas = sorted(by["아이디어"], key=lambda g: (-total(g), g["id"]))
    head = "".join(f'<th title="{e(r["q"])}">{e(r["label"])}</th>' for r in rub)
    rows, line_done = [], False
    for g in ideas:
        t = total(g)
        if not line_done and t < pass_score:
            rows.append(f'<tr class="passline"><td colspan="{len(rub) + 3}"></td></tr>')
            line_done = True
        s = g.get("scores", {})
        types = "".join(f'<span class="chip">{e(x)}</span>' for x in (g.get("type"), g.get("type2")) if x)
        rows.append(
            f'<tr class="{"pass" if t >= pass_score else "fail"}"><td class="n">{e(g["id"])}</td>'
            f'<td class="idea"><b>{e(g["title"])}</b> {types}<span class="ol">{e(g.get("one_liner", ""))}</span>'
            f'<details><summary>왜 · 위험 · 참고</summary><p><b>왜</b> {e(g.get("why", ""))}</p>'
            f'<p><b>위험</b> {e(g.get("risk", ""))}</p><p><b>참고 장르</b> {e(" / ".join(g.get("refs", [])))}</p></details></td>'
            + "".join(f'<td class="n">{e(s.get(k, "-"))}</td>' for k in KEYS)
            + f'<td class="t">{t}</td></tr>')
    itable = (f'<table class="itable"><thead><tr><th>ID</th><th>아이디어</th>{head}<th>합</th></tr></thead>'
              f'<tbody>{"".join(rows)}</tbody></table>') if ideas else '<div class="none">아이디어 없음</div>'
    scored_by = {g.get("scores_by", "claude") for g in ideas}
    who = "사용자" if scored_by == {"user"} else "Claude 첫 판단(사용자가 다시 매길 것)"

    grave = "".join(
        f'<div><b>{"⏸ " if g.get("stage") == "보류" else ""}{e(g["id"])} {e(g["title"])}</b><br>{e((g.get("decision") or {}).get("date", ""))} · {e((g.get("decision") or {}).get("reason", ""))}'
        f'{"<br>레슨: " + e(" / ".join(g.get("lessons", []))) if g.get("lessons") else ""}</div>' for g in by["보류"] + by["폐기"])

    rules = [("동시 진행 8개", "프로토 + 플레이테스트 합쳐 8개. 재미없는 건 보류로 내려 자리를 비움"),
             ("7일 기한", "기한을 넘기면 폐기 후보. 연장은 1회 3일"),
             ("심사 18/25", "훅·클립·반복·범위·새로움 각 5점"),
             ("판정", "5명 중 3명이 시키지 않았는데 한 판 더 → 유지. 애매하면 폐기"),
             ("폐기는 지우지 않음", "폴더·ID 유지, 이유와 살릴 부품을 남김"),
             ("원작 복제 금지", "장르·메커닉 참고만. 이름·캐릭터·그림 복제 금지")]
    rules_html = '<div class="rules">' + "".join(f"<div><b>{e(a)}</b>{e(b)}</div>" for a, b in rules) + "</div>"

    body = f"""<p class="crumb"><a href="{BIZ}/ideas.html">← 아이디어 파이프라인(business)</a><a href="{BIZ}/start.html">오늘의 판</a><a href="arcade/index.html">🎮 오락실</a><a href="README.md">규칙 원문</a><a href="CLAUDE.md">프로젝트 안내</a></p>
<h1>게임 공장</h1>
<p class="sub" style="color:var(--sub)">작은 게임을 만들고, 사람에게 해 보게 하고, 숫자로 남길지 버릴지 정합니다. 실험 {e(meta.get('experiment', ''))} · 기준일 {e(meta.get('updated', '-'))} · 생성 {now}{f' · <b style="color:var(--red)">검사 오류 {len(errs)}</b>' if errs else ''}</p>
<div class="flow">{flow}</div>

<section><h2>지금 진행 중</h2>
<p class="lead2">한 번에 하나만 만듭니다. 플레이 링크는 게임 폴더의 index.html을 바로 엽니다.</p>
<div class="lanes">{lanes}</div></section>

<section><h2>아이디어 심사</h2>
<p class="lead2">점수 순. 초록 점선 위(합 {pass_score}점 이상)만 프로토로 갈 수 있습니다. 점수: {e(who)}. 칸 이름에 마우스를 올리면 질문이 보입니다.</p>
{itable}</section>

<section><h2>보류·폐기된 게임</h2>
<p class="lead2">⏸ 보류는 오락실에서 빼 둔 것(다시 꺼낼 수 있음). 폐기는 버린 이유와 레슨. 같은 실수를 다시 하지 않기 위한 기록입니다.</p>
{f'<div class="grave">{grave}</div>' if grave else '<div class="none">아직 없음</div>'}</section>

<section><h2>규칙</h2>{rules_html}</section>
"""
    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>게임 공장</title>
<style>{base_css()}{EXTRA_CSS}</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""
    (G / "board.html").write_text(page, encoding="utf-8")
    print(f"board.html 생성: 아이디어 {len(by['아이디어'])} · 진행 {sum(len(by[s]) for s in ACTIVE)} · 유지 {len(by['유지'])} · 폐기 {len(by['폐기'])} · 검사 오류 {len(errs)}")


if __name__ == "__main__":
    build()
