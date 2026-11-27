/* NHC game-lab 코인 시스템 v1 (2026-11-27) — 인앱 코인(현금화 없음, 이 브라우저에만 저장)
   - 저장: localStorage "gl_coins" = {n: 잔액, t: 저장 시각, c: 체크섬}. 오락실과 게임(iframe)이 같은 출처라 잔액을 같이 쓴다
   - 최대 보유 500. 체크섬이 안 맞으면(직접 고침) 0으로 리셋
   - 한계(정직하게): 브라우저 안 검증이라 코드를 읽은 사람은 우회할 수 있다. '그냥 숫자 바꾸기'를 막는 수준. 코인에 실제 가치가 생기면 서버 장부(Supabase)로 옮긴다
   쓰는 법: CoinSystem.getCoins() / addCoins(n) → 새 잔액 / spendCoins(n) → true|false
   바뀔 때마다 window 에 "gl-coins" 이벤트(detail=잔액). 다른 창(오락실↔게임)은 "storage" 이벤트로 알 수 있다 */
(function () {
  if (window.CoinSystem) return;
  var KEY = "gl_coins", MAX = 500, SALT = "nhc-game-lab|coins|v1";
  function sum(n, t) {   // FNV-1a 32bit 두 번 — 위조 방지가 아니라 손 편집 감지용
    var s = SALT + "|" + n + "|" + t + "|" + SALT.length, h = 2166136261, g = 5381;
    for (var i = 0; i < s.length; i++) { var ch = s.charCodeAt(i); h ^= ch; h = Math.imul(h, 16777619); g = (Math.imul(g, 33) + ch) | 0; }
    return (h >>> 0).toString(36) + "." + (g >>> 0).toString(36);
  }
  function write(n) {
    var t = Date.now();
    try { localStorage.setItem(KEY, JSON.stringify({ n: n, t: t, c: sum(n, t) })); } catch (e) {}
    try { window.dispatchEvent(new CustomEvent("gl-coins", { detail: n })); } catch (e) {}
    return n;
  }
  function read() {
    var raw = null;
    try { raw = localStorage.getItem(KEY); } catch (e) { return 0; }
    if (raw === null) return 0;
    try {
      var o = JSON.parse(raw);
      if (!o || typeof o.n !== "number" || typeof o.t !== "number" || o.n !== Math.floor(o.n) || o.n < 0 || o.n > MAX || o.c !== sum(o.n, o.t)) return write(0);
      return o.n;
    } catch (e) { return write(0); }
  }
  window.CoinSystem = {
    MAX: MAX,
    getCoins: read,
    addCoins: function (n) { n = Math.floor(+n || 0); if (n <= 0) return read(); return write(Math.min(MAX, read() + n)); },
    spendCoins: function (n) { n = Math.floor(+n || 0); var v = read(); if (n <= 0 || v < n) return false; write(v - n); return true; },
  };
})();
