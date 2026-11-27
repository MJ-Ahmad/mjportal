Prettier দিয়ে একটি বা একাধিক JSON ফাইল ফরম্যাট করতে নিচের কমান্ডগুলো ব্যবহার করতে পারেন।

**একটি নির্দিষ্ট JSON ফাইল ফরম্যাট করতে:**
```bash
npx prettier --write data.json
```

**বর্তমান ফোল্ডারের সব JSON ফাইল ফরম্যাট করতে:**
```bash
npx prettier --write "*.json"
```

**সাবফোল্ডারসহ সব JSON ফাইল ফরম্যাট করতে:**
```bash
npx prettier --write "**/*.json"
```

**প্রজেক্টের সব JSON, JS, TS ইত্যাদি Prettier-supported ফাইল ফরম্যাট করতে:**
```bash
npx prettier --write .
```

**Prettier ইনস্টল না থাকলে:**
```bash
npm install --save-dev prettier
```

তারপর:
```bash
npx prettier --write "**/*.json"
```

**আগে চেক করতে চান, কিন্তু ফাইল পরিবর্তন করতে চান না:**
```bash
npx prettier --check "**/*.json"
```

**package.json এ script যোগ করলে:**
```json
{
  "scripts": {
    "format:json": "prettier --write \"**/*.json\""
  }
}
```

এরপর চালান:
```bash
npm run format:json
```

এভাবে আপনার প্রজেক্টের সব JSON ফাইল স্বয়ংক্রিয়ভাবে সুন্দরভাবে (pretty formatted) ফরম্যাট হয়ে যাবে।

