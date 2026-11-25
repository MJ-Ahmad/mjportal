/* লগইন (ইউজার আইডি + পাসওয়ার্ড), প্রোফাইল, লেজার, গ্যালারি ও অ্যাডমিন প্যানেল।
   অ্যাকাউন্ট: auth.json · প্রোফাইল: client.json · গ্যালারি: gallery.json
   নোট: স্ট্যাটিক সাইটে এটি শুধু প্রবেশ-নিয়ন্ত্রণ। আসল গোপনীয়তার জন্য ভল্ট (এনক্রিপ্টেড) ব্যবহার করুন। */
(() => {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const role = new URLSearchParams(location.search).get('role') === 'admin' ? 'admin' : 'user';
  let session = null; // শুধু মেমোরিতে, কোথাও সংরক্ষণ হয় না

  const sha = async (t) => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)))]
    .map((x) => x.toString(16).padStart(2, '0')).join('');
  const getJSON = async (p) => { const r = await fetch(p, { cache: 'no-cache' }); if (!r.ok) throw new Error(p); return r.json(); };
  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) { if (k === 'text') n.textContent = v; else if (k === 'on') n.addEventListener(v[0], v[1]); else n.setAttribute(k, v); }
    for (const c of kids) if (c) n.append(c);
    return n;
  };
  const bn = (o) => (o && (o.bn || o.en)) || '';
  const money = (n) => '৳ ' + Number(n).toLocaleString('bn-BD');
  const when = (d) => new Date(d).toLocaleString('bn-BD', { timeZone: 'Asia/Dhaka', dateStyle: 'medium', timeStyle: 'short' });

  const ledgerTable = (entries) => {
    const rows = [...entries].sort((a, b) => new Date(a.date) - new Date(b.date)).map((e) => el('tr', {},
      el('td', { text: when(e.date) }),
      el('td', { text: e.type === 'payment' ? 'পরিশোধ' : 'চুক্তি' }),
      el('td', { text: e.amount ? money(e.amount) : '—' }),
      el('td', { text: bn(e.note) + (e.method ? ' · ' + e.method : '') })));
    return el('table', { class: 'ledger' },
      el('thead', {}, el('tr', {}, el('th', { text: 'তারিখ' }), el('th', { text: 'ধরন' }), el('th', { text: 'টাকা' }), el('th', { text: 'বিবরণ' }))),
      el('tbody', {}, ...rows));
  };
  const paidTotal = (c) => c.ledger.filter((e) => e.countsAsPaid).reduce((s, e) => s + Number(e.amount || 0), 0);

  const mediaNode = (it) => {
    if (!it.src) return el('p', { text: 'ফাইল যুক্ত হয়নি' });
    if (it.type === 'video') return el('video', { src: it.src, controls: '', playsinline: '' });
    if (it.type === 'audio') return el('audio', { src: it.src, controls: '', style: 'width:100%' });
    return el('img', { src: it.src, alt: bn(it.title) });
  };
  const gallery = (items) => {
    const wrap = el('div', { class: 'gallery' });
    const tabs = el('div', { class: 'tabs2' });
    const show = (type) => {
      [...tabs.children].forEach((b) => b.setAttribute('aria-selected', String(b.dataset.t === type)));
      wrap.querySelector('.items').replaceChildren(...items.filter((i) => i.type === type).map((i) =>
        el('div', { class: 'item' }, mediaNode(i), el('p', { text: bn(i.title) }))));
      if (!wrap.querySelector('.items').children.length) wrap.querySelector('.items').append(el('p', { text: 'এই বিভাগে এখনো কিছু নেই।' }));
    };
    [['photo', 'ছবি'], ['video', 'ভিডিও'], ['audio', 'অডিও']].forEach(([t, l]) =>
      tabs.append(el('button', { type: 'button', 'data-t': t, 'aria-selected': 'false', on: ['click', () => show(t)] }, l)));
    wrap.append(tabs, el('div', { class: 'items' }));
    show('photo');
    return wrap;
  };

  async function showProfile() {
    const [c, g] = await Promise.all([getJSON('private/client.json'), getJSON('private/gallery.json')]);
    $('#profileBody').replaceChildren(
      el('section', { class: 'hero' },
        el('img', { src: c.photo, alt: bn(c.name) }),
        el('div', {}, el('h2', { text: bn(c.name) }), el('small', { text: c.formalName }),
          el('div', { text: (c.roles || []).map(bn).join(' · ') }))),
      el('h3', { class: 'sec', text: 'লেজার' }),
      ledgerTable(c.ledger),
      el('p', { class: 'total', text: 'মোট পরিশোধ: ' + money(paidTotal(c)) }),
      el('h3', { class: 'sec', text: 'গ্যালারি' }),
      gallery(g.items || []),
      el('h3', { class: 'sec', text: 'ব্যক্তিগত নথি (ভল্ট)' }),
      el('button', { type: 'button', class: 'ghost', on: ['click', () => { $('#profile').hidden = true; $('#gate').hidden = false; }] }, 'ভল্ট পাসফ্রেজ দিয়ে খুলুন'));
    $('#profile').hidden = false;
  }

  async function showAdmin() {
    const c = await getJSON('private/client.json');
    $('#adminBody').replaceChildren(
      el('h3', { class: 'sec', text: 'ক্লায়েন্ট তালিকা' }),
      el('article', { class: 'row' }, el('div', { class: 'meta' },
        el('strong', { text: bn(c.name) }), el('small', { text: c.id + ' · ' + money(paidTotal(c)) + ' পরিশোধ' }))),
      el('h3', { class: 'sec', text: 'আল-আমিনের লেজার' }),
      ledgerTable(c.ledger));
    $('#adminView').hidden = false;
  }

  $('#authForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = $('#authMsg'); msg.textContent = '';
    try {
      const auth = await getJSON('private/auth.json');
      const id = $('#uid').value.trim().toLowerCase();
      const acc = auth.accounts.find((a) => a.id.toLowerCase() === id && a.role === role);
      if (!acc) { msg.textContent = 'আইডি মিলছে না।'; return; }
      if ((await sha($('#upw').value)) !== acc.passwordSha256) { msg.textContent = 'পাসওয়ার্ড ভুল হয়েছে।'; return; }
      session = acc; $('#upw').value = ''; $('#authGate').hidden = true;
      if (role === 'admin') await showAdmin(); else await showProfile();
    } catch { msg.textContent = 'তথ্য লোড হয়নি। HTTPS সাইটে খুলুন।'; }
  });

  document.querySelectorAll('[data-logout]').forEach((b) => b.addEventListener('click', () => {
    session = null;
    ['#profile', '#adminView', '#gate'].forEach((s) => { $(s).hidden = true; });
    $('#profileBody').replaceChildren(); $('#adminBody').replaceChildren();
    $('#authGate').hidden = false; $('#uid').value = ''; $('#upw').value = ''; $('#authMsg').textContent = '';
  }));

  $('#authTitle').textContent = role === 'admin' ? 'অ্যাডমিন লগইন' : 'ইউজার লগইন';
  $('#authSub').textContent = role === 'admin' ? 'অ্যাডমিন আইডি ও পাসওয়ার্ড দিন।' : 'ইউজার আইডি ও পাসওয়ার্ড দিয়ে প্রবেশ করুন।';
})();
