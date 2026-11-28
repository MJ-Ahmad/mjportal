`Enhancement_Request.md`-এর মূল চাহিদা পরিষ্কার: `.md` ফাইলের লেখা dashboard-এ **পাঠযোগ্যভাবে render** হবে, কিন্তু copy করলে **মূল Markdown source**-ই কপি হবে। Request-টি [এখানে](https://github.com/MJ-Ahmad/mjportal/blob/2bf0ce99428a384853adb8d784d155001c50b1a8/Enhancement_Request.md#L35-L67)।

কোডে একটি গুরুত্বপূর্ণ বিষয় আছে: `life.py add --body-file` এখন ফাইলের লেখা `description`-এ রাখে, কিন্তু সেটি Markdown কি না—এমন কোনো metadata রাখে না। `create_entry()`-ও description-এ `.strip()` করে, ফলে source-এর শুরু/শেষের whitespace বদলে যেতে পারে ([`life.py`](https://github.com/MJ-Ahmad/mjportal/blob/2bf0ce99428a384853adb8d784d155001c50b1a8/life.py#L119-L159), [`cmd_add`](https://github.com/MJ-Ahmad/mjportal/blob/2bf0ce99428a384853adb8d784d155001c50b1a8/life.py#L167-L175))। তাই নিচের পরিবর্তনে নতুন `.md` entry-তে `description_format: "markdown"` যোগ হবে। বিদ্যমান copy-record feature অপরিবর্তিত থাকবে; Markdown source copy করার জন্য আলাদা button যোগ হবে। Dashboard বর্তমানে description-কে plain text হিসেবে দেখায় ([`index.html`](https://github.com/MJ-Ahmad/mjportal/blob/7b8f6918c51c79f395fc72c16e75abeeb2d16189/index.html#L544-L560))।

## ১. `life.py`-তে Markdown metadata ও source সংরক্ষণ

`create_entry()`-এ description পরিষ্কার করার অংশটি খুঁজে এই logic ব্যবহার করুন। Markdown body-file হলে text trim হবে না; শুধু খালি কি না যাচাই হবে।

```python name=life.py
    body_file = getattr(args, "body_file", None)
    is_markdown = bool(
        body_file and os.path.splitext(body_file)[1].lower() == ".md"
    )

    # Markdown source হুবহু রাখুন; সাধারণ description আগের মতো trim হবে।
    description = description if is_markdown else description.strip()

    if not heading:
        fail("heading must not be empty")
    if len(heading) > HEADING_MAX:
        fail(f"heading must be {HEADING_MAX} characters or fewer")
    if not description.strip():
        fail("description must not be empty (or use --body-file)")
```

`entry` dictionary তৈরি হওয়ার পরে, attachment handling-এর আগে metadata যোগ করুন:

```python name=life.py
    if is_markdown:
        entry["description_format"] = "markdown"
        entry["description_source"] = os.path.basename(body_file)
```

`cmd_add()`-এ Markdown file পড়ার অংশে newline সংরক্ষণ করতে `newline=""` দিন:

```python name=life.py
    if args.body_file:
        if not os.path.isfile(args.body_file):
            fail(f"body file not found: {args.body_file}")
        with open(args.body_file, encoding="utf-8", newline="") as f:
            description = f.read()
```

## ২. `index.html`-এ Markdown parser ও sanitizer যোগ

বর্তমান inline application `<script>`-এর **আগে** এই দুইটি script দিন। Library CDN থেকে আসে, তাই network বন্ধ থাকলে fallback plain text দেখাবে।

```html name=index.html
<script src="https://cdn.jsdelivr.net/npm/marked@15.0.7/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js"></script>
```

এখানে `marked` Markdown parse করে এবং `DOMPurify` output sanitize করে। User-provided Markdown-কে sanitize না করে `innerHTML`-এ বসাবেন না।

## ৩. Markdown display এবং copy button যোগ

`entryHtml(e)` function-এ বর্তমান `long` declaration-এর পর এই অংশ যোগ করুন:

```javascript name=index.html
  const isMarkdown = e.description_format === "markdown";
  const markdownReady = isMarkdown && window.marked && window.DOMPurify;

  const descriptionHtml = markdownReady
    ? window.DOMPurify.sanitize(
        window.marked.parse(e.description, { gfm: true, breaks: false })
      )
    : `<p>${esc(e.description).replace(/\r?\n/g, "<br>")}</p>`;
```

তারপর `entryHtml(e)` template-এ এই বর্তমান plain-text অংশটি:

```javascript
<p class="desc ...">${esc(e.description)}</p>
```

নিচেরটিতে বদলান:

```javascript name=index.html
<div class="desc ${isMarkdown ? "markdown" : ""} ${long && !open ? "clamp" : ""}">
  ${descriptionHtml}
</div>
```

`entryHtml(e)`-এর actions-এ আগের `copyRecord` button রাখুন এবং Markdown source copy-র আলাদা button যোগ করুন:

```javascript name=index.html
<div class="actions">
  <button data-md="${esc(e.tracking_id)}">${t("copyRecord")}</button>
  ${isMarkdown
    ? `<button data-md-source="${esc(e.tracking_id)}">${t("copyOriginalMarkdown")}</button>`
    : ""}
  ${a ? `<button data-copy="${esc(a.sha256)}">${t("copySha")}</button>` : ""}
</div>
```

এতে existing `copyRecord` আচরণ বজায় থাকবে; নতুন button শুধু মূল `description` Markdown source কপি করবে।

## ৪. Click handler-এ source copy যোগ

বিদ্যমান delegated click handler-এ `data-md` record-copy handling-এর পরে এই অংশ যোগ করুন:

```javascript name=index.html
  const markdownSource = ev.target.closest("[data-md-source]");
  if (markdownSource) {
    const entry = state.entries.find(
      item => item.tracking_id === markdownSource.dataset.mdSource
    );
    if (entry) await copyText(entry.description);
    return;
  }
```

## ৫. Markdown content-এর CSS

`index.html`-এর style block-এর শেষে যোগ করুন:

```css name=index.html
.desc.markdown {
  white-space: normal;
  line-height: 1.7;
  overflow-wrap: anywhere;
}

.desc.markdown p,
.desc.markdown ul,
.desc.markdown ol,
.desc.markdown blockquote,
.desc.markdown pre,
.desc.markdown table {
  margin: 0 0 12px;
}

.desc.markdown h1,
.desc.markdown h2,
.desc.markdown h3,
.desc.markdown h4 {
  margin: 14px 0 7px;
  line-height: 1.35;
  color: var(--text);
}

.desc.markdown ul,
.desc.markdown ol {
  padding-inline-start: 24px;
}

.desc.markdown blockquote {
  padding: 8px 12px;
  border-inline-start: 3px solid var(--gold);
  border-radius: 0 7px 7px 0;
  background: var(--surface);
}

.desc.markdown pre {
  max-width: 100%;
  overflow: auto;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-2);
  direction: ltr;
  text-align: left;
}

.desc.markdown pre code,
.desc.markdown :not(pre) > code {
  font-family: var(--mono);
  font-size: .9em;
}

.desc.markdown :not(pre) > code {
  padding: 2px 5px;
  border-radius: 4px;
  background: var(--surface-2);
}

.desc.markdown table {
  display: block;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
}

.desc.markdown th,
.desc.markdown td {
  padding: 6px 9px;
  border: 1px solid var(--line);
}

.desc.markdown a {
  color: var(--focus);
  text-underline-offset: 3px;
}

.desc.markdown img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.desc.markdown.clamp {
  max-height: 13em;
  overflow: hidden;
}

@media (max-width: 600px) {
  .desc.markdown pre {
    font-size: 12px;
  }
}
```

## ৬. EN/বাংলা label যোগ

`index.html`-এর interface translation object-এ এই key যোগ করুন:

```javascript name=index.html
// bn:
copyOriginalMarkdown: "মূল Markdown কপি",

// en:
copyOriginalMarkdown: "Copy original Markdown",
```

## যাচাই

Backup নেওয়ার পর নতুন Markdown body-file entry তৈরি করে পরীক্ষা করুন:

```bash
cp data.json "data.json.backup-$(date +%Y%m%d-%H%M%S)"
python3 life.py add "Markdown render test" --body-file ./markdown/notes/test.md --category learning
```

Dashboard চালিয়ে যাচাই করুন:

```bash
./run.sh
```

পরীক্ষায় দেখুন:

- heading, list, bold, quote ও code block rendered হিসেবে দেখা যায়;
- **মূল Markdown কপি** button শুধু source কপি করে;
- আগের **Copy record** button-এর আচরণ আগের মতো থাকে;
- সাধারণ plain-text entry আগের মতোই প্রদর্শিত হয়;
- `--body-file` দিয়ে `.md` নয় এমন ফাইল দিলে তা Markdown হিসেবে render হয় না।

আগের database entry-তে `description_format` না থাকলে সেগুলো plain text হিসেবেই থাকবে। পুরোনো entry-র format অনুমান করে স্বয়ংক্রিয়ভাবে বদলানো নিরাপদ নয়; নিশ্চিত entry-গুলো আলাদা করে migrate করতে হবে।


