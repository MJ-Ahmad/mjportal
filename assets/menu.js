/* Nijer Khata bottom bar: Main site · Dashboard · Learning hub · Terminal · Menu.
   The Menu sheet lists menu / sub menu / sub-sub menu from menu.json, which is edited by hand (see README). */
(function () {
  var cs = document.currentScript || document.querySelector('script[src*="menu.js"]');
  var ROOT = new URL("../", cs.src).href, RP = new URL(ROOT).pathname;
  var LB = {
    en: { site: "Main site", dash: "Dashboard", learn: "Learning hub", term: "Terminal", menu: "Menu" },
    bn: { site: "মূল সাইট", dash: "ড্যাশবোর্ড", learn: "শেখার হাব", term: "টার্মিনাল", menu: "মেনু" },
    ar: { site: "الموقع", dash: "اللوحة", learn: "مركز التعلم", term: "الطرفية", menu: "القائمة" }
  };
  var IC = {
    site: '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>', dash: '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    learn: '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2zM8 7h7"/>', term: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M13 15h4"/>',
    menu: '<path d="M4 7h16M4 12h16M4 17h16"/>'
  };
  var LINK = { site: "../", dash: "index.html#dash", learn: "learn/", term: "terminal/" };
  var P = location.pathname, norm = function (p) { return p.replace(/index\.html$/, ""); };
  var CUR = { dash: norm(P) === RP, learn: P.indexOf(RP + "learn/") === 0, term: P.indexOf(RP + "terminal/") === 0 };
  var lang = function () { return LB[document.documentElement.lang] ? document.documentElement.lang : "en"; };
  var pick = function (v) { return typeof v === "string" ? v : (v && (v[lang()] || v.en)) || ""; };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var V = "var(--surface,var(--panel,#f8fbfa))", LN = "var(--line,#d3dfd8)", MU = "var(--muted,#5b7270)", MO = "var(--moss,#2e6b55)", AM = "var(--amber,#c7851c)";
  var css = "body{box-sizing:border-box;padding-bottom:calc(64px + env(safe-area-inset-bottom,0px))!important}.toast{bottom:calc(78px + env(safe-area-inset-bottom,0px))}" +
    ".mjn{position:fixed;inset:auto 0 0 0;z-index:60;display:flex;background:" + V + ";border-top:1px solid " + LN + ";padding-bottom:env(safe-area-inset-bottom,0px)}" +
    ".mjn a,.mjn button{position:relative;flex:1 1 0;min-width:0;height:60px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;padding:6px 2px;background:none;border:0;color:" + MU + ";font:500 11px/1.15 'Hind Siliguri',system-ui,sans-serif;text-decoration:none;cursor:pointer;-webkit-tap-highlight-color:transparent}" +
    ".mjn svg{width:24px;height:24px;flex:none;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.mjn span{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
    ".mjn [aria-current=page],.mjn [aria-expanded=true]{color:" + MO + "}.mjn [aria-current=page]:before,.mjn [aria-expanded=true]:before{content:'';position:absolute;top:0;width:30px;height:3px;border-radius:0 0 3px 3px;background:" + AM + "}" +
    ".mjn a:focus-visible,.mjn button:focus-visible,.mjn-p a:focus-visible,.mjn-p summary:focus-visible{outline:2px solid " + AM + ";outline-offset:-2px}" +
    ".mjn-s{position:fixed;inset:0;z-index:58;background:#0008;opacity:0;visibility:hidden;transition:opacity .2s,visibility .2s}" +
    ".mjn-p{position:fixed;inset-inline:0;bottom:calc(60px + env(safe-area-inset-bottom,0px));z-index:59;max-height:68vh;overflow:auto;background:" + V + ";color:var(--ink,#14303a);border:1px solid " + LN + ";border-bottom:0;border-radius:18px 18px 0 0;box-shadow:0 -12px 30px #0005;padding:8px 10px 12px;transform:translateY(105%);visibility:hidden;transition:transform .25s,visibility .25s;font:16px/1.45 'Hind Siliguri',system-ui,sans-serif}" +
    ".mjn-o .mjn-s{opacity:1;visibility:visible}.mjn-o .mjn-p{transform:none;visibility:visible}.mjn-in{max-width:760px;margin:auto}" +
    ".mjn-d>summary,.mjn-l{display:flex;align-items:center;gap:8px;padding:11px 8px;padding-inline-start:calc(8px + var(--d,0)*18px);color:inherit;text-decoration:none;border-radius:8px;cursor:pointer;list-style:none;text-transform:capitalize}.mjn-d>summary::-webkit-details-marker{display:none}" +
    ".mjn-d>summary{font-weight:600}.mjn-d>summary:after{content:'▾';margin-inline-start:auto;color:" + AM + ";transition:transform .2s}.mjn-d[open]>summary:after{transform:rotate(180deg)}" +
    ".mjn-d[style*='--d:0']{border-top:1px solid " + LN + "}.mjn-d[style*='--d:0']:first-child{border-top:0}.mjn-l:hover,.mjn-d>summary:hover{background:var(--c0,#e0e9e4)}.mjn-l[aria-current]{color:" + MO + ";font-weight:600;background:var(--c0,#e0e9e4)}" +
    "@media(prefers-reduced-motion:reduce){.mjn-p,.mjn-s{transition:none}}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  var box = document.createElement("div"), data = [];
  box.innerHTML = '<div class="mjn-s"></div><div class="mjn-p" id="mjn-p" role="region"><div class="mjn-in"></div></div><nav class="mjn"></nav>';
  document.body.appendChild(box);
  var bar = box.querySelector(".mjn"), list = box.querySelector(".mjn-in"), sheet = box.querySelector(".mjn-p");
  function url(h) { try { var u = new URL(encodeURI(h || ""), ROOT); return /^https?:$/.test(u.protocol) ? u.href : "#"; } catch (e) { return "#"; } }
  var cur = function (u) { return u !== "#" && norm(new URL(u).pathname) === norm(P); };
  function has(n) { return n.children ? n.children.some(has) : cur(url(n.href)); }
  function node(n, d) {
    var t = esc(pick(n.title));
    if (n.children) return '<details class="mjn-d" name="mjn' + d + '" style="--d:' + d + '"' + (has(n) ? " open" : "") + "><summary>" + t + "</summary>" + n.children.map(function (c) { return node(c, d + 1); }).join("") + "</details>";
    var u = url(n.href); return '<a class="mjn-l" style="--d:' + d + '" href="' + esc(u) + '"' + (cur(u) ? ' aria-current="page"' : "") + ">" + t + "</a>";
  }
  function paintBar() {
    var l = LB[lang()], open = box.classList.contains("mjn-o");
    bar.innerHTML = ["site", "dash", "learn", "term"].map(function (k) {
      return '<a href="' + esc(new URL(LINK[k], ROOT).href) + '"' + (CUR[k] ? ' aria-current="page"' : "") + '><svg viewBox="0 0 24 24" aria-hidden="true">' + IC[k] + "</svg><span>" + l[k] + "</span></a>";
    }).join("") + '<button type="button" aria-expanded="' + open + '" aria-controls="mjn-p"><svg viewBox="0 0 24 24" aria-hidden="true">' + IC.menu + "</svg><span>" + l.menu + "</span></button>";
    sheet.setAttribute("aria-label", l.menu);
  }
  function paintList() { list.innerHTML = data.map(function (n) { return node(n, 0); }).join(""); }
  function set(o) { box.classList.toggle("mjn-o", o); if (o) paintList(); paintBar(); if (!o) bar.querySelector("button").focus(); }
  bar.addEventListener("click", function (e) { if (e.target.closest("button")) set(!box.classList.contains("mjn-o")); });
  box.querySelector(".mjn-s").addEventListener("click", function () { set(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && box.classList.contains("mjn-o")) set(false); });
  new MutationObserver(function () { paintBar(); if (box.classList.contains("mjn-o")) paintList(); }).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
  paintBar();
  fetch(ROOT + "menu.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (j) { data = j.menu || []; }).catch(function () { data = []; });
})();
