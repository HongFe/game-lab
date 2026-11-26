#!/usr/bin/env python3
"""G001 이중주차 탈출 — 풀 수 있는 레벨만 생성하고 최적해(최소 전화, 그다음 최소 이동)를 계산한다.

사용: python3 tools/gen_levels.py [--seed 1] [--count 20]   (수 분 걸림)
      python3 tools/gen_levels.py --inject-only            (levels.json → index.html만)
결과: game/levels.json, 그리고 game/index.html의 /*LEVELS_START*/ ... /*LEVELS_END*/ 사이에 주입.
표준 라이브러리만.

규칙 (게임과 같아야 함)
- 6×6 격자. 내 차(0번)는 가로 2칸, 2행. 출구는 2행 오른쪽 끝
- 차는 자기 방향(가로/세로)으로만 민다. 한 번 밀기 = 이동 1 (몇 칸이든)
- P 차는 전화 1번으로 N이 된다. 비용은 전화 우선(전화 1 > 이동 어떤 수)
"""
import heapq, json, pathlib, random, re, sys

W = H = 6
EXIT_ROW = 2
HERE = pathlib.Path(__file__).resolve().parent.parent
CALL = 1000


def cells(r, c, ln, d):
    return [(r, c + k) if d == "H" else (r + k, c) for k in range(ln)]


def solve(cars, cap=250_000):
    """cars: [[r,c,len,dir,kind]]. 반환 (calls, moves) 또는 None."""
    n = len(cars)
    fixed = [(r if d == "H" else c) for r, c, ln, d, k in cars]   # 고정 좌표
    start = tuple((c if d == "H" else r) for r, c, ln, d, k in cars)
    pmask = sum(1 << i for i, x in enumerate(cars) if x[4] == "P")
    dist = {(start, 0): 0}
    pq = [(0, start, 0)]
    seen = 0
    while pq:
        cost, pos, mask = heapq.heappop(pq)
        if dist.get((pos, mask), 1 << 60) < cost:
            continue
        if pos[0] + cars[0][2] == W:
            return cost // CALL, cost % CALL
        seen += 1
        if seen > cap:
            return None
        grid = [[-1] * W for _ in range(H)]
        for i in range(n):
            ln, d = cars[i][2], cars[i][3]
            r, c = (fixed[i], pos[i]) if d == "H" else (pos[i], fixed[i])
            for rr, cc in cells(r, c, ln, d):
                grid[rr][cc] = i
        for i in range(n):
            locked = (pmask >> i) & 1 and not (mask >> i) & 1
            if locked:
                nm = mask | (1 << i)
                nc = cost + CALL
                if nc < dist.get((pos, nm), 1 << 60):
                    dist[(pos, nm)] = nc
                    heapq.heappush(pq, (nc, pos, nm))
                continue
            ln, d, v, f = cars[i][2], cars[i][3], pos[i], fixed[i]
            limit = W if d == "H" else H
            for step in (-1, 1):
                k = v
                while True:
                    k += step
                    head = k if step < 0 else k + ln - 1
                    if head < 0 or head >= limit:
                        break
                    occ = grid[f][head] if d == "H" else grid[head][f]
                    if occ != -1:
                        break
                    np = pos[:i] + (k,) + pos[i + 1:]
                    nc = cost + 1
                    if nc < dist.get((np, mask), 1 << 60):
                        dist[(np, mask)] = nc
                        heapq.heappush(pq, (nc, np, mask))
    return None


def random_level(rng):
    me_c = rng.choice([0, 1])
    cars = [[EXIT_ROW, me_c, 2, "H", "ME"]]
    occ = set(cells(*cars[0][:4]))
    target = rng.randint(7, 12)
    tries = 0
    while len(cars) < target + 1 and tries < 300:
        tries += 1
        ln = 3 if rng.random() < 0.25 else 2
        d = rng.choice("HV")
        if d == "H":
            r, c = rng.randrange(H), rng.randrange(W - ln + 1)
            if r == EXIT_ROW:
                continue  # 출구 줄의 가로 차는 영원히 못 빠짐
        else:
            r, c = rng.randrange(H - ln + 1), rng.randrange(W)
        cs = cells(r, c, ln, d)
        if any(x in occ for x in cs):
            continue
        occ.update(cs)
        cars.append([r, c, ln, d, "P" if rng.random() < 0.38 else "N"])
    return cars


def inject(out):
    data = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    idx = HERE / "game" / "index.html"
    s = idx.read_text(encoding="utf-8")
    idx.write_text(re.sub(r"/\*LEVELS_START\*/.*?/\*LEVELS_END\*/", lambda m: "/*LEVELS_START*/" + data + "/*LEVELS_END*/", s, flags=re.S), encoding="utf-8")


def main():
    if "--inject-only" in sys.argv:  # 이미 만든 levels.json을 index.html에 다시 넣기만 (풀이 계산 생략)
        out = json.loads((HERE / "game" / "levels.json").read_text(encoding="utf-8"))
        inject(out)
        print(f"레벨 {len(out)}개 주입")
        return
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1
    count = int(sys.argv[sys.argv.index("--count") + 1]) if "--count" in sys.argv else 20
    rng = random.Random(seed)
    pool = {}
    for _ in range(4000):
        lv = random_level(rng)
        res = solve(lv)
        if not res:
            continue
        calls, moves = res
        if moves < 3 or calls > 3:
            continue
        diff = moves + 4 * calls
        key = (calls, moves)
        pool.setdefault(key, []).append({"cars": lv, "opt_calls": calls, "opt_moves": moves, "diff": diff})
    # 구성: 전화 0번 쉬운 판 2개 → 전화 1번 → 점점 어렵게
    want = [(0, 3), (0, 5), (1, 4), (1, 6), (1, 7), (0, 9), (1, 8), (2, 6), (1, 10), (2, 8),
            (1, 12), (2, 10), (0, 14), (2, 12), (3, 8), (1, 15), (2, 14), (3, 11), (2, 17), (3, 14)]
    out, used = [], set()
    for calls, moves in want[:count]:
        best = None
        for (c, m), lst in pool.items():
            if c != calls or (c, m) in used:
                continue
            if best is None or abs(m - moves) < abs(best[1] - moves):
                best = (c, m)
        if best:
            used.add(best)
            out.append(pool[best][0])
    out.sort(key=lambda x: x["diff"])
    for i, lv in enumerate(out, 1):
        lv["n"] = i
    (HERE / "game" / "levels.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    if (HERE / "game" / "index.html").exists():
        inject(out)
    print(f"레벨 {len(out)}개: " + ", ".join(f"{l['n']}:전화{l['opt_calls']}·이동{l['opt_moves']}" for l in out))


if __name__ == "__main__":
    main()
