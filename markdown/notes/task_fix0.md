নিশ্চয়ই। নিচে `task/index.html`, `task/run.sh`, `task/_lib.py` ও `task/validate.py`—চারটি ফাইলের পূর্ণ বিকল্প দিলাম। এগুলো পুরোনো task data পড়ার সঙ্গে সামঞ্জস্য রাখে; নতুন task-এ step-এর parent ও note field যোগ করে, মোবাইল layout উন্নত করে, header-এর ভুল “Last updated” বাদ দেয় এবং footer-এ শুধু CLI বোতাম রাখে।

**প্রতিস্থাপনের আগে backup নিন**, বিশেষ করে `task/data.json`, `task/registry.json` ও `task/attachments/`-এর। নিচের চারটি ফাইলের প্রতিটির সম্পূর্ণ content দিয়ে সংশ্লিষ্ট ফাইলটি replace করুন।

## ১. `task/index.html`

```html name=task/index.html url=https://github.com/MJ-Ahmad/mjportal/blob/main/task/index.html
<!doctype html>
<html lang="bn">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="description" content="Stewardship Task System: task tracking, nested steps and audit dashboard">
  <meta name="theme-color" content="#0f2a44">
  <title>Stewardship Task System</title>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">

  <style>
    :root {
      --ink: #0f2a44;
      --ink-2: #1e4467;
      --paper: #f4f2ec;
      --surface: #ffffff;
      --surface-2: #faf9f5;
      --line: #e2ded3;
      --text: #1b2430;
      --muted: #5d6878;
      --gold: #a87a2c;
      --done: #2e7d5b;
      --live: #b5651d;
      --focus: #2b6cb0;
      --danger: #ad3f32;
      --radius: 12px;
      --shadow: 0 1px 2px rgba(15, 42, 68, .06), 0 8px 22px rgba(15, 42, 68, .06);
      --sans: "Hind Siliguri", system-ui, -apple-system, "Segoe UI", sans-serif;
      --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
      color-scheme: light;
    }

    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) {
        --ink: #0a1b2c;
        --ink-2: #17324f;
        --paper: #0c1620;
        --surface: #122131;
        --surface-2: #0f1d2b;
        --line: #24364a;
        --text: #e5ebf2;
        --muted: #9aa8b9;
        --gold: #d9a54b;
        --done: #4fb88a;
        --live: #e0964d;
        --focus: #7fb2ec;
        --danger: #f08a7b;
        --shadow: none;
        color-scheme: dark;
      }
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    html {
      scroll-behavior: smooth;
      scroll-padding-top: 16px;
    }

    body {
      min-height: 100vh;
      padding-top: env(safe-area-inset-top, 0px);
      padding-bottom: env(safe-area-inset-bottom, 0px);
      background: var(--paper);
      color: var(--text);
      font-family: var(--sans);
      font-size: 16px;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }

    button,
    input {
      font: inherit;
    }

    button {
      color: inherit;
    }

    :focus-visible {
      outline: 2px solid var(--focus);
      outline-offset: 2px;
      border-radius: 6px;
    }

    .wrap {
      width: min(1180px, 100% - 32px);
      margin-inline: auto;
    }

    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
      white-space: nowrap;
    }

    /* Header */
    .masthead {
      padding: 27px 0 25px;
      border-bottom: 3px solid var(--gold);
      background: var(--ink);
      color: #f4f7fb;
    }

    .masthead-row {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }

    .logo,
    .logo-fallback {
      width: 62px;
      height: 62px;
      flex: 0 0 62px;
      border: 1px solid rgba(255, 255, 255, .18);
      border-radius: 14px;
      background: rgba(255, 255, 255, .08);
      object-fit: contain;
    }

    .logo-fallback {
      display: grid;
      place-items: center;
      color: var(--gold);
      font: 600 18px var(--mono);
      letter-spacing: .04em;
    }

    .masthead h1 {
      font-size: clamp(1.35rem, 2.6vw, 1.85rem);
      font-weight: 700;
      line-height: 1.25;
    }

    .masthead .sub {
      margin-top: 3px;
      opacity: .8;
      font-size: .94rem;
    }

    .masthead-tools {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-inline-start: auto;
    }

    .lang-switch {
      display: inline-flex;
      padding: 3px;
      border: 1px solid rgba(255, 255, 255, .25);
      border-radius: 999px;
      background: rgba(255, 255, 255, .06);
    }

    .lang-switch button {
      min-width: 44px;
      padding: 6px 12px;
      border: 0;
      border-radius: 999px;
      background: transparent;
      color: #cfd9e6;
      font: 600 13px var(--mono);
      cursor: pointer;
    }

    .lang-switch button[aria-pressed="true"] {
      background: #f4f7fb;
      color: var(--ink);
    }

    .lang-switch button[lang="bn"] {
      font-family: var(--sans);
      font-size: 14px;
    }

    /* Statistics */
    .stats {
      position: relative;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 13px;
      margin: -22px 0 23px;
    }

    .stat {
      min-width: 0;
      padding: 15px 17px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: var(--shadow);
    }

    .stat .label {
      color: var(--muted);
      font-size: 13px;
    }

    .stat .value {
      margin-top: 4px;
      color: var(--text);
      font-size: clamp(1.55rem, 3vw, 2.05rem);
      font-weight: 700;
      line-height: 1.15;
      font-variant-numeric: tabular-nums;
    }

    .stat .bar {
      height: 6px;
      margin-top: 10px;
      overflow: hidden;
      border-radius: 6px;
      background: var(--line);
    }

    .stat .bar span {
      display: block;
      height: 100%;
      background: var(--done);
      transition: width .4s ease;
    }

    /* Search and filters */
    .toolbar {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 17px;
    }

    .search {
      position: relative;
      flex: 1 1 270px;
    }

    .search input {
      width: 100%;
      padding: 11px 13px 11px 39px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--surface);
      color: var(--text);
      font: inherit;
      font-size: 15px;
    }

    .search input::placeholder {
      color: var(--muted);
    }

    .search svg {
      position: absolute;
      top: 50%;
      left: 13px;
      width: 16px;
      height: 16px;
      color: var(--muted);
      transform: translateY(-50%);
    }

    .filters {
      display: inline-flex;
      gap: 4px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--surface);
    }

    .filters button {
      padding: 7px 12px;
      border: 0;
      border-radius: 7px;
      background: transparent;
      color: var(--muted);
      font-size: 14px;
      cursor: pointer;
    }

    .filters button[aria-pressed="true"] {
      background: var(--ink);
      color: #f4f7fb;
    }

    .count {
      margin-inline-start: auto;
      color: var(--muted);
      font: 400 12px var(--mono);
    }

    /* Task cards */
    .list {
      display: grid;
      gap: 14px;
    }

    .card {
      min-width: 0;
      padding: 19px 21px;
      border: 1px solid var(--line);
      border-inline-start: 4px solid var(--live);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: var(--shadow);
    }

    .card.is-done {
      border-inline-start-color: var(--done);
    }

    .card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 9px;
      flex-wrap: wrap;
    }

    .status {
      padding: 3px 10px;
      border-radius: 999px;
      color: #fff;
      font-size: 12px;
      font-weight: 600;
    }

    .status.live {
      background: var(--live);
    }

    .status.done {
      background: var(--done);
    }

    .ids,
    .stamps {
      display: flex;
      gap: 7px;
      flex-wrap: wrap;
    }

    .ids span,
    .stamps span {
      max-width: 100%;
      padding: 4px 8px;
      overflow-wrap: anywhere;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--surface-2);
      color: var(--text);
      font: 500 11px var(--mono);
    }

    .stamps {
      margin-top: 11px;
    }

    .stamps b {
      margin-inline-end: 4px;
      color: var(--muted);
      font-weight: 600;
    }

    .card-title {
      margin: 13px 0 7px;
      color: var(--text);
      font-size: 1.2rem;
      font-weight: 700;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }

    .preview {
      display: -webkit-box;
      overflow: hidden;
      color: var(--muted);
      white-space: pre-line;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 4;
    }

    .progress-row {
      display: flex;
      align-items: center;
      gap: 11px;
      margin-top: 14px;
    }

    .progress-row .bar {
      height: 8px;
      flex: 1;
      overflow: hidden;
      border-radius: 8px;
      background: var(--line);
    }

    .progress-row .bar span {
      display: block;
      height: 100%;
      border-radius: 8px;
      background: var(--done);
    }

    .pct {
      color: var(--muted);
      font: 500 12px var(--mono);
      white-space: nowrap;
    }

    .toggle {
      width: 100%;
      margin-top: 14px;
      padding: 10px 13px;
      border: 1px solid var(--focus);
      border-radius: 9px;
      background: transparent;
      color: var(--focus);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: background .15s, color .15s;
    }

    .toggle:hover {
      border-color: var(--ink);
      background: var(--ink);
      color: #f4f7fb;
    }

    .details {
      margin-top: 16px;
      padding-top: 5px;
      border-top: 1px solid var(--line);
    }

    .details[hidden] {
      display: none;
    }

    .details h3 {
      margin: 18px 0 8px;
      color: var(--focus);
      font-size: 15px;
      font-weight: 700;
    }

    .full {
      white-space: pre-line;
      overflow-wrap: anywhere;
    }

    .note {
      margin-bottom: 7px;
      padding: 9px 11px;
      border-inline-start: 3px solid var(--gold);
      border-radius: 6px;
      background: var(--surface-2);
      overflow-wrap: anywhere;
    }

    .note small {
      display: block;
      margin-top: 3px;
      color: var(--muted);
      font: 400 11px/1.5 var(--mono);
    }

    .steps {
      display: grid;
      gap: 7px;
      list-style: none;
    }

    .step {
      display: flex;
      align-items: flex-start;
      gap: 9px;
      min-width: 0;
      padding: 9px 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface-2);
    }

    .step-content {
      min-width: 0;
      flex: 1;
    }

    .step .mark {
      width: 25px;
      height: 25px;
      display: grid;
      flex: 0 0 25px;
      place-items: center;
      border: 1.5px solid var(--muted);
      border-radius: 50%;
      color: var(--muted);
      font: 600 11px var(--mono);
    }

    .step.ok .mark {
      border-color: var(--done);
      background: var(--done);
      color: #fff;
    }

    .step-title {
      font-weight: 500;
      overflow-wrap: anywhere;
    }

    .step:not(.ok) .step-title {
      color: var(--muted);
    }

    .step-time {
      margin-top: 2px;
      color: var(--muted);
      font: 400 11px/1.5 var(--mono);
      overflow-wrap: anywhere;
    }

    .nested-steps {
      margin-top: 8px;
      margin-inline-start: 14px;
      padding-inline-start: 9px;
      border-inline-start: 2px solid var(--line);
    }

    .step-notes {
      display: grid;
      gap: 5px;
      margin-top: 7px;
    }

    .step-note {
      display: grid;
      gap: 2px;
      padding: 7px 9px;
      border-inline-start: 3px solid var(--gold);
      border-radius: 6px;
      background: var(--surface);
      font-size: 13px;
      overflow-wrap: anywhere;
    }

    .step-note small {
      color: var(--muted);
      font: 400 10px/1.5 var(--mono);
    }

    .history {
      display: grid;
      gap: 9px;
      margin-inline-start: 6px;
      padding-inline-start: 15px;
      border-inline-start: 2px solid var(--line);
      list-style: none;
    }

    .history li {
      position: relative;
      overflow-wrap: anywhere;
    }

    .history li::before {
      position: absolute;
      top: 8px;
      inset-inline-start: -20px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--gold);
      content: "";
    }

    .history .mono {
      display: block;
      color: var(--muted);
      font: 400 11px/1.5 var(--mono);
    }

    .files {
      display: flex;
      gap: 7px;
      flex-wrap: wrap;
    }

    .file {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      max-width: 100%;
      padding: 7px 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface-2);
      color: var(--focus);
      font-size: 13px;
      text-decoration: none;
      overflow-wrap: anywhere;
    }

    .file small {
      color: var(--muted);
      font: 400 10px var(--mono);
    }

    .muted {
      color: var(--muted);
      font-size: 14px;
    }

    .completed-box {
      margin-top: 11px;
      padding: 11px;
      border: 1px solid color-mix(in srgb, var(--done) 40%, transparent);
      border-radius: 8px;
      background: color-mix(in srgb, var(--done) 12%, transparent);
      font: 400 12px/1.7 var(--mono);
      overflow-wrap: anywhere;
    }

    .overview {
      margin-top: 9px;
      padding: 11px 13px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface-2);
      color: var(--muted);
      font: 400 13px/1.7 var(--sans);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .empty,
    .error {
      padding: 25px;
      border: 1px dashed var(--line);
      border-radius: var(--radius);
      background: var(--surface);
      color: var(--muted);
      text-align: center;
      overflow-wrap: anywhere;
    }

    .error {
      border-color: var(--live);
      color: var(--text);
      text-align: start;
    }

    .error code,
    .empty code,
    .dlg-body code {
      padding: 2px 5px;
      border-radius: 4px;
      background: var(--surface-2);
      font: 500 12px var(--mono);
      overflow-wrap: anywhere;
    }

    /* Footer: CLI only */
    .footer {
      margin-top: 42px;
      padding: 28px 0 19px;
      background: var(--ink);
      color: #e8eef6;
    }

    .footer-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      flex-wrap: wrap;
    }

    .footer h4 {
      margin-bottom: 5px;
      color: var(--gold);
      font-size: 14px;
    }

    .footer p {
      font-size: 13px;
      opacity: .86;
    }

    .footer-owner {
      margin-top: 5px;
    }

    .footer-cli {
      min-height: 40px;
      padding: 8px 14px;
      border: 1px solid rgba(255, 255, 255, .32);
      border-radius: 8px;
      background: transparent;
      color: #e8eef6;
      cursor: pointer;
    }

    .footer-cli:hover {
      border-color: var(--gold);
      color: var(--gold);
    }

    .footer-bottom {
      width: 100%;
      display: flex;
      justify-content: space-between;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid rgba(255, 255, 255, .14);
      opacity: .68;
      font: 400 10px var(--mono);
    }

    /* CLI dialog */
    dialog {
      width: min(680px, 94vw);
      max-height: 86dvh;
      padding: 0;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: var(--surface);
      color: var(--text);
      box-shadow: 0 24px 60px rgba(0, 0, 0, .35);
    }

    dialog::backdrop {
      background: rgba(8, 20, 34, .58);
    }

    .dlg-head {
      position: sticky;
      top: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 14px 18px;
      border-bottom: 1px solid var(--line);
      background: var(--surface);
    }

    .dlg-head h2 {
      font-size: 1.08rem;
    }

    .dlg-body {
      display: grid;
      gap: 14px;
      padding: 16px 18px 20px;
      font-size: 14px;
    }

    .dlg-body h3 {
      margin-bottom: 6px;
      color: var(--focus);
      font-size: 14px;
    }

    .cmd {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface-2);
    }

    .cmd code {
      min-width: 0;
      flex: 1;
      overflow: auto;
      font: 400 11px/1.5 var(--mono);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .cmd button,
    .close {
      min-height: 32px;
      padding: 5px 9px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--surface);
      color: var(--text);
      font-size: 12px;
      cursor: pointer;
      white-space: nowrap;
    }

    @media (max-width: 900px) {
      .stats {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 600px) {
      .wrap {
        width: min(100% - 24px, 1180px);
      }

      .masthead {
        padding: 18px 0 52px;
      }

      .masthead-row {
        align-items: flex-start;
        gap: 11px;
      }

      .logo,
      .logo-fallback {
        width: 50px;
        height: 50px;
        flex-basis: 50px;
      }

      .masthead .sub {
        font-size: 13px;
      }

      .masthead-tools {
        width: 100%;
        justify-content: flex-end;
        margin-inline-start: 0;
      }

      .stats {
        gap: 8px;
        margin-top: -36px;
      }

      .stat {
        padding: 11px 12px;
      }

      .stat .label {
        font-size: 12px;
      }

      .stat .value {
        font-size: 1.55rem;
      }

      .toolbar {
        align-items: stretch;
        gap: 8px;
      }

      .search {
        flex-basis: 100%;
      }

      .filters {
        width: 100%;
      }

      .filters button {
        min-width: 0;
        flex: 1;
        padding: 8px 4px;
        font-size: 13px;
      }

      .count {
        margin-inline-start: 0;
      }

      .card {
        padding: 15px 13px;
      }

      .card-title {
        font-size: 1.08rem;
      }

      .ids,
      .stamps {
        gap: 5px;
      }

      .ids span,
      .stamps span {
        font-size: 9px;
      }

      .step {
        gap: 7px;
        padding: 8px 7px;
      }

      .nested-steps {
        margin-inline-start: 6px;
        padding-inline-start: 6px;
      }

      .footer {
        margin-top: 28px;
        padding: 20px 0 calc(17px + env(safe-area-inset-bottom, 0px));
      }

      .footer-inner {
        align-items: stretch;
        flex-direction: column;
        gap: 12px;
      }

      .footer-cli {
        width: 100%;
      }

      .footer-bottom {
        flex-direction: column;
      }

      .dlg-body {
        padding: 13px;
      }

      .cmd {
        align-items: stretch;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      html {
        scroll-behavior: auto;
      }

      *,
      *::before,
      *::after {
        transition: none !important;
      }
    }
  </style>
</head>

<body>
  <header class="masthead">
    <div class="wrap masthead-row">
      <img class="logo" id="logo" src="assets/logo.png" alt="">
      <div>
        <h1 data-i18n="title">Stewardship Task System</h1>
        <div class="sub" data-i18n="subtitle"></div>
      </div>
      <div class="masthead-tools">
        <div class="lang-switch" role="group" aria-label="Language / ভাষা">
          <button type="button" data-lang-btn="en" lang="en" aria-pressed="false">EN</button>
          <button type="button" data-lang-btn="bn" lang="bn" aria-pressed="true">বাংলা</button>
        </div>
      </div>
    </div>
  </header>

  <main class="wrap">
    <section class="stats" id="stats" aria-live="polite"></section>

    <div class="toolbar">
      <label class="search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2" aria-hidden="true">
          <circle cx="11" cy="11" r="7"></circle>
          <path d="m20 20-3.5-3.5"></path>
        </svg>
        <span class="sr-only" data-i18n="searchLabel"></span>
        <input id="search" type="search" autocomplete="off" data-i18n-ph="searchPh">
      </label>

      <div class="filters" role="group" data-i18n-aria="filterLabel">
        <button type="button" data-filter="all" aria-pressed="true" data-i18n="filterAll"></button>
        <button type="button" data-filter="active" aria-pressed="false" data-i18n="filterActive"></button>
        <button type="button" data-filter="completed" aria-pressed="false" data-i18n="filterCompleted"></button>
      </div>

      <span class="count" id="count"></span>
    </div>

    <section class="list" id="list" aria-live="polite"></section>
  </main>

  <footer class="footer">
    <div class="wrap footer-inner">
      <div>
        <h4 data-i18n="footBrand"></h4>
        <p data-i18n="footDesc"></p>
        <p class="footer-owner">
          <span data-i18n="footOwner"></span>
          <strong>mj-ahmad</strong>
        </p>
      </div>

      <button class="footer-cli" type="button" data-open-cli data-i18n="linkCli"></button>

      <div class="footer-bottom">
        <span>© 2026 Stewardship Task System</span>
        <span>Dhaka UTC+06 · ISO 8601</span>
      </div>
    </div>
  </footer>

  <dialog id="dlg-cli" aria-labelledby="h-cli">
    <div class="dlg-head">
      <h2 id="h-cli" data-i18n="cliTitle"></h2>
      <button class="close" type="button" data-close data-i18n="close"></button>
    </div>

    <div class="dlg-body">
      <div>
        <h3 data-i18n="cliNew"></h3>
        <div class="cmd">
          <code>./run.sh task "Heading" "Description" --steps "Step 1, Step 2"</code>
          <button type="button" data-copy='./run.sh task "Heading" "Description" --steps "Step 1, Step 2"'></button>
        </div>
      </div>

      <div>
        <h3 data-i18n="cliAddStep"></h3>
        <div class="cmd">
          <code>./run.sh step-add TASK-000001 "New step"</code>
          <button type="button" data-copy='./run.sh step-add TASK-000001 "New step"'></button>
        </div>
      </div>

      <div>
        <h3 data-i18n="cliSubstep"></h3>
        <div class="cmd">
          <code>./run.sh step-add TASK-000001 "Substep" --parent 2</code>
          <button type="button" data-copy='./run.sh step-add TASK-000001 "Substep" --parent 2'></button>
        </div>
      </div>

      <div>
        <h3 data-i18n="cliStepNote"></h3>
        <div class="cmd">
          <code>./run.sh step-note TASK-000001 2 "Step note"</code>
          <button type="button" data-copy='./run.sh step-note TASK-000001 2 "Step note"'></button>
        </div>
      </div>

      <div>
        <h3 data-i18n="cliTrack"></h3>
        <div class="cmd">
          <code>./run.sh track TASK-000001 1</code>
          <button type="button" data-copy="./run.sh track TASK-000001 1"></button>
        </div>
      </div>

      <div>
        <h3 data-i18n="cliComplete"></h3>
        <div class="cmd">
          <code>./run.sh complete TASK-000001</code>
          <button type="button" data-copy="./run.sh complete TASK-000001"></button>
        </div>
      </div>

      <div>
        <h3 data-i18n="cliValidate"></h3>
        <div class="cmd">
          <code>./run.sh validate</code>
          <button type="button" data-copy="./run.sh validate"></button>
        </div>
      </div>

      <div>
        <h3 data-i18n="cliWeb"></h3>
        <div class="cmd">
          <code>./run.sh web</code>
          <button type="button" data-copy="./run.sh web"></button>
        </div>
        <p class="muted" style="margin-top:7px" data-i18n="cliPhone"></p>
      </div>
    </div>
  </dialog>

  <script>
    (() => {
      "use strict";

      const STRINGS = {
        bn: {
          title: "Stewardship Task System",
          subtitle: "টাস্ক ট্র্যাকিং · রেজিস্ট্রি · ধাপভিত্তিক অগ্রগতি",
          statTotal: "মোট টাস্ক",
          statActive: "সক্রিয়",
          statCompleted: "সম্পন্ন",
          statProgress: "সামগ্রিক ধাপের অগ্রগতি",
          steps: "ধাপ",
          searchLabel: "অনুসন্ধান",
          searchPh: "TASK / REG ID, শিরোনাম, নোট, ধাপ বা সাবধাপ খুঁজুন…",
          filterLabel: "স্ট্যাটাস ফিল্টার",
          filterAll: "সব",
          filterActive: "সক্রিয়",
          filterCompleted: "সম্পন্ন",
          statusActive: "সক্রিয়",
          statusDone: "সম্পন্ন",
          idTask: "টাস্ক আইডি",
          idReg: "রেজিস্ট্রি আইডি",
          dhaka: "ঢাকা",
          viewRecord: "সম্পূর্ণ রেকর্ড দেখুন",
          hideRecord: "রেকর্ড বন্ধ করুন",
          fullDesc: "পূর্ণ বিবরণ",
          completedAt: "সম্পন্ন",
          notes: "টাস্কের নোট",
          noNotes: "কোনো টাস্ক নোট নেই।",
          stepsTitle: "ধাপ ও সাবধাপ",
          noSteps: "কোনো ধাপ নির্ধারিত নেই।",
          pending: "বাকি",
          files: "সংযুক্তি",
          noFiles: "কোনো সংযুক্তি নেই।",
          archive: "আর্কাইভ রিপোর্ট",
          history: "কার্যক্রম ইতিহাস",
          noHistory: "কোনো ইতিহাস নেই।",
          countOf: (n, m) => `${n} / ${m} টাস্ক`,
          emptyAll: 'এখনও কোনো টাস্ক নেই। <code>./run.sh task "শিরোনাম" "বিবরণ"</code> দিয়ে শুরু করুন।',
          emptyFilter: "কোনো টাস্ক মেলেনি। অনুসন্ধান বা ফিল্টার বদলান।",
          loadFail: "ডেটা লোড হয়নি",
          loadFailHelp: 'পেজটি HTTP সার্ভারে চালান: <code>./run.sh web</code>। সরাসরি ফাইল হিসেবে খুললে browser <code>data.json</code> পড়তে পারবে না।',
          copy: "কপি",
          copied: "কপি হয়েছে ✓",
          copyFail: "কপি হয়নি",
          footBrand: "Stewardship Task System",
          footDesc: "প্রতিটি টাস্ক, ধাপ, নোট ও সময়ের রেকর্ড এক জায়গায় রাখুন।",
          footOwner: "মালিক:",
          linkCli: "CLI কমান্ড",
          close: "বন্ধ করুন",
          cliTitle: "CLI কমান্ড",
          cliNew: "নতুন টাস্ক",
          cliAddStep: "নতুন ধাপ যোগ",
          cliSubstep: "ধাপের অধীনে সাবধাপ যোগ",
          cliStepNote: "ধাপে timestamp-সহ নোট যোগ",
          cliTrack: "ধাপ সম্পন্ন",
          cliComplete: "টাস্ক সম্পন্ন ও আর্কাইভ",
          cliValidate: "ডেটা যাচাই",
          cliWeb: "ড্যাশবোর্ড চালু",
          cliPhone: 'নিজের trusted network-এ অন্য device থেকে দেখতে: <code>BIND=0.0.0.0 ./run.sh web</code>',
          copyCommand: "কপি",
          invalidData: "ডেটার কাঠামো সঠিক নয়।",
          attachmentUnavailable: "সংযুক্তি পাওয়া যায়নি।"
        },
        en: {
          title: "Stewardship Task System",
          subtitle: "Task tracking · Registry · Nested-step progress",
          statTotal: "Total tasks",
          statActive: "Active",
          statCompleted: "Completed",
          statProgress: "Overall step progress",
          steps: "steps",
          searchLabel: "Search",
          searchPh: "Search TASK / REG ID, title, notes, steps or substeps…",
          filterLabel: "Status filter",
          filterAll: "All",
          filterActive: "Active",
          filterCompleted: "Completed",
          statusActive: "Active",
          statusDone: "Completed",
          idTask: "Task ID",
          idReg: "Registry ID",
          dhaka: "Dhaka",
          viewRecord: "View full record",
          hideRecord: "Hide record",
          fullDesc: "Full description",
          completedAt: "Completed",
          notes: "Task notes",
          noNotes: "No task notes.",
          stepsTitle: "Steps and substeps",
          noSteps: "No steps defined.",
          pending: "Pending",
          files: "Attachments",
          noFiles: "No attachments.",
          archive: "Archive report",
          history: "Activity history",
          noHistory: "No history.",
          countOf: (n, m) => `${n} / ${m} tasks`,
          emptyAll: 'No tasks yet. Start with <code>./run.sh task "Heading" "Description"</code>.',
          emptyFilter: "No tasks match. Change the search or filter.",
          loadFail: "Could not load data",
          loadFailHelp: 'Serve this page over HTTP with <code>./run.sh web</code>. Opening the file directly prevents the browser from reading <code>data.json</code>.',
          copy: "Copy",
          copied: "Copied ✓",
          copyFail: "Copy failed",
          footBrand: "Stewardship Task System",
          footDesc: "Keep task, step, note, and timestamp records in one place.",
          footOwner: "Owner:",
          linkCli: "CLI commands",
          close: "Close",
          cliTitle: "CLI commands",
          cliNew: "Create a task",
          cliAddStep: "Add a step",
          cliSubstep: "Add a substep",
          cliStepNote: "Add a timestamped step note",
          cliTrack: "Complete a step",
          cliComplete: "Complete and archive a task",
          cliValidate: "Validate data",
          cliWeb: "Start dashboard",
          cliPhone: 'On your trusted local network: <code>BIND=0.0.0.0 ./run.sh web</code>',
          copyCommand: "Copy",
          invalidData: "The data structure is invalid.",
          attachmentUnavailable: "Attachment is unavailable."
        }
      };

      const LANG_KEY = "sts-lang";
      const $ = (selector, root = document) => root.querySelector(selector);
      const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

      const state = {
        lang: "bn",
        tasks: [],
        filter: "all",
        query: "",
        open: new Set()
      };

      const t = (key, ...args) => {
        const value = STRINGS[state.lang][key] ?? STRINGS.en[key] ?? key;
        return typeof value === "function" ? value(...args) : value;
      };

      const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
      }[char]));

      const array = value => Array.isArray(value) ? value : [];

      const localize = (task, name) => {
        const localized = task[`${name}_${state.lang}`];
        return localized && String(localized).trim() ? localized : (task[name] ?? "");
      };

      const allSteps = task => array(task.steps);

      const stepStats = task => {
        const steps = allSteps(task);
        const done = steps.filter(step => step.completed).length;
        const total = steps.length;
        return {
          done,
          total,
          pct: total ? Math.round(done / total * 100) : 0
        };
      };

      const taskMatches = task => {
        if (state.filter !== "all" && task.status !== state.filter) return false;
        if (!state.query) return true;

        const stepText = allSteps(task).flatMap(step => [
          step.id,
          step.title,
          step.parent_id,
          ...array(step.notes).map(note =>
            typeof note === "string" ? note : note?.text
          )
        ]);

        const taskNotes = array(task.notes).map(note =>
          typeof note === "string" ? note : note?.text
        );

        const history = array(task.history).map(item => item.action);

        const haystack = [
          task.task_id,
          task.registry,
          task.heading,
          task.heading_en,
          task.heading_bn,
          task.description,
          task.description_en,
          task.description_bn,
          ...taskNotes,
          ...stepText,
          ...history
        ].filter(Boolean).join(" ").toLocaleLowerCase();

        return haystack.includes(state.query);
      };

      const formatSize = bytes => {
        const value = Number(bytes);
        if (!Number.isFinite(value)) return "";
        if (value < 1024) return `${value} B`;
        if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
        return `${(value / 1024 / 1024).toFixed(1)} MB`;
      };

      const safeAttachmentHref = value => {
        const path = String(value ?? "");
        if (!path || path.startsWith("/") || path.includes("\\") || /^[a-z]+:/i.test(path)) {
          return "";
        }

        const segments = path.split("/");
        if (segments.some(part => !part || part === "." || part === "..")) return "";
        if (segments[0] !== "attachments") return "";

        return segments.map(encodeURIComponent).join("/");
      };

      const noteHTML = note => {
        const text = typeof note === "string" ? note : note?.text;
        const dhaka = typeof note === "object" && note ? note.dhaka : "";
        const utc = typeof note === "object" && note ? note.utc : "";
        const stamp = [dhaka && `${t("dhaka")} ${dhaka}`, utc && `UTC ${utc}`]
          .filter(Boolean)
          .join(" · ");

        return `<div class="note">${esc(text || "")}${stamp ? `<small>${esc(stamp)}</small>` : ""}</div>`;
      };

      const makeStepTree = task => {
        const steps = allSteps(task);
        const byParent = new Map();

        for (const step of steps) {
          const parent = step.parent_id ?? null;
          if (!byParent.has(parent)) byParent.set(parent, []);
          byParent.get(parent).push(step);
        }

        const renderChildren = (parentId = null, depth = 0, ancestors = new Set()) => {
          const children = byParent.get(parentId) || [];
          if (!children.length) return "";

          return `<ol class="steps ${depth ? "nested-steps" : ""}">${
            children.map(step => {
              const stepId = step.id;
              const cycle = ancestors.has(stepId);
              const nextAncestors = new Set(ancestors);
              nextAncestors.add(stepId);

              const stepNotes = array(step.notes);
              const notes = stepNotes.length
                ? `<div class="step-notes">${stepNotes.map(note => {
                    const text = typeof note === "string" ? note : note?.text;
                    const dhaka = typeof note === "object" && note ? note.dhaka : "";
                    const utc = typeof note === "object" && note ? note.utc : "";
                    const stamp = [dhaka && `${t("dhaka")} ${dhaka}`, utc && `UTC ${utc}`]
                      .filter(Boolean)
                      .join(" · ");
                    return `<div class="step-note"><span>${esc(text || "")}</span>${stamp ? `<small>${esc(stamp)}</small>` : ""}</div>`;
                  }).join("")}</div>`
                : "";

              const completedTime = step.completed
                ? `${esc(t("dhaka"))} ${esc(step.completed_dhaka || "")} · UTC ${esc(step.completed_utc || "")}`
                : esc(t("pending"));

              const nested = cycle
                ? ""
                : renderChildren(stepId, depth + 1, nextAncestors);

              return `
                <li class="step ${step.completed ? "ok" : ""}">
                  <span class="mark">${step.completed ? "✓" : esc(step.id)}</span>
                  <div class="step-content">
                    <div class="step-title">${esc(step.title)}</div>
                    <div class="step-time">${completedTime}</div>
                    ${notes}
                    ${nested}
                  </div>
                </li>`;
            }).join("")
          }</ol>`;
        };

        const topLevel = renderChildren(null);
        const orphanSteps = steps.filter(step =>
          step.parent_id != null && !steps.some(parent => parent.id === step.parent_id)
        );

        const orphanHTML = orphanSteps.length
          ? `<h3>${esc(state.lang === "bn" ? "Parent ধাপ পাওয়া যায়নি" : "Steps with missing parent")}</h3>
             <ol class="steps">${orphanSteps.map(step => `
               <li class="step">
                 <span class="mark">${esc(step.id)}</span>
                 <div class="step-content">
                   <div class="step-title">${esc(step.title)}</div>
                 </div>
               </li>`).join("")}</ol>`
          : "";

        return (topLevel || orphanHTML)
          ? `${topLevel}${orphanHTML}`
          : `<p class="muted">${esc(t("noSteps"))}</p>`;
      };

      const detailsHTML = task => {
        const notes = array(task.notes).length
          ? array(task.notes).map(noteHTML).join("")
          : `<p class="muted">${esc(t("noNotes"))}</p>`;

        const attachments = array(task.attachments);
        const files = attachments.length
          ? `<div class="files">${attachments.map(item => {
              const href = safeAttachmentHref(item.file);
              if (!href) {
                return `<span class="file">${esc(item.original || item.file || t("attachmentUnavailable"))}</span>`;
              }
              return `<a class="file" href="${esc(href)}" target="_blank" rel="noopener">
                ${esc(item.original || item.file)}
                <small>${esc(formatSize(item.size))}</small>
              </a>`;
            }).join("")}</div>`
          : `<p class="muted">${esc(t("noFiles"))}</p>`;

        const history = array(task.history).length
          ? `<ol class="history">${array(task.history).slice().reverse().map(item => `
              <li>
                <span class="mono">${esc(t("dhaka"))} ${esc(item.dhaka || "—")} · UTC ${esc(item.utc || "—")}</span>
                ${esc(item.action || "")}
              </li>`).join("")}</ol>`
          : `<p class="muted">${esc(t("noHistory"))}</p>`;

        const completed = task.completed_utc
          ? `<div class="completed-box">${esc(t("completedAt"))}: ${esc(t("dhaka"))} ${esc(task.completed_dhaka || "")} · UTC ${esc(task.completed_utc)}</div>`
          : "";

        const overview = task.overview
          ? `<h3>${esc(t("archive"))}</h3><pre class="overview">${esc(task.overview)}</pre>`
          : "";

        return `
          <h3>${esc(t("fullDesc"))}</h3>
          <p class="full">${esc(localize(task, "description"))}</p>
          ${completed}
          <h3>${esc(t("notes"))}</h3>
          ${notes}
          <h3>${esc(t("stepsTitle"))}</h3>
          ${makeStepTree(task)}
          <h3>${esc(t("files"))}</h3>
          ${files}
          ${overview}
          <h3>${esc(t("history"))}</h3>
          ${history}`;
      };

      const cardHTML = task => {
        const isDone = task.status === "completed";
        const isOpen = state.open.has(task.task_id);
        const { total, done, pct } = stepStats(task);
        const detailId = `details-${String(task.task_id).replace(/[^a-zA-Z0-9_-]/g, "")}`;

        return `
          <article class="card ${isDone ? "is-done" : ""}">
            <div class="card-top">
              <span class="status ${isDone ? "done" : "live"}">${esc(isDone ? t("statusDone") : t("statusActive"))}</span>
              <div class="ids">
                <span title="${esc(t("idTask"))}">${esc(task.task_id)}</span>
                <span title="${esc(t("idReg"))}">${esc(task.registry)}</span>
              </div>
            </div>

            <div class="stamps">
              <span><b>${esc(t("dhaka"))}</b>${esc(task.created_dhaka || "—")}</span>
              <span><b>UTC</b>${esc(task.created_utc || "—")}</span>
            </div>

            <h2 class="card-title">${esc(localize(task, "heading"))}</h2>
            <p class="preview">${esc(localize(task, "description"))}</p>

            <div class="progress-row">
              <div class="bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}">
                <span style="width:${pct}%"></span>
              </div>
              <span class="pct">${done}/${total} · ${pct}%</span>
            </div>

            <button class="toggle" type="button"
              data-toggle="${esc(task.task_id)}"
              aria-expanded="${isOpen}"
              aria-controls="${detailId}">
              ${esc(isOpen ? t("hideRecord") : t("viewRecord"))}
            </button>

            <div class="details" id="${detailId}" ${isOpen ? "" : "hidden"}>
              ${detailsHTML(task)}
            </div>
          </article>`;
      };

      const renderStats = () => {
        const tasks = state.tasks;
        const active = tasks.filter(task => task.status === "active").length;
        const completed = tasks.filter(task => task.status === "completed").length;
        const steps = tasks.flatMap(allSteps);
        const stepsDone = steps.filter(step => step.completed).length;
        const overall = steps.length ? Math.round(stepsDone / steps.length * 100) : 0;

        $("#stats").innerHTML = `
          <div class="stat">
            <div class="label">${esc(t("statTotal"))}</div>
            <div class="value">${tasks.length}</div>
          </div>
          <div class="stat">
            <div class="label">${esc(t("statActive"))}</div>
            <div class="value">${active}</div>
          </div>
          <div class="stat">
            <div class="label">${esc(t("statCompleted"))}</div>
            <div class="value">${completed}</div>
          </div>
          <div class="stat">
            <div class="label">${esc(t("statProgress"))} · ${stepsDone}/${steps.length} ${esc(t("steps"))}</div>
            <div class="value">${overall}%</div>
            <div class="bar"><span style="width:${overall}%"></span></div>
          </div>`;
      };

      const render = () => {
        renderStats();

        const visible = state.tasks.filter(taskMatches);
        $("#count").textContent = t("countOf", visible.length, state.tasks.length);

        if (!state.tasks.length) {
          $("#list").innerHTML = `<div class="empty">${t("emptyAll")}</div>`;
          return;
        }

        $("#list").innerHTML = visible.length
          ? visible.map(cardHTML).join("")
          : `<div class="empty">${esc(t("emptyFilter"))}</div>`;
      };

      const applyStatic = () => {
        $$("[data-i18n]").forEach(element => {
          element.textContent = t(element.dataset.i18n);
        });

        $$("[data-i18n-ph]").forEach(element => {
          element.placeholder = t(element.dataset.i18nPh);
        });

        $$("[data-i18n-aria]").forEach(element => {
          element.setAttribute("aria-label", t(element.dataset.i18nAria));
        });

        $$("[data-copy]").forEach(button => {
          if (!button.dataset.busy) button.textContent = t("copyCommand");
        });

        $("#search").setAttribute("aria-label", t("searchLabel"));
        document.documentElement.lang = state.lang;

        const logo = $("#logo");
        if (logo) logo.alt = state.lang === "bn" ? "লোগো" : "Logo";
      };

      const setLang = lang => {
        if (!STRINGS[lang]) return;

        state.lang = lang;
        $$("[data-lang-btn]").forEach(button => {
          button.setAttribute("aria-pressed", String(button.dataset.langBtn === lang));
        });

        try {
          localStorage.setItem(LANG_KEY, lang);
        } catch {
          // Browser storage may be unavailable.
        }

        applyStatic();
        render();
      };

      const loadLanguage = () => {
        try {
          const saved = localStorage.getItem(LANG_KEY);
          if (saved && STRINGS[saved]) return saved;
        } catch {
          // Ignore unavailable storage.
        }
        return "bn";
      };

      const loadData = async () => {
        try {
          const response = await fetch("data.json", { cache: "no-store" });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);

          const data = await response.json();
          if (!data || !Array.isArray(data.tasks)) {
            throw new Error(t("invalidData"));
          }

          state.tasks = data.tasks;
          render();
        } catch (error) {
          $("#stats").replaceChildren();
          $("#count").textContent = "";
          $("#list").innerHTML = `
            <div class="error">
              <strong>${esc(t("loadFail"))}</strong> (${esc(error.message || error)})<br>
              ${t("loadFailHelp")}
            </div>`;
        }
      };

      const openCliDialog = () => {
        const dialog = $("#dlg-cli");
        if (typeof dialog.showModal === "function") dialog.showModal();
        else dialog.setAttribute("open", "");
      };

      $$("[data-lang-btn]").forEach(button => {
        button.addEventListener("click", () => setLang(button.dataset.langBtn));
      });

      $("#search").addEventListener("input", event => {
        state.query = event.target.value.trim().toLocaleLowerCase();
        render();
      });

      $(".filters").addEventListener("click", event => {
        const button = event.target.closest("button[data-filter]");
        if (!button) return;

        state.filter = button.dataset.filter;
        $$(".filters button").forEach(item => {
          item.setAttribute("aria-pressed", String(item === button));
        });
        render();
      });

      $("#list").addEventListener("click", event => {
        const button = event.target.closest("button[data-toggle]");
        if (!button) return;

        const id = button.dataset.toggle;
        if (state.open.has(id)) state.open.delete(id);
        else state.open.add(id);
        render();
      });

      $$("[data-open-cli]").forEach(button => {
        button.addEventListener("click", openCliDialog);
      });

      $$("dialog").forEach(dialog => {
        dialog.addEventListener("click", event => {
          if (event.target === dialog) dialog.close();
        });

        dialog.querySelector("[data-close]")?.addEventListener("click", () => {
          dialog.close();
        });
      });

      $$("[data-copy]").forEach(button => {
        button.addEventListener("click", async () => {
          button.dataset.busy = "1";
          const original = t("copyCommand");

          try {
            if (navigator.clipboard && window.isSecureContext) {
              await navigator.clipboard.writeText(button.dataset.copy);
            } else {
              const textarea = document.createElement("textarea");
              textarea.value = button.dataset.copy;
              textarea.style.position = "fixed";
              textarea.style.opacity = "0";
              document.body.append(textarea);
              textarea.select();
              const ok = document.execCommand("copy");
              textarea.remove();
              if (!ok) throw new Error("Copy failed");
            }
            button.textContent = t("copied");
          } catch {
            button.textContent = t("copyFail");
          }

          window.setTimeout(() => {
            button.textContent = original;
            delete button.dataset.busy;
          }, 1400);
        });
      });

      const logo = $("#logo");
      const useFallbackLogo = () => {
        if (!logo?.isConnected) return;
        const fallback = document.createElement("div");
        fallback.className = "logo-fallback";
        fallback.textContent = "ST";
        fallback.setAttribute("role", "img");
        fallback.setAttribute("aria-label", state.lang === "bn" ? "লোগো" : "Logo");
        logo.replaceWith(fallback);
      };

      if (logo.complete && logo.naturalWidth === 0) {
        useFallbackLogo();
      } else {
        logo.addEventListener("error", useFallbackLogo, { once: true });
      }

      setLang(loadLanguage());
      loadData();
    })();
  </script>
</body>
</html>
```

