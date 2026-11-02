"""Choose a Twemoji picture for every work and exam word: tools/work/work_emoji.json, and fetch the SVGs.

Words take their picture from the beginnings in emoji_roots.txt, then from the main list's
hand-picked emoji (tools/emoji/*.json), looking at the last word of a phrase first."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
sys.path.insert(0, str(TOOLS))
from fetch_emoji import load_mapping, twemoji_name, BASE, SVG_DIR, USER_AGENT  # noqa: E402
import urllib.request  # noqa: E402

SKIP = {"a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "with", "from", "and", "or", "sb", "sth", "as", "may", "be", "up", "out", "off", "down", "into", "about", "over", "than"}
BY_TYPE = {"v": "▶️", "adj": "🔷", "adv": "➡️", "n": "📌", "phr": "🧩", "prep": "🧩", "conj": "🧩"}


def main() -> None:
    roots: list[tuple[str, str]] = []
    exact: dict[str, str] = {}
    for line in (HERE / "emoji_roots.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or ":" not in line:
            continue
        emoji, words = line.split(":", 1)
        for word in words.split():
            if word.startswith("="):
                exact[word[1:]] = emoji.strip()
            else:
                roots.append((word, emoji.strip()))
    roots.sort(key=lambda item: -len(item[0]))
    base = {word.lower(): emoji for word, emoji in load_mapping().items()}

    words: dict[str, str] = {}
    for name in ("ai_it", "industrial_design", "business", "exam_words"):
        for line in (HERE / f"{name}.txt").read_text(encoding="utf-8").splitlines():
            if " | " in line and not line.startswith("#"):
                words[line.split(" | ")[0].strip().lower()] = ""
    kinds: dict[str, str] = {}
    sentences = json.loads((HERE / "extra_sentences.json").read_text(encoding="utf-8"))
    for word, groups in sentences.items():
        kinds[word] = next(iter(groups))
    for path in sorted(HERE.glob("written_sentences_*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if " | " in line and not line.startswith("#"):
                bits = line.split(" | ")
                kinds.setdefault(bits[0].strip().lower(), bits[1].strip())

    def pick(part: str) -> str:
        if part in exact:
            return exact[part]
        if part in base:
            return base[part]
        for root, emoji in roots:
            if len(root) >= 3 and part.startswith(root):
                return emoji
        return ""

    out, general = {}, 0
    for word in words:
        parts = [part for part in re.findall(r"[a-z0-9'-]+", word) if part not in SKIP]
        chosen = pick(word) if " " not in word else ""
        for part in reversed(parts):
            chosen = chosen or pick(part)
        if not chosen:
            for root in sorted(base, key=len, reverse=True):
                if len(root) >= 5 and parts and parts[-1].startswith(root[:max(5, len(root) - 1)]) and abs(len(parts[-1]) - len(root)) <= 7:
                    chosen = base[root]
                    break
        if not chosen:
            chosen = BY_TYPE.get(kinds.get(word, "phr" if " " in word else "n"), "📌")
            general += 1
        out[word] = chosen
    (HERE / "work_emoji.json").write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    print("words", len(out), "general pictures", general, "different emoji", len(set(out.values())))

    missing = 0
    for emoji in sorted(set(out.values())):
        svg = SVG_DIR / f"{twemoji_name(emoji)}.svg"
        if svg.exists():
            continue
        request = urllib.request.Request(BASE + f"{twemoji_name(emoji)}.svg", headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                svg.write_bytes(response.read())
        except Exception as err:
            missing += 1
            print("no picture for", emoji, twemoji_name(emoji), err)
    print("fetch problems:", missing)


if __name__ == "__main__":
    main()
