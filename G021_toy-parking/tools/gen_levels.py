#!/usr/bin/env python3
"""G021 꼬마 주차요원 — 레벨 30개 생성기 (G001 gen_levels.py 틀 재사용).

사용: python3 tools/gen_levels.py [--seed 21]      (레벨 생성 → game/levels.json + index.html 주입)
      python3 tools/gen_levels.py --only 13,14 --seed 1314   (그 레벨만 다시 뽑기)
      python3 tools/gen_levels.py --inject-only   (levels.json → index.html만)
표준 라이브러리만.

규칙 (게임과 같아야 함)
- N×N 격자. 차는 자기 방향으로만 민다. 한 번 끌기 = 이동 1 (몇 칸이든)
- 색 차(C)마다 자기 줄 위에 주차칸(tgt). 모든 색 차가 tgt에 있으면 끝. 회색 차(G)는 칸 없음. 🚧 고깔은 안 움직임
방법
- 차를 무작위로 놓고 그 배치의 '도달 가능한 상태 전체'를 BFS로 펼친 뒤, 목표 상태들에서 거꾸로 BFS해서
  거리 표를 만든다. 그 안에서 목표 최소 수(±1)인 상태를 시작 배치로 고른다
"""
import json, math, pathlib, random, re, sys
from collections import deque

HERE = pathlib.Path(__file__).resolve().parent.parent

# 레벨 표 (brief.md): (격자, 색 차, 회색 차, 고깔, 최소)
TABLE = [
    (4, 1, 0, 0, 1), (4, 1, 1, 0, 2), (4, 1, 2, 0, 3), (4, 2, 1, 0, 3), (4, 2, 2, 0, 4),
    (5, 2, 2, 0, 4), (5, 2, 3, 0, 5), (5, 2, 3, 0, 6), (5, 2, 4, 0, 6), (5, 3, 3, 0, 7),
    (5, 3, 3, 1, 7), (5, 3, 4, 1, 8), (5, 3, 4, 1, 9), (5, 3, 5, 1, 9), (5, 3, 4, 1, 10),
    (6, 3, 5, 1, 9), (6, 3, 6, 1, 10), (6, 3, 6, 2, 11), (6, 3, 7, 2, 12), (6, 4, 6, 1, 12),
    (6, 4, 6, 2, 13), (6, 4, 7, 2, 14), (6, 4, 7, 2, 14), (6, 4, 8, 2, 15), (6, 4, 7, 2, 16),
    (6, 5, 6, 2, 16), (6, 5, 7, 2, 17), (6, 5, 7, 3, 18), (6, 5, 8, 3, 19), (6, 5, 8, 3, 20),
]
TRUCK_FROM, COLOR_TRUCK_FROM = 7, 23
PARKED = {15: 1, 25: 2}   # 처음부터 칸에 든 색 차 수 (이 레벨만)


def cells(r, c, ln, d):
    return [(r, c + k) if d == "H" else (r + k, c) for k in range(ln)]


class Model:
    def __init__(self, n, cars, cones):
        self.n, self.cars, self.cones = n, cars, set(map(tuple, cones))
        self.fixed = [(r if d == "H" else c) for r, c, ln, d, *_ in cars]

    def grid(self, pos):
        n = self.n
        g = [[-1] * n for _ in range(n)]
        for (r, c) in self.cones:
            g[r][c] = -2
        for i, (r0, c0, ln, d, *_) in enumerate(self.cars):
            r, c = (self.fixed[i], pos[i]) if d == "H" else (pos[i], self.fixed[i])
            for rr, cc in cells(r, c, ln, d):
                g[rr][cc] = i
        return g

    def moves(self, pos):
        g, n, out = self.grid(pos), self.n, []
        for i, (r0, c0, ln, d, *_) in enumerate(self.cars):
            f = self.fixed[i]
            for st in (-1, 1):
                k = pos[i]
                while True:
                    k += st
                    head = k if st < 0 else k + ln - 1
                    if head < 0 or head >= n:
                        break
                    if (g[f][head] if d == "H" else g[head][f]) != -1:
                        break
                    out.append((i, k, pos[:i] + (k,) + pos[i + 1:]))
        return out

    def goal(self, pos):
        return all(pos[i] == c[6] for i, c in enumerate(self.cars) if c[4] == "C")


def component(m, start, cap=400_000):
    seen = {start: None}
    q = deque([start])
    adj = {}
    while q:
        p = q.popleft()
        nb = [np for _, _, np in m.moves(p)]
        adj[p] = nb
        for np in nb:
            if np not in seen:
                seen[np] = 1
                if len(seen) > cap:
                    return None
                q.append(np)
    return adj


def dist_to_goal(m, adj, frozen=()):
    dist = {}
    q = deque()
    for p in adj:
        if m.goal(p):
            dist[p] = 0
            q.append(p)
    while q:
        p = q.popleft()
        for np in adj[p]:
            if np in dist:
                continue
            if any(np[i] != p[i] for i in frozen):
                continue
            dist[np] = dist[p] + 1
            q.append(np)
    return dist


def min_from(m, start, frozen=(), lock_parked=False):
    """frozen 차는 움직이지 않는 조건에서 최소 수 (없으면 None).
    lock_parked: 칸에 들어간 색 차는 다시 빼지 않는다(15레벨 전 규칙)."""
    if m.goal(start):
        return 0
    seen = {start}
    q = deque([(start, 0)])
    while q:
        p, d = q.popleft()
        for i, _, np in m.moves(p):
            if i in frozen or np in seen:
                continue
            if lock_parked and m.cars[i][4] == "C" and p[i] == m.cars[i][6]:
                continue
            if m.goal(np):
                return d + 1
            seen.add(np)
            q.append((np, d + 1))
    return None


