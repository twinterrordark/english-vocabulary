"""Apply reviewed, exact-entry corrections without rewriting the legacy source.

The catalogue keeps the old and new values together. A stale ID, word or old
value fails the build rather than accidentally correcting a different sense.
"""
import json
from pathlib import Path

FIELDS = {"meaning", "example", "exampleTr", "definition", "pron"}
POS = {"n", "v", "adj", "adv", "prep", "conj", "pron", "det", "num", "int", "phr"}


def apply_corrections(main, work, pictures, path=None):
    path = path or Path(__file__).with_name("vocabulary_corrections.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ValueError("Unknown vocabulary correction catalogue version")
    entries = {entry["id"]: entry for entry in main + work}
    if len(entries) != len(main) + len(work):
        raise ValueError("Duplicate vocabulary IDs")
    overrides, seen = {}, set()
    for fix in data["corrections"]:
        entry = entries.get(fix["id"])
        if fix["id"] in seen or entry is None or entry["word"] != fix["word"]:
            raise ValueError(f"Unknown, duplicate or mismatched correction: {fix['id']}")
        seen.add(fix["id"])
        before, after = fix["before"], fix["after"]
        if not before or set(before) != set(after) or not set(after) <= FIELDS or not fix["reason"].strip():
            raise ValueError(f"Invalid correction fields: {fix['id']}")
        if any(entry.get(key) != value for key, value in before.items()):
            raise ValueError(f"Stale original value in correction: {fix['id']}")
        if any(not isinstance(value, str) or not value.strip() for value in after.values()):
            raise ValueError(f"Empty correction: {fix['id']}")
        entry.update(after)
        if "sentenceGroups" in fix:
            overrides[entry["word"].strip().lower()] = fix["sentenceGroups"]
    words = {entry["word"].strip().lower() for entry in main + work}
    for addition in data["additions"]:
        entry = addition["entry"].copy()
        key = entry["word"].strip().lower()
        if entry["id"] in entries or key in words or entry["level"] not in {"A2", "B1", "B2", "C1", "C1+"}:
            raise ValueError(f"Duplicate or invalid addition: {key}")
        if any(not isinstance(entry.get(field), str) or not entry[field].strip() for field in ["id", "word", "meaning", "example", "exampleTr"]):
            raise ValueError(f"Incomplete addition: {key}")
        image = pictures.get(addition["pictureFrom"])
        if not image:
            raise ValueError(f"Missing picture for addition: {key}")
        entry["n"] = max(item["n"] for item in main) + 1
        pictures[key] = image
        main.append(entry)
        entries[entry["id"]] = entry
        words.add(key)
        overrides[key] = addition["sentenceGroups"]
    for word, groups in overrides.items():
        if not groups or not set(groups) <= POS:
            raise ValueError(f"Invalid sentence groups: {word}")
        for pairs in groups.values():
            if not pairs or any(not isinstance(pair, list) or len(pair) != 2 or any(not isinstance(s, str) or not s.strip() for s in pair) for pair in pairs):
                raise ValueError(f"Invalid sentence pair: {word}")
    print(f"corrections     {len(data['corrections'])} reviewed entries; {len(data['additions'])} additions")
    return overrides
