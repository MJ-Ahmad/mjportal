সম্ভবত `notes-index.json` তৈরি হওয়ার **পরে** অন্য নোটগুলো যোগ করেছেন। `./run.sh serve` চালুর সময়ই তালিকাটি তৈরি হয়, তাই সার্ভার চালু থাকা অবস্থায় নতুন ফাইল যোগ করলে তালিকায় আসে না।

সার্ভার বন্ধ না করেও তালিকা নতুন করে তৈরি করতে রিপোর মূল ডিরেক্টরি থেকে চালান:

```bash
python3 scripts/content_setup.py --index-only
```

তারপর ব্রাউজারে `/markdown/` পেজটি রিফ্রেশ করুন। ফাইলগুলো ঠিক এই ফোল্ডারের মধ্যে এবং `.md` এক্সটেনশনে আছে কি না দেখুন:

```text
markdown/notes/
```

সাবফোল্ডারেও রাখা যায়, যেমন `markdown/notes/projects/plan.md`।

যদি নোটের এক্সটেনশন `.MD` (বড় হাতের অক্ষর) হয়, স্ক্রিপ্টের `refresh_markdown_index()` ফাংশনে এই অংশটি:

```python
for path in sorted(notes_dir.rglob("*.md")):
```

এভাবে বদলান, যাতে `.md` ও `.MD`—দুটিই ধরা পড়ে:

```python
for path in sorted(
    (p for p in notes_dir.rglob("*") if p.is_file() and p.suffix.lower() == ".md")
):
```

তারপর আবার চালান:

```bash
python3 scripts/content_setup.py --index-only
```

তালিকায় কী ধরা পড়েছে নিশ্চিত হতে `markdown/notes-index.json` খুলে দেখুন—আপনার নোটের নাম সেখানে থাকা উচিত।
