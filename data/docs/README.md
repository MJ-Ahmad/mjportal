# Registry — Docs

স্ট্যাটিক সাইট (GitHub Pages / যেকোনো হোস্টিং)। মেনু: **Dashboard · Docs · Registry**

```
index.html            ভিউয়ার (একটি ফাইল, কোনো বাইরের ফন্ট/লাইব্রেরি নেই)
data.json             সাইট সেটিং ও মূল মেনু — খুব ছোট, হোম পেজ শুধু এটি লোড করে
docs/index.json       Docs-এর ফোল্ডার-ট্রি + প্রতিটি ফাইলের মেটাডাটা (কনটেন্ট ছাড়া)
docs/files/<ID>.txt   প্রতিটি ফাইলের কনটেন্ট — ফাইল খুললে তবেই লোড হয়
tools/                Python টুল (core.py, registry.py)
_backup/              পুরনো ডাটার ব্যাকআপ (ডিপ্লয় করবেন না; .gitignore-এ আছে)
```

## দৈনন্দিন কমান্ড
```
./run.sh serve                       # http://localhost:8000
./run.sh add ফাইল "শিরোনাম" "বিবরণ" --menu "Web/Portal"
./run.sh add-dir ~/project --menu "Web"      # পুরো ডিরেক্টরি, ফোল্ডার-কাঠামোসহ
./run.sh menu                        # ফোল্ডার-ট্রি দেখুন
./run.sh menu --new "Web/Portal" --bn "ওয়েব/পোর্টাল"
./run.sh menu --move DOC-2026-0001 --to "Web/Portal"
./run.sh menu --move-menu "Web/Portal" --to "Tools"
./run.sh rm DOC-2026-0001
./run.sh check                       # ডাটা যাচাই (হ্যাশসহ)
```
জরুরি: `cp docs/index.json.bak docs/index.json && ./run.sh check`
