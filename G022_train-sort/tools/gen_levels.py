#!/usr/bin/env python3
"""G022 기차 칸 줄 세우기 — 레벨 생성기 (표준 라이브러리만).

규칙은 game/index.html 과 같다.
- train: 들어오는 선로의 칸 색, 맨 앞(갈림길 쪽) 칸이 index 0
- 옆 선로: 막다른 스택, 입구 쪽(마지막 원소)만 꺼낸다, 길이 cap
- 역: order[s] 색만 받는다
- 한 번 옮기기 = 이동 1. 들어오는 선로로 되돌려 넣기 없음

사용: python3 tools/gen_levels.py  → game/index.html 의 /*LEVELS_START*/ ... /*LEVELS_END*/ 를 바꾼다
"""
import itertools, json, random, re, sys
from collections import deque
from pathlib import Path

# (칸, 옆 선로, 선로 길이, 목표 최소 수)
TABLE = [
    (3, 0, 0, 3), (3, 1, 4, 4), (3, 1, 4, 5), (4, 1, 4, 6), (4, 1, 4, 7),
    (4, 2, 4, 6), (4, 2, 4, 7), (5, 2, 4, 8), (5, 2, 4, 9), (5, 2, 4, 10),
    (5, 2, 2, 9), (5, 2, 2, 10), (5, 2, 2, 11), (6, 2, 2, 12), (6, 2, 2, 13),
    (5, 2, 2, 11), (6, 2, 2, 13), (6, 2, 2, 14), (6, 2, 2, 15), (6, 2, 2, 16),
    (6, 2, 2, 15), (6, 2, 2, 16), (7, 2, 2, 17), (7, 2, 2, 18), (7, 2, 2, 19),
    (7, 2, 2, 18), (7, 2, 2, 19), (7, 2, 2, 20), (7, 2, 2, 21), (7, 2, 2, 22),
]
ST = 9
# 고정 배열(QA 1차 고칠 2): 16레벨은 옆→옆이 꼭 필요하면서 막힌 상태가 없는 쉬운 판.
# 다른 레벨이 바뀌지 않게 난수는 평소대로 쓰고, 고른 결과만 이것으로 바꾼다
FORCED = {16: [2, 3, 4, 0, 1]}
# 기획 표 값 중 이 규칙(옆 선로 최대 2개, 16레벨 전에는 옆→옆 없이 최소 해)으로 만들 수 없는 값을 고친 곡선.
# 5칸·옆→옆 없이 최대 9, 6칸 없이 최대 10, 6칸 옆→옆 허용 최대 13, 7칸(같은 색 포함) 최대 14 (전수 계산)
CURVE = [3, 4, 5, 6, 7, 6, 7, 8, 9, 9, 8, 9, 9, 10, 10, 9, 11, 12, 13, 13, 12, 13, 13, 14, 14, 13, 13, 14, 14, 14]


def rand_rate(train, order, ns, cap, runs=50, seed=7):
    rng = random.Random(seed)
    ok = 0
    for _ in range(runs):
        st = (0, tuple(() for _ in range(ns)), 0)
        for _ in range(200):
            if st[2] == len(train):
                ok += 1; break
            mv = moves_of(st, train, order, cap)
            if not mv:
                break
            st = apply(st, mv[rng.randrange(len(mv))], train)
    return ok / runs


def moves_of(state, train, order, cap, allow_ss=True):
    r, sd, s = state
    n = len(train)
    srcs = []
    if r < n:
        srcs.append((-1, train[r]))
    for j, st in enumerate(sd):
        if st:
            srcs.append((j, st[-1]))
    out = []
    for src, c in srcs:
        if s < len(order) and c == order[s]:
            out.append((src, ST))
        for k in range(len(sd)):
            if k == src or len(sd[k]) >= cap:
                continue
            if src >= 0 and not allow_ss:
                continue
            out.append((src, k))
    return out


