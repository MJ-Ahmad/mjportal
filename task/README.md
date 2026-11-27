# Tasks

ব্যক্তিগত ও দলগত টাস্ক ম্যানেজার। ওয়েব অ্যাপ (মোবাইল ও ডেস্কটপ) এবং CLI, দুটোই একই ডেটা ব্যবহার করে।

## শুরু করুন

```bash
chmod +x run.sh
./run.sh migrate              # পুরনো ডেটা নতুন ফরম্যাটে আনুন (আগে ব্যাকআপ নেয়)
./run.sh passwd               # ওয়েব লগইনের পাসওয়ার্ড সেট করুন
./run.sh web 8000             # http://127.0.0.1:8000
BIND=0.0.0.0 ./run.sh web     # ফোন বা নেটওয়ার্কের অন্য ডিভাইস থেকে
```

## CLI

```bash
./run.sh add "দুধ কিনতে হবে" -l inbox -d tomorrow -m
./run.sh add "রিপোর্ট" -d +3d -p high -r weekly --step "খসড়া" --step "পর্যালোচনা"
./run.sh ls                   # সক্রিয় সব টাস্ক
./run.sh ls today             # আমার দিন (today / important / planned / done / trash)
./run.sh done 12              # সম্পন্ন (পুনরাবৃত্ত টাস্ক পরের তারিখে চলে যায়)
./run.sh step done 12 2       # চেকলিস্টের ২ নম্বর আইটেম; 2.1 দিলে উপ-আইটেম
./run.sh note add 12 "ক্লায়েন্ট সম্মত"
./run.sh rm 12 ; ./run.sh restore 12 ; ./run.sh purge 12
./run.sh list add "অফিস"
./run.sh validate ; ./run.sh backup
```

ID ছোট করে লেখা যায় (`12` মানে TASK-000012)। তারিখ: `today`, `tomorrow`, `+3d`, `+2w`, `YYYY-MM-DD`।

## নিরাপত্তা

- পাসওয়ার্ড PBKDF2 দিয়ে হ্যাশ করা, `config.json`-এ।
- সেশন: স্বাক্ষরিত HttpOnly কুকি, ৩০ দিন।
- লগইনে ৫ বার ভুল হলে ১৫ মিনিট ব্লক।
- API লেখায় বিশেষ হেডার লাগে (cross-site আক্রমণ আটকায়)।
- বাইরের ইন্টারনেটে খুললে HTTPS রিভার্স প্রক্সির (Caddy/Nginx) পেছনে চালান এবং `HTTPS=1` দিন।

## ফাইল

`data.json` (টাস্ক), `registry.json` (ID), `audit.jsonl` (পরিবর্তনের লগ), `attachments/`, `backups/`, `config.json` ও `.secret` (গোপন, কখনো শেয়ার করবেন না)।
