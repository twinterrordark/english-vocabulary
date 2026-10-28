#!/usr/bin/env python3
"""Give a scanned novel PDF a text layer so the reader can show and translate it.

Scanned books (page photos, no text) look empty in the reader. This script reads
each page with the Windows built-in OCR (tools/novel/ocr_windows.ps1, English),
keeps only the story text and writes it into the PDF as invisible text over the
page images. The reader then finds paragraphs, chapters and words as usual.

Left out: running headers and page numbers, picture captions and side notes
(small print), and words printed on gray boxes (glossary bubbles). Chapter
openings ("CHAPTER" + a big title) become "Chapter N" and the title; "PART"
pages become "PART ONE", "PART TWO"... A missing drop cap ("NCE UPON" ->
"ONCE UPON") and common OCR slips ("che" -> "the") are fixed with the dictionary.

  python tools/novel/ocr_scanned.py novels/novel_3.pdf [--last 256]

--last: the last PDF page (1-based) of the story; later pages (biography,
notes) get no text, so the reader ends there. Needs PyMuPDF, Pillow, nltk +
wordnet and Windows 10/11 with the English OCR language.
"""
import argparse
import json
import re
import statistics
import subprocess
import tempfile
from pathlib import Path

import fitz
from nltk.corpus import wordnet as wn
from PIL import Image

HERE = Path(__file__).resolve().parent
DPI = 200
NUMBERS = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN"]
# OCR slips that a one-letter change does not explain.
FIXES = {"cm": "can", "Offa": "Off a", "Neu": "New", "[he": "the", "rhe": "the", "hc": "he", "ts": "is", "thc": "the", "ro": "to",
         "dol": "del", "[ime": "time", "[hst": "fast", r"\X/ho": "Who", "()ne": "one", "wæs": "was", "sa_id": "said", "ges": "eyes", "gare": "gate"}
# Common words WordNet does not list, so they are never "corrected".
SMALL = set("a an the and or but if of to in on at by for from with as is am are was were be been being it its he him his she her hers "
            "they them their we us our you your i me my mine who whom whose which what that this these those there here not no nor "
            "so than then too very can could shall should will would may might must do does did has have had into onto upon "
            "about above after against along among around before behind below beneath beside between beyond during except "
            "inside near off out over since through till toward towards under until unless up via within without yet "
            "whether while whilst although though because whereas whoever whatever whichever thee thou thy thine ye la de del".split())
# Words the OCR runs together: "ifyou" -> "if you".
GLUED = ("of", "if", "and", "himself", "wishes", "will", "a")
# Letters the OCR confuses, tried when a word is not English.
SWAPS = [("c", "t"), ("t", "c"), ("l", "i"), ("i", "l"), ("rn", "m"), ("m", "rn"), ("m", "n"), ("ii", "u"), ("cl", "d"), ("o", "e"), ("e", "o"),
         ("c", "e"), ("u", "w"), ("v", "y"), ("vv", "w"), ("z", "r"), ("fill", "ful"), ("fr", "fy"), ("fb", "fo"), ("ff", "ffi"), ("fl", "fi"),
         ("1", "l"), ("0", "o")]


def load_words() -> set:
    words = set()
    for path in HERE.glob("dict_*.json"):
        words.update(json.loads(path.read_text(encoding="utf-8")))
    words.update(json.loads((HERE / "forms.json").read_text(encoding="utf-8")))
    return words


WORDS = load_words()


def known(word: str) -> bool:
    w = word.lower()
    return w in WORDS or w in SMALL or any(wn.morphy(w, pos) for pos in ("n", "v", "a", "r"))


def fix_word(token: str) -> str:
    if token.strip(",.;:!?\"'") in FIXES:
        bare = token.strip(",.;:!?\"'")
        return token.replace(bare, FIXES[bare])
    match = re.fullmatch(r"([\"'“‘(]*)([A-Za-z\[]+)([^A-Za-z]*)", token)
    if not match:
        return token
    lead, word, tail = match.groups()
    if word in FIXES:
        return lead + FIXES[word] + tail
    if known(word) or word[0].isupper():
        return token
    for prefix in GLUED:
        rest = word[len(prefix):]
        if word.startswith(prefix) and rest and (known(rest) or rest[0].isupper()):
            return lead + prefix + " " + rest + tail
    for wrong, right in SWAPS:
        for at in [m.start() for m in re.finditer(wrong, word)]:
            guess = word[:at] + right + word[at + len(wrong):]
            if known(guess):
                return lead + guess + tail
    return token


def run_ocr(pdf: fitz.Document, pages: list, work: Path) -> None:
    for index in pages:
        if not (work / f"{index:03d}.json").exists():
            pdf[index].get_pixmap(dpi=DPI, colorspace=fitz.csGRAY).save(work / f"{index:03d}.png")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HERE / "ocr_windows.ps1"), "-Dir", str(work)], check=True)