## ২. `task/run.sh`

```bash name=task/run.sh url=https://github.com/MJ-Ahmad/mjportal/blob/main/task/run.sh
#!/usr/bin/env bash
# Stewardship Task System runner.
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

usage() {
  cat <<'EOF'

Stewardship Task System

Usage:
  ./run.sh init
  ./run.sh task "Heading" "Description" [options]
      --steps "step one, step two"
      --add-note "task note"          (repeatable)
      --add-file path/to/file         (repeatable)
      --heading-en "English heading"
      --heading-bn "বাংলা শিরোনাম"
      --description-en "English description"
      --description-bn "বাংলা বিবরণ"

  ./run.sh track TASK-000001 <step_id>
  ./run.sh step-add TASK-000001 "New step"
  ./run.sh step-add TASK-000001 "Substep" --parent 2
  ./run.sh step-note TASK-000001 <step_id> "Note text"
  ./run.sh complete TASK-000001
  ./run.sh validate
  ./run.sh web [port]

Environment:
  BIND=0.0.0.0 ./run.sh web
      Allow other devices on your trusted local network to view the dashboard.

EOF
}

case "${1:-help}" in
  init)
    "$PY" -c "import _lib; _lib.ensure_structure(); print('Ready: data.json, registry.json, attachments/, assets/')"
    ;;

  task)
    shift
    "$PY" add_task.py "$@"
    ;;

  track)
    shift
    "$PY" track_task.py "$@"
    ;;

  step-add)
    shift
    "$PY" manage_steps.py add "$@"
    ;;

  step-note)
    shift
    "$PY" manage_steps.py note "$@"
    ;;

  complete)
    shift
    "$PY" complete_task.py "$@"
    ;;

  validate)
    "$PY" validate.py
    ;;

  web)
    PORT="${2:-8000}"
    BIND="${BIND:-127.0.0.1}"

    "$PY" -c "import _lib; _lib.ensure_structure()"

    echo "Dashboard: http://${BIND}:${PORT}/"
    echo "For local-only access, use the default BIND=127.0.0.1."
    exec "$PY" -m http.server "$PORT" --bind "$BIND"
    ;;

  help|-h|--help)
    usage
    ;;

  *)
    usage
    echo "Unknown command: $1" >&2
    exit 1
    ;;
esac
```

