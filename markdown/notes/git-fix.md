আপনি যদি পুরো রিপোজিটরি `git clone` না করে শুধু নির্দিষ্ট ফাইল/ফোল্ডার আপডেট বা নতুন ফাইল পুশ করতে চান, তাহলে **sparse checkout + partial clone** ব্যবহার করতে পারেন। এতে মোবাইল স্টোরেজ অনেক কম ব্যবহার হবে।

## পদ্ধতি ১: Sparse Clone (প্রস্তাবিত)

ধরুন রিপো:

```bash
https://github.com/USERNAME/REPO.git
```

### ১. রিপো Initialize করুন

```bash
mkdir myrepo
cd myrepo

git init
git remote add origin https://github.com/USERNAME/REPO.git
```

### ২. Sparse Checkout চালু করুন

```bash
git sparse-checkout init --cone
```

### ৩. শুধুমাত্র প্রয়োজনীয় ফোল্ডার নামিয়ে আনুন

ধরুন `src/` ফোল্ডার নিয়ে কাজ করবেন:

```bash
git sparse-checkout set src
```

### ৪. ডাউনলোড করুন

```bash
git pull origin main
```

এখন পুরো রিপো না এনে শুধু `src` ফোল্ডার আসবে।

---

## নতুন ফাইল Push করা

ধরুন:

```bash
mkdir docs
nano docs/readme.txt
```

এরপর:

```bash
git add docs/readme.txt
git commit -m "Add readme"
git push origin main
```

---

## অন্য ফোল্ডার পরে দরকার হলে

বর্তমান sparse checkout-এ নতুন ফোল্ডার যোগ করুন:

```bash
git sparse-checkout add assets
```

অথবা:

```bash
git sparse-checkout set src assets docs
```

তারপর:

```bash
git pull
```

---

## পদ্ধতি ২: Partial Clone (আরও কম ডাটা)

```bash
git clone --filter=blob:none --sparse https://github.com/USERNAME/REPO.git
```

রিপোতে ঢুকে:

```bash
cd REPO
git sparse-checkout set src
```

এতে Git শুধুমাত্র প্রয়োজনীয় ফাইলের কনটেন্ট ডাউনলোড করবে।

---

## শুধু একটি ফাইল আপডেট করতে চাইলে

যদি `config/settings.json` পরিবর্তন করতে চান:

```bash
git sparse-checkout set config
```

ফাইল এডিট:

```bash
nano config/settings.json
```

তারপর:

```bash
git add config/settings.json
git commit -m "Update settings"
git push origin main
```

---

## Termux + proot Ubuntu-তে স্টোরেজ বাঁচানোর অতিরিক্ত টিপস

Clone করার সময়:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/USERNAME/REPO.git
```

এখানে:

- `--depth 1` = শুধু সর্বশেষ commit
- `--filter=blob:none` = ফাইল ডাটা প্রয়োজন হলে নামাবে
- `--sparse` = নির্দিষ্ট ফোল্ডার নির্বাচন

ফলে শত শত MB-এর রিপোও কয়েক MB-তে কাজ করা যায়।

### আপনার বর্তমান GitHub রিপোর উদাহরণ

যদি আপনি রিপোর URL দেন, আমি আপনার রিপোর স্ট্রাকচার অনুযায়ী Termux/proot-Ubuntu-র জন্য একদম প্রস্তুত কমান্ড সেট লিখে দিতে পারি।

---

আপনি সম্ভবত GitHub রিপো **MJ-Ahmad/uqns** বোঝাতে চেয়েছেন। যদি রিপোর URL হয়:

```bash
https://github.com/MJ-Ahmad/uqns.git
```

তাহলে Termux proot-distro Ubuntu-তে স্টোরেজ সাশ্রয় করে কাজ করার জন্য নিচের পদ্ধতি ব্যবহার করুন।

### প্রথমবার সেটআপ

```bash
mkdir ~/uqns-work
cd ~/uqns-work

git clone --depth 1 --filter=blob:none --sparse https://github.com/MJ-Ahmad/uqns.git
cd uqns
```

এরপর ধরুন শুধু `docs` ফোল্ডার নিয়ে কাজ করবেন:

```bash
git sparse-checkout set docs
```

---

### নতুন ফাইল যোগ করে Push

```bash
mkdir -p docs
nano docs/newfile.md
```

এরপর:

```bash
git add docs/newfile.md
git commit -m "Add new file"
git push origin main
```

যদি ডিফল্ট ব্রাঞ্চ `master` হয়, তাহলে `main` এর বদলে `master` ব্যবহার করবেন।

---

### অন্য ফোল্ডার পরে দরকার হলে

```bash
git sparse-checkout add assets
```

অথবা

```bash
git sparse-checkout add src
```

তারপর:

```bash
git pull
```

---

### বর্তমানে কোন ব্রাঞ্চ ব্যবহার হচ্ছে দেখুন

```bash
git branch -a
```

অথবা

```bash
git remote show origin
```

---

### রিপোর ফাইল না নামিয়ে শুধু ব্রাঞ্চ তথ্য দেখতে

```bash
git ls-remote --heads origin
```

---

### স্টোরেজ আরও কমাতে

কাজ শেষে:

```bash
git gc --aggressive
```

এবং পুরনো history না আনার জন্য সবসময়:

```bash
git pull --depth 1
```

ব্যবহার করতে পারেন।

যদি **MJ-Ahmad/uqns** রিপোর সঠিক GitHub URL দেন (যেমন `https://github.com/MJ-Ahmad/uqns.git`), তাহলে আমি আপনার রিপোর ফোল্ডার স্ট্রাকচার দেখে কোন কোন sparse-checkout কমান্ড ব্যবহার করলে সবচেয়ে কম স্টোরেজ লাগবে, সেটাও নির্দিষ্টভাবে লিখে দিতে পারব।

---


