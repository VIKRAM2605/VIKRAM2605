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


def resize_image(image: Image.Image, width: int) -> Image.Image:
    aspect_ratio = image.height / image.width
    height = max(1, int(width * aspect_ratio * 0.46))
    return image.resize((width, height))


def tone_to_char(pixel: int, row_index: int, total_rows: int) -> str:
    hair_band = row_index < max(1, int(total_rows * 0.42))

    if hair_band:
        if pixel < 90:
            return " "
        if pixel < 115:
            return ":"
        if pixel < 140:
            return "-"
        if pixel < 165:
            return "="
        if pixel < 190:
            return "+"
        if pixel < 220:
            return "."
        return " "

    if pixel < 128:
        return " "
    if pixel < 154:
        return "."
    if pixel < 180:
        return ":"
    if pixel < 205:
        return "-"
    if pixel < 230:
        return "="
    return " "


def to_ascii(image: Image.Image, width: int) -> str:
    processed = ImageOps.autocontrast(image.convert("L"))
    processed = ImageEnhance.Contrast(processed).enhance(1.2)
    processed = processed.filter(ImageFilter.SHARPEN)
    resized = resize_image(processed, width)
    pixels = resized.tobytes()
    rows = []
    total_rows = len(pixels) // width

    for row_index, index in enumerate(range(0, len(pixels), width)):
        row_pixels = pixels[index : index + width]
        rows.append("".join(tone_to_char(pixel, row_index, total_rows) for pixel in row_pixels))

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
