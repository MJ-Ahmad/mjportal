/* Task app front end. Plain JavaScript, no dependencies. All server text is escaped. */
(() => {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const STRINGS = {
    bn: {
      appName: "টাস্ক", password: "পাসওয়ার্ড", signin: "প্রবেশ করুন", logout: "লগআউট", lists: "তালিকা",
      newList: "নতুন তালিকা", search: "খুঁজুন", searchPh: "টাস্ক খুঁজুন…", addPh: "নতুন টাস্ক লিখুন…", add: "যোগ করুন",
      myday: "আমার দিন", important: "গুরুত্বপূর্ণ", planned: "পরিকল্পিত", all: "সব টাস্ক", done: "সম্পন্ন", trash: "ট্র্যাশ",
      inbox: "ইনবক্স", empty: "এখানে কিছু নেই", doneN: "সম্পন্ন", pickTask: "একটি টাস্ক বেছে নিন",
      rename: "নাম বদলান", colour: "রং", deleteList: "তালিকা মুছুন", notes: "নোট", notePh: "বিবরণ বা নোট লিখুন…",
      list: "তালিকা", due: "তারিখ", time: "সময়", repeat: "পুনরাবৃত্তি", priority: "অগ্রাধিকার",
      myDayToggle: "আমার দিনে", starToggle: "গুরুত্বপূর্ণ", checklist: "চেকলিস্ট", addItem: "আইটেম যোগ করুন",
      addSub: "উপ-আইটেম", subPh: "উপ-আইটেম যোগ করুন", tags: "ট্যাগ", tagsPh: "কমা দিয়ে আলাদা করুন",
      comments: "মন্তব্য", commentPh: "মন্তব্য লিখুন…", send: "পাঠান", files: "সংযুক্তি", noFiles: "কোনো সংযুক্তি নেই",
      imported: "পুরনো তথ্য", activity: "কার্যক্রম", created: "তৈরি", trashAction: "ট্র্যাশে সরান",
      restore: "ফিরিয়ে আনুন", purge: "চিরতরে মুছুন", complete: "সম্পন্ন করুন", reopen: "আবার খুলুন",
      today: "আজ", tomorrow: "আগামীকাল", overdue: "মেয়াদোত্তীর্ণ", never: "না", daily: "প্রতিদিন", weekly: "প্রতি সপ্তাহে",
      monthly: "প্রতি মাসে", none: "কিছু না", low: "কম", medium: "মাঝারি", high: "উচ্চ", close: "বন্ধ", lang: "English",
      confirmPurge: "এই টাস্কটি চিরতরে মুছে যাবে। নিশ্চিত?", confirmDeleteList: "তালিকা মুছলে তার টাস্কগুলো ইনবক্সে যাবে। নিশ্চিত?",
      newListPrompt: "নতুন তালিকার নাম", renamePrompt: "নতুন নাম", colourPrompt: "রং (যেমন #7a5af8)",
      wrongPw: "পাসওয়ার্ড ভুল", networkError: "সংযোগ সমস্যা, আবার চেষ্টা করুন", loginNeeded: "আবার প্রবেশ করুন",
      repeatsNext: "পরবর্তী", notAdded: "যোগ করা যায়নি",
    },
    en: {
      appName: "Tasks", password: "Password", signin: "Sign in", logout: "Sign out", lists: "Lists",
      newList: "New list", search: "Search", searchPh: "Search tasks…", addPh: "Add a task…", add: "Add",
      myday: "My Day", important: "Important", planned: "Planned", all: "All tasks", done: "Completed", trash: "Trash",
      inbox: "Inbox", empty: "Nothing here", doneN: "Completed", pickTask: "Select a task",
      rename: "Rename", colour: "Colour", deleteList: "Delete list", notes: "Notes", notePh: "Add details or notes…",
      list: "List", due: "Due date", time: "Time", repeat: "Repeat", priority: "Priority",
      myDayToggle: "In My Day", starToggle: "Important", checklist: "Checklist", addItem: "Add item",
      addSub: "Sub-item", subPh: "Add sub-item", tags: "Tags", tagsPh: "Separate with commas",
      comments: "Comments", commentPh: "Write a comment…", send: "Send", files: "Files", noFiles: "No files",
      imported: "Imported details", activity: "Activity", created: "Created", trashAction: "Move to trash",
      restore: "Restore", purge: "Delete forever", complete: "Complete", reopen: "Reopen",
      today: "Today", tomorrow: "Tomorrow", overdue: "Overdue", never: "Never", daily: "Daily", weekly: "Weekly",
      monthly: "Monthly", none: "None", low: "Low", medium: "Medium", high: "High", close: "Close", lang: "বাংলা",
      confirmPurge: "This task will be deleted permanently. Continue?", confirmDeleteList: "Its tasks will move to Inbox. Continue?",
      newListPrompt: "Name of the new list", renamePrompt: "New name", colourPrompt: "Colour (for example #7a5af8)",
      wrongPw: "Wrong password", networkError: "Connection problem, please try again", loginNeeded: "Please sign in again",
      repeatsNext: "Next", notAdded: "Could not add",
    },
  };

  const LANG_KEY = "tasks-lang";
  const SMART = {
    myday: { icon: "☀", pred: (x) => isOpen(x) && x.my_day },
    important: { icon: "★", pred: (x) => isOpen(x) && x.important },
    planned: { icon: "◷", pred: (x) => isOpen(x) && !!x.due },
    all: { icon: "≡", pred: (x) => isOpen(x) },
    done: { icon: "✓", pred: (x) => !x.deleted_utc && x.status === "done" },
    trash: { icon: "⌧", pred: (x) => !!x.deleted_utc },
  };
  const PRIORITY_RANK = { high: 0, medium: 1, low: 2, none: 3 };

  const state = {
    lang: (() => { try { return localStorage.getItem(LANG_KEY) || "bn"; } catch { return "bn"; } })(),
    lists: [], tasks: [], today: "", view: { kind: "smart", key: "myday" },
    selected: null, search: "", drawer: false, detailOpen: false, showDone: false,
  };

  const t = (key) => STRINGS[state.lang][key] ?? STRINGS.en[key] ?? key;
  const isOpen = (x) => !x.deleted_utc && x.status === "open";
  const listById = (id) => state.lists.find((l) => l.id === id);
  const listName = (id) => {
    const l = listById(id);
    if (!l) return "";
    return l.id === "inbox" ? t("inbox") : l.name;
  };
  const taskById = (id) => state.tasks.find((x) => x.task_id === id);

  /* ---------- dates ---------- */
  const dateLabel = (iso) => {
    const [y, m, d] = iso.split("-").map(Number);
    return new Intl.DateTimeFormat(state.lang === "bn" ? "bn-BD" : "en-GB",
      { day: "numeric", month: "short" }).format(new Date(y, m - 1, d));
  };
  const addDays = (iso, n) => {
    const [y, m, d] = iso.split("-").map(Number);
    const dt = new Date(Date.UTC(y, m - 1, d + n));
    return dt.toISOString().slice(0, 10);
  };
  const dueChip = (x) => {
    if (!x.due || x.status === "done") return null;
    if (x.due < state.today) return { text: `${t("overdue")} · ${dateLabel(x.due)}`, cls: "overdue" };
    if (x.due === state.today) return { text: t("today") + (x.due_time ? ` ${x.due_time}` : ""), cls: "today" };
    if (x.due === addDays(state.today, 1)) return { text: t("tomorrow"), cls: "" };
    return { text: dateLabel(x.due) + (x.due_time ? ` ${x.due_time}` : ""), cls: "" };
  };

  /* ---------- toast and API ---------- */
  let toastTimer = null;
  const toast = (message) => {
    const el = $("#toast");
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
  };

  const request = async (url, options = {}) => {
    const res = await fetch(url, {
      credentials: "same-origin",
      ...options,
      headers: { "Content-Type": "application/json", "X-Requested-With": "taskapp", ...(options.headers || {}) },
    });
    let body = {};
    try { body = await res.json(); } catch { /* empty body */ }
    return { status: res.status, ok: res.ok, body };
  };

  const loadState = async () => {
    const res = await request("/api/state");
    if (res.status === 401) return showLogin();
    if (!res.ok) return toast(t("networkError"));
    state.lists = res.body.lists;
    state.tasks = res.body.tasks;
    state.today = res.body.today;
    if (state.selected && !taskById(state.selected)) state.selected = null;
    showApp();
    render(true);
  };

  /* Every change goes through here. detail=false keeps focus in inputs while typing. */
  const act = async (op, args = {}, detail = true) => {
    const res = await request("/api/op", { method: "POST", body: JSON.stringify({ op, args }) });
    if (res.status === 401) { showLogin(); return null; }
    if (!res.ok) {
      toast(res.body.error || t("notAdded"));
      await loadState();
      return null;
    }
    const result = res.body.result;
    if (op.startsWith("list_")) {
      await loadState();
    } else if (op === "purge") {
      state.tasks = state.tasks.filter((x) => x.task_id !== result.purged);
      if (state.selected === result.purged) state.selected = null;
    } else if (result && result.task_id) {
      const idx = state.tasks.findIndex((x) => x.task_id === result.task_id);
      if (idx >= 0) state.tasks[idx] = result; else state.tasks.unshift(result);
    }
    render(detail);
    return result;
  };

  /* ---------- rendering ---------- */
  const sorted = (rows) => {
    if (state.view.kind === "smart" && state.view.key === "done") {
      return rows.sort((a, b) => (b.done_utc || "").localeCompare(a.done_utc || ""));
    }
    if (state.view.kind === "smart" && state.view.key === "trash") {
      return rows.sort((a, b) => (b.deleted_utc || "").localeCompare(a.deleted_utc || ""));
    }
    return rows.sort((a, b) =>
      (a.due || "9999").localeCompare(b.due || "9999") ||
      (a.due_time || "99:99").localeCompare(b.due_time || "99:99") ||
      PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority] ||
      (a.created_utc || "").localeCompare(b.created_utc || ""));
  };

  const viewPredicate = () => state.view.kind === "smart"
    ? SMART[state.view.key].pred
    : (x) => isOpen(x) && x.list === state.view.key;

  const matchesSearch = (x, q) => {
    if (!q) return true;
    const text = [x.title, x.body, ...x.tags,
      ...x.checklist.flatMap((i) => [i.title, ...i.children.map((c) => c.title)]),
      ...x.comments.map((c) => c.text)].join(" ").toLowerCase();
    return text.includes(q);
  };

  const rowHTML = (x) => {
    const done = x.status === "done";
    const trash = !!x.deleted_utc;
    const meta = [];
    const showList = state.view.kind === "smart" && ["myday", "important", "planned", "all"].includes(state.view.key);
    if (showList) meta.push(`<span class="chip">${esc(listName(x.list))}</span>`);
    const due = dueChip(x);
    if (due) meta.push(`<span class="chip ${due.cls}">${esc(due.text)}</span>`);
    if (x.repeat !== "none") meta.push(`<span class="chip">↻ ${esc(t(x.repeat))}</span>`);
    if (x.checklist.length) {
      const n = x.checklist.filter((i) => i.done).length;
      meta.push(`<span class="chip">☑ ${n}/${x.checklist.length}</span>`);
    }
    if (x.comments.length) meta.push(`<span class="chip">✎ ${x.comments.length}</span>`);
    if (x.attachments.length) meta.push(`<span class="chip">⎘ ${x.attachments.length}</span>`);
    if (x.priority !== "none") meta.push(`<span class="chip prio-${esc(x.priority)}">${esc(t(x.priority))}</span>`);

    const left = trash
      ? ""
      : `<button class="check ${done ? "on" : ""}" type="button" data-act="toggle" data-id="${esc(x.task_id)}"
           aria-label="${esc(done ? t("reopen") : t("complete"))}">${done ? "✓" : ""}</button>`;
    const right = trash
      ? `<div class="task-actions">
           <button class="pill" type="button" data-act="restore" data-id="${esc(x.task_id)}">${esc(t("restore"))}</button>
           <button class="danger" type="button" data-act="purge" data-id="${esc(x.task_id)}">${esc(t("purge"))}</button>
         </div>`
      : `<button class="star ${x.important ? "on" : ""}" type="button" data-act="star" data-id="${esc(x.task_id)}"
           aria-label="${esc(t("starToggle"))}">★</button>`;
    return `<li class="task ${done ? "is-done" : ""} ${state.selected === x.task_id ? "selected" : ""}"
        data-id="${esc(x.task_id)}">
        ${left}
        <div class="tbody" data-act="open" data-id="${esc(x.task_id)}">
          <div class="ttitle">${esc(x.title)}</div>
          ${meta.length ? `<div class="tmeta">${meta.join("")}</div>` : ""}
        </div>
        ${right}
      </li>`;
  };

  const renderSide = () => {
    $("#smart").innerHTML = Object.keys(SMART).map((key) => {
      const count = state.tasks.filter(SMART[key].pred).length;
      const active = state.view.kind === "smart" && state.view.key === key;
      return `<button class="nav-item ${active ? "active" : ""}" type="button" data-act="view"
          data-kind="smart" data-key="${key}">
          <span class="nav-ico">${SMART[key].icon}</span>
          <span class="nav-label">${esc(t(key))}</span>
          <span class="count">${count || ""}</span></button>`;
    }).join("");
    $("#lists").innerHTML = state.lists.map((l) => {
      const count = state.tasks.filter((x) => isOpen(x) && x.list === l.id).length;
      const active = state.view.kind === "list" && state.view.key === l.id;
      return `<button class="nav-item ${active ? "active" : ""}" type="button" data-act="view"
          data-kind="list" data-key="${esc(l.id)}">
          <span class="dot" style="background:${esc(l.color)}"></span>
          <span class="nav-label">${esc(listName(l.id))}</span>
          <span class="count">${count || ""}</span></button>`;
    }).join("");
    $("#langBtn").textContent = t("lang");
  };

  const renderMain = () => {
    const isList = state.view.kind === "list";
    const title = isList ? listName(state.view.key) : t(state.view.key);
    $("#viewTitle").textContent = title;
    $("#listActions").hidden = !isList;
    const hideQuick = state.view.kind === "smart" && (state.view.key === "done" || state.view.key === "trash");
    $("#quick").hidden = hideQuick;

    const q = state.search.trim().toLowerCase();
    const pred = viewPredicate();
    const rows = sorted(state.tasks.filter((x) => pred(x) && matchesSearch(x, q)));
    $("#tasks").innerHTML = rows.length
      ? rows.map(rowHTML).join("")
      : `<li class="empty">${esc(t("empty"))}</li>`;

    const doneRows = isList
      ? state.tasks.filter((x) => !x.deleted_utc && x.status === "done" && x.list === state.view.key && matchesSearch(x, q))
      : [];
    if (doneRows.length) {
      $("#doneWrap").innerHTML = `
        <button class="done-toggle" type="button" data-act="toggleDone" aria-expanded="${state.showDone}">
          ${state.showDone ? "▾" : "▸"} ${esc(t("doneN"))} (${doneRows.length})</button>
        ${state.showDone ? `<ul class="tasks">${sorted(doneRows).map(rowHTML).join("")}</ul>` : ""}`;
    } else {
      $("#doneWrap").innerHTML = "";
    }
  };

  const selectOptions = (items, current, labelFor) => items.map((v) =>
    `<option value="${esc(v)}" ${v === current ? "selected" : ""}>${esc(labelFor(v))}</option>`).join("");

  const itemHTML = (item, parentId) => {
    const isChild = parentId !== null;
    return `<li class="citem ${item.done ? "done" : ""}">
        <input type="checkbox" data-item-check data-item="${item.id}" data-parent="${parentId ?? ""}"
          ${item.done ? "checked" : ""} aria-label="${esc(item.title)}">
        <input class="item-title" value="${esc(item.title)}" data-item-title data-item="${item.id}"
          data-parent="${parentId ?? ""}" data-orig="${esc(item.title)}" maxlength="300">
        ${isChild ? "" : `<button class="mini" type="button" data-act="addsub" data-item="${item.id}" aria-label="${esc(t("addSub"))}">＋</button>`}
        <button class="mini" type="button" data-act="delItem" data-item="${item.id}" data-parent="${parentId ?? ""}"
          aria-label="Delete">×</button>
      </li>`;
  };

  const checklistHTML = (task) => task.checklist.map((item) => {
    const kids = item.children.map((c) => itemHTML(c, item.id)).join("");
    return `${itemHTML(item, null)}
      ${kids ? `<ul class="sub">${kids}</ul>` : ""}
      <form class="item-add sub" data-form="sub" data-parent="${item.id}" hidden>
        <input name="text" maxlength="300" placeholder="${esc(t("subPh"))}" autocomplete="off">
        <button type="submit" aria-label="${esc(t("addSub"))}">＋</button>
      </form>`;
  }).join("");

  const renderDetail = () => {
    const el = $("#detail");
    const x = state.selected ? taskById(state.selected) : null;
    if (!x) {
      el.innerHTML = `<div class="detail-empty">${esc(t("pickTask"))}</div>`;
      return;
    }
    const listOptions = selectOptions(state.lists.map((l) => l.id), x.list, listName);
    const repeatOptions = selectOptions(["none", "daily", "weekly", "monthly"], x.repeat, (v) => t(v === "none" ? "never" : v));
    const prioOptions = selectOptions(["none", "low", "medium", "high"], x.priority, (v) => t(v));
    const legacy = x.legacy || {};
    const legacyRows = [["summary", legacy.summary], ["next_steps", (legacy.next_steps || []).join("\n")],
      ["instructions", (legacy.instructions || []).join("\n")],
      ["references", (legacy.references || []).map((r) => `${r.label}: ${r.value}`).join("\n")],
      ["figures", (legacy.figures || []).map((f) => `${f.label}: ${f.value}`).join("\n")]]
      .filter(([, v]) => v && String(v).trim());
    const legacyHTML = legacyRows.length ? `<section><details><summary>${esc(t("imported"))}</summary>
        <dl class="legacy">${legacyRows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
      </details></section>` : "";
    const comments = x.comments.map((c) => `
      <div class="comment">
        <div class="comment-meta"><span>${esc(c.author || "")} · ${esc(c.dhaka || "")}</span>
          <button class="mini" type="button" data-act="delComment" data-comment="${c.id}" aria-label="Delete">×</button></div>
        <p>${esc(c.text)}</p>
      </div>`).join("");
    const files = x.attachments.length
      ? x.attachments.map((a) => `<a href="/${esc(a.file)}" download>${esc(a.original)}</a>`).join("")
      : `<p class="muted">${esc(t("noFiles"))}</p>`;
    const history = (x.history || []).slice().reverse().map((h) =>
      `<li><small>${esc(h.dhaka)}</small>${esc(h.action)}</li>`).join("");
    const trash = !!x.deleted_utc;

    el.innerHTML = `
      <div class="dhead">
        <button class="icon-btn back" type="button" data-act="close" aria-label="${esc(t("close"))}">←</button>
        ${trash ? "" : `<button class="check ${x.status === "done" ? "on" : ""}" type="button" data-act="toggle"
            data-id="${esc(x.task_id)}" aria-label="${esc(x.status === "done" ? t("reopen") : t("complete"))}">✓</button>`}
        <span class="muted" style="flex:1"></span>
        ${trash ? "" : `<button class="star ${x.important ? "on" : ""}" type="button" data-act="detailStar"
            aria-label="${esc(t("starToggle"))}">★</button>`}
      </div>
      <textarea class="d-title" rows="1" data-field="title" aria-label="${esc(t("list"))}" ${trash ? "disabled" : ""}>${esc(x.title)}</textarea>
      <textarea class="d-body" rows="3" data-field="body" data-i18n-ph="notePh" placeholder="${esc(t("notePh"))}" ${trash ? "disabled" : ""}>${esc(x.body)}</textarea>

      <div class="form-grid">
        <label>${esc(t("list"))}<select data-field="list" ${trash ? "disabled" : ""}>${listOptions}</select></label>
        <label>${esc(t("priority"))}<select data-field="priority" ${trash ? "disabled" : ""}>${prioOptions}</select></label>
        <label>${esc(t("due"))}<input type="date" data-field="due" value="${esc(x.due)}" ${trash ? "disabled" : ""}></label>
        <label>${esc(t("time"))}<input type="time" data-field="due_time" value="${esc(x.due_time)}" ${trash ? "disabled" : ""}></label>
        <label style="grid-column: 1 / -1">${esc(t("repeat"))}<select data-field="repeat" ${trash ? "disabled" : ""}>${repeatOptions}</select></label>
      </div>
      <div class="toggles">
        <button class="pill ${x.my_day ? "on" : ""}" type="button" data-act="myday" ${trash ? "disabled" : ""}>☀ ${esc(t("myDayToggle"))}</button>
        <button class="pill ${x.important ? "on" : ""}" type="button" data-act="detailStar" ${trash ? "disabled" : ""}>★ ${esc(t("starToggle"))}</button>
      </div>

      <section><h3>${esc(t("checklist"))}</h3>
        <ul class="checklist">${checklistHTML(x)}</ul>
        ${trash ? "" : `<form class="item-add" data-form="item">
          <input name="text" maxlength="300" placeholder="${esc(t("addItem"))}" autocomplete="off">
          <button type="submit" aria-label="${esc(t("addItem"))}">＋</button></form>`}
      </section>

      <section><h3>${esc(t("tags"))}</h3>
        <input data-field="tags" value="${esc(x.tags.join(", "))}" placeholder="${esc(t("tagsPh"))}" ${trash ? "disabled" : ""}></section>

      <section><h3>${esc(t("comments"))}</h3>
        ${comments}
        ${trash ? "" : `<form class="comment-form" data-form="comment">
          <textarea name="text" rows="2" maxlength="5000" placeholder="${esc(t("commentPh"))}"></textarea>
          <button class="btn-primary" type="submit">${esc(t("send"))}</button></form>`}
      </section>

      <section><h3>${esc(t("files"))}</h3><div class="files">${files}</div></section>
      ${legacyHTML}

      <section><details><summary>${esc(t("activity"))}</summary>
        <ol class="history">${history}</ol></details></section>

      <div class="dfoot">
        <span class="muted">${esc(t("created"))}: ${esc((x.created_dhaka || "").slice(0, 16))}</span>
        <div class="actions">
          ${trash
            ? `<button class="pill" type="button" data-act="restore" data-id="${esc(x.task_id)}">${esc(t("restore"))}</button>
               <button class="danger" type="button" data-act="purge" data-id="${esc(x.task_id)}">${esc(t("purge"))}</button>`
            : `<button class="danger" type="button" data-act="trashTask" data-id="${esc(x.task_id)}">${esc(t("trashAction"))}</button>`}
        </div>
      </div>`;
  };

  const render = (withDetail) => {
    renderSide();
    renderMain();
    if (withDetail) renderDetail();
    const app = $("#app");
    app.classList.toggle("drawer-open", state.drawer);
    app.classList.toggle("detail-open", state.detailOpen && !!state.selected);
  };

  const applyStatic = () => {
    document.documentElement.lang = state.lang;
    document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
    document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
    document.querySelectorAll("[data-i18n-aria]").forEach((el) => { el.setAttribute("aria-label", t(el.dataset.i18nAria)); });
    $("#langBtn").textContent = t("lang");
  };

  /* ---------- views ---------- */
  const setView = (kind, key) => {
    state.view = { kind, key };
    state.drawer = false;
    state.showDone = false;
    render(false);
  };

  const selectTask = (id) => {
    state.selected = id;
    state.detailOpen = true;
    render(true);
  };

  const closeDetail = () => {
    state.detailOpen = false;
    render(false);
  };

  /* ---------- auth ---------- */
  const showLogin = () => {
    $("#app").hidden = true;
    $("#login").hidden = false;
    setTimeout(() => $("#pw").focus(), 50);
  };
  const showApp = () => {
    $("#login").hidden = true;
    $("#app").hidden = false;
  };

  /* ---------- helpers for forms ---------- */
  const idOf = (el) => el.closest("[data-id]")?.dataset.id;
  const readItem = (el) => ({
    item: parseInt(el.dataset.item, 10),
    parent: el.dataset.parent === "" || el.dataset.parent === undefined ? null : parseInt(el.dataset.parent, 10),
  });

  /* ---------- events ---------- */
  document.addEventListener("click", async (e) => {
    const el = e.target.closest("[data-act]");
    if (!el || el.disabled) return;
    const act_ = el.dataset.act;
    const id = el.dataset.id || idOf(el) || state.selected;

    switch (act_) {
      case "view": return setView(el.dataset.kind, el.dataset.key);
      case "drawer": state.drawer = !state.drawer; return render(false);
      case "lang":
        state.lang = state.lang === "bn" ? "en" : "bn";
        try { localStorage.setItem(LANG_KEY, state.lang); } catch { /* storage blocked */ }
        applyStatic(); return render(true);
      case "logout":
        await request("/api/logout", { method: "POST" });
        state.tasks = []; state.selected = null;
        return showLogin();
      case "toggle":
        e.stopPropagation();
        return act("toggle", { ref: id }, true);
      case "star": {
        const x = taskById(id);
        return act("update", { ref: id, important: !x.important }, false);
      }
      case "detailStar": {
        const x = taskById(state.selected);
        return act("update", { ref: x.task_id, important: !x.important }, true);
      }
      case "myday": {
        const x = taskById(state.selected);
        return act("update", { ref: x.task_id, my_day: !x.my_day }, true);
      }
      case "open": return selectTask(id);
      case "close": return closeDetail();
      case "trashTask":
        await act("delete", { ref: id }, true);
        if (state.selected === id) state.selected = null;
        state.detailOpen = false;
        return render(true);
      case "restore": return act("restore", { ref: id }, true);
      case "purge":
        if (!confirm(t("confirmPurge"))) return;
        if (state.selected === id) state.selected = null;
        return act("purge", { ref: id }, true);
      case "addsub": {
        const form = document.querySelector(`[data-form="sub"][data-parent="${el.dataset.item}"]`);
        if (form) { form.hidden = !form.hidden; if (!form.hidden) form.querySelector("input").focus(); }
        return;
      }
      case "delItem": {
        const { item, parent } = readItem(el);
        return act("check_del", { ref: state.selected, item, parent }, true);
      }
      case "delComment":
        return act("comment_del", { ref: state.selected, comment: parseInt(el.dataset.comment, 10) }, true);
      case "toggleDone":
        state.showDone = !state.showDone; return render(false);
      case "newList": {
        const name = prompt(t("newListPrompt"));
        if (!name || !name.trim()) return;
        const created = await act("list_add", { name: name.trim() }, false);
        if (created) setView("list", created.id);
        return;
      }
      case "renameList": {
        const current = listById(state.view.key);
        const name = prompt(t("renamePrompt"), current ? current.name : "");
        if (!name || !name.trim()) return;
        return act("list_update", { list_id: state.view.key, name: name.trim() }, false);
      }
      case "colourList": {
        const color = prompt(t("colourPrompt"), listById(state.view.key)?.color || "#7a5af8");
        if (!color) return;
        return act("list_update", { list_id: state.view.key, color: color.trim() }, false);
      }
      case "deleteList":
        if (!confirm(t("confirmDeleteList"))) return;
        await act("list_delete", { list_id: state.view.key }, false);
        return setView("smart", "all");
      default: return;
    }
  });

  document.addEventListener("change", (e) => {
    const el = e.target;
    if (el.matches("[data-item-check]")) {
      const { item, parent } = readItem(el);
      return act("check_set", { ref: state.selected, item, parent, done: el.checked }, true);
    }
    if (el.matches("[data-field]") && el.tagName !== "TEXTAREA" && el.type !== "text") {
      return saveField(el);
    }
  });

  document.addEventListener("focusout", (e) => {
    const el = e.target;
    if (el.matches("[data-item-title]")) {
      const text = el.value.trim();
      if (!text) { el.value = el.dataset.orig; return; }
      if (text === el.dataset.orig) return;
      const { item, parent } = readItem(el);
      return act("check_set", { ref: state.selected, item, parent, title: text }, false);
    }
    if (el.matches("[data-field]") && (el.tagName === "TEXTAREA" || el.type === "text")) {
      return saveField(el);
    }
  });

  const saveField = (el) => {
    const x = taskById(state.selected);
    if (!x) return;
    const field = el.dataset.field;
    let value = el.value;
    if (field === "title" && !value.trim()) { el.value = x.title; return; }
    if (field === "tags") value = value.split(",").map((s) => s.trim()).filter(Boolean);
    if (field === "due" || field === "due_time") value = value || "";
    const current = field === "tags" ? x.tags : x[field];
    if (JSON.stringify(current) === JSON.stringify(value)) return;
    act("update", { ref: x.task_id, [field]: value }, false);
  };

  document.addEventListener("submit", async (e) => {
    const form = e.target;
    if (form.id === "loginForm") {
      e.preventDefault();
      const res = await request("/api/login", { method: "POST", body: JSON.stringify({ password: $("#pw").value }) });
      const err = $("#loginErr");
      if (!res.ok) {
        err.textContent = res.body.error || t("wrongPw");
        err.hidden = false;
        return;
      }
      err.hidden = true;
      $("#pw").value = "";
      return loadState();
    }
    if (form.id === "quick") {
      e.preventDefault();
      const input = $("#quickInput");
      const title = input.value.trim();
      if (!title) return;
      const args = { title };
      if (state.view.kind === "list") args.list = state.view.key;
      if (state.view.kind === "smart") {
        if (state.view.key === "myday") args.my_day = true;
        if (state.view.key === "important") args.important = true;
        if (state.view.key === "planned") args.due = "today";
      }
      input.value = "";
      input.focus();
      const created = await act("create", args, false);
      if (!created) input.value = title;
      return;
    }
    if (form.dataset.form === "item") {
      e.preventDefault();
      const text = form.text.value.trim();
      if (!text || !state.selected) return;
      form.text.value = "";
      await act("check_add", { ref: state.selected, title: text }, true);
      return;
    }
    if (form.dataset.form === "sub") {
      e.preventDefault();
      const text = form.text.value.trim();
      if (!text || !state.selected) return;
      form.text.value = "";
      await act("check_add", { ref: state.selected, title: text, parent: parseInt(form.dataset.parent, 10) }, true);
      return;
    }
    if (form.dataset.form === "comment") {
      e.preventDefault();
      const text = form.text.value.trim();
      if (!text || !state.selected) return;
      await act("comment_add", { ref: state.selected, text }, true);
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (state.drawer) { state.drawer = false; render(false); }
      else if (state.detailOpen) closeDetail();
    }
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && e.target.name === "text") {
      e.target.form?.requestSubmit();
    }
  });

  $("#search").addEventListener("input", (e) => {
    state.search = e.target.value;
    renderMain();
  });

  /* ---------- boot ---------- */
  applyStatic();
  request("/api/me").then((res) => (res.ok ? loadState() : showLogin()));

  setInterval(() => {
    const busy = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName);
    if (document.hidden || busy || $("#app").hidden) return;
    loadState();
  }, 30000);
})();
