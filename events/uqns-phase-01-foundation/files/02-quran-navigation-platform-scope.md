# Qur'an Navigation Platform — Initial Scope

## README-তে উল্লেখিত capabilities

- Vector Mushaf
- Ayah, Surah, Juz, Hizb ও Ruku navigation
- Semantic search ও root-word search
- Cross references
- Audio synchronization
- Multilingual translation
- Research workspace

## এই ইভেন্টে নির্ধারণ করতে হবে

- কোন capabilities প্রথম foundation tree-তে শুধু directory placeholder হবে
- navigation, search, reader, content ও data layer-এর ownership boundary
- প্রতিটি feature-এর সম্ভাব্য input/output এবং interdependency
- Arabic text, translation, audio ও reference data-এর provenance/license যাচাই কীভাবে হবে
- কোন capability Phase-01-এর বাইরে থাকবে

## প্রাথমিক mapping — অনুমোদনের অপেক্ষায়

- `content/` — language/source অনুযায়ী content organization
- `data/quran/` — structural metadata ও machine-readable records
- `navigation/` — page/surah/juz/hizb/ruku/ayah navigation
- `search/` — text, root-word ও semantic search
- `reader/` — Mushaf, ayah, translation ও comparison views
- `audio/` — reciter, stream ও synchronization metadata
- `study/` — notes, bookmarks, highlights ও research workspace
- `api/` — Quran/navigation/search/translation/audio interfaces
- `apps/` — web, PWA, Android, iOS, desktop ও kiosk app boundaries

এই mapping একটি draft; event review ও approval-এর আগে এটিকে final ধরা যাবে না।
