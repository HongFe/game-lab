/* NHC game-lab 보상형 광고 모듈 v1 (2026-11-27) — 프로토: 실제 SDK 없이 회색 박스 + 카운트다운 스텁
   나중에 실제 광고를 붙일 때는 playStub() 자리만 SDK 호출로 바꾼다(보상 판정·한도·쿨다운은 그대로)

   쓰는 법 (coin-system.js 가 먼저 있어야 코인이 들어간다):
     RewardedAd.show({ coins: 5, onComplete: function (coins) {}, onSkipped: function (info) {} })
       → 끝까지 보고 '광고 종료'를 누르면 coins 지급 후 onComplete(coins)
       → 창 전환·ESC·한도 초과·쿨다운 중이면 지급 없이 onSkipped({reason}) — reason: "hidden" | "esc" | "limit" | "cooldown" | "busy"
     RewardedAd.status() → { left: 오늘 남은 횟수, cooldown: 남은 쿨다운 초, canShow: bool, label: 버튼에 쓸 짧은 글 }

   규칙: 하루 5회(자정에 리셋), 직전 광고 완료 후 60초 쿨다운, 기본 15초
   스킵 방지: 닫기 버튼은 끝나기 전 비활성 / visibilitychange(hidden)·ESC 감지 시 즉시 실패
   시간 검증: 진행은 setInterval 횟수가 아니라 Date.now() 와 performance.now() 두 시계의 실제 경과로만 판정(둘 다 기준을 넘어야 완료)
   한계: 브라우저 안 판정이라 개발자 도구로 우회할 수 있다. 코인에 실제 가치가 생기면 광고 SDK의 서버 검증 콜백(SSV)으로 옮긴다 */
