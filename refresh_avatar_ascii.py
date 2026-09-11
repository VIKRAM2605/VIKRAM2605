#!/usr/bin/env python3
"""Refresh the README's ASCII avatar block from the live GitHub profile image."""

from __future__ import annotations

from pathlib import Path

from profile_ascii_converter import DEFAULT_GITHUB_USER, load_image, to_ascii


README_PATH = Path(__file__).with_name("README.md")
START_MARKER = "<!-- avatar-ascii:start -->"
END_MARKER = "<!-- avatar-ascii:end -->"


def build_block(ascii_art: str) -> str:
    return f"{START_MARKER}\n```text\n{ascii_art}\n```\n{END_MARKER}"


def main() -> int:
    class Args:
        image = None
        github_user = DEFAULT_GITHUB_USER

    with load_image(Args()) as image:
        ascii_art = to_ascii(image, 48)

    readme = README_PATH.read_text(encoding="utf-8")
    start = readme.index(START_MARKER)
    end = readme.index(END_MARKER) + len(END_MARKER)
    updated = readme[:start] + build_block(ascii_art) + readme[end:]
    README_PATH.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
