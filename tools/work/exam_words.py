"""Collect the English words of the study PDFs in Language/ into tools/work/exam_words.txt.

Only the English words are taken. Their Turkish meanings are not read from the PDFs:
they come from this site's own dictionaries and, for the rest, from machine translation.
The PDFs themselves stay out of the repository (see .gitignore)."""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "exam_words.txt"
CACHE = HERE / "exam_words_tr.json"
AGENT = "EnglishStudyBuild/1.0 (personal offline study page)"

TYPE = re.compile(r"^(fiil|.sim|s.fat|zarf|edat|ba.la.|.nlem|zamir|p\.? ?verb|phrasal( verb)?|prep\.?( phrase)?|phrase|deyim|kal.p)$", re.I)
HEAD = re.compile(r"^(.ngilizce|t.rk.e|t.r|di.er yap.lar.|e. anlaml.lar.?|collocation|preposition|synonyms)$", re.I)
WORD = re.compile(r"^[A-Za-z][A-Za-z'/ -]{0,40}$")
PAIR = re.compile(r"^([A-Za-z][A-Za-z' /-]{1,40}?)\s*(?:\((?:n|v|adj|adv|prep|conj|phr)[^)]*\))?\s*:\s*.{2,}$")
DEFINED = re.compile(r"^(n|v|adj|adv|abbr|phr|prep|conj)\.(\s|$)")
LISTS = re.compile(r"Kelime|Önemli|Okuma|essential-business|^\d", re.I)


def broken(strings: list[str]) -> bool:
    words = " ".join(strings).replace("\x03", " ").split()
    bad = [w for w in words if re.search(r"[a-zçğıöşü][A-ZÇĞİÖŞÜ]|[\x00-\x1f]|[\]\[\\^`]", w)]
    return len(words) >= 5 and len(bad) / len(words) > 0.25


def shifted(text: str) -> str:
    """ASCII in these fonts sits 29 places away; other letters are not needed for English words."""
    return "".join(" " if ch == " " else chr(ord(ch) + 29) if 32 <= ord(ch) + 29 <= 122 else "?" for ch in text)


def rows(doc) -> list[list[dict]]:
    fonts: dict[str, list[str]] = {}
    pages = []
    for page in doc:
        spans = [span for block in page.get_text("dict")["blocks"] for line in block.get("lines", []) for span in line["spans"] if span["text"].strip()]
        for span in spans:
            fonts.setdefault(span["font"], []).append(span["text"])
        pages.append(spans)
    bad = {font for font, strings in fonts.items() if broken(strings)}
    out = []
    for spans in pages:
        lines: list[dict] = []
        for span in spans:
            x, y = span["origin"]
            text = shifted(span["text"]) if span["font"] in bad else span["text"]
            line = next((item for item in lines if abs(item["y"] - y) < 2), None)
            if line is None:
                lines.append(line := {"y": y, "parts": []})
            line["parts"].append({"x": x, "end": span["bbox"][2], "text": re.sub(r"\s+", " ", text)})
        for line in sorted(lines, key=lambda item: item["y"]):
            cells: list[dict] = []
            for part in sorted(line["parts"], key=lambda item: item["x"]):
                clean = part["text"].strip()
                apart = TYPE.match(clean) or re.match(r"^\d+\.?$", clean) or (cells and TYPE.match(cells[-1]["text"].strip()))
                if cells and not apart and part["x"] - cells[-1]["end"] < 3:
                    cells[-1]["text"] += part["text"]
                    cells[-1]["end"] = part["end"]
                else:
                    cells.append(dict(part))
            for cell in cells:
                cell["text"] = cell["text"].strip()
            out.append([cell for cell in cells if cell["text"] and not re.match(r"^\d+\.?$", cell["text"])])
    return out


