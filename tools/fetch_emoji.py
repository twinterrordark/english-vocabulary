#!/usr/bin/env python3
"""Download the Twemoji illustration chosen for each word in tools/emoji/*.json.

Words that have neither a fitting Wikimedia photo nor an illustration made for
them on the original page get an emoji picked by hand to show the meaning
(e.g. agree -> handshake, fear -> fearful face). Graphics: Twemoji by Twitter
and contributors (jdecked/twemoji), CC BY 4.0.

  python tools/fetch_emoji.py      -> tools/emoji/svg/<codepoints>.svg
"""
import json
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
EMOJI_DIR = HERE / "emoji"
SVG_DIR = EMOJI_DIR / "svg"
BASE = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/svg/"
USER_AGENT = "EnglishStudyBuild/1.0 (personal offline study page)"


def load_mapping() -> dict:
    mapping = {}
    for path in sorted(EMOJI_DIR.glob("*.json")):
        mapping.update(json.loads(path.read_text(encoding="utf-8")))
    return mapping


def twemoji_name(emoji: str) -> str:
    """Twemoji file name: code points joined by '-'; FE0F is dropped unless the emoji contains ZWJ."""
    if "‍" not in emoji:
        emoji = emoji.replace("️", "")
    return "-".join(f"{ord(ch):x}" for ch in emoji)


def main() -> None:
    SVG_DIR.mkdir(exist_ok=True)
    mapping = load_mapping()
    missing = []
    for emoji in sorted(set(mapping.values())):
        target = SVG_DIR / f"{twemoji_name(emoji)}.svg"
        if target.exists():
            continue
        request = urllib.request.Request(BASE + target.name, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                target.write_bytes(response.read())
        except Exception as error:
            missing.append((emoji, target.name, str(error)))
        time.sleep(0.05)
    words = [w for w, e in mapping.items() if not (SVG_DIR / f"{twemoji_name(e)}.svg").exists()]
    print(f"{len(mapping)} words, {len(set(mapping.values()))} emoji, {len(missing)} downloads failed")
    for item in missing:
        print("  failed:", *item)
    if words:
        print("  words without an emoji file:", words)


if __name__ == "__main__":
    main()
