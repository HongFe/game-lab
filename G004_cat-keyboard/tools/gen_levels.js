#!/usr/bin/env node
// G004 고양이 타자수 — 레벨 생성기.
// game/index.html 의 /*CORE_START*/…/*CORE_END*/ (키보드·걷기 규칙)를 그대로 가져와 쓰므로 게임과 판정이 같다.
// 사용: node tools/gen_levels.js [--seed 7]   → game/levels.json + index.html 의 LEVELS 자리에 주입
const fs = require("fs"), path = require("path");
const GAME = path.join(__dirname, "..", "game", "index.html");
const html = fs.readFileSync(GAME, "utf8");
const core = html.match(/\/\*CORE_START\*\/([\s\S]*?)\/\*CORE_END\*\//)[1];
const { KEYS, BS, walk } = new Function(core + "; return { KEYS, BS, walk };")();
const seedArg = process.argv.indexOf("--seed"); let seed = seedArg > 0 ? +process.argv[seedArg + 1] : 7;
const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };

const WORDS = ["HI", "OK", "NO", "YES", "BYE", "SOS", "NAP", "CAT", "JOB", "ZZZ", "HELP", "LATE", "SICK", "QUIT", "HOME", "MEOW", "TUNA", "FISH", "PURR", "BOSS", "DONE", "WIFI", "TACO", "EXIT", "MILK", "WORK", "LUNCH", "SORRY"];
const idOf = ch => KEYS.findIndex(k => k.ch === ch);

// 한 구간(pos → t)을 걸었을/뛰었을 때 typed 가 어떻게 바뀌나
function seg(pos, t, typed) { const r = walk(pos, [t]); for (const e of r.ev) typed = e.key === BS ? typed.slice(0, -1) : typed + KEYS[e.key].ch; return typed; }
function ok(typed, word) {
  if (typed.length > word.length + 2) return false;
  let p = 0; while (p < typed.length && p < word.length && typed[p] === word[p]) p++;
  return typed.length - p <= 2;
}
// 점프 J번까지 허용할 때 최소 간식 수 해답 (BFS)
function solve(word, start, J, maxDepth = 7) {
  let frontier = [{ pos: start, typed: "", jj: 0, path: [] }]; const seen = new Set([start + "||0"]);
  for (let d = 1; d <= maxDepth; d++) {
    const next = [];
    for (const s of frontier) for (let k = 0; k < KEYS.length; k++) for (const j of [false, true]) {
      if (k === s.pos || (j && s.jj >= J)) continue;
      const t = { k, j }, typed = seg(s.pos, t, s.typed), jj = s.jj + (j ? 1 : 0);
      if (typed === word) return [...s.path, t];
      if (!ok(typed, word)) continue;
      const key = k + "|" + typed + "|" + jj; if (seen.has(key)) continue; seen.add(key);
      next.push({ pos: k, typed, jj, path: [...s.path, t] });
    }
    frontier = next; if (!frontier.length) break;
  }
  return null;
}
const WORDS2 = WORDS.concat(["TYPE", "WEST", "QUEST", "ASK", "DESK", "POOL", "TREE", "ZOOM", "BUG", "FIX", "SAVE", "CODE", "SAD", "WET", "RED", "TOP", "HOP", "JOKE", "POLO", "ERROR", "TEXT", "FAX", "NEWS", "ZIP", "GAS", "FUN", "HUG", "YOU", "WHY"]);
const cands = [];
for (const word of WORDS2) {
  for (let tries = 0; tries < 3; tries++) {
    const start = Math.floor(rnd() * (KEYS.length - 1));
    if (word.includes(KEYS[start].ch)) continue;
    let sol = null, J = 0;
    for (J = 0; J < word.length; J++) { sol = solve(word, start, J, Math.min(7, word.length + 2)); if (sol) break; }
    if (!sol || J >= word.length) continue;               // 글자마다 점프해야 하면 퍼즐이 아님
    const r = walk(start, sol), usesBS = r.ev.some(e => e.key === BS);
    const walkCount = sol.filter(t => !t.j).length, multi = r.ev.length - sol.length;   // 한 번 걸어서 여러 글자를 친 횟수
    cands.push({ word, start, sol, opt: sol.length, jumps: J, usesBS, trap: multi > 0 || usesBS, score: sol.length + J * .5 + (usesBS ? 2.5 : 0) + word.length * .4 });
  }
}
// 단어마다 가장 '퍼즐다운' 후보 하나: 점프가 적고, 한 번 걸어서 여러 글자를 치는 것
const best = {};
for (const c of cands) { const r = walk(c.start, c.sol), multi = r.ev.length - c.sol.length; c.fun = multi * 2 - c.jumps + (c.usesBS ? 2 : 0); if (!best[c.word] || c.fun > best[c.word].fun) best[c.word] = c; }
cands.length = 0; Object.values(best).forEach(c => cands.push(c));
const used = new Set(), out = [];
const take = (f, n) => { cands.filter(c => !used.has(c.word) && f(c)).sort((a, b) => a.score - b.score).slice(0, n).forEach(c => { used.add(c.word); out.push(c); }); };
take(c => c.word.length <= 2, 2);
take(c => c.jumps === 0, 3);
take(c => c.jumps === 1 && !c.usesBS, 4);
take(c => c.usesBS, 3);
take(c => c.jumps >= 2 && !c.usesBS, 3);
take(c => c.word.length >= 5, 2);
out.sort((a, b) => a.score - b.score);
out.forEach((c, i) => { c.n = i + 1; delete c.score; delete c.fun; });
fs.writeFileSync(path.join(__dirname, "..", "game", "levels.json"), JSON.stringify(out, null, 1));
const data = JSON.stringify(out);
fs.writeFileSync(GAME, html.replace(/\/\*LEVELS_START\*\/[\s\S]*?\/\*LEVELS_END\*\//, () => "/*LEVELS_START*/" + data + "/*LEVELS_END*/"));
console.log(`레벨 ${out.length}개 (후보 ${cands.length})`);
out.forEach(c => console.log(`${c.n}\t${c.word}\t시작 ${KEYS[c.start].ch}\t간식 ${c.opt}\t점프 ${c.jumps}\t⌫ ${c.usesBS ? "O" : "-"}\t해답 ${c.sol.map(t => (t.j ? "^" : "") + KEYS[t.k].ch).join(" > ")}`));
