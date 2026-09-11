#!/usr/bin/env python3
"""Convert an image into ASCII art."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


DEFAULT_GITHUB_USER = "VIKRAM2605"
DETAIL_CHARS = " .,:;-~=+*#%@"


def resize_image(image: Image.Image, width: int) -> Image.Image:
    aspect_ratio = image.height / image.width
    height = max(1, int(width * aspect_ratio * 0.34))
    return image.resize((width, height))


def block_to_char(block: list[int], row_index: int, total_rows: int) -> str:
    average = sum(block) / len(block)
    spread = max(block) - min(block)
    hair_band = row_index < max(1, int(total_rows * 0.4))

    if average < 90:
        return " "

    if hair_band:
        if spread > 80:
            return "/" if block[0] < block[-1] else "\\"
        if average < 120:
            return "."
        if average < 145:
            return ":"
        if average < 170:
            return "-"
        if average < 195:
            return "="
        if average < 220:
            return "+"
        return "."

    if spread > 70:
        return ":"
    if average < 135:
        return "."
    if average < 160:
        return ":"
    if average < 185:
        return "-"
    if average < 210:
        return "="
    if average < 235:
        return "+"
    return " "


def sample_block(pixels: bytes, image_width: int, x: int, y: int, block_size: int) -> list[int]:
    values: list[int] = []
    for row in range(block_size):
        base = (y + row) * image_width + x
        values.extend(pixels[base : base + block_size])
    return values


def to_ascii(image: Image.Image, width: int) -> str:
    processed = ImageOps.autocontrast(image.convert("L"))
    processed = ImageEnhance.Contrast(processed).enhance(1.28)
    processed = ImageEnhance.Sharpness(processed).enhance(1.35)
    processed = processed.filter(ImageFilter.SHARPEN)
    resized = resize_image(processed, width)
    block_size = 2 if width >= 64 else 1
    sampled_width = max(1, resized.width // block_size)
    sampled_height = max(1, resized.height // block_size)
    sampled = processed.resize((sampled_width * block_size, sampled_height * block_size))
    pixels = sampled.tobytes()
    rows = []
    total_rows = sampled.height // block_size

    for row_index in range(0, sampled.height, block_size):
        row_chars = []
        for col_index in range(0, sampled.width, block_size):
            block = sample_block(pixels, sampled.width, col_index, row_index, block_size)
            row_chars.append(block_to_char(block, row_index // block_size, total_rows))
        rows.append("".join(row_chars))

    return "\n".join(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert an image to ASCII art.")
    parser.add_argument("image", nargs="?", type=Path, help="Path to the input image")
    parser.add_argument(
        "--github-user",
        default=DEFAULT_GITHUB_USER,
        help="GitHub username to fetch the live profile avatar from",
    )
    parser.add_argument("--width", type=int, default=80, help="Output width in characters")
    parser.add_argument("--output", type=Path, help="Optional file to write the ASCII art to")
    return parser


def load_image(args: argparse.Namespace) -> Image.Image:
    if args.image is not None:
        if not args.image.exists():
            raise FileNotFoundError(f"Image not found: {args.image}")
        return Image.open(args.image)

    avatar_url = f"https://github.com/{args.github_user}.png?size=512"
    try:
        with urlopen(avatar_url) as response:
            return Image.open(io.BytesIO(response.read()))
    except URLError as error:
        raise RuntimeError(f"Failed to download GitHub avatar for {args.github_user}") from error


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.width < 1:
        parser.error("--width must be at least 1")

    try:
        image = load_image(args)
    except (FileNotFoundError, RuntimeError) as error:
        parser.error(str(error))

    with image:
        ascii_art = to_ascii(image, args.width)

    if args.output:
        args.output.write_text(ascii_art + "\n", encoding="utf-8")
    else:
        print(ascii_art)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