## ৩. `task/_lib.py`

```python name=task/_lib.py url=https://github.com/MJ-Ahmad/mjportal/blob/main/task/_lib.py
#!/usr/bin/env python3
"""Shared core for the Stewardship Task System.

All task database reads/writes, IDs, timestamps, progress and validation
helpers live here. Existing flat-step records remain supported; new steps
include parent_id and step-specific notes.
"""

import hashlib
import json
import mimetypes
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
REGISTRY_FILE = os.path.join(BASE_DIR, "registry.json")
ATTACHMENTS_DIR = os.path.join(BASE_DIR, "attachments")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

DHAKA_TZ = timezone(timedelta(hours=6))
TS_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

VALID_STATUSES = ("active", "completed")
TASK_ID_RE = re.compile(r"^TASK-\d{6}$")
REG_ID_RE = re.compile(r"^REG-\d{6}$")


# ---------------------------------------------------------------- time

def now_stamps():
    """Return the current moment as Dhaka and UTC strings."""
    utc_now = datetime.now(timezone.utc)
    return {
        "dhaka": utc_now.astimezone(DHAKA_TZ).strftime(TS_FORMAT)[:-3],
        "utc": utc_now.strftime(TS_FORMAT)[:-3],
    }


# ---------------------------------------------------------------- storage

def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path, data):
    """Write JSON atomically so an interrupted write does not corrupt the file."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)

    fd, temporary_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=4, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary_path, path)
    except BaseException:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise


def ensure_structure():
    """Create folders and empty database files on first use."""
    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        save_json(DATA_FILE, {"tasks": []})

    if not os.path.exists(REGISTRY_FILE):
        save_json(REGISTRY_FILE, {"last_registry": 0, "last_task": 0})


# ---------------------------------------------------------------- IDs

def generate_ids():
    """Allocate the next TASK-XXXXXX and REG-XXXXXX IDs."""
    registry = load_json(REGISTRY_FILE)

    if not isinstance(registry, dict):
        raise ValueError("registry.json must contain a JSON object")

    last_registry = int(registry.get("last_registry", 0))
    last_task = int(registry.get("last_task", 0))

    registry["last_registry"] = last_registry + 1
    registry["last_task"] = last_task + 1
    save_json(REGISTRY_FILE, registry)

    return (
        f"TASK-{registry['last_task']:06d}",
        f"REG-{registry['last_registry']:06d}",
    )


# ---------------------------------------------------------------- attachments

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def store_attachment(task_id, file_path):
    """Copy a file into attachments/ and return metadata."""
    if not os.path.isfile(file_path):
        return None

    original = os.path.basename(file_path)
    extension = os.path.splitext(original)[1].lower()
    save_name = f"{task_id}{extension}"
    destination = os.path.join(ATTACHMENTS_DIR, save_name)

    # Keep the existing task-ID naming scheme, but do not silently overwrite
    # a previous attachment with the same extension.
    if os.path.exists(destination):
        stem, suffix = os.path.splitext(save_name)
        counter = 2
        while os.path.exists(os.path.join(ATTACHMENTS_DIR, f"{stem}-{counter}{suffix}")):
            counter += 1
        save_name = f"{stem}-{counter}{suffix}"
        destination = os.path.join(ATTACHMENTS_DIR, save_name)

    shutil.copy2(file_path, destination)

    return {
        "file": f"attachments/{save_name}",
        "original": original,
        "size": os.path.getsize(destination),
        "mime": mimetypes.guess_type(destination)[0] or "application/octet-stream",
        "sha256": sha256_file(destination),
    }


# ---------------------------------------------------------------- steps

def create_steps(step_string):
    """Turn comma-separated titles into numbered top-level step records."""
    if not step_string:
        return []

    titles = [item.strip() for item in step_string.split(",") if item.strip()]

    return [
        {
            "id": index,
            "parent_id": None,
            "title": title,
            "completed": False,
            "completed_dhaka": None,
            "completed_utc": None,
            "notes": [],
        }
        for index, title in enumerate(titles, start=1)
    ]


def calculate_progress(task):
    """Recompute task progress from every step, including nested steps."""
    steps = task.get("steps", [])
    if not isinstance(steps, list):
        steps = []

    total = len(steps)
    completed = sum(1 for step in steps if step.get("completed"))

    task["progress"] = {
        "completed": completed,
        "remaining": total - completed,
        "percentage": int(completed / total * 100) if total else 0,
    }
    return task["progress"]


def find_task(task_id, data):
    for task in data.get("tasks", []):
        if task.get("task_id") == task_id:
            return task
    return None


def append_history(task, action, stamps):
    task.setdefault("history", []).append({
        "dhaka": stamps["dhaka"],
        "utc": stamps["utc"],
        "action": action,
    })


# ---------------------------------------------------------------- completion

def build_completion_report(task):
    """Build a factual archive summary from the stored task record."""
    steps = task.get("steps", [])
    total = len(steps)
    completed = sum(1 for step in steps if step.get("completed"))
    progress = task.get("progress") or {}
    percentage = progress.get("percentage", 0)

    overview = (
        "Task record marked complete.\n\n"
        f"Task:\n{task.get('heading', '')}\n\n"
        "The task's tracked steps were completed before archival.\n"
        "Review supporting notes and attachments separately when needed.\n\n"
        f"Tracked step completion: {percentage}%\n"
    )

    evaluation = {
        "steps_total": total,
        "steps_completed": completed,
        "completion_percentage": percentage,
        "notes": len(task.get("notes", [])),
        "attachments": len(task.get("attachments", [])),
        "archive_ready": True,
    }

    return overview, evaluation


# ---------------------------------------------------------------- integrity

def validate_database(data, registry):
    """Return (errors, summary). Empty errors means the database is consistent."""
    errors = []

    if not isinstance(data, dict):
        return ["data.json must contain a JSON object"], {}

    tasks = data.get("tasks")
    if not isinstance(tasks, list):
        return ["'tasks' must be a list"], {}

    if not isinstance(registry, dict):
        return ["registry.json must contain a JSON object"], {}

    seen_task_ids = set()
    seen_reg_ids = set()
    total_steps = completed_steps = active = completed = 0
    max_task_no = max_reg_no = 0

    for task in tasks:
        if not isinstance(task, dict):
            errors.append("A task record is not a JSON object")
            continue

        task_id = str(task.get("task_id", "<missing>"))
        registry_id = str(task.get("registry", "<missing>"))

        if not TASK_ID_RE.fullmatch(task_id):
            errors.append(f"{task_id}: bad task_id format")
        if not REG_ID_RE.fullmatch(registry_id):
            errors.append(f"{task_id}: bad registry format ({registry_id})")

        if task_id in seen_task_ids:
            errors.append(f"{task_id}: duplicate task_id")
        seen_task_ids.add(task_id)

        if registry_id in seen_reg_ids:
            errors.append(f"{task_id}: duplicate registry ({registry_id})")
        seen_reg_ids.add(registry_id)

        if TASK_ID_RE.fullmatch(task_id):
            max_task_no = max(max_task_no, int(task_id.split("-")[1]))
        if REG_ID_RE.fullmatch(registry_id):
            max_reg_no = max(max_reg_no, int(registry_id.split("-")[1]))

        status = task.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"{task_id}: invalid status '{status}'")

        if not str(task.get("heading", "")).strip():
            errors.append(f"{task_id}: empty heading")

        steps = task.get("steps", [])
        if not isinstance(steps, list):
            errors.append(f"{task_id}: steps must be a list")
            steps = []

        step_ids = []
        for step in steps:
            if not isinstance(step, dict):
                errors.append(f"{task_id}: a step is not a JSON object")
                continue
            step_ids.append(step.get("id"))

        try:
            if len(step_ids) != len(set(step_ids)):
                errors.append(f"{task_id}: duplicate step ids")
        except TypeError:
            errors.append(f"{task_id}: step IDs must be scalar values")

        step_by_id = {
            step.get("id"): step
            for step in steps
            if isinstance(step, dict) and step.get("id") is not None
        }

        for step in steps:
            if not isinstance(step, dict):
                continue

            step_id = step.get("id")
            parent_id = step.get("parent_id")

            # Old database records do not have parent_id; that is equivalent to None.
            if parent_id is not None:
                if parent_id not in step_by_id:
                    errors.append(
                        f"{task_id} step {step_id}: parent step {parent_id} not found"
                    )
                elif parent_id == step_id:
                    errors.append(f"{task_id} step {step_id}: cannot be its own parent")

            if not isinstance(step.get("title", ""), str):
                errors.append(f"{task_id} step {step_id}: title must be a string")

            if step.get("completed"):
                if not step.get("completed_utc") or not step.get("completed_dhaka"):
                    errors.append(
                        f"{task_id} step {step_id}: completed without timestamps"
                    )
            elif step.get("completed_utc") or step.get("completed_dhaka"):
                errors.append(
                    f"{task_id} step {step_id}: timestamps on an incomplete step"
                )

            notes = step.get("notes", [])
            if notes is not None and not isinstance(notes, list):
                errors.append(f"{task_id} step {step_id}: notes must be a list")

        # Detect parent cycles in the flat parent_id representation.
        for step_id in step_by_id:
            visited = set()
            current_id = step_id

            while current_id in step_by_id:
                if current_id in visited:
                    errors.append(f"{task_id} step {step_id}: parent cycle detected")
                    break
                visited.add(current_id)
                current_id = step_by_id[current_id].get("parent_id")

                if current_id is None:
                    break

        done = sum(
            1 for step in steps
            if isinstance(step, dict) and step.get("completed")
        )

        progress = task.get("progress", {})
        if not isinstance(progress, dict):
            errors.append(f"{task_id}: progress must be an object")
            progress = {}

        expected_percentage = int(done / len(steps) * 100) if steps else 0
        if progress.get("completed") != done:
            errors.append(
                f"{task_id}: progress.completed={progress.get('completed')} "
                f"but {done} steps are completed"
            )
        if progress.get("remaining") != len(steps) - done:
            errors.append(
                f"{task_id}: progress.remaining={progress.get('remaining')} "
                f"but {len(steps) - done} steps remain"
            )
        if progress.get("percentage") != expected_percentage:
            errors.append(
                f"{task_id}: progress.percentage={progress.get('percentage')} "
                f"but expected {expected_percentage}"
            )

        if status == "completed" and done != len(steps):
            errors.append(f"{task_id}: marked completed with unfinished steps")

        attachments = task.get("attachments", [])
        if not isinstance(attachments, list):
            errors.append(f"{task_id}: attachments must be a list")
            attachments = []

        for attachment in attachments:
            if not isinstance(attachment, dict):
                errors.append(f"{task_id}: an attachment record is not an object")
                continue

            relative = str(attachment.get("file", ""))
            normalized = os.path.normpath(relative)
            expected_prefix = "attachments" + os.sep

            if (
                os.path.isabs(relative)
                or normalized == ".."
                or normalized.startswith(".." + os.sep)
                or not normalized.startswith(expected_prefix)
            ):
                errors.append(f"{task_id}: unsafe attachment path {relative}")
                continue

            full_path = os.path.abspath(os.path.join(BASE_DIR, normalized))
            attachments_root = os.path.abspath(ATTACHMENTS_DIR)

            try:
                inside_attachment_dir = os.path.commonpath(
                    [full_path, attachments_root]
                ) == attachments_root
            except ValueError:
                inside_attachment_dir = False

            if not inside_attachment_dir:
                errors.append(f"{task_id}: unsafe attachment path {relative}")
            elif not os.path.isfile(full_path):
                errors.append(f"{task_id}: missing attachment file {relative}")

        total_steps += len(steps)
        completed_steps += done

        if status == "active":
            active += 1
        elif status == "completed":
            completed += 1

    try:
        last_task = int(registry.get("last_task", 0))
        last_registry = int(registry.get("last_registry", 0))
    except (TypeError, ValueError):
        last_task = last_registry = 0
        errors.append("registry counters must be integers")

    if last_task < max_task_no:
        errors.append("registry.last_task is behind the highest TASK id")
    if last_registry < max_reg_no:
        errors.append("registry.last_registry is behind the highest REG id")

    summary = {
        "total_tasks": len(tasks),
        "active_tasks": active,
        "completed_tasks": completed,
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "last_registry": registry.get("last_registry", 0),
        "last_task": registry.get("last_task", 0),
    }

    return errors, summary
```

