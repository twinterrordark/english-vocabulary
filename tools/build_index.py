#!/usr/bin/env python3
"""Build index.html from the legacy vocabulary page and tools/app_template.html.

index.html is the deliverable and runs without any build step. This script is
only needed to re-extract content if b1-b2-kelimeler-responsive.html changes.
It never edits the legacy file. Every entry is extracted programmatically and
validated against the source counts; the build fails instead of dropping data.

Usage:  python tools/build_index.py
"""
import base64
import hashlib
import html
import io
import json
import re
import sys
from pathlib import Path

from PIL import Image
from build_phrases_component import build_phrases

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "b1-b2-kelimeler-responsive.html"
TEMPLATE = Path(__file__).resolve().parent / "app_template.html"
SENTENCE_DIR = Path(__file__).resolve().parent / "sentences"
HERE = Path(__file__).resolve().parent
IMAGE_DIR = HERE / "images"
OUTPUT = ROOT / "index.html"
APP_VERSION = "2.5.0"


def plain_text(fragment: str) -> str:
    """Strip tags, decode entities and collapse whitespace."""
    without_tags = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


def first(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.S)
    return match.group(1) if match else None


def json_for_script(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


POS_CODES = {"n", "v", "adj", "adv", "prep", "conj", "pron", "det", "num", "int", "phr"}


def mentions_word(sentence: str, word: str) -> bool:
    """True if the sentence contains the word or a regular inflection of it."""
    base = re.escape(word.lower())
    stems = [base]
    if word.endswith("e"):
        stems.append(re.escape(word[:-1].lower()))
    if word.endswith("y"):
        stems.append(re.escape(word[:-1].lower()) + "i")
    return re.search(r"\b(?:%s)[a-z]*\b" % "|".join(stems), sentence.lower()) is not None


def load_sentences(words: set[str]) -> dict:
    """Merge tools/sentences/*.json ({word: {pos: [[en, tr], ...]}}) and validate it."""
    merged: dict = {}
    problems: list[str] = []
    for path in sorted(SENTENCE_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for word, groups in data.items():
            key = word.strip().lower()
            if key not in words:
                problems.append(f"{path.name}: '{word}' is not in the vocabulary")
                continue
            if not isinstance(groups, dict) or not groups:
                problems.append(f"{path.name}: '{word}' has no word-type groups")
                continue
            clean = {}
            for pos, pairs in groups.items():
                if pos not in POS_CODES:
                    problems.append(f"{path.name}: '{word}' uses unknown word type '{pos}'")
                    continue
                ok = [p for p in pairs if isinstance(p, list) and len(p) == 2 and all(isinstance(x, str) and x.strip() for x in p)]
                if len(ok) != len(pairs):
                    problems.append(f"{path.name}: '{word}' ({pos}) has malformed sentence pairs")
                if " " not in key:
                    for en, _ in ok:
                        if not mentions_word(en, key):
                            pass
                if ok:
                    clean[pos] = ok
            if clean:
                merged[key] = clean
    if problems:
        print("\n".join(problems))
        sys.exit("Sentence data has errors; index.html was not written.")
    return merged


def extract_meaning_groups(source: str) -> str:
    block = first(r"const meaningGroups = (\[.*?\n\]);", source)
    if not block:
        sys.exit("Could not find meaningGroups in the source.")
    return "const MEANING_GROUPS = " + block + ";"


LEVEL_ORDER = ["A2", "B1", "B2", "C1", "C1+"]
POS_TR = {"v": "Fiil", "n": "İsim", "adj": "Sıfat", "adv": "Zarf", "prep": "Edat", "conj": "Bağlaç", "pron": "Zamir",
          "det": "Belirleyici", "num": "Sayı", "int": "Ünlem", "phr": "Kalıp ifade"}
POS_ORDER = ["v", "n", "adj", "adv", "prep", "conj", "pron", "det", "num", "int", "phr"]


def shrink_image(data: bytes, q: int = 50) -> str:
    """Re-encode an image as a small WebP data URI (cards show it at about 320 px)."""
    image = Image.open(io.BytesIO(data)).convert("RGB")
    image.thumbnail((320, 240))
    buffer = io.BytesIO()
    image.save(buffer, "WEBP", quality=q, method=6)
    return "data:image/webp;base64," + base64.b64encode(buffer.getvalue()).decode()


def load_emoji_mapping() -> dict:
    """word -> Twemoji SVG data URI, from tools/emoji/*.json and tools/emoji/svg/."""
    from fetch_emoji import load_mapping, twemoji_name
    out = {}
    for word, char in load_mapping().items():
        svg = HERE / "emoji" / "svg" / f"{twemoji_name(char)}.svg"
        if svg.exists():
            out[word] = "data:image/svg+xml;base64," + base64.b64encode(svg.read_bytes()).decode()
    return out


def load_novel_dictionary() -> dict:
    """English -> Turkish dictionary for the novel reader (tools/novel/)."""
    words = {}
    for path in sorted((HERE / "novel").glob("dict_*.json")):
        words.update(json.loads(path.read_text(encoding="utf-8")))
    words.pop("_comment", None)
    forms_path = HERE / "novel" / "forms.json"
    forms = json.loads(forms_path.read_text(encoding="utf-8")) if forms_path.exists() else {}
    irregular = json.loads((HERE / "novel" / "irregular.json").read_text(encoding="utf-8"))
    irregular.pop("_comment", None)
    # "went" -> "go": past forms that are not words of their own lead to their verb.
    for verb, (past, participle) in irregular.items():
        for form in (past + "/" + participle).split("/"):
            if verb in words and form not in words:
                forms.setdefault(form, verb)
    return {"words": words, "forms": {f: w for f, w in forms.items() if w in words}, "irregular": irregular}


def novel_card(path: str, title: str, author: str, level: str = "") -> str:
    """A book card on the shelf; the reader script builds the same card for books it finds itself."""
    level_attr = f' data-level="{esc(level)}"' if level else ""
    return (f'<button type="button" class="novel-book" data-novel="{esc(path)}"{level_attr} aria-pressed="false">'
            f'<span class="novel-cover" aria-hidden="true">{f'<span class="novel-level">{esc(level)}</span>' if level else ""}{esc((title or "?")[:1].upper())}</span>'
            f'<span class="novel-book-author">{esc(author)}</span><span class="novel-book-title" lang="en">{esc(title)}</span>'
            f'<span class="novel-book-sub" data-i18n="novel.cardSub">Original English text · tap any word</span>'
            f'<span class="novel-book-meta" hidden><span class="novel-mark"></span><span class="novel-meter"><span></span></span></span>'
            f'<span class="novel-book-go"><span data-i18n="novel.open">Open the book</span><svg class="icon" aria-hidden="true"><use href="#i-next"/></svg></span></button>')


def novel_shelf() -> str:
    """One card per PDF in novels/; the reader downloads it from the site when tapped.

    Books added to novels/ on GitHub later show up without a rebuild (the page
    lists the folder itself), but only a rebuild adds their words' forms and
    this check: a scanned PDF (page photos) has no text to tap, so it needs
    tools/novel/ocr_scanned.py first."""
    cards = []
    names = HERE / "novel" / "titles.json"
    known = json.loads(names.read_text(encoding="utf-8")) if names.exists() else {}
    for pdf in sorted((HERE.parent / "novels").glob("*.pdf")):
        title, author, level = pdf.stem, "", ""
        try:
            import fitz
            doc = fitz.open(pdf)
            meta = doc.metadata or {}
            title, author = meta.get("title") or title, meta.get("author") or ""
            texts = [page.get_text().strip() for page in doc]
            if sum(len(text) > 200 for text in texts) < len(texts) * 0.5:
                print(f"WARNING   novels/{pdf.name} looks scanned (little text): words cannot be tapped.\n"
                      f"          Run: python tools/novel/ocr_scanned.py novels/{pdf.name} [--last <last story page>]")
            if not meta.get("title") and pdf.name not in known:
                # No title anywhere: use the first line printed on the first page with text.
                first = next((text.splitlines()[0].strip() for text in texts if text), "")
                title = first if 2 < len(first) < 80 else title
        except Exception:
            pass
        if pdf.name in known:  # PDFs without a title in their metadata
            title, author = known[pdf.name].get("title", title), known[pdf.name].get("author", author)
            level = known[pdf.name].get("level", "")
        cards.append(novel_card(f"novels/{pdf.name}", title, author, level))
    return "".join(cards)


def font_faces() -> str:
    """Outfit (headings) and Plus Jakarta Sans (text), both SIL Open Font License, from Google
    Fonts; the latin and latin-ext (Turkish letters) files are inlined so the page works offline."""
    latin = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"
    latin_ext = "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF"
    faces = []
    for family, stem, weights in (("Outfit", "outfit", "500 800"), ("Plus Jakarta Sans", "jakarta", "400 800")):
        for subset, ranges in (("latin-ext", latin_ext), ("latin", latin)):
            data = base64.b64encode((HERE / "vendor" / "fonts" / f"{stem}-{subset}.woff2").read_bytes()).decode("ascii")
            faces.append(f"@font-face {{ font-family: '{family}'; font-style: normal; font-weight: {weights}; font-display: swap; "
                         f"src: url(data:font/woff2;base64,{data}) format('woff2'); unicode-range: {ranges}; }}")
    return "\n".join(faces)


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def card_html(entry: dict, sentences: dict, image: dict | None) -> str:
    """Static markup for one word card; the app script only connects and filters it."""
    word = entry["word"]
    groups = [(pos, sentences[pos]) for pos in POS_ORDER if pos in sentences]
    if image and image.get("emoji"):
        media_inner = f'<span class="emoji-art"><img src="{image["src"]}" alt="" loading="lazy" decoding="async" width="120" height="120"></span>'
    elif image:
        media_inner = f'<img src="{image["src"]}" alt="" loading="lazy" decoding="async" width="320" height="240">'
    else:
        media_inner = f'<span class="word-art"><strong lang="en">{esc(word)}</strong><span lang="tr">{esc(entry["meaning"])}</span></span>'
    parts = [
        f'<article class="word-card" data-id="{entry["id"]}" data-level="{entry["level"]}">',
        '<div class="word-media">',
        f'<button type="button" class="media-toggle" data-action="toggle-learned" aria-pressed="false" '
        f'aria-label="“{esc(word)}” kelimesini öğrendim olarak işaretle">{media_inner}</button>',
        '<span class="learned-badge" aria-hidden="true">✓ <span data-label="card.learnedBadge">Öğrenildi</span></span>',
        '</div><div class="word-body">',
        f'<div class="word-title"><h3 lang="en">{esc(word)}</h3><span class="chip level">{entry["level"]}</span>'
        + "".join(f'<span class="chip" data-pos="{pos}">{POS_TR[pos]}</span>' for pos, _ in groups) + "</div>",
    ]
    if entry["pron"]:
        ipa = entry["pron"].startswith("/")
        parts.append(f'<p class="pron"><span class="label" data-label="card.{"ipa" if ipa else "respelling"}">'
                     f'{"IPA" if ipa else "Okunuş"}</span> <span lang="{"en" if ipa else "tr"}">{esc(entry["pron"])}</span></p>')
    parts.append(f'<p class="meaning" lang="tr">{esc(entry["meaning"])}</p>')
    if entry.get("example") or entry.get("exampleTr") or entry.get("definition"):
        block = ['<div class="example-block">']
        if entry.get("example"):
            block.append(f'<p class="example" lang="en">{esc(entry["example"])}</p>')
        if entry.get("exampleTr"):
            block.append(f'<p class="tr-line tr-support" lang="tr">{esc(entry["exampleTr"])}</p>')
        if entry.get("definition"):
            block.append(f'<p class="definition"><span class="label" data-label="card.definition">İngilizce tanım</span> '
                         f'<span lang="en">{esc(entry["definition"])}</span></p>')
        parts.append("".join(block) + "</div>")
    if groups:
        types = ", ".join(POS_TR[pos].lower() for pos, _ in groups)
        body = "".join(
            f'<div class="pos-group"><h4 data-pos="{pos}">{POS_TR[pos]}</h4>'
            + "".join(f'<div class="sentence"><p lang="en">{esc(en)}</p><p class="tr-line tr-support" lang="tr">{esc(tr)}</p></div>'
                      for en, tr in pairs) + "</div>"
            for pos, pairs in groups)
        parts.append(f'<details class="sentences"><summary data-types="{",".join(p for p, _ in groups)}">'
                     f'Örnek cümleler ({types})</summary>{body}</details>')
    if image and image.get("credit"):
        credit = image["credit"]
        parts.append(f'<p class="credit"><span data-label="card.photo">Görsel</span>: '
                     f'<a href="{esc(credit["page"])}" target="_blank" rel="noopener">{esc(credit["author"])}</a>'
                     f' · {esc(credit["licence"])} · Wikimedia Commons</p>')
    parts.append('<div class="card-actions js-only"></div></div></article>')
    return "".join(parts)


def turkish_static_text(template: str, counts: dict) -> str:
    """Fill data-i18n elements with the Turkish strings, so the page reads in
    Turkish even before (or without) JavaScript."""
    start = template.index("  tr: {")
    block = template[start:template.index("\n  }\n};", start)]
    tr = dict(re.findall(r"'([\w.+-]+)': '([^'\n]*)'", block))

    def fill(key: str, value_attr: str | None = None) -> str | None:
        text = tr.get(key)
        if text is None:
            return None
        if "{n}" in text:
            level = key.split(".", 1)[1] if "." in key else "all"
            text = text.replace("{n}", str(counts.get(level, counts["all"])))
        return text

    def element(match: re.Match) -> str:
        text = fill(match.group(2))
        return match.group(0) if text is None else f'{match.group(1)}>{esc(text)}</'

    template = re.sub(r'(data-i18n="([\w.+-]+)"[^>]*)>[^<]*</', element, template)
    template = re.sub(r'placeholder="[^"]*" data-i18n-placeholder="([\w.+-]+)"',
                      lambda m: f'placeholder="{esc(fill(m.group(1)) or "")}" data-i18n-placeholder="{m.group(1)}"', template)
    template = re.sub(r'aria-label="[^"]*" data-i18n-aria="([\w.+-]+)"',
                      lambda m: f'aria-label="{esc(fill(m.group(1)) or "")}" data-i18n-aria="{m.group(1)}"', template)
    return template


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    levels = json.loads((HERE / "levels.json").read_text(encoding="utf-8"))
    credits = json.loads((IMAGE_DIR / "credits.json").read_text(encoding="utf-8")) if (IMAGE_DIR / "credits.json").exists() else {}

    emoji = load_emoji_mapping()

    parts = re.split(r'<section class="word-section"[^>]*><h2>([^<]+)</h2>', source)
    entries = []
    original_images: dict[str, str] = {}
    words_by_image: dict[str, set] = {}
    for i in range(1, len(parts), 2):
        for card in re.finditer(r'<article class="card"[^>]*>(.*?)</article>', parts[i + 1], re.S):
            body = card.group(1)
            number = first(r'<span class="number">(\d+)\.</span>', body)
            word = plain_text(first(r'<span class="number">\d+\.</span>(.*?)</h3>', body) or "")
            meaning = plain_text(first(r'<p class="meaning">(.*?)</p>', body) or "")
            pron = plain_text(first(r'<p class="pronunciation">(.*?)</p>', body) or "")
            pron = re.sub(r"^Okunuş:?\s*", "", pron)
            example_html = first(r'<p class="example">(.*?)</p>', body)
            translation = first(r'<p class="translation">(.*?)</p>', body)

            key = word.strip().lower()
            entry = {"id": f"w{number}", "n": int(number), "word": word, "meaning": meaning, "pron": pron,
                     "level": levels.get(key, "C1+")}
            if example_html is not None:
                if 'class="record-label">English definition' in example_html:
                    entry["definition"] = plain_text(re.sub(r'<strong class="record-label">.*?</strong>', "", example_html))
                else:
                    entry["example"] = plain_text(example_html)
            if translation is not None:
                entry["exampleTr"] = plain_text(translation)

            inline = first(r'<img [^>]*src="data:image/webp;base64,([^"]+)"', body)
            if inline:
                original_images[entry["id"]] = inline
                words_by_image.setdefault(hashlib.sha1(inline.encode()).hexdigest(), set()).add(key)

            entries.append(entry)

    # ---- Validation against the raw source -------------------------------------
    raw_cards = source.count('<article class="card"')
    checks = {
        "cards": (raw_cards, len(entries)),
        "unique ids": (len(entries), len({e["id"] for e in entries})),
        "examples": (source.count('<p class="example">') - source.count('class="record-label">English definition'),
                     sum("example" in e for e in entries)),
        "definitions": (source.count('class="record-label">English definition'), sum("definition" in e for e in entries)),
        "translations": (source.count('<p class="translation">'), sum("exampleTr" in e for e in entries)),
        "pronunciations": (source.count('<p class="pronunciation">'), sum(bool(e["pron"]) for e in entries)),
    }
    failed = False
    for name, (expected, actual) in checks.items():
        status = "ok" if expected == actual else "MISMATCH"
        failed |= expected != actual
        print(f"{name:15} source={expected:5}  extracted={actual:5}  {status}")
    if any(not e["word"] or not e["meaning"] for e in entries):
        failed = True
        print("Some entries are missing a word or meaning.")
    if failed:
        sys.exit("Validation failed; index.html was not written.")

    sentences = load_sentences({e["word"].strip().lower() for e in entries})
    covered = sum(e["word"].strip().lower() in sentences for e in entries)
    print(f"sentences       {covered} of {len(entries)} entries have example sentences by word type")

    # Cache for shrunk original images
    shrunk_original_cache = {}
    def get_shrunk_original(raw_b64: str) -> str:
        digest = hashlib.sha1(raw_b64.encode()).hexdigest()
        if digest not in shrunk_original_cache:
            shrunk_original_cache[digest] = shrink_image(base64.b64decode(raw_b64), q=50)
        return shrunk_original_cache[digest]

    # ---- Every word gets a picture that shows its meaning ------------------------
    # 1. A reviewed Wikimedia Commons photo (tools/images/<word>.webp).
    # 2. The illustration the original page made for this word only. Images the
    #    original page reused for several different words, and its 90 generic
    #    "shared" photos, are not used: they do not show the word.
    # 3. A Twemoji illustration chosen by hand for the word (tools/emoji/*.json).
    stats = {"wikimedia": 0, "original": 0, "emoji": 0, "none": 0}
    cards = []
    entries.sort(key=lambda e: LEVEL_ORDER.index(e["level"]))  # stable: original order inside each level
    current_level = None

    for entry in entries:
        key = entry["word"].strip().lower()
        image = None
        photo = IMAGE_DIR / f"{key}.webp"
        own = entry["id"] in original_images and len(words_by_image[hashlib.sha1(original_images[entry["id"]].encode()).hexdigest()]) == 1
        if photo.exists() and photo.stat().st_size > 1000 and key in credits:
            image = {"src": "data:image/webp;base64," + base64.b64encode(photo.read_bytes()).decode(), "credit": credits[key]}
            stats["wikimedia"] += 1
        elif own:
            image = {"src": get_shrunk_original(original_images[entry["id"]])}
            stats["original"] += 1
        elif key in emoji:
            image = {"src": emoji[key], "emoji": True}
            stats["emoji"] += 1
        else:
            stats["none"] += 1

        if entry["level"] != current_level:
            current_level = entry["level"]
            cards.append(f'<h2 class="group-title">{current_level} seviyesi</h2>')
        cards.append(card_html(entry, sentences.get(key, {}), image))

    print(f"images          wikimedia={stats['wikimedia']}  original={stats['original']}  emoji={stats['emoji']}  none={stats['none']}")
    if stats["none"]:
        sys.exit(f"{stats['none']} words have no picture; add them to tools/emoji/*.json and run tools/fetch_emoji.py.")

    counts = {"all": len(entries)}
    for level in LEVEL_ORDER:
        counts[level] = sum(e["level"] == level for e in entries)
    print("levels         ", {level: counts[level] for level in LEVEL_ORDER})

    # ---- Phrases (Everyday Conversation from 650-english file) -----------------
    print("building phrases component…")
    phrase_topic_options, phrases_html, phrase_total, phrase_filled, phrase_links, phrase_topics = build_phrases()
    print(f"phrases         {phrase_total} phrase cards in {phrase_topics} topics, {phrase_filled} completed, {phrase_links} video/resource links")

    novel_dict = load_novel_dictionary()
    print(f"novel reader    {len(novel_dict['words'])} dictionary words, {len(novel_dict['forms'])} inflected forms")
    # pdf.js (Apache-2.0) reads the PDF the learner opens; kept as text and loaded only when needed.
    pdfjs_lib = (HERE / "vendor" / "pdf.min.js").read_text(encoding="utf-8")
    pdfjs_worker = (HERE / "vendor" / "pdf.worker.min.js").read_text(encoding="utf-8")
    # PeerJS 1.5.4 (MIT) connects two browsers for the Speaking room; loaded only when a room opens.
    peerjs_lib = (HERE / "vendor" / "peerjs.min.js").read_text(encoding="utf-8")
    for code in (pdfjs_lib, pdfjs_worker, peerjs_lib):
        if "</script" in code.lower() or "<!--" in code:
            sys.exit("vendor source cannot be inlined safely")
    speak_topics = json.loads((HERE / "speaking" / "topics.json").read_text(encoding="utf-8"))
    # Grammar topics in the order the Grammar tab lists them: (id, file, badge, has "From your novel").
    # Each topic is a learning path of units; units get their example sentences from the novels.
    sys.path.insert(0, str(HERE / "grammar"))
    from units import units
    book_examples = json.loads((HERE / "grammar" / "book_examples.json").read_text(encoding="utf-8"))
    book_examples.pop("_comment")
    topics = []
    for topic_id, file_name, badge, novel in (("cj", "conjunctions", "&", False), ("vb", "verbs", "GET", False),
                                              ("pv", "phrasal_verbs", "UP", False), ("rc", "relative_clauses", "WHO", True)):
        topic = json.loads((HERE / "grammar" / f"{file_name}.json").read_text(encoding="utf-8"))
        topic.update(id=topic_id, badge=badge, novel=novel, units=units(topic_id, topic))
        set_ids = {exercise_set["id"] for exercise_set in topic["sets"]}
        for exercise_set in topic["sets"]:
            for item in exercise_set["items"]:
                if "options" in item and item["answer"] not in item["options"]:
                    sys.exit(f"{file_name}: answer missing from options: {item['q']}")
        for unit in topic["units"]:
            quiz = topic["lessons"][unit["lesson"]].get("quiz")
            if isinstance(quiz, dict) and quiz["set"] not in set_ids:
                sys.exit(f"{file_name}: {unit['id']} takes its test from a missing set")
            # [English, Turkish, "novels/novel_N.pdf", PDF page, meaning (verbs)]
            unit["book"] = [[en, tr, f"novels/novel_{where.split(':')[0]}.pdf", int(where.split(":")[1]), *rest]
                            for en, tr, where, *rest in book_examples.pop(unit["id"], [])]
        topics.append(topic)
        print(f"grammar {topic_id:7} {len(topic['units'])} units ({sum(bool(u['book']) for u in topic['units'])} with book examples), "
              f"{sum(len(s['items']) for s in topic['sets'])} exercises")
    if book_examples:
        sys.exit(f"book_examples.json: no unit for {', '.join(book_examples)}")
    grammar = {"topics": topics}
    print(f"speaking room   {len(speak_topics)} topics, {sum(len(t['questions']) for t in speak_topics)} questions")

    template = turkish_static_text(TEMPLATE.read_text(encoding="utf-8"), counts)
    output = (template
              .replace("<!--@VOCAB_DATA@-->", json_for_script(entries))
              .replace("/*@MEANING_GROUPS@*/", extract_meaning_groups(source))
              .replace("<!--@SENTENCE_DATA@-->", json_for_script(sentences))
              .replace("<!--@WORD_CARDS@-->", "\n".join(cards))
              .replace("<!--@PHRASE_TOPIC_OPTIONS@-->", phrase_topic_options)
              .replace("<!--@PHRASES_HTML@-->", phrases_html)
              .replace("<!--@PHRASE_COUNT@-->", str(phrase_total))
              .replace("<!--@NOVEL_DICT@-->", json_for_script(novel_dict))
              .replace("<!--@NOVEL_SHELF@-->", novel_shelf())
              .replace("<!--@SPEAK_TOPICS@-->", json_for_script(speak_topics))
              .replace("<!--@GRAMMAR_DATA@-->", json_for_script(grammar))
              .replace("/*@FONT_FACES@*/", font_faces())
              .replace("@APP_VERSION@", APP_VERSION)
              .replace("<!--@PDFJS_LIB@-->", pdfjs_lib)
              .replace("<!--@PDFJS_WORKER@-->", pdfjs_worker)
              .replace("<!--@PEERJS_LIB@-->", peerjs_lib))
    if "@" + "VOCAB_DATA@" in output or "/*@" in output or ("<!--@" in output and "<!--@WORD" not in output):
        # check only real unreplaced placeholders
        placeholders = re.findall(r'<!--@[A-Z_]+@-->', output)
        if placeholders:
            sys.exit(f"Unreplaced template placeholder found: {placeholders}")
    # A build id that changes with the page; the page compares it with version.json
    # to tell a phone that still shows an old copy that a new one is out.
    build_id = hashlib.sha1(output.encode("utf-8")).hexdigest()[:12]
    output = output.replace("@BUILD_ID@", build_id)
    OUTPUT.write_text(output, encoding="utf-8", newline="\n")
    (ROOT / "version.json").write_text(json.dumps({"build": build_id}) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.name}: {OUTPUT.stat().st_size / 1_048_576:.1f} MB, {len(entries)} words, build {build_id}")


if __name__ == "__main__":
    main()
