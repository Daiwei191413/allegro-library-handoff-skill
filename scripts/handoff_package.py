"""Create or verify an integrity manifest for an Allegro library handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROLE_BY_SUFFIX = {
    ".dra": "symbol_source",
    ".psm": "compiled_symbol",
    ".pad": "padstack",
    ".ssm": "compiled_shape",
    ".bsm": "compiled_shape",
}
REQUIRED_ROLES = {"symbol_source", "compiled_symbol", "padstack"}


def safe_file(root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError(f"unsafe relative path: {name!r}")
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"path escapes package root: {name!r}")
    return candidate


def digest(path: Path) -> tuple[int, str]:
    hasher = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            hasher.update(chunk)
    return size, hasher.hexdigest()


def snapshot(root: Path, names: list[str]) -> dict:
    records = []
    roles = set()
    seen = set()
    for name in names:
        path = safe_file(root, name)
        normalized = Path(name).as_posix()
        if normalized.casefold() in seen:
            raise ValueError(f"duplicate package path: {name!r}")
        if not path.is_file():
            raise ValueError(f"not a regular file: {name!r}")
        seen.add(normalized.casefold())
        role = ROLE_BY_SUFFIX.get(path.suffix.lower(), "supporting")
        roles.add(role)
        size, sha256 = digest(path)
        records.append({"path": normalized, "role": role, "size": size, "sha256": sha256})
    missing_roles = sorted(REQUIRED_ROLES - roles)
    if missing_roles:
        raise ValueError("missing required roles: " + ", ".join(missing_roles))
    return {"schema": 1, "files": sorted(records, key=lambda item: item["path"].casefold())}


def verify(root: Path, manifest: object) -> list[str]:
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise ValueError("unsupported manifest schema")
    records = manifest.get("files")
    if not isinstance(records, list) or not records:
        raise ValueError("manifest files must be a non-empty list")
    issues = []
    roles = set()
    seen = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"files[{index}] must be an object")
        name = record.get("path")
        role = record.get("role")
        if not isinstance(name, str) or not isinstance(role, str):
            raise ValueError(f"files[{index}] has invalid path or role")
        if name.casefold() in seen:
            raise ValueError(f"duplicate manifest path: {name!r}")
        seen.add(name.casefold())
        roles.add(role)
        path = safe_file(root, name)
        if not path.is_file():
            issues.append(f"MISSING: {name}")
            continue
        size, sha256 = digest(path)
        if size != record.get("size") or sha256 != record.get("sha256"):
            issues.append(f"CHANGED: {name}")
    missing_roles = sorted(REQUIRED_ROLES - roles)
    if missing_roles:
        raise ValueError("manifest lacks required roles: " + ", ".join(missing_roles))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("snapshot")
    create.add_argument("root", type=Path)
    create.add_argument("manifest", type=Path)
    create.add_argument("files", nargs="+")
    check = subparsers.add_parser("verify")
    check.add_argument("root", type=Path)
    check.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("package root must be a directory")
        if args.command == "snapshot":
            document = snapshot(root, args.files)
            with args.manifest.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(document, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            print(f"SNAPSHOT: {len(document['files'])} file(s)")
            return 0
        document = json.loads(args.manifest.read_text(encoding="utf-8"))
        issues = verify(root, document)
        if issues:
            print("\n".join(issues))
            return 1
        print(f"MATCH: {len(document['files'])} file(s)")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

