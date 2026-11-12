#!/usr/bin/env python3
"""Lint shortcut plist: structural validation only."""
from __future__ import annotations

import plistlib
import sys
from collections import Counter
from pathlib import Path


def fail(msg: str) -> None:
    print(msg)
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: lint_plist.py <plist>")
    path = Path(sys.argv[1])
    if not path.is_file():
        fail(f"missing plist: {path}")
    with path.open("rb") as f:
        try:
            data = plistlib.load(f)
        except Exception as e:
            fail(f"plistlib.load failed: {e}")

    actions = data.get("WFWorkflowActions")
    if not isinstance(actions, list):
        fail("WFWorkflowActions is not an array")
    if not actions:
        fail("WFWorkflowActions is empty")

    for i, a in enumerate(actions):
        ident = a.get("WFWorkflowActionIdentifier")
        if not ident:
            fail(f"action {i} missing WFWorkflowActionIdentifier")
        if not str(ident).startswith("is.workflow.actions."):
            fail(f"action {i} bad identifier: {ident}")

    uuids = []
    for i, a in enumerate(actions):
        params = a.get("WFWorkflowActionParameters") or {}
        u = params.get("UUID")
        if u:
            uuids.append(u)

    dup = [u for u, n in Counter(uuids).items() if n > 1]
    if dup:
        fail(f"duplicate UUID(s): {dup}")

    print(f"PASS actions={len(actions)} uuids={len(uuids)}")


if __name__ == "__main__":
    main()