## ৪. `task/validate.py`

```python name=task/validate.py url=https://github.com/MJ-Ahmad/mjportal/blob/main/task/validate.py
#!/usr/bin/env python3
"""Validate task data, nested steps, timestamps, attachments and ID registry."""

import sys

from _lib import (
    DATA_FILE,
    REGISTRY_FILE,
    load_json,
    validate_database,
)


def main():
    try:
        data = load_json(DATA_FILE)
        registry = load_json(REGISTRY_FILE)
    except (OSError, ValueError) as error:
        print(f"\nValidation failed: cannot read database files: {error}\n")
        return 1

    errors, summary = validate_database(data, registry)

    if errors:
        print("\nValidation failed\n")
        for error in errors:
            print(f"  - {error}")
        print(f"\n{len(errors)} problem(s) found.\n")
        return 1

    print("\nDatabase validation successful\n")
    print(f"Total tasks      : {summary['total_tasks']}")
    print(f"Active tasks     : {summary['active_tasks']}")
    print(f"Completed tasks  : {summary['completed_tasks']}")
    print(f"Total steps      : {summary['total_steps']}")
    print(f"Completed steps  : {summary['completed_steps']}")
    print(f"Last registry ID : {summary['last_registry']}")
    print(f"Last task ID     : {summary['last_task']}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## অতিরিক্ত দরকারি ফাইল: `task/manage_steps.py`

`run.sh`-এর `step-add` ও `step-note` command কাজ করতে এই script-টিও `task/`-এ তৈরি করতে হবে।

```python name=task/manage_steps.py
#!/usr/bin/env python3
"""Add task steps/substeps and timestamped notes attached to a step."""