def on_gray(image: Image.Image, word: dict) -> bool:
    """Words in gray side-note boxes: the paper around the letters is not white."""
    box = image.crop((word["x"], word["y"], word["x"] + word["w"], word["y"] + word["h"]))
    values = sorted(box.getdata())
    return values[int(len(values) * 0.9)] < 215 if values else False


def page_lines(image: Image.Image, data: dict) -> list:
    lines = []
    for words in data["lines"]:
        kept = [w for w in words if not on_gray(image, w)]
        if kept:
            lines.append({"x": kept[0]["x"], "y": min(w["y"] for w in kept), "end": kept[-1]["x"] + kept[-1]["w"],
                          "h": max(w["h"] for w in kept), "text": " ".join(w["t"] for w in kept)})
    return lines


def story_lines(lines: list, counters: dict, body_h: float) -> list:
    """[(text, starts_paragraph)] for one page. body_h: the book's usual line height."""
    if not lines:
        return []
    big = [line for line in lines if line["h"] > body_h * 1.4]
    # Part pages: a few big lines alone ("PART ONE", or the book title before part two).
    if big and len(lines) <= 4 and (counters["part"] or any(re.match(r"PART\b", line["text"]) for line in lines)):
        counters["part"] += 1
        return [("PART " + NUMBERS[counters["part"] - 1], True)]
    out = []
    # Chapter openings: a title of two or more big lines over the first text.
    if len(big) >= 2 and len(lines) > 4 and counters["part"]:
        counters["chapter"] += 1
        out.append((f"Chapter {counters['chapter']}", True))
        title = re.sub(r"(\w)- (\w)", r"\g<1>-\g<2>", " ".join(line["text"] for line in big))
        out.append((re.sub(r" 's\b", "'s", " ".join(fix_word(token) for token in title.split())), True))
        lines = [line for line in lines if line["y"] > big[-1]["y"] and line not in big]
        if lines:
            first, _, rest = lines[0]["text"].partition(" ")
            word = first.strip(",.;:")
            if word.isupper() and not known(word):  # missing drop cap
                letter = next((c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if known(c + word)), "")
                lines[0] = dict(lines[0], text=(letter + first + " " + rest).strip())
    # Body text only: headers, page numbers, captions and notes are smaller print.
    body = [line for line in lines if body_h * 0.69 <= line["h"] <= body_h * 1.5 and not re.fullmatch(r"[\d\s]+", line["text"])]
    if not body:
        return out
    left = statistics.mode([round(line["x"] / 10) * 10 for line in body])
    right = max(line["end"] for line in body)
    previous = None
    for line in body:
        tokens = line["text"].split()
        # Halves of a word broken at a line end ("con-" / "cern") are left as printed.
        broken = previous is not None and previous["text"].endswith("-")
        text = " ".join(token if (i == 0 and broken) or token.endswith("-") else fix_word(token) for i, token in enumerate(tokens))
        indent = line["x"] - left
        if previous is None:
            starts = 70 < indent < 140
        else:
            ended = re.search(r"[.!?:\"'”’)]$", previous["text"])
            starts = bool(ended) and (previous["end"] < right - 60 or 70 < indent < 140)
        out.append((re.sub(r"(\w) '(s|ll|re|ve|d|t)\b", r"\g<1>'\g<2>", text), starts))
        previous = line
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--last", type=int, help="last PDF page (1-based) of the story")
    parser.add_argument("--work", type=Path, help="folder for page images and OCR results (kept between runs)")
    args = parser.parse_args()
    pdf = fitz.open(args.pdf)
    last = args.last or len(pdf)
    pages = [i for i in range(last) if len(pdf[i].get_text().strip()) < 20]
    work = args.work or Path(tempfile.mkdtemp(prefix="ocr_"))
    work.mkdir(parents=True, exist_ok=True)
    run_ocr(pdf, pages, work)
    counters = {"part": 0, "chapter": 0}
    font = fitz.Font("helv")
    read = {}
    for index in pages:
        data = json.loads((work / f"{index:03d}.json").read_text(encoding="utf-8-sig"))
        read[index] = page_lines(Image.open(work / f"{index:03d}.png").convert("L"), data)
    body_h = statistics.median([line["h"] for lines in read.values() for line in lines])
    for index in pages:
        page = pdf[index]
        writer = fitz.TextWriter(page.rect)
        y = 60
        for text, starts in story_lines(read[index], counters, body_h):
            # Paragraph starts are indented; the reader splits paragraphs on that.
            writer.append((54 + (24 if starts else 0), y), text, font=font, fontsize=9)
            y += 13
        writer.write_text(page, render_mode=3)
    # Pages after the story (biography, back cover) keep their pictures but no text.
    for index in range(last, len(pdf)):
        pdf[index].add_redact_annot(pdf[index].rect)
        pdf[index].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    out = args.pdf.with_suffix(".ocr.pdf")
    pdf.save(out, garbage=3, deflate=True)
    pdf.close()
    out.replace(args.pdf)
    print(f"{args.pdf.name}: text added to {len(pages)} pages, {counters['part']} parts, {counters['chapter']} chapters")


if __name__ == "__main__":
    main()
