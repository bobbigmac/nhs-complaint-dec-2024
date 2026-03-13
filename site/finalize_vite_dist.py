#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_static_tree(source_dir: Path, destination_dir: Path) -> None:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")
    if not destination_dir.exists():
        raise FileNotFoundError(f"Destination directory does not exist: {destination_dir}")

    for item in source_dir.iterdir():
        if item.name == "index.html":
            continue
        target = destination_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy non-index static site output into the Vite dist directory.")
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("destination_dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    copy_static_tree(args.source_dir, args.destination_dir)
    print(args.destination_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
