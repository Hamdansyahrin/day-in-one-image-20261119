#!/usr/bin/env python3
"""Entrypoint for the news-image-20261119 entry.

Validates the bundled entry.png (PNG or JPEG magic, 1 MiB cap,
1024 px-per-side cap, strict PNG chunk-trailer check), copies it to
$MAKEFUN_OUTPUT_DIR/entry.png and verifies the copy by sha256
read-back. Standard library only; exits non-zero on failure.
"""

import hashlib
import os
import struct
import sys

MAX_BYTES = 1024 * 1024
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def png_dimensions(data):
    if len(data) < 24:
        raise ValueError("PNG too short for IHDR")
    return struct.unpack(">II", data[16:24])


def check_png_trailer(data):
    """Walk the PNG chunk stream; the file must end exactly at IEND.

    Each chunk is length(4) + type(4) + data(length) + CRC(4). Any byte
    after IEND (or a missing IEND) means the file is corrupt or carries
    data smuggled past the image, and it is rejected.
    """
    pos = len(PNG_MAGIC)
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            raise ValueError("truncated PNG chunk header")
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4
        if end > len(data):
            raise ValueError("truncated PNG chunk body")
        pos = end
        if ctype == b"IEND":
            seen_iend = True
            break
    if not seen_iend:
        raise ValueError("PNG has no IEND chunk")
    if pos != len(data):
        raise ValueError("trailing data after PNG IEND")


def jpeg_dimensions(data):
    """(width, height) from the first SOF marker of a JPEG stream."""
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            raise ValueError("JPEG marker expected")
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg_len
    raise ValueError("no JPEG SOF marker found")


def validate(data):
    if len(data) > MAX_BYTES:
        raise ValueError("entry exceeds the 1 MiB cap")
    if data.startswith(PNG_MAGIC):
        width, height = png_dimensions(data)
        check_png_trailer(data)
    elif data.startswith(JPEG_MAGIC):
        width, height = jpeg_dimensions(data)
    else:
        raise ValueError("entry is neither PNG nor JPEG (bad magic)")
    if width <= 0 or height <= 0:
        raise ValueError("entry has a zero dimension")
    if width > MAX_DIM or height > MAX_DIM:
        raise ValueError("entry exceeds the 1024 px-per-side cap")
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "entry.png"), "rb") as fh:
        data = fh.read()
    width, height = validate(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as fh:
        fh.write(data)

    with open(dst, "rb") as fh:
        written = fh.read()
    digest = hashlib.sha256(data).hexdigest()
    if written != data or hashlib.sha256(written).hexdigest() != digest:
        raise ValueError("read-back verification failed")
    print(f"entry.png OK: {width}x{height}, {len(data)} bytes, "
          f"sha256 {digest}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
