/* ব্যক্তিগত ভল্ট — পাসওয়ার্ড দিয়ে ব্রাউজারে ডিক্রিপ্ট করে দেখায়।
   এনক্রিপশন ফরম্যাট private_vault.py এর সাথে মেলে:
   PBKDF2-SHA256 → AES-256-GCM; প্রতিটি blob = 12 বাইট IV + ciphertext(+tag)।
   পাসওয়ার্ড বা ডিক্রিপ্ট করা ডেটা কোথাও সংরক্ষিত হয় না (localStorage ব্যবহার হয় না)। */
(() => {
  'use strict';
  const VAULT = 'vault/';
  const AUTO_LOCK_MS = 5 * 60 * 1000;
  const LABEL = { photos: 'ফটো', videos: 'ভিডিও', audio: 'অডিও', documents: 'ডকুমেন্ট' };
  const $ = (s) => document.querySelector(s);
  const state = { key: null, items: [], tab: 'photos', q: '', urls: new Map(), io: null };
  let lb = { items: [], idx: 0 };
  let hideTimer = null;

  const gate = $('#gate'), vault = $('#vault'), list = $('#list'), msg = $('#msg'), pw = $('#pw');

  function el(tag, attrs = {}, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') n.className = v;
      else if (k === 'text') n.textContent = v;
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    }
    for (const c of kids) if (c) n.append(c);
    return n;
  }
  const human = (n) => n < 1024 ? n + ' B' : n < 1048576 ? (n / 1024).toFixed(1) + ' KB'
    : n < 1073741824 ? (n / 1048576).toFixed(1) + ' MB' : (n / 1073741824).toFixed(2) + ' GB';
  const b64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

  async function fetchBytes(url) {
    const r = await fetch(url, { cache: 'no-cache' });
    if (!r.ok) throw new Error('missing:' + url);
    return r.arrayBuffer();
  }

  // ফরম্যাট: 16 বাইট IV + ciphertext + 32 বাইট HMAC-SHA256(IV+ciphertext). private_vault.py এর সাথে মেলে।
  async function deriveKeys(password, meta) {
    const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits']);
    const bits = new Uint8Array(await crypto.subtle.deriveBits(
      { name: 'PBKDF2', salt: b64(meta.salt), iterations: meta.iterations, hash: 'SHA-256' }, base, 512));
    return {
      enc: await crypto.subtle.importKey('raw', bits.slice(0, 32), { name: 'AES-CTR' }, false, ['decrypt']),
      mac: await crypto.subtle.importKey('raw', bits.slice(32, 64), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']),
    };
  }

  async function decryptWith(keys, buf) {
    const u = new Uint8Array(buf);
    const body = u.subarray(0, u.length - 32), tag = u.subarray(u.length - 32);
    const iv = u.subarray(0, 16), ct = u.subarray(16, u.length - 32);
    if (!(await crypto.subtle.verify('HMAC', keys.mac, tag, body))) {
      throw new DOMException('tag mismatch', 'OperationError'); // ভুল পাসওয়ার্ড বা নষ্ট ফাইল
    }
    return crypto.subtle.decrypt({ name: 'AES-CTR', counter: iv, length: 128 }, keys.enc, ct);
  }

  async function unlock(password) {
    const meta = JSON.parse(new TextDecoder().decode(await fetchBytes(VAULT + 'vault.json')));
    const keys = await deriveKeys(password, meta);
    const manifest = JSON.parse(new TextDecoder().decode(await decryptWith(keys, await fetchBytes(VAULT + 'manifest.bin'))));
    state.key = keys;
    state.items = manifest.items || [];
  }

  function urlFor(item) {
    if (!state.urls.has(item.id)) {
      const p = (async () => {
        const plain = await decryptWith(state.key, await fetchBytes(VAULT + 'files/' + item.file));
        return URL.createObjectURL(new Blob([plain], { type: item.mime }));
      })();
      state.urls.set(item.id, p);
      p.catch(() => state.urls.delete(item.id));
    }
    return state.urls.get(item.id);
  }

  function visible() {
    return state.items.filter((i) => i.category === state.tab && i.name.toLowerCase().includes(state.q));
  }

  function render() {
    if (state.io) state.io.disconnect();
    list.replaceChildren();
    document.querySelectorAll('[data-tab]').forEach((b) => {
      const cat = b.dataset.tab;
      b.setAttribute('aria-selected', String(cat === state.tab));
      b.querySelector('span').textContent = state.items.filter((i) => i.category === cat).length;
    });
    const items = visible();
    if (!items.length) {
      list.append(el('p', { class: 'empty', text: state.q ? 'মিলছে না এমন কিছু।' : 'এই বিভাগে এখনো কিছু নেই।' }));
      return;
    }
    if (state.tab === 'photos') renderPhotos(items);
    else if (state.tab === 'documents') renderDocs(items);
    else renderMedia(items);
  }

  function renderPhotos(items) {
    const grid = el('div', { class: 'grid' });
    items.forEach((it, idx) => {
      const img = el('img', { alt: it.name, 'data-idx': idx });
      grid.append(el('button', { class: 'tile', type: 'button', title: it.name, onclick: () => openLight(items, idx) }, img));
    });
    list.append(grid);
    state.io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        state.io.unobserve(e.target);
        const it = items[+e.target.dataset.idx];
        urlFor(it).then((u) => { e.target.src = u; }).catch(() => { e.target.alt = '⚠ ' + it.name; });
      }
    }, { rootMargin: '300px' });
    grid.querySelectorAll('img').forEach((i) => state.io.observe(i));
  }

  function renderMedia(items) {
    const isVideo = state.tab === 'videos';
    for (const it of items) {
      const player = el(isVideo ? 'video' : 'audio', { controls: '', preload: 'none', playsinline: '' });
      const btn = el('button', { type: 'button', class: 'ghost', text: 'লোড করুন' });
      btn.addEventListener('click', async () => {
        btn.disabled = true; btn.textContent = 'লোড হচ্ছে…';
        try {
          player.src = await urlFor(it);
          btn.remove();
          player.play().catch(() => {});
        } catch {
          btn.disabled = false; btn.textContent = 'আবার চেষ্টা করুন';
        }
      });
      list.append(el('article', { class: 'row' },
        el('div', { class: 'meta' }, el('strong', { text: it.name }), el('small', { text: human(it.size) })),
        btn, player));
    }
  }

  function renderDocs(items) {
    for (const it of items) {
      const btn = el('button', { type: 'button', class: 'ghost', text: 'খুলুন / ডাউনলোড' });
      btn.addEventListener('click', async () => {
        btn.disabled = true;
        try {
          const a = el('a', { href: await urlFor(it), download: it.name });
          document.body.append(a); a.click(); a.remove();
        } catch {
          msg.textContent = 'ফাইলটি খোলা যায়নি।';
        } finally {
          btn.disabled = false;
        }
      });
      list.append(el('article', { class: 'row' },
        el('div', { class: 'meta' }, el('strong', { text: it.name }), el('small', { text: human(it.size) })),
        btn));
    }
  }

  function openLight(items, idx) {
    lb = { items, idx };
    $('#lightbox').hidden = false;
    showLight();
  }
  async function showLight() {
    const it = lb.items[lb.idx];
    $('#lbCap').textContent = `${lb.idx + 1} / ${lb.items.length} · ${it.name}`;
    const img = $('#lbImg');
    img.removeAttribute('src');
    img.alt = it.name;
    try { img.src = await urlFor(it); } catch { $('#lbCap').textContent = '⚠ ছবিটি খোলা যায়নি'; }
  }
  function moveLight(d) {
    lb.idx = (lb.idx + d + lb.items.length) % lb.items.length;
    showLight();
  }
  function closeLight() {
    $('#lightbox').hidden = true;
    $('#lbImg').removeAttribute('src');
  }

  function lock() {
    for (const p of state.urls.values()) Promise.resolve(p).then((u) => URL.revokeObjectURL(u)).catch(() => {});
    state.urls.clear();
    if (state.io) state.io.disconnect();
    list.replaceChildren();
    closeLight();
    state.key = null; state.items = []; state.q = '';
    $('#search').value = '';
    vault.hidden = true; gate.hidden = false;
    pw.value = ''; pw.focus();
  }

  $('#loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = '';
    if (!window.crypto || !crypto.subtle) {
      msg.textContent = 'এই ব্রাউজারে নিরাপদ এনক্রিপশন নেই। HTTPS সাইটে খুলুন।';
      return;
    }
    const btn = $('#unlockBtn');
    btn.disabled = true; btn.textContent = 'যাচাই হচ্ছে…';
    try {
      await unlock(pw.value);
      pw.value = '';
      gate.hidden = true; vault.hidden = false;
      render();
    } catch (err) {
      msg.textContent = err && err.name === 'OperationError'
        ? 'পাসওয়ার্ড ভুল হয়েছে।'
        : 'ভল্ট পাওয়া যায়নি। প্রথমে private_vault.py দিয়ে ভল্ট তৈরি করুন।';
    } finally {
      btn.disabled = false; btn.textContent = 'খুলুন';
    }
  });

  document.querySelectorAll('[data-tab]').forEach((b) => b.addEventListener('click', () => {
    state.tab = b.dataset.tab; render();
  }));
  $('#search').addEventListener('input', (e) => { state.q = e.target.value.trim().toLowerCase(); render(); });
  $('#lockBtn').addEventListener('click', lock);
  $('#lbClose').addEventListener('click', closeLight);
  $('#lbPrev').addEventListener('click', () => moveLight(-1));
  $('#lbNext').addEventListener('click', () => moveLight(1));
  document.addEventListener('keydown', (e) => {
    if ($('#lightbox').hidden) return;
    if (e.key === 'Escape') closeLight();
    if (e.key === 'ArrowLeft') moveLight(-1);
    if (e.key === 'ArrowRight') moveLight(1);
  });
  // কিছুক্ষণ অ্যাপ ব্যাকগ্রাউন্ডে থাকলে নিজে থেকে লক হবে
  document.addEventListener('visibilitychange', () => {
    clearTimeout(hideTimer);
    if (document.hidden && state.key) hideTimer = setTimeout(lock, AUTO_LOCK_MS);
  });
  if (!window.crypto || !crypto.subtle) msg.textContent = 'এই ব্রাউজারে নিরাপদ এনক্রিপশন নেই। HTTPS সাইটে খুলুন।';
})();
