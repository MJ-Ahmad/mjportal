#!/usr/bin/env python3

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from copy import deepcopy

MENU_FILE = Path("menu.json")
BACKUP_DIR = Path("backups")


class MenuManager:

    def __init__(self):

        if not MENU_FILE.exists():
            raise FileNotFoundError(
                f"{MENU_FILE} not found"
            )

        with open(
            MENU_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            self.data = json.load(f)

    def save(self):

        with open(
            MENU_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.data,
                f,
                indent=2,
                ensure_ascii=False
            )

    # -------------------------

    def get_title(self, node):

        title = node.get("title")

        if isinstance(title, dict):
            return title.get("en", "")

        return str(title)

    # -------------------------

    def find_node(
        self,
        nodes,
        parts
    ):

        if not parts:
            return None

        current = parts[0]

        for node in nodes:

            name = self.get_title(node)

            if name.lower() == current.lower():

                if len(parts) == 1:
                    return node

                return self.find_node(
                    node.get("children", []),
                    parts[1:]
                )

        return None

    # -------------------------

    def find_parent(
        self,
        nodes,
        parts
    ):

        if len(parts) == 1:
            return None

        return self.find_node(
            nodes,
            parts[:-1]
        )

    # -------------------------
    # TREE

    def tree(self):

        def walk(
            nodes,
            level=0
        ):

            for node in nodes:

                print(
                    "    " * level
                    + "└── "
                    + self.get_title(node)
                )

                walk(
                    node.get(
                        "children",
                        []
                    ),
                    level + 1
                )

        walk(self.data["menu"])

    # -------------------------
    # FIND

    def find(self, path):

        node = self.find_node(
            self.data["menu"],
            path.split("/")
        )

        if not node:
            print("Not found")
            return

        print(
            json.dumps(
                node,
                indent=2,
                ensure_ascii=False
            )
        )

    # -------------------------
    # ADD

    def add(
        self,
        parent_path,
        title,
        href
    ):

        parent = self.find_node(
            self.data["menu"],
            parent_path.split("/")
        )

        if not parent:
            print(
                "Parent not found"
            )
            return

        parent.setdefault(
            "children",
            []
        )

        parent["children"].append(
            {
                "title": {
                    "en": title
                },
                "href": href
            }
        )

        self.save()

        print(
            f"Added: {title}"
        )

    # -------------------------
    # ADD GROUP

    def add_group(
        self,
        parent_path,
        title
    ):

        parent = self.find_node(
            self.data["menu"],
            parent_path.split("/")
        )

        if not parent:
            print(
                "Parent not found"
            )
            return

        parent.setdefault(
            "children",
            []
        )

        parent["children"].append(
            {
                "title": {
                    "en": title
                },
                "children": []
            }
        )

        self.save()

        print(
            f"Group Added: {title}"
        )

    # -------------------------
    # REMOVE

    def remove(self, path):

        parts = path.split("/")

        parent = self.find_parent(
            self.data["menu"],
            parts
        )

        if not parent:
            print(
                "Parent not found"
            )
            return

        target = parts[-1]

        children = parent.get(
            "children",
            []
        )

        for item in children:

            if (
                self.get_title(item)
                .lower()
                ==
                target.lower()
            ):

                children.remove(item)

                self.save()

                print(
                    f"Removed: {target}"
                )

                return

        print("Not found")

    # -------------------------
    # RENAME

    def rename(
        self,
        path,
        new_name
    ):

        node = self.find_node(
            self.data["menu"],
            path.split("/")
        )

        if not node:

            print(
                "Not found"
            )

            return

        old = self.get_title(node)

        title = node.get("title")

        if isinstance(title, dict):
            title["en"] = new_name
        else:
            node["title"] = new_name

        self.save()

        print(
            f"{old} -> {new_name}"
        )

    # -------------------------
    # MOVE

    def move(
        self,
        source,
        target_parent
    ):

        source_parts = source.split("/")

        src_parent = self.find_parent(
            self.data["menu"],
            source_parts
        )

        target = self.find_node(
            self.data["menu"],
            target_parent.split("/")
        )

        if not src_parent:

            print(
                "Source parent not found"
            )

            return

        if not target:

            print(
                "Target parent not found"
            )

            return

        item_name = source_parts[-1]

        for item in src_parent.get(
            "children",
            []
        ):

            if (
                self.get_title(item)
                .lower()
                ==
                item_name.lower()
            ):

                src_parent[
                    "children"
                ].remove(item)

                target.setdefault(
                    "children",
                    []
                ).append(item)

                self.save()

                print(
                    "Moved"
                )

                return

        print("Item not found")

    # -------------------------
    # COPY

    def copy(
        self,
        source,
        target_parent
    ):

        src = self.find_node(
            self.data["menu"],
            source.split("/")
        )

        target = self.find_node(
            self.data["menu"],
            target_parent.split("/")
        )

        if not src:
            print("Source not found")
            return

        if not target:
            print("Target not found")
            return

        target.setdefault(
            "children",
            []
        )

        target[
            "children"
        ].append(
            deepcopy(src)
        )

        self.save()

        print("Copied")

    # -------------------------
    # VALIDATE

    def validate(self):

        errors = []
        hrefs = set()

        def walk(
            nodes,
            path="root"
        ):

            for node in nodes:

                if (
                    "title"
                    not in node
                ):
                    errors.append(
                        f"{path}: title missing"
                    )

                if (
                    "href"
                    not in node
                    and
                    "children"
                    not in node
                ):
                    errors.append(
                        f"{path}: href/children missing"
                    )

                if "href" in node:

                    href = node["href"]

                    if href in hrefs:

                        errors.append(
                            f"Duplicate href: {href}"
                        )

                    hrefs.add(href)

                walk(
                    node.get(
                        "children",
                        []
                    ),
                    path
                    + "/"
                    + self.get_title(node)
                )

        walk(
            self.data["menu"]
        )

        if errors:

            print(
                "\nValidation Errors:\n"
            )

            for e in errors:
                print("-", e)

        else:

            print(
                "Validation Passed"
            )

    # -------------------------
    # BACKUP

    def backup(self):

        BACKUP_DIR.mkdir(
            exist_ok=True
        )

        ts = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        dst = (
            BACKUP_DIR
            /
            f"menu_{ts}.json"
        )

        shutil.copy2(
            MENU_FILE,
            dst
        )

        print(
            f"Backup: {dst}"
        )

    # -------------------------
    # RESTORE

    def restore(self):

        if not BACKUP_DIR.exists():

            print(
                "No backup folder"
            )

            return

        files = sorted(
            BACKUP_DIR.glob(
                "menu_*.json"
            )
        )

        if not files:

            print(
                "No backup files"
            )

            return

        latest = files[-1]

        shutil.copy2(
            latest,
            MENU_FILE
        )

        print(
            f"Restored: {latest}"
        )

    # -------------------------
    # STATS

    def stats(self):

        total = 0
        folders = 0
        links = 0
        max_depth = 0

        def walk(
            nodes,
            depth=1
        ):

            nonlocal total
            nonlocal folders
            nonlocal links
            nonlocal max_depth

            max_depth = max(
                max_depth,
                depth
            )

            for node in nodes:

                total += 1

                if (
                    "children"
                    in node
                ):
                    folders += 1

                if (
                    "href"
                    in node
                ):
                    links += 1

                walk(
                    node.get(
                        "children",
                        []
                    ),
                    depth + 1
                )

        walk(
            self.data["menu"]
        )

        print(
            f"Total Nodes : {total}"
        )

        print(
            f"Folders     : {folders}"
        )

        print(
            f"Links       : {links}"
        )

        print(
            f"Max Depth   : {max_depth}"
        )

    # -------------------------
    # SORT

    def sort(self):

        def walk(nodes):

            nodes.sort(
                key=lambda x:
                self.get_title(x)
                .lower()
            )

            for node in nodes:

                walk(
                    node.get(
                        "children",
                        []
                    )
                )

        walk(
            self.data["menu"]
        )

        self.save()

        print(
            "Menu sorted"
        )


# ======================================

def usage():

    print("""
Commands

tree

find PATH

add PARENT TITLE HREF

add-group PARENT TITLE

remove PATH

rename PATH NEW_NAME

move SOURCE TARGET_PARENT

copy SOURCE TARGET_PARENT

validate

backup

restore

stats

sort

Examples

python menu_manager.py tree

python menu_manager.py find "Help/Docs"

python menu_manager.py add \
"Help/Docs" \
"API" \
"helping_source/api/"

python menu_manager.py add-group \
"Help" \
"References"

python menu_manager.py rename \
"Help/Docs/SDF" \
"SDF Specification"

python menu_manager.py move \
"Help/Docs/SDF" \
"Projects"

python menu_manager.py copy \
"Help/Docs/Protocol" \
"Learn"

python menu_manager.py validate

python menu_manager.py backup

python menu_manager.py restore

python menu_manager.py stats

python menu_manager.py sort
""")


# ======================================

def main():

    manager = MenuManager()

    if len(sys.argv) < 2:
        usage()
        return

    cmd = sys.argv[1]

    try:

        if cmd == "tree":
            manager.tree()

        elif cmd == "find":
            manager.find(sys.argv[2])

        elif cmd == "add":
            manager.add(
                sys.argv[2],
                sys.argv[3],
                sys.argv[4]
            )

        elif cmd == "add-group":
            manager.add_group(
                sys.argv[2],
                sys.argv[3]
            )

        elif cmd == "remove":
            manager.remove(
                sys.argv[2]
            )

        elif cmd == "rename":
            manager.rename(
                sys.argv[2],
                sys.argv[3]
            )

        elif cmd == "move":
            manager.move(
                sys.argv[2],
                sys.argv[3]
            )

        elif cmd == "copy":
            manager.copy(
                sys.argv[2],
                sys.argv[3]
            )

        elif cmd == "validate":
            manager.validate()

        elif cmd == "backup":
            manager.backup()

        elif cmd == "restore":
            manager.restore()

        elif cmd == "stats":
            manager.stats()

        elif cmd == "sort":
            manager.sort()

        else:
            usage()

    except IndexError:

        print(
            "Missing argument.\n"
        )

        usage()


if __name__ == "__main__":
    main()