import argparse
import sys

from _lib import (
    DATA_FILE,
    append_history,
    calculate_progress,
    find_task,
    load_json,
    now_stamps,
    save_json,
)


def fail(message):
    raise SystemExit(f"\n{message}\n")


def find_step(task, step_id):
    return next(
        (step for step in task.get("steps", []) if step.get("id") == step_id),
        None,
    )


def add_step(args):
    title = args.title.strip()
    if not title:
        fail("Step title cannot be empty.")

    data = load_json(DATA_FILE)
    task = find_task(args.task_id.strip().upper(), data)

    if task is None:
        fail(f"Task not found: {args.task_id}")
    if task.get("status") == "completed":
        fail("Cannot add a step to a completed task.")

    steps = task.setdefault("steps", [])
    parent = None

    if args.parent is not None:
        parent = find_step(task, args.parent)
        if parent is None:
            fail(f"Parent step not found: {args.parent}")
        if parent.get("completed"):
            fail("Cannot add a substep under a completed step.")

    step_id = max(
        (int(step.get("id", 0)) for step in steps),
        default=0,
    ) + 1

    step = {
        "id": step_id,
        "parent_id": args.parent,
        "title": title,
        "completed": False,
        "completed_dhaka": None,
        "completed_utc": None,
        "notes": [],
    }
    steps.append(step)

    stamps = now_stamps()
    calculate_progress(task)
    parent_label = f" under step {args.parent}" if args.parent is not None else ""
    append_history(task, f"Added step {step_id}{parent_label}: {title}", stamps)
    save_json(DATA_FILE, data)

    print(f"Step added : {step_id}")
    print(f"Task       : {task['task_id']}")
    print(f"Parent     : {args.parent if args.parent is not None else 'top-level'}")
    print(f"Title      : {title}")


