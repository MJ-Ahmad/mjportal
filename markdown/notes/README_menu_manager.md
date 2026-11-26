# Menu Manager

menu_manager.py হলো menu.json পরিচালনার জন্য একটি CLI Tool।

---

## Requirements

Python 3.8+

---

## Structure

Example:

Help
└── Docs
    ├── Protocol
    └── SDF

---

## Show Full Menu Tree

```bash
python menu_manager.py tree
```

Output:

```text
└── Help
    └── Docs
        ├── Protocol
        └── SDF
```

---

## Validate JSON

```bash
python menu_manager.py validate
```

Checks:

- Missing title
- Missing href
- Missing children
- Duplicate href
- Invalid nodes

Success:

```text
Validation Passed
```

---

## Find Menu

```bash
python menu_manager.py find "Help/Docs"
```

Output:

```json
{
  "title": {
    "en": "Docs"
  },
  "children": []
}
```

---

## Add New Menu

### Example

```bash
python menu_manager.py add \
"Help/Docs" \
"API" \
"helping_source/api/"
```

Result:

```text
Added: API
```

Menu becomes:

```text
Help
└── Docs
    ├── Protocol
    ├── SDF
    └── API
```

---

## Add Deep Nested Menu

```bash
python menu_manager.py add \
"Help/Docs/API" \
"V1" \
"helping_source/api/v1/"
```

Result:

```text
Help
└── Docs
    └── API
        └── V1
```

---

## Remove Menu

```bash
python menu_manager.py remove \
"Help/Docs/API"
```

Result:

```text
Removed: API
```

---

## Recommended Workflow

1. Add new menu
2. Validate menu.json
3. Open tree view
4. Commit to git

Example:

```bash
python menu_manager.py add \
"Learn/Media" \
"OBS" \
"learn/obs/"

python menu_manager.py validate

python menu_manager.py tree
```

---

## Backup Recommendation

Before major changes:

```bash
cp menu.json menu.json.bak
```

Restore:

```bash
cp menu.json.bak menu.json
```

---

## Supported Features

✅ Recursive menu

✅ Nested submenu

✅ Add node

✅ Remove node

✅ Find node

✅ Tree view

✅ Validation

✅ Duplicate href detection

✅ UTF-8 support

✅ Bengali titles supported

✅ Arabic titles supported

