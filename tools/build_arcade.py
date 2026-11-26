#!/usr/bin/env python3
"""games.json (+ arcade/ratings.json, git 기록) → arcade/catalog.js (오락실에 꽂힐 게임 목록). 표준 라이브러리만.

사용: python3 tools/build_arcade.py   (build_board.py 뒤에 같이 돌린다)
- 단계가 프로토·플레이테스트·유지이고 G###_<slug>/game/index.html 이 있는 게임만 넣는다 (폐기·아이디어 제외)
- version 은 game/index.html 수정 시각(YYYY-MM-DD HH:MM). 피드백이 어느 빌드에 대한 것인지 구분하고, 오락실의 UP 표시에도 쓴다
- note 는 그 게임 폴더의 마지막 커밋 제목에서 '—' 뒤 한 줄(짧게). 게임을 커밋한 뒤 이 스크립트를 다시 돌리면 최신 내용이 들어간다
- arcade/ratings.json (선택): 모든 테스터가 보는 평점·인기 표시. playtest-recorder/관리자가 관리자 화면 집계로 갱신한다
  {"G003": {"avg": 4.3, "n": 6, "hot": true, "src": "2026-11-26 관리자 집계"}}  — 숫자는 실제 집계만 넣는다
"""
import datetime, json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOW = {"프로토", "플레이테스트", "유지"}
COLORS = ["#ff5d5d", "#4d9dff", "#ffb020", "#3cc98a", "#b07bff", "#ff7ab6", "#2fc4c4", "#8fa3ff"]


def last_note(folder):
    try:
        s = subprocess.run(["git", "log", "-1", "--format=%s", "--", str(folder)], cwd=ROOT,
                           capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""
    if "—" in s:
        s = s.split("—", 1)[1]
    elif ":" in s:
        s = s.split(":", 1)[1]
    s = s.strip()
    return s if len(s) <= 40 else s[:39].rstrip(" ,·") + "…"


def main():
    d = json.loads((ROOT / "games.json").read_text(encoding="utf-8"))
    rf = ROOT / "arcade" / "ratings.json"
    ratings = json.loads(rf.read_text(encoding="utf-8")) if rf.exists() else {}
    cat = []
    for i, g in enumerate(d.get("games", [])):
        if g.get("stage") not in SHOW:
            continue
        folder = ROOT / f"{g['id']}_{g['slug']}"
        f = folder / "game" / "index.html"
        if not f.exists():
            continue
        ver = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        r = ratings.get(g["id"], {})
        cat.append({
            "id": g["id"], "title": g["title"], "one_liner": g.get("one_liner", ""),
            "type": g.get("type", ""), "stage": g["stage"], "deadline": g.get("deadline", ""),
            "created": g.get("started") or g.get("created", ""),
            "path": f"../{g['id']}_{g['slug']}/game/index.html",
            "color": g.get("color") or COLORS[i % len(COLORS)], "icon": g.get("icon", "🎮"), "version": ver,
            "note": last_note(folder),
            "rating": {k: r[k] for k in ("avg", "n") if k in r} or None, "hot": bool(r.get("hot")),
        })
    out = ROOT / "arcade" / "catalog.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("// 생성물: python3 tools/build_arcade.py (games.json·ratings.json·git에서 만든다. 직접 고치지 않는다)\n"
                   "window.CATALOG = " + json.dumps(cat, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"arcade/catalog.js 생성: 게임 {len(cat)}개 ({', '.join(c['id'] for c in cat) or '없음'})")


if __name__ == "__main__":
    main()
