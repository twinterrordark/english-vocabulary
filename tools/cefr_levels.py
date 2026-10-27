#!/usr/bin/env python3
"""Assign a CEFR level (A2, B1, B2, C1) to every vocabulary entry.

Source: the Oxford 3000 and Oxford 5000 word lists (levels A1–C1), as cleaned
TSV files in https://github.com/voothi/20260715190122-oxford-3000-5000 (MIT).
Download the two TSV files into tools/cefr/ and run:  python tools/cefr_levels.py

Rules (written to tools/levels.json, which build_index.py reads):
  * the lowest level listed for any sense of the word is used;
  * A1 words are shown as A2, because the app starts at A2;
  * British/American spelling variants are matched (analyze/analyse, ...);
  * words that are not in the Oxford 5000 at all are advanced vocabulary and
    are labelled "C1+" (beyond the Oxford 5000; often C2 in other lists).
"""
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5}


def load_oxford() -> dict:
    levels: dict[str, str] = {}
    for path in sorted((HERE / "cefr").glob("*.tsv")):
        for row in csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"):
            found = [lv for lv in re.findall(r"\b(A1|A2|B1|B2|C1)\b", row["Level"])]
            if not found:
                continue
            lowest = min(found, key=ORDER.get)
            for word in row["Word"].split(","):
                key = re.sub(r"\d+$", "", word.strip().lower())
                if key and (key not in levels or ORDER[lowest] < ORDER[levels[key]]):
                    levels[key] = lowest
    return levels


def variants(word: str) -> list[str]:
    out = [word, word.replace("ize", "ise").replace("yze", "yse"), word.replace("ise", "ize").replace("yse", "yze")]
    if word.endswith("or"):
        out.append(word[:-2] + "our")
    if word.endswith("ll"):
        out.append(word[:-1])
    if word.endswith(" to"):
        out.append(word[:-3])
    return out


def main() -> None:
    oxford = load_oxford()
    # Every distinct vocabulary word has an entry in the sentence files.
    words = sorted({w for path in (HERE / "sentences").glob("*.json") for w in json.loads(path.read_text(encoding="utf-8"))})
    result = {}
    for word in words:
        level = next((oxford[v] for v in variants(word) if v in oxford), None)
        result[word] = "A2" if level == "A1" else (level or "C1+")
    (HERE / "levels.json").write_text(json.dumps(result, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    counts = {}
    for level in result.values():
        counts[level] = counts.get(level, 0) + 1
    print("levels:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
