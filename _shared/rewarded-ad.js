/* NHC game-lab 보상형 광고 모듈 v1.1 (2026-11-27) — 어댑터 방식
   - 기본 어댑터 "stub": 회색 박스 + 카운트다운(외부 스크립트 없음 — game-lab 오프라인 규칙 그대로). 개발·플레이테스트용
   - 플랫폼 출시 빌드에서만 그 플랫폼 SDK <script> 1줄과 window.NHC_AD_ADAPTER = "crazygames" | "poki" 를 이 모듈보다 앞에 넣는다
     (게임 본체 game/index.html 은 바꾸지 않는다. 출시용 사본은 build/<플랫폼>/ 에 따로 만든다)
   - SDK가 없거나 실패하면 보상 없이 onSkipped({reason:"unavailable"|"error"}) — 게임은 그대로 진행(우아한 실패). 출시 빌드에서 stub으로 몰래 보상하지 않는다
   - 한도(하루 5회)·쿨다운(60초)·코인 지급은 어댑터와 무관하게 이 모듈이 판정. 완료 여부는 stub은 두 시계, 실제 SDK는 SDK 콜백이 판정
   - 실제 SDK 함수 이름은 출시 직전에 각 플랫폼 최신 문서로 다시 확인할 것(아래 어댑터는 2026-11 기준 알려진 형태)

   쓰는 법 (coin-system.js 가 먼저 있어야 코인이 들어간다):
     RewardedAd.show({ coins: 5, onComplete: function (coins) {}, onSkipped: function (info) {} })
       → 끝까지 보고 '광고 종료'를 누르면 coins 지급 후 onComplete(coins)
       → 창 전환·ESC·한도 초과·쿨다운 중이면 지급 없이 onSkipped({reason}) — reason: "hidden" | "esc" | "limit" | "cooldown" | "busy" | "unavailable" | "error" | "skipped"
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
    var av = adapter().a;
    return { left: left, cooldown: cd, canShow: !!av && left > 0 && cd === 0 && !busy, label: !av ? "광고 준비 안 됨" : left <= 0 ? "오늘 광고 한도 초과" : cd > 0 ? cd + "초 뒤 다시" : busy ? "광고 중" : "광고 보기" };
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

  // ── 어댑터: play(sec, coins, done(ok, reason)) ──
  var ADAPTERS = {
    stub: { available: function () { return true; }, play: playStub },
    crazygames: {   // CrazyGames HTML5 SDK v3 — 출시 빌드에서 SDK 스크립트를 먼저 넣는다
      available: function () { return !!(window.CrazyGames && window.CrazyGames.SDK && window.CrazyGames.SDK.ad); },
      play: function (sec, coins, done) {
        var fin = false, end = function (ok, r) { if (!fin) { fin = true; done(ok, r); } };
        try { window.CrazyGames.SDK.ad.requestAd("rewarded", { adStarted: function () {}, adFinished: function () { end(true); }, adError: function () { end(false, "error"); } }); }
        catch (e) { end(false, "error"); }
      },
    },
    poki: {   // Poki SDK — rewardedBreak() 가 Promise<boolean>(끝까지 봤는지)
      available: function () { return !!(window.PokiSDK && window.PokiSDK.rewardedBreak); },
      play: function (sec, coins, done) {
        try { window.PokiSDK.rewardedBreak().then(function (ok) { done(!!ok, ok ? null : "skipped"); }, function () { done(false, "error"); }); }
        catch (e) { done(false, "error"); }
      },
    },
  };
  function adapter() {
    var name = window.NHC_AD_ADAPTER || "stub", a = ADAPTERS[name];
    return { name: name, a: a && a.available() ? a : null };
  }

  window.RewardedAd = {
    PER_DAY: PER_DAY, COOLDOWN: COOLDOWN, DURATION: DURATION,
    status: status,
    adapter: function () { var x = adapter(); return x.a ? x.name : "none"; },
    register: function (name, impl) { ADAPTERS[name] = impl; },   // 새 플랫폼(예: Capacitor AdMob) 붙일 때
    show: function (opt) {
      opt = opt || {};
      var coins = Math.max(0, Math.floor(opt.coins == null ? 5 : opt.coins)), sec = Math.max(1, opt.duration || DURATION);
      var s = status();
      var skip = function (reason) { if (typeof opt.onSkipped === "function") opt.onSkipped({ reason: reason }); return { ok: false, reason: reason }; };
      if (busy) return skip("busy");
      if (s.left <= 0) return skip("limit");
      if (s.cooldown > 0) return skip("cooldown");
      var ad = adapter();
      if (!ad.a) return skip("unavailable");   // 출시 빌드인데 SDK가 없음 → 보상 없이 게임 계속
      busy = true;
      ad.a.play(sec, coins, function (ok, reason) {
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
