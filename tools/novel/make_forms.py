#!/usr/bin/env python3
"""Map inflected word forms to the dictionary word they come from.

The reader's dictionary (tools/novel/dict_*.json) lists base words ("dig",
"lizard"). Novels use other forms ("dug", "lizards"). This script reads the
PDFs in novels/ and writes tools/novel/forms.json: {"dug": "dig", ...} for
every form that is not itself in the dictionary but whose WordNet base word
is. Only the word list is saved, not the book text.

  python tools/novel/make_forms.py      (needs PyMuPDF and nltk + wordnet)
"""
import json
import re
from pathlib import Path

import fitz
from nltk.corpus import wordnet as wn

HERE = Path(__file__).resolve().parent
NOVELS = HERE.parent.parent / "novels"
# Calibre PDFs draw ligatures with these glyphs.
LIGATURES = {"ɹ": "fi", "ʃ": "ff", "ɻ": "fl", "ɽ": "ffi", "ʀ": "ffl"}


def load_dictionary() -> dict:
    words = {}
    for path in sorted(HERE.glob("dict_*.json")):
        words.update(json.loads(path.read_text(encoding="utf-8")))
    words.pop("_comment", None)
    return words


def main() -> None:
    words = load_dictionary()
    forms_path = HERE / "forms.json"
    forms = json.loads(forms_path.read_text(encoding="utf-8")) if forms_path.exists() else {}
    for pdf in sorted(NOVELS.glob("*.pdf")):
        text = "\n".join(page.get_text() for page in fitz.open(pdf))
        for glyph, letters in LIGATURES.items():
            text = text.replace(glyph, letters)
        for token in set(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*", text)):
            form = token.lower().replace("’", "'")
            base = re.sub(r"'s$", "", form)
            if form in words or form in forms:
                continue
            for pos in ("v", "n", "a", "r"):
                lemma = wn.morphy(base, pos)
                if lemma and lemma != form and lemma in words:
                    forms[form] = lemma
                    break
    forms_path.write_text(json.dumps(dict(sorted(forms.items())), ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(words)} dictionary words, {len(forms)} inflected forms -> {forms_path.name}")


if __name__ == "__main__":
    main()
