"""Lists sentences from the novels in ../../novels that use each grammar unit.

    python tools/grammar/book_candidates.py > candidates.txt

The output is for choosing book examples by hand: each chosen sentence goes
into book_examples.json with its Turkish translation (the key words in
[brackets]), the book file and its 0-based PDF page.
"""
import json
import pathlib
import re
import sys

import fitz  # PyMuPDF

from units import units

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LIGATURES = {"ɹ": "fi", "ʃ": "ff", "ɻ": "fl", "ɽ": "ffi", "ʀ": "ffl", "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", " ": " "}
TOPICS = (("cj", "conjunctions"), ("vb", "verbs"), ("pv", "phrasal_verbs"), ("rc", "relative_clauses"))
RELATIVE = [
    r"\b(?:who|which|that)\b", r"\S\s+(?:who|which)\b", r"\S\s+whose\b", r"\b(?:the|a) \w+ (?:where|when|why)\b",
    r"\b(?:the|a|an) \w+ (?:I|you|he|she|we|they) \w+(?:ed)?\b", r", (?:who|which)\b", r"\b(?:in|on|at|with|to|for|of|from|about|by) (?:which|whom)\b",
    r"\bwhom\b", r", which\b", r"\b(?:the|a) \w+ (?:sitting|standing|lying|wearing|holding|called|named)\b",
]


def verb_forms(verb):
    irregular = json.loads((HERE.parent / "novel" / "irregular.json").read_text(encoding="utf-8"))
    forms = {verb, verb + "s", verb + "es", verb + "ing", verb + verb[-1] + "ing", verb[:-1] + "ing", verb + "ed", verb + "d"}
    if verb.endswith("y"):
        forms |= {verb[:-1] + "ies", verb[:-1] + "ied"}
    for form in irregular.get(verb, []):
        forms |= set(form.split("/"))
    return "(?:" + "|".join(sorted(forms, key=len, reverse=True)) + ")"


def pattern(topic_id, unit):
    if topic_id == "rc":
        return RELATIVE[unit["lesson"]]
    if topic_id == "vb":
        verb = unit["title"].lower()
        return rf"\b{verb_forms(verb)}\b" if re.fullmatch(r"[a-z]+", verb) else None
    if not unit["meaning"]:
        return None
    if topic_id == "pv":
        words = unit["title"].split(" + ")[0].split(" / ")[0].split()
        return rf"\b{verb_forms(words[0])}(?:\s+[\w’']+){{0,2}}?\s+{r'\s+'.join(words[1:])}\b"
    parts = re.findall(r"\[([^\]]+)\]", unit["examples"][0][0])
    if len(parts) > 2:
        return None
    return r".{1,60}?".join(rf"\b{re.escape(part.lower())}\b" for part in parts)


def sentences():
    """(book, page, sentence) for every sentence of every novel."""
    for path in sorted((ROOT / "novels").glob("*.pdf")):
        for page_number, page in enumerate(fitz.open(path)):
            text = page.get_text()
            for wrong, right in LIGATURES.items():
                text = text.replace(wrong, right)
            text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
            text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.M)
            text = re.sub(r"\s+", " ", text).strip()
            for sentence in re.split(r"(?:(?<=[.!?])|(?<=[.!?][”\"’]))\s+(?=[“\"A-Z])", text):
                if 25 <= len(sentence) <= 140:
                    yield path.name, page_number, sentence


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pool = list(sentences())
    for topic_id, name in TOPICS:
        topic = json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))
        for unit in units(topic_id, topic):
            regex = pattern(topic_id, unit)
            if not regex:
                continue
            found = {}
            for book, page, sentence in pool:
                match = re.search(regex, sentence, flags=re.I)
                if match:
                    marked = sentence[:match.start()] + "[" + match.group(0) + "]" + sentence[match.end():]
                    found.setdefault(book, []).append((abs(len(sentence) - 80), page, marked))
            print(f"## {unit['id']} | {unit['title']} = {unit['meaning']}")
            limit = 7 if topic_id in ("vb", "rc") else 3
            for book, items in sorted(found.items()):
                for _, page, marked in sorted(items)[:limit]:
                    print(f"  {book[6]}:{page} {marked}")


if __name__ == "__main__":
    main()
