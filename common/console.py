"""fix_windows_console_encoding — call this first thing in any entry-point
script that prints free-form text, especially LLM output.

Windows consoles often default to a legacy codepage (cp1252) that can't
encode arbitrary Unicode (smart quotes, non-breaking hyphens, em dashes,
...). This was manageable while every printed string was hand-written (a
handful of em dashes and a "★" got caught and swapped for ASCII in earlier
phases) — it stopped being manageable the moment real LLM-generated text
started getting printed (the Groq integration), since that text isn't
under this project's control. Reconfiguring stdout/stderr to UTF-8 with
errors="replace" means an unprintable character degrades to a replacement
glyph instead of crashing the whole script.
"""

from __future__ import annotations

import sys


def fix_windows_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass  # best-effort only — never let this break the actual script
