---
name: allegro-library-handoff-skill
description: Create, review, package, receive, and adopt Allegro PCB library symbols and padstacks through a traceable handoff. Use for DRA/PSM/PAD delivery, footprint revisions, delegated library work, isolated-board refresh, save-and-reopen validation, or when library-level checks must remain distinct from board-level adoption and manufacturing approval.
---

# Allegro Library Handoff

Protect the source library and target board. Work on explicit D-drive copies unless the user gives another location. Do not update a production BRD before an isolated adoption check succeeds.

## Define the task

Record package name, device identity, source drawing/datasheet revision, units, origin, pin map, pad requirements, courtyard/height constraints, Allegro version, allowed changes, and acceptance owner. Resolve ambiguous dimensions before construction.

## Build or review the native library

1. Inspect the actual `.dra`, `.psm`, `.pad`, shapes, text, properties, and dependency search paths.
2. Check pad drill/slot, plating intent, annular ring, copper, mask, paste, thermal behavior, pin numbering, body, assembly, silkscreen, place boundary, height, origin, and orientation.
3. Save native tool reports and measurements. A rendered image alone is insufficient evidence of database content.
4. Package only the fixed candidate and its dependencies. Use `scripts/handoff_package.py` to bind listed files to a manifest.

Read `references/acceptance-flow.md` for the receiver workflow.

## Receive and adopt

Verify the manifest, then use a disposable or isolated BRD to load the exact library candidate. Refresh the symbol, compare pin-to-net membership, measure critical geometry, run relevant checks, save, close, reopen, and repeat the essential checks. Record whether the result is only received, library-reviewed, board-verified, approved for a named project, or released to a controlled library.

Use `assets/handoff-record.md` for evidence. Never equate package integrity with footprint correctness, board adoption, or manufacturing release.

