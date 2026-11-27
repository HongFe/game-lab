#!/usr/bin/env python3
"""공용 UI 키트(_shared/ui-kit)를 게임 index.html 안에 넣거나 최신으로 바꾼다. 표준 라이브러리만.

사용:
  python3 tools/ui_kit.py G003            # 한 게임에 넣기/갱신
  python3 tools/ui_kit.py --all           # 이미 키트가 들어 있는 게임 전부 갱신
  python3 tools/ui_kit.py --preview       # _shared/ui-kit/preview.html 만들기(부품 전시)

- 게임은 오프라인 단일 파일이라 외부 CSS를 못 불러온다 → <!-- nhc-ui-kit:start --> ~ <!-- nhc-ui-kit:end --> 사이에 통째로 넣는다
- 처음 넣을 때는 <body> 바로 뒤에 넣는다. 이후에는 표시 사이만 바꾼다(게임 코드는 건드리지 않음)
- 넣는 것: kit.css, 아이콘 <symbol> 묶음(Lucide, ISC — 라이선스 주석 포함), 작은 도우미 window.UI(icon·stars·toast)
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KIT = ROOT / "_shared" / "ui-kit"
START, END = "<!-- nhc-ui-kit:start -->", "<!-- nhc-ui-kit:end -->"

JS = """window.UI=window.UI||{};
UI.icon=function(n,c){return '<svg class="ui-icon'+(c?' '+c:'')+'" aria-hidden="true"><use href="#i-'+n+'"/></svg>';};
UI.stars=function(n,max,c){max=max||3;var s='<span class="ui-stars'+(c?' '+c:'')+'" aria-label="별 '+n+'/'+max+'">';for(var i=0;i<max;i++)s+='<svg class="ui-icon fill'+(i<n?'':' off')+'" aria-hidden="true"><use href="#i-star"/></svg>';return s+'</span>';};
UI.toast=function(m,ms){var t=document.getElementById('ui-toast');if(!t){t=document.createElement('div');t.id='ui-toast';t.className='ui-toast';t.setAttribute('role','status');document.body.appendChild(t);}t.textContent=m;t.classList.add('on');clearTimeout(UI._tt);UI._tt=setTimeout(function(){t.classList.remove('on');},ms||2000);};"""


def symbols():
    out = []
    for f in sorted((KIT / "icons").glob("*.svg")):
        s = f.read_text(encoding="utf-8")
        inner = re.search(r"<svg[^>]*>(.*)</svg>", s, re.S).group(1)
        inner = re.sub(r"\s+", " ", inner).strip()
        out.append(f'<symbol id="i-{f.stem}" viewBox="0 0 24 24">{inner}</symbol>')
    return "".join(out)


def block():
    css = (KIT / "kit.css").read_text(encoding="utf-8")
    lic = "Lucide icons (lucide-static 0.460.0) — ISC License. Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2022."
    return (f"{START}\n<style id=\"nhc-ui-kit\">\n{css}</style>\n"
            f"<!-- {lic} -->\n<svg xmlns=\"http://www.w3.org/2000/svg\" style=\"display:none\" aria-hidden=\"true\">{symbols()}</svg>\n"
            f"<script>{JS}</script>\n{END}")


def apply(path):
    s = path.read_text(encoding="utf-8")
    b = block()
    if START in s:
        s2 = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: b, s, flags=re.S)
    else:
        m = re.search(r"<body[^>]*>", s)
        if not m:
            raise SystemExit(f"{path}: <body> 없음")
        s2 = s[:m.end()] + "\n" + b + "\n" + s[m.end():]
    if s2 != s:
        path.write_text(s2, encoding="utf-8")
    return s2 != s


def game_file(gid):
    hits = list(ROOT.glob(f"{gid}_*/game/index.html"))
    if not hits:
        raise SystemExit(f"{gid}: game/index.html 없음")
    return hits[0]


def preview():
    p = KIT / "preview.html"
    body = """<div class="ui-screen" style="position:static;min-height:100vh">
<div class="ui-col">
 <p class="ui-cap">NHC UI KIT · 부품 전시</p>
 <div class="ui-col ui-center"><div class="ui-hero">📉</div><h1 class="ui-title">폭락 러너</h1><p class="ui-sub">개미에서 고래까지, 차트를 달린다</p></div>
 <button class="ui-btn primary"><svg class="ui-icon lg"><use href="#i-play"/></svg>1단계 시작</button>
 <div class="ui-row"><button class="ui-btn"><svg class="ui-icon"><use href="#i-store"/></svg>상점</button><button class="ui-btn"><svg class="ui-icon"><use href="#i-book-open"/></svg>도감 <span class="ui-badge">3</span></button></div>
 <div class="ui-stats"><div class="ui-stat"><span><svg class="ui-icon sm"><use href="#i-coins"/></svg>자산</span><b>1,000,000</b></div><div class="ui-stat"><span><svg class="ui-icon sm"><use href="#i-trophy"/></svg>최고</span><b>3단계</b></div><div class="ui-stat"><span><svg class="ui-icon sm"><use href="#i-star"/></svg>별</span><b>7/18</b></div></div>
 <div class="ui-levels" id="lv"></div>
 <div class="ui-card ui-col ui-center"><p class="ui-cap">결과</p><div id="st"></div><div class="ui-big">+212%</div><p class="ui-sub">최고 기록 갱신</p><div class="ui-row" style="width:100%"><button class="ui-btn icon"><svg class="ui-icon"><use href="#i-rotate-ccw"/></svg></button><button class="ui-btn primary" style="flex:1">다음 단계<svg class="ui-icon"><use href="#i-arrow-right"/></svg></button></div></div>
 <div class="ui-tip"><svg class="ui-icon lg"><use href="#i-lightbulb"/></svg>빨간 칸을 밟으면 수익</div>
 <div class="ui-row"><span class="ui-chip accent"><svg class="ui-icon"><use href="#i-coins"/></svg>300만</span><span class="ui-chip"><svg class="ui-icon"><use href="#i-clock"/></svg>0:42</span><span class="ui-spacer"></span><button class="ui-btn icon round"><svg class="ui-icon"><use href="#i-pause"/></svg></button></div>
 <div class="ui-meter"><i style="width:62%"></i></div>
 <button class="ui-btn ghost" onclick="document.documentElement.classList.toggle('ui-light')">밝게/어둡게</button>
</div></div>
<script>document.getElementById('lv').innerHTML=[1,2,3,4,5,6,7,8].map(function(n){return '<button class="ui-level'+(n==3?' cur':'')+(n>4?' lock':'')+'">'+(n>4?UI.icon('lock'):n)+(n<4?UI.stars(n==1?3:2):'')+'</button>'}).join('');document.getElementById('st').innerHTML=UI.stars(2,3,'big');</script>"""
    p.write_text(f"<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content=\"width=device-width,initial-scale=1,viewport-fit=cover\"><title>UI kit</title><style>body{{margin:0;background:var(--ui-bg)}}</style></head><body>\n{block()}\n{body}</body></html>", encoding="utf-8")
    print(f"미리보기: {p}")


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == "--preview":
        preview(); return
    if a[0] == "--all":
        files = [f for f in ROOT.glob("G*_*/game/index.html") if START in f.read_text(encoding="utf-8")]
    else:
        files = [game_file(x) for x in a]
    for f in files:
        print(("갱신" if apply(f) else "변화 없음") + f": {f.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