def random_layout(rng, lvno, n, nc, ng, ncone):
    """cars: [r, c, len, dir, kind, color, tgt]. 위치는 임시(나중에 시작 상태로 바꿈)."""
    occ = set()
    cones = []
    for _ in range(ncone):
        for _t in range(50):
            r, c = rng.randrange(n), rng.randrange(n)
            if (r, c) not in occ:
                occ.add((r, c)); cones.append([r, c]); break
        else:
            return None
    specs = []
    for j in range(nc):
        ln = 3 if (lvno >= COLOR_TRUCK_FROM and j == nc - 1) else 2
        specs.append(("C", j, ln))
    for j in range(ng):
        ln = 3 if (lvno >= TRUCK_FROM and rng.random() < (0.55 if lvno == TRUCK_FROM and j == 0 else 0.25)) else 2
        specs.append(("G", -1, ln))
    if lvno == TRUCK_FROM and not any(s[2] == 3 and s[0] == "G" for s in specs):
        specs[nc] = ("G", -1, 3)
    cars = []
    for kind, col, ln in specs:
        for _t in range(80):
            d = rng.choice("HV")
            r = rng.randrange(n) if d == "H" else rng.randrange(n - ln + 1)
            c = rng.randrange(n - ln + 1) if d == "H" else rng.randrange(n)
            cs = cells(r, c, ln, d)
            if any(x in occ for x in cs):
                continue
            tgt = -1
            if kind == "C":
                fixed = r if d == "H" else c
                opts = []
                for t in range(n - ln + 1):
                    tc = cells(fixed, t, ln, "H") if d == "H" else cells(t, fixed, ln, "V")
                    if not any(x in set(map(tuple, cones)) for x in tc):
                        opts.append(t)
                if not opts:
                    continue
                tgt = rng.choice(opts)
            occ.update(cs)
            cars.append([r, c, ln, d, kind, col, tgt])
            break
        else:
            return None
    return cars, cones


def make_level(rng, lvno, tries=4000):
    n, nc, ng, ncone, target = TABLE[lvno - 1]
    npark = PARKED.get(lvno, 0)
    best = None
    for _ in range(tries):
        lay = random_layout(rng, lvno, n, nc, ng, ncone)
        if not lay:
            continue
        cars, cones = lay
        m = Model(n, cars, cones)
        start = tuple((c if d == "H" else r) for r, c, ln, d, *_ in cars)
        adj = component(m, start)
        if not adj:
            continue
        dist = dist_to_goal(m, adj)
        if start not in dist:
            continue
        cidx = [i for i, c in enumerate(cars) if c[4] == "C"]
        cands = []
        for p, dd in dist.items():
            if abs(dd - target) > 1:
                continue
            parked = [i for i in cidx if p[i] == cars[i][6]]
            if len(parked) != npark:
                continue
            cands.append((abs(dd - target), p, dd, parked))
        rng.shuffle(cands)
        cands.sort(key=lambda x: x[0])
        for err, p, dd, parked in cands[:40]:
            # 1레벨: 첫 끌기가 어디든 1~2수 안
            if lvno == 1 and any(dist.get(np, 99) > 1 for _, _, np in m.moves(p)):
                continue
            # 15레벨('빼고 다시') 소개 전: 칸에 넣은 차를 다시 빼지 않고도 최소 해가 있어야 함
            if lvno < 15 and min_from(m, p, lock_parked=True) != dd:
                continue
            if npark:
                # 칸에 든 차는 모두 한 번은 나와야 풀림
                if any((min_from(m, p, frozen=(i,)) or 999) <= dd for i in parked):
                    continue
            lvcars = []
            for i, (r, c, ln, d, kind, col, tgt) in enumerate(cars):
                if d == "H":
                    c = p[i]
                else:
                    r = p[i]
                lvcars.append([r, c, ln, d, kind, col, tgt])
            lv = {"n": n, "cars": lvcars, "cones": cones, "opt_moves": dd, "target": target, "states": len(adj)}
            if err == 0:
                return lv
            if best is None:
                best = lv
            break
    return best


def inject(levels):
    html = HERE / "game" / "index.html"
    if not html.exists():
        return
    s = html.read_text(encoding="utf-8")
    js = json.dumps([{k: v for k, v in lv.items() if k not in ("states", "target")} for lv in levels], ensure_ascii=False, separators=(",", ":"))
    s2 = re.sub(r"/\*LEVELS_START\*/.*?/\*LEVELS_END\*/", lambda _: "/*LEVELS_START*/" + js + "/*LEVELS_END*/", s, flags=re.S)
    html.write_text(s2, encoding="utf-8")


def main():
    args = sys.argv[1:]
    out = HERE / "game" / "levels.json"
    if "--inject-only" in args:
        inject(json.loads(out.read_text(encoding="utf-8")))
        return
    seed = int(args[args.index("--seed") + 1]) if "--seed" in args else 21
    rng = random.Random(seed)
    only = None
    if "--only" in args:   # 일부 레벨만 다시 뽑기 (나머지는 levels.json 그대로)
        only = {int(x) for x in args[args.index("--only") + 1].split(",")}
        old = json.loads(out.read_text(encoding="utf-8"))
    levels = []
    for lvno in range(1, 31):
        if only is not None and lvno not in only:
            levels.append(old[lvno - 1])
            continue
        lv = None
        while lv is None:
            lv = make_level(rng, lvno)
        lv["no"] = lvno
        levels.append(lv)
        print(f"L{lvno:2d} n={lv['n']} opt={lv['opt_moves']:2d} (목표 {lv['target']:2d}) states={lv['states']}", flush=True)
    out.write_text(json.dumps(levels, ensure_ascii=False, indent=0), encoding="utf-8")
    inject(levels)


if __name__ == "__main__":
    main()