def apply(state, mv, train):
    r, sd, s = state
    src, dst = mv
    sd = [list(x) for x in sd]
    if src == -1:
        c = train[r]; r += 1
    else:
        c = sd[src].pop()
    if dst == ST:
        s += 1
    else:
        sd[dst].append(c)
    return (r, tuple(tuple(x) for x in sd), s)


def solve(train, order, ns, cap, allow_ss=True):
    start = (0, tuple(() for _ in range(ns)), 0)
    n = len(train)
    dist = {start: 0}
    q = deque([start])
    while q:
        st = q.popleft()
        if st[2] == n:
            return dist[st]
        for mv in moves_of(st, train, order, cap, allow_ss):
            nx = apply(st, mv, train)
            if nx not in dist:
                dist[nx] = dist[st] + 1
                q.append(nx)
    return None


def main():
    rng = random.Random(22022)
    levels = []
    used = set()
    for i, (n, ns, cap, brief_target) in enumerate(TABLE):
        L = i + 1
        target = CURVE[i]
        dup = L >= 21
        custom = L >= 26
        if dup:
            distinct = n - 1
            base = list(range(distinct))
            d = rng.randrange(distinct)
            colors = sorted(base + [d])
        else:
            colors = list(range(n))
        order = list(colors)
        if custom:
            while order == sorted(order):
                rng.shuffle(order)
        if L == 1:
            cands = [tuple(order)]
        else:
            cands = sorted(set(itertools.permutations(order)))
        best = []
        for t in cands:
            if (t, ns, cap, tuple(order)) in used:
                continue
            m = solve(t, order, ns, cap)
            if m is None:
                continue
            score = abs(m - target) * 100
            if ns == 2 and L < 16:
                if solve(t, order, ns, cap, allow_ss=False) != m:
                    continue  # 16레벨 전에는 옆→옆 없이도 최소 해가 있어야 함
            if L == 16:
                if solve(t, order, ns, cap, allow_ss=False) == m:
                    continue  # 16레벨은 모든 최소 해에 옆→옆이 꼭 필요
            if L == 6:
                one = solve(t, order, 1, cap)
                if one is not None and one <= m:
                    score += 10  # 옆 선로 2개를 써야 최소
            if L == 11:
                if solve(t, order, ns, 4) == m:
                    score += 10  # 짧은 선로가 실제로 영향
            if L >= 2 and t[0] == order[0]:
                score += 3
            if abs(m - target) > 1:
                continue
            best.append((score, t, m))
        if not best:
            print(f"L{L}: 후보 없음", file=sys.stderr)
            sys.exit(1)
        lo = min(b[0] for b in best)
        pick = [b for b in best if b[0] == lo]
        rng.shuffle(pick)
        if L >= 8:  # 같은 최소 수면 무작위 봇이 덜 풀리는(헷갈리는) 배치를 고른다
            pick = sorted(pick[:40], key=lambda b: rand_rate(b[1], order, ns, cap))
        score, t, m = pick[0]
        if L in FORCED:
            t = tuple(FORCED[L]); m = solve(t, order, ns, cap)
            assert solve(t, order, ns, cap, allow_ss=False) != m, "16레벨은 옆→옆이 꼭 필요해야 함"
        used.add((t, ns, cap, tuple(order)))
        levels.append({"n": L, "train": list(t), "order": order, "sidings": ns, "cap": cap,
                       "opt_moves": m, "target": target, "brief": brief_target})
        print(f"L{L:2d} cars={n} sd={ns} cap={cap} brief={brief_target} target={target} opt={m} train={list(t)} order={order}")
    html = Path(__file__).resolve().parent.parent / "game" / "index.html"
    if html.exists():
        src = html.read_text(encoding="utf-8")
        js = json.dumps(levels, separators=(",", ":"))
        new = re.sub(r"/\*LEVELS_START\*/.*?/\*LEVELS_END\*/", lambda _: "/*LEVELS_START*/" + js + "/*LEVELS_END*/", src, flags=re.S)
        html.write_text(new, encoding="utf-8")
        print("index.html 갱신")


if __name__ == "__main__":
    main()