def add_note(args):
    text = args.text.strip()
    if not text:
        fail("Note cannot be empty.")

    data = load_json(DATA_FILE)
    task = find_task(args.task_id.strip().upper(), data)

    if task is None:
        fail(f"Task not found: {args.task_id}")

    step = find_step(task, args.step_id)
    if step is None:
        fail(f"Step not found: {args.step_id}")

    stamps = now_stamps()
    note = {
        "text": text,
        "dhaka": stamps["dhaka"],
        "utc": stamps["utc"],
    }

    step.setdefault("notes", []).append(note)
    append_history(task, f"Added note to step {args.step_id}: {text}", stamps)
    save_json(DATA_FILE, data)

    print(f"Note added to {task['task_id']} step {args.step_id}.")
    print(f"Dhaka: {stamps['dhaka']} · UTC: {stamps['utc']}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage task steps, substeps and step notes."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="Add a top-level step or substep")
    add.add_argument("task_id")
    add.add_argument("title")
    add.add_argument("--parent", type=int, help="Parent step ID")
    add.set_defaults(func=add_step)

    note = commands.add_parser("note", help="Add a timestamped note to a step")
    note.add_argument("task_id")
    note.add_argument("step_id", type=int)
    note.add_argument("text")
    note.set_defaults(func=add_note)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
```

## Backup, permission এবং যাচাই

Backup নেওয়ার পর scripts executable করুন এবং validation চালান:

```bash
mkdir -p task-backup
cp task/data.json task/registry.json task-backup/
cp -r task/attachments task-backup/

chmod +x task/run.sh task/manage_steps.py
./task/run.sh validate
```

Task, substep ও step note যোগের উদাহরণ:

```bash
cd task

./run.sh task "MJ-AI setup" "প্রাথমিক project structure তৈরি" \
  --steps "Scope review, Folder tree draft"

./run.sh step-add TASK-000033 "Security checklist review"
./run.sh step-add TASK-000033 "Permission policy লিখুন" --parent 2
./run.sh step-note TASK-000033 3 "প্রথমে read-only scope যাচাই করতে হবে"

./run.sh validate
./run.sh web
```

Dashboard: `http://127.0.0.1:8000`

নিজের **trusted local network**-এর অন্য device থেকে দেখতে হলে:

```bash
BIND=0.0.0.0 ./run.sh web
```

Development server-কে public internet-এ প্রকাশ করবেন না। `BIND=0.0.0.0` ব্যবহার করলে একই network-এর অন্য device-ও task data দেখতে পারে।