(function () {
  if (window.RewardedAd) return;
  var KEY = "gl_ad", PER_DAY = 5, COOLDOWN = 60, DURATION = 15;
  var busy = false;
  function today() { var d = new Date(); return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate(); }
  function load() {
    var o = null; try { o = JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) {}
    if (!o || o.day !== today()) o = { day: today(), count: 0, last: (o && o.last) || 0 };
    return o;
  }
  function save(o) { try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {} }
  function status() {
    var o = load(), left = Math.max(0, PER_DAY - o.count);
    var cd = Math.max(0, Math.ceil(COOLDOWN - (Date.now() - (o.last || 0)) / 1000));
    if (o.last > Date.now()) cd = COOLDOWN;   // 시계를 뒤로 돌린 경우
    return { left: left, cooldown: cd, canShow: left > 0 && cd === 0 && !busy, label: left <= 0 ? "오늘 광고 한도 초과" : cd > 0 ? cd + "초 뒤 다시" : busy ? "광고 중" : "광고 보기" };
  }

  var CSS = ".gl-ad{position:fixed;inset:0;z-index:2147483000;background:#0b0d12;color:#f2f4f8;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;padding:24px;font:400 14px/1.5 -apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR',sans-serif;-webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none;animation:gl-ad-in 200ms cubic-bezier(0,0,.2,1)}" +
    "@keyframes gl-ad-in{from{opacity:0}}" +
    ".gl-ad-top{position:absolute;left:16px;right:16px;top:max(16px,env(safe-area-inset-top));display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#9aa3b2}" +
    ".gl-ad-box{width:min(320px,100%);aspect-ratio:9/16;max-height:56vh;border-radius:20px;background:repeating-linear-gradient(45deg,#2a2f3a 0 12px,#252a34 12px 24px);display:grid;place-items:center;color:#9aa3b2;font-weight:700;letter-spacing:.04em}" +
    ".gl-ad-ring{position:relative;width:64px;height:64px}.gl-ad-ring svg{width:64px;height:64px;transform:rotate(-90deg)}.gl-ad-ring circle{fill:none;stroke-width:5}.gl-ad-ring b{position:absolute;inset:0;display:grid;place-items:center;font:700 20px/1 inherit;font-variant-numeric:tabular-nums}" +
    ".gl-ad-btn{appearance:none;border:0;min-height:48px;min-width:200px;padding:0 24px;border-radius:12px;font:700 16px/1 inherit;background:#ffc83d;color:#1a1406;cursor:pointer;transition:transform 90ms,opacity 150ms}.gl-ad-btn:active{transform:scale(.96)}.gl-ad-btn:disabled{opacity:.35;pointer-events:none;background:#3a404c;color:#9aa3b2}" +
    ".gl-ad-msg{min-height:20px;color:#9aa3b2;font-size:14px}";

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

  function playStub(sec, coins, done) {   // ← 실제 SDK로 바꿀 자리. done(ok, reason)
    if (!document.getElementById("gl-ad-css")) { var st = el("style"); st.id = "gl-ad-css"; st.textContent = CSS; document.head.appendChild(st); }
    var root = el("div", "gl-ad"); root.setAttribute("role", "dialog"); root.setAttribute("aria-label", "광고");
    var C = 2 * Math.PI * 28;
    root.innerHTML = '<div class="gl-ad-top"><span>광고 · 테스트</span><span>보상 +' + coins + ' 코인</span></div>' +
      '<div class="gl-ad-box">AD</div>' +
      '<div class="gl-ad-ring"><svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" stroke="#2a2f3a"/><circle class="gl-ad-arc" cx="32" cy="32" r="28" stroke="#ffc83d" stroke-linecap="round" stroke-dasharray="' + C + '" stroke-dashoffset="' + C + '"/></svg><b>' + sec + '</b></div>' +
      '<div class="gl-ad-msg">끝까지 보면 코인을 받아요</div>' +
      '<button class="gl-ad-btn" disabled>광고 종료</button>';
    document.body.appendChild(root);
    var arc = root.querySelector(".gl-ad-arc"), num = root.querySelector(".gl-ad-ring b"), btn = root.querySelector(".gl-ad-btn"), msg = root.querySelector(".gl-ad-msg");
    var t0 = Date.now(), p0 = performance.now(), need = sec * 1000, over = false, ready = false, iv;
    function elapsed() { return Math.min(Date.now() - t0, performance.now() - p0); }   // 두 시계 중 느린 쪽
    function finish(ok, reason) {
      if (over) return; over = true; clearInterval(iv);
      document.removeEventListener("visibilitychange", onVis); document.removeEventListener("keydown", onKey, true);
      if (ok) { root.remove(); done(true); return; }
      msg.textContent = "광고를 끝까지 보지 않아 보상이 없어요"; btn.disabled = false; btn.textContent = "닫기";
      btn.onclick = function () { root.remove(); };
      setTimeout(function () { if (root.parentNode) root.remove(); }, 2500);
      done(false, reason);
    }
    function onVis() { if (document.visibilityState === "hidden" && !ready) finish(false, "hidden"); }
    function onKey(e) { if (e.key === "Escape" || e.key === "Esc") { e.preventDefault(); e.stopPropagation(); if (!ready) finish(false, "esc"); } }
    document.addEventListener("visibilitychange", onVis);
    document.addEventListener("keydown", onKey, true);
    iv = setInterval(function () {
      var e = elapsed(), left = Math.max(0, Math.ceil((need - e) / 1000));
      num.textContent = left; arc.setAttribute("stroke-dashoffset", String(C * (1 - Math.min(1, e / need))));
      if (e >= need && !ready) { ready = true; clearInterval(iv); btn.disabled = false; msg.textContent = "다 봤어요!"; num.textContent = "✓"; }
    }, 200);
    btn.onclick = function () {
      if (over) return;
      if (!ready || elapsed() < need) return;   // 버튼을 강제로 켜도 실제 경과가 모자라면 무시
      finish(true);
    };
  }

  window.RewardedAd = {
    PER_DAY: PER_DAY, COOLDOWN: COOLDOWN, DURATION: DURATION,
    status: status,
    show: function (opt) {
      opt = opt || {};
      var coins = Math.max(0, Math.floor(opt.coins == null ? 5 : opt.coins)), sec = Math.max(1, opt.duration || DURATION);
      var s = status();
      var skip = function (reason) { if (typeof opt.onSkipped === "function") opt.onSkipped({ reason: reason }); return { ok: false, reason: reason }; };
      if (busy) return skip("busy");
      if (s.left <= 0) return skip("limit");
      if (s.cooldown > 0) return skip("cooldown");
      busy = true;
      playStub(sec, coins, function (ok, reason) {
        busy = false;
        if (!ok) { skip(reason); return; }
        var o = load(); o.count++; o.last = Date.now(); save(o);
        if (window.CoinSystem && coins) window.CoinSystem.addCoins(coins);
        if (typeof opt.onComplete === "function") opt.onComplete(coins);
      });
      return { ok: true };
    },
  };
})();
