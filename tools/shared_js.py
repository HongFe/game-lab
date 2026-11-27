#!/usr/bin/env python3
"""공용 JS 모듈(_shared/coin-system.js, rewarded-ad.js)을 게임 index.html 안에 넣거나 최신으로 바꾼다. 표준 라이브러리만.

사용:
  python3 tools/shared_js.py G003        # 한 게임에 넣기/갱신
  python3 tools/shared_js.py --all       # 이미 들어 있는 게임 전부 갱신

- 게임은 오프라인 단일 파일 규칙이라 외부 .js 를 불러오지 않는다 → <!-- nhc-shared:start --> ~ <!-- nhc-shared:end --> 사이에 통째로 넣는다
- 처음엔 </head> 바로 앞에 넣는다(게임 스크립트보다 먼저 정의되게). 그 사이는 손으로 고치지 않는다
- 오락실(arcade/index.html)은 게임이 아니라 <script src="../_shared/…"> 로 직접 불러온다
- 아이 대상 게임(G021·G022)에는 넣지 않는다(광고·코인 보상 금지 원칙)
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODS = ["coin-system.js", "rewarded-ad.js"]
START, END = "<!-- nhc-shared:start -->", "<!-- nhc-shared:end -->"
KIDS = {"G021", "G022"}


def block():
    parts = [f"<script data-shared=\"{m}\">\n{(ROOT / '_shared' / m).read_text(encoding='utf-8')}</script>" for m in MODS]
    return START + "\n" + "\n".join(parts) + "\n" + END


def apply(path):
    s = path.read_text(encoding="utf-8")
    b = block()
    if START in s:
        s2 = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: b, s, flags=re.S)
    else:
        i = s.find("</head>")
        if i < 0:
            raise SystemExit(f"{path}: </head> 없음")
        s2 = s[:i] + b + "\n" + s[i:]
    if s2 != s:
        path.write_text(s2, encoding="utf-8")
    return s2 != s


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == "--all":
        files = [f for f in ROOT.glob("G*_*/game/index.html") if START in f.read_text(encoding="utf-8")]
    else:
        files = []
        for gid in a:
            if gid in KIDS:
                raise SystemExit(f"{gid}: 아이 대상 게임에는 광고·코인을 넣지 않는다")
            hits = list(ROOT.glob(f"{gid}_*/game/index.html"))
            if not hits:
                raise SystemExit(f"{gid}: game/index.html 없음")
            files.append(hits[0])
    for f in files:
        print(("갱신" if apply(f) else "변화 없음") + f": {f.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
