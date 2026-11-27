# Folder Tree Acceptance Checklist

প্রতিটি item review ও evidence পাওয়ার আগে completed/verified হিসেবে চিহ্নিত করবেন না।

- [ ] README-এর Foundation root directory list মিলিয়ে দেখা
- [ ] README-এর Layer 01 directory list মিলিয়ে দেখা
- [ ] দুই তালিকার অমিলের জন্য সিদ্ধান্ত/ব্যাখ্যা লেখা
- [ ] Qur'an Navigation Platform-এর directory mapping approve করা
- [ ] Quran Memorize Ecosystem-এর directory mapping approve করা
- [ ] `content/` ও `data/`-এর পার্থক্য ও data ownership লেখা
- [ ] `navigation/`, `reader/` ও `search/`-এর boundary লেখা
- [ ] `audio/` ও media metadata-এর boundary লেখা
- [ ] `study/` ও user-specific data-এর boundary লেখা
- [ ] `profiles/`, `analytics/` ও privacy consideration review করা
- [ ] `api/` ও `apps/` placement review করা
- [ ] `documentation/` ও `governance/` ownership review করা
- [ ] Naming convention এবং lowercase/kebab-case policy লেখা
- [ ] Copyright/license/provenance review ছাড়া content যোগ না করার সিদ্ধান্ত লেখা
- [ ] Final tree README বা architecture decision note-এ commit করা
- [ ] Final commit/backup evidence সংরক্ষণ করা
- [ ] Deferred item ও Phase-02 task তালিকাভুক্ত করা

## Final tree draft — approval pending

```text
quran-navigation/
├── assets/
├── content/
├── data/
├── localization/
├── navigation/
├── search/
├── reader/
├── audio/
├── study/
├── analytics/
├── api/
├── apps/
├── profiles/
├── documentation/
└── governance/
```

README-র tree-তে কোনো directory অতিরিক্ত, অনুপস্থিত বা আলাদা অবস্থানে থাকলে
review decision নথিভুক্ত করে final version তৈরি করুন।
