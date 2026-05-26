#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PR_DRAFT = ROOT / "submission" / "PR_DRAFT.md"
URL_RE = re.compile(r"^https://(www\.)?(youtube\.com|youtu\.be|loom\.com|vimeo\.com)/\S+$")


def fail(message: str) -> int:
    print(f"ERROR {message}")
    return 1


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: attach-final-demo-video.py <https-video-url>")
        return 2
    url = argv[1].strip()
    lowered = url.lower()
    if not URL_RE.match(url):
        return fail("demo URL must be a supported https video URL")
    if any(marker in lowered for marker in ["pending", "demo_pending", "placeholder", "tbd", "old-pr", "lp0005", "lp0002"]):
        return fail("refusing placeholder/pending demo URL")
    if not PR_DRAFT.exists():
        return fail("submission/PR_DRAFT.md missing")

    text = PR_DRAFT.read_text()
    line = f"- **Narrated demo:** {url}"
    if re.search(r"^- \*\*Narrated demo:\*\* .*$", text, flags=re.MULTILINE):
        text = re.sub(r"^- \*\*Narrated demo:\*\* .*$", line, text, flags=re.MULTILINE)
    elif "## Supporting Materials" in text:
        text = text.replace("## Supporting Materials\n", "## Supporting Materials\n\n" + line + "\n", 1)
    else:
        text += "\n## Supporting Materials\n\n" + line + "\n"
    PR_DRAFT.write_text(text)
    print("updated submission/PR_DRAFT.md narrated demo URL")
    print("note: video attachment does not mark LEZ/RISC0/Basecamp evidence ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
