#!/usr/bin/env python3
"""games.json → arcade/catalog.js (오락실에 꽂힐 게임 목록). 표준 라이브러리만.

사용: python3 tools/build_arcade.py   (build_board.py 뒤에 같이 돌린다)
- 단계가 프로토·플레이테스트·유지이고 G###_<slug>/game/index.html 이 있는 게임만 넣는다 (폐기·아이디어 제외)
- version 은 game/index.html 수정 시각(YYYY-MM-DD HH:MM). 피드백이 어느 빌드에 대한 것인지 구분한다
"""
import datetime, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOW = {"프로토", "플레이테스트", "유지"}
COLORS = ["#ff5d5d", "#4d9dff", "#ffb020", "#3cc98a", "#b07bff", "#ff7ab6", "#2fc4c4", "#8fa3ff"]


def main():
    d = json.loads((ROOT / "games.json").read_text(encoding="utf-8"))
    cat = []
    for i, g in enumerate(d.get("games", [])):
        if g.get("stage") not in SHOW:
            continue
        f = ROOT / f"{g['id']}_{g['slug']}" / "game" / "index.html"
        if not f.exists():
            continue
        ver = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        cat.append({
            "id": g["id"], "title": g["title"], "one_liner": g.get("one_liner", ""),
            "type": g.get("type", ""), "stage": g["stage"], "deadline": g.get("deadline", ""),
            "path": f"../{g['id']}_{g['slug']}/game/index.html",
            "color": g.get("color") or COLORS[i % len(COLORS)], "icon": g.get("icon", "🎮"), "version": ver,
        })
    out = ROOT / "arcade" / "catalog.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("// 생성물: python3 tools/build_arcade.py (games.json에서 만든다. 직접 고치지 않는다)\n"
                   "window.CATALOG = " + json.dumps(cat, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"arcade/catalog.js 생성: 게임 {len(cat)}개 ({', '.join(c['id'] for c in cat) or '없음'})")


if __name__ == "__main__":
    main()