def words_of(path: Path) -> set[str]:
    found: set[str] = set()
    columns: list[float] = []
    near = lambda x: any(abs(column - x) < 4 for column in columns)

    def add(word: str) -> None:
        word = re.sub(r"^\d+\.?\s+", "", word).strip(" .,")
        if WORD.match(word) and not HEAD.match(word) and len(word.split()) <= 4 and len(word) > 1:
            found.add(word)

    for cells in rows(fitz.open(path)):
        if not cells:
            continue
        if any(TYPE.match(cell["text"]) for cell in cells):
            row: list[dict] = []
            for cell in cells:
                if not TYPE.match(cell["text"]):
                    row.append(cell)
                    continue
                if len(row) >= 2:
                    if not near(row[1]["x"]):
                        columns.append(row[1]["x"])
                    add(row[0]["text"])
                row = []
            continue
        if len(cells) > 1 and DEFINED.match(cells[1]["text"]):
            add(cells[0]["text"])
            continue
        groups: list[list[dict]] = []
        for index, cell in enumerate(cells):
            if index and cell["x"] - cells[index - 1]["end"] <= 20:
                groups[-1].append(cell)
            else:
                groups.append([cell])
        matched = False
        for group in groups:
            pair = PAIR.match(re.sub(r"\s+", " ", " ".join(cell["text"] for cell in group)))
            if pair:
                add(pair.group(1))
                matched = True
        if not matched:
            for before, cell in zip(cells, cells[1:]):
                if near(cell["x"]) and cell["x"] - before["x"] < 120:
                    add(before["text"])
    return found


def known_meanings() -> dict[str, str]:
    """What the site already knows, so only the rest goes to machine translation."""
    meanings: dict[str, str] = {}
    for path in sorted((HERE.parent / "novel").glob("dict_*.json")):
        meanings.update({k.lower(): v for k, v in json.loads(path.read_text(encoding="utf-8")).items() if k != "_comment"})
    for line in (HERE.parent / "novel" / "phrasal_lexicon.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            phrase, turkish = (part.strip() for part in line.split("|", 1))
            meanings[phrase.rstrip("*").lower()] = turkish.replace(";", ",")
    return meanings


def translate(lines: list[str]) -> list[str] | None:
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=tr&dt=t&q=" + urllib.parse.quote("\n".join(lines))
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    parts = "".join(part[0] or "" for part in data[0]).split("\n")
    return [part.strip() for part in parts] if len(parts) == len(lines) else None


def main() -> None:
    words: dict[str, str] = {}
    for path in sorted((ROOT / "Language").rglob("*.pdf")):
        if " (1)" in path.name or "Soru Tipi" in path.name or "Deneme" in path.name or not LISTS.search(path.name):
            continue
        found = words_of(path)
        print(f"{len(found):6} {path.name}")
        for word in found:
            words.setdefault(word.lower(), word.lower())
    print("different words:", len(words))

    known = known_meanings()
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    missing = sorted(word for word in words if word not in known and word not in cache)
    print("known:", len(words) - len(missing), "to translate:", len(missing))
    index = 0
    while index < len(missing):
        chunk: list[str] = []
        size = 0
        while index + len(chunk) < len(missing) and len(chunk) < 80 and size + len(missing[index + len(chunk)]) < 1400:
            size += len(missing[index + len(chunk)]) + 1
            chunk.append(missing[index + len(chunk)])
        try:
            result = translate(chunk)
        except Exception as err:  # the service refused: keep what is done, run again later
            print("stopped:", err)
            break
        if result:
            cache.update({english: turkish for english, turkish in zip(chunk, result) if turkish})
        index += len(chunk)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
        print(f"\r{index}/{len(missing)}", end="", flush=True)
        time.sleep(0.4)
    print()
    lines = ["# English words of exam study lists; Turkish from this site's dictionaries and machine translation.", "# word | Turkish meaning"]
    kept = 0
    for word in sorted(words):
        turkish = known.get(word) or cache.get(word)
        # A "translation" equal to the word means the service did not know it.
        if turkish and turkish.lower() != word:
            lines.append(f"{word} | {turkish}")
            kept += 1
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("written:", kept)


if __name__ == "__main__":
    sys.exit(main())
