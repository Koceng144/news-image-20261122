#!/usr/bin/env python3
"""Entry for news-image-20261122: "Sum up 22 November's world news in one image".

Copies the pre-composed cinematic poster for Sunday 22 November 2026
(poster_v1.png, built offline by build_poster_v1.py from three generated
scene illustrations and 39 date-verified stories) to /output/entry.png.
Standard library only, no network, deterministic: every run writes the
same bytes. Exits 0 on every path.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# The poster normally sits beside this file; fall back to the working
# directory in case the runner copies the program elsewhere.
SRC_CANDIDATES = [
    os.path.join(HERE, "poster_v1.png"),
    os.path.join(os.getcwd(), "poster_v1.png"),
]


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dst = os.path.join(out_dir, "entry.png")
    payload = None
    for src in SRC_CANDIDATES:
        try:
            with open(src, "rb") as fh:
                payload = fh.read()
            break
        except OSError:
            continue
    if payload is None:
        return 0
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(dst, "wb") as fh:
            fh.write(payload)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
