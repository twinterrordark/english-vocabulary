#!/usr/bin/env python3
"""Builds the Phrases tab from 650-english-textwork-mobile-v2.html.

The source was converted from a PDF, so every printed line became a "phrase".
Before rendering, each topic is cleaned:
  * label-only lines ("Video:", "1-", "Additional Resources", ":") are dropped;
  * lines that are the titles of the topic's links become real links in a
    "Videos and resources" block (YouTube links are marked as videos);
  * definitions split over two lines ("Single" + ": alone, …",
    "2:00" + "= It's two o'clock.") are joined back into one card;
  * section titles ("Example Sentences", lines ending with ":") become
    sub-headings instead of empty-looking cards;
  * blanks are filled (blank_replacements.py) and sentence starters such as
    "I like…" get a full example (phrase_examples.py).
"""
import html
import re
from pathlib import Path

from blank_replacements import REPLACEMENTS
from phrase_examples import STARTER_EXAMPLES

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "650-english-textwork-mobile-v2.html"

# Lines that only labelled something in the PDF layout.
LABEL = re.compile(r"^(\d+\s*[-.)]\s*)?((video(\s*lesson)?(/song)?|additional resources|text( (&|with) audio)?)(\s*:\s*3 min\. english)?)?\s*[:\-–“”]*\s*$", re.I)
# Section titles printed as their own line (besides lines ending with ":").
HEADINGS = {
    "example sentences", "examples", "formal greetings", "informal greetings", "formal", "informal", "really informal",
    "introducing yourself", "examples introductions", "some everyday answers", "looking for something",
    "trying clothes on", "paying/price", "extra food", "giving advice", "problem", "i am + verb +ing",
}
# Links that only advertise the original book or a newsletter.
PROMO = re.compile(r"amazon\.com|aweber\.com|englishtonightbooks\.com", re.I)


def esc(s):
    return html.escape(s or "", quote=True)


def clean(s):
    if not s:
        return ""
    t = re.sub(r"<[^>]+>", " ", s)
    t = re.sub(r"\s+", " ", html.unescape(t)).strip()
    return re.sub(r"(\d) (st|nd|rd|th)\b", r"\1\2", t)  # "May 18 th" -> "May 18th"


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def fill_blank(en, tr):
    if en in REPLACEMENTS:
        new_en, new_tr = REPLACEMENTS[en]
        # The replacement may complete only the last sentence of a longer line; keep the rest.
        i, j = en.find(new_en[:15]), tr.find(new_tr[:12])
        if i > 0 and j > 0:
            return en[:i] + new_en, tr[:j] + new_tr
        return new_en, new_tr
    if "34,999" in en and "How many" in en:
        return ("When talking about numbers or amounts: 'How many books do you have?'",
                "Sayılardan veya miktarlardan bahsederken: 'Kaç tane kitabın var?'")
    return en, tr


def parse_answers(p_html):
    answers = []
    for cls, a_html in re.findall(r'<div class="answer-example\s*([^"]*)">(.*?)</div>\s*</div>', p_html, re.S):
        en = re.search(r'<div class="answer-en"[^>]*>(.*?)</div>', a_html, re.S)
        tr = re.search(r'<div class="answer-tr"[^>]*>(.*?)</div>', a_html, re.S)
        if en and clean(en.group(1)):
            kind = "negative" if "negative" in cls else ("neutral" if "neutral" in cls else "positive")
            answers.append((kind, clean(en.group(1)), clean(tr.group(1)) if tr else ""))
    return answers


HEADINGS = {re.sub(r"[^a-z0-9]+", " ", h).strip() for h in HEADINGS}
# Typos in the source text; an empty value drops a stray line.
FIXES = {"I’m tried.": "I’m tired.", "to help practice present continuous.": ""}


def is_fragment(en):
    """A line that continues the previous one (definition, explanation, '= Say:' answer)."""
    return bool(re.match(r"^([:=(,.”\"]|- ([a-z]|Say)|Expresses:)", en))


def is_definition(term, en):
    """'Rent:' followed by 'you pay a monthly fee…' is a term and its meaning, not a section title."""
    if norm(term) in HEADINGS or re.match(r"(?i)(examples?|questions?)", term):
        return False
    return len(term.split()) <= 3 and (en[:1].islower() or (
        len(en) > 25 and "?" not in en and "__" not in en and (not en.endswith(".") or len(en) > 60)))


def is_title(en):
    """'Most Common Verbs Used to Talk about the Past': a section title printed without a colon."""
    words = re.findall(r"[A-Za-z’']+", en)
    if len(words) < 3 or "," in en or re.search(r"[.?!…,;)\d]$", en):
        return False
    big = [w for w in words if w.lower() not in {"a", "an", "the", "to", "of", "for", "about", "and", "or", "in", "at", "on", "you", "can"}]
    return sum(w[0].isupper() for w in big) >= 0.75 * len(big)


def join(prev, cur):
    sep = "" if re.match(r"^[:,]", cur) else " "
    return (prev.rstrip() + sep + cur.lstrip()).strip()


# Terms the PDF printed at the end of the previous line ("…in the same building Condo:").
TRAILING_TERMS = {
    "Break up": "Ayrılmak", "Example Sentences": "Örnek Cümleler", "Months": "Aylar", "Date": "Tarih",
    "For example": "Örneğin", "Condo": "Kondominyum", "Duplex": "Dubleks", "House": "Ev", "Coupons": "Kuponlar",
    "In Case of an Emergency": "Acil Durumda",
}


def split_terms(items):
    """'…in the same building Condo:' -> the definition, then 'Condo:' as the next term."""
    out = []
    for item in items:
        term = next((t for t in TRAILING_TERMS if item["en"].endswith(" " + t + ":")), None)
        if term and not item["answers"]:
            tr_words = len(TRAILING_TERMS[term].split())
            out.append({"en": item["en"][:-len(term) - 1].strip(),
                        "tr": re.sub(r"(\s+\S+){%d}:$" % tr_words, "", item["tr"]).strip(), "answers": []})
            out.append({"en": term + ":", "tr": TRAILING_TERMS[term] + ":", "answers": []})
        else:
            out.append(item)
    return out


def clean_topic(items, resources):
    """items: list of dicts {en, tr, answers}; resources: list of (title, url)."""
    out = []
    used_resources = {}
    titles = {norm(t): (t, u) for t, u in resources}
    for item in split_terms(items):
        en, tr = FIXES.get(item["en"], item["en"]), item["tr"]
        if item["en"] in FIXES and not en:
            continue
        filled_en, filled_tr = fill_blank(en, tr)
        filled = filled_en != en
        en, tr = clean(filled_en), clean(filled_tr)
        if not en or LABEL.match(en):
            continue
        key = norm(en)
        # A line that is (or starts with) a link title becomes that link's description.
        match = titles.get(key) or next((v for k, v in titles.items() if k and (
            (key.startswith(k) and len(key) < 2 * len(k) + 70) or (k.startswith(key) and len(key) > 0.6 * len(k)))), None)
        if match and not item["answers"]:
            # A line holding two link titles cannot describe one of them.
            two = sum(1 for k in titles if k and k in key) > 1
            used_resources.setdefault(match[1], (match[0], "") if two else (en.rstrip(":"), tr.rstrip(":")))
            continue
        # A term printed on its own line ("Rent:") followed by its meaning.
        if out and out[-1]["type"] == "heading" and is_definition(out[-1]["en"], en) and not item["answers"]:
            term = out.pop()
            out.append({"type": "card", "en": join(term["en"] + ":", en), "tr": join(term["tr"] + ":", tr), "answers": [], "filled": filled})
            continue
        # Join definitions split over two lines.
        if out and out[-1]["type"] == "card" and not out[-1]["answers"] and (
                is_fragment(en) or re.search(r"(Say|[A-Za-z]):$|=$", out[-1]["en"]) and not en.endswith(":")):
            out[-1]["en"] = join(out[-1]["en"], en)
            out[-1]["tr"] = join(out[-1]["tr"], tr)
            out[-1]["filled"] = out[-1].get("filled") or filled
            continue
        en = re.sub(r"^(\d+\s*[-.)]\s+|-\s*)", "", en)
        tr = re.sub(r"^(\d+\s*[-.)]\s+|-\s*)", "", tr)
        if not item["answers"] and (norm(en) in HEADINGS or is_title(en) or (en.endswith(":") and len(en.split()) <= 7)):
            out.append({"type": "heading", "en": en.rstrip(":").strip(), "tr": tr.rstrip(":").strip()})
            continue
        out.append({"type": "card", "en": en, "tr": tr, "answers": item["answers"], "filled": filled})
    for block in out:
        for f in ("en", "tr"):  # quotes the PDF split onto separate lines
            if block[f].count("“") != block[f].count("”"):
                block[f] = re.sub(r"\s*[“”]\s*", " ", block[f]).replace(" .", ".").strip()
    # A heading with nothing after it (before the next heading) is not useful.
    cleaned = []
    for i, block in enumerate(out):
        if block["type"] == "heading" and (i + 1 == len(out) or out[i + 1]["type"] == "heading"):
            continue
        cleaned.append(block)
    links = []
    for title, url in resources:
        if PROMO.search(url):
            continue
        desc = used_resources.get(url)
        links.append({"url": url, "en": desc[0] if desc else title, "tr": desc[1] if desc else "",
                      "video": "youtube.com" in url or "youtu.be" in url})
    return cleaned, links


def render_card(block, number, topic_id, title_tr, title_en):
    en, tr = block["en"], block["tr"]
    filled = block.get("filled", False)
    speak = en
    example = ""
    starter = STARTER_EXAMPLES.get(en)
    if starter:
        tr, ex_en, ex_tr = starter
        speak = ex_en
        filled = True
        example = (f'<div class="phrase-example"><span class="phrase-example-label">Örnek</span>'
                   f'<p class="phrase-example-en" lang="en">{esc(ex_en)}</p>'
                   f'<p class="phrase-example-tr" lang="tr">{esc(ex_tr)}</p></div>')
    answers = "".join(
        f'<div class="phrase-answer-item {kind}"><span class="phrase-ans-sign" aria-hidden="true">'
        f'{"+" if kind == "positive" else ("−" if kind == "negative" else "•")}</span>'
        f'<div class="phrase-ans-content"><span class="phrase-ans-en">{esc(a_en)}</span>'
        f'<span class="phrase-ans-tr">{esc(a_tr)}</span></div></div>'
        for kind, a_en, a_tr in block["answers"])
    answers = f'<div class="phrase-answers">{answers}</div>' if answers else ""
    search = " ".join([en, tr, starter[1] + " " + starter[2] if starter else "", title_tr, title_en]).lower()
    card = (f'<article class="phrase-item" data-id="p{number}" data-topic="{esc(topic_id)}" data-search="{esc(search)}">'
            f'<div class="phrase-item-top"><div class="phrase-en" lang="en">{esc(en)}</div>'
            f'<button type="button" class="phrase-speak-btn" data-action="speak-phrase" data-text="{esc(speak)}" aria-label="Telaffuzu dinle">'
            f'<svg class="icon" aria-hidden="true"><use href="#i-sound"/></svg></button></div>'
            f'<p class="phrase-tr" lang="tr">{esc(tr)}</p>{example}{answers}</article>')
    return card, filled


def build_phrases():
    text = SOURCE.read_text(encoding="utf-8")
    options, sections = [], []
    total = filled_total = link_total = 0
    for topic_id, t_html in re.findall(r'<section class="topic" id="(topic-\d+)">(.*?)</section>', text, re.S):
        heading = re.search(r'<div class="topic-heading"><p>(.*?)</p><h2>(.*?)</h2>(?:<span>(.*?)</span>)?</div>', t_html)
        title_tr = clean(heading.group(2)) if heading else ""
        title_en = clean(heading.group(3)) if heading and heading.group(3) else ""
        items = []
        for p_html in re.findall(r'<li class="phrase"[^>]*>(.*?)</li>', t_html, re.S):
            en = re.search(r'<div class="english"[^>]*>(.*?)</div>', p_html, re.S)
            tr = re.search(r'<div class="turkish"[^>]*>(.*?)</div>', p_html, re.S)
            items.append({"en": clean(en.group(1)) if en else "", "tr": clean(tr.group(1)) if tr else "",
                          "answers": parse_answers(p_html)})
        if not items:
            continue  # topic 1 only advertised the original book
        resources = [(clean(a).replace("↗", "").strip(), url)
                     for url, a in re.findall(r'<a class="resource" href="([^"]+)"[^>]*>(.*?)</a>', t_html, re.S)]
        blocks, links = clean_topic(items, resources)
        body, cards = [], 0
        for block in blocks:
            if block["type"] == "heading":
                body.append(f'<h3 class="phrase-subheading"><span lang="en">{esc(block["en"])}</span>'
                            f'<span class="phrase-subheading-tr" lang="tr">{esc(block["tr"])}</span></h3>')
                continue
            total += 1
            cards += 1
            card, filled = render_card(block, total, topic_id, title_tr, title_en)
            filled_total += filled
            body.append(card)
        link_html = ""
        if links:
            link_total += len(links)
            link_html = ('<div class="phrase-resources"><h3 class="phrase-resources-title">Videolar ve ek kaynaklar</h3><ul>'
                         + "".join(
                             f'<li><a href="{esc(l["url"])}" target="_blank" rel="noopener noreferrer">'
                             f'<span class="phrase-res-kind">{"▶ Video" if l["video"] else "↗ Kaynak"}</span>'
                             f'<span class="phrase-res-en" lang="en">{esc(l["en"])}</span>'
                             + (f'<span class="phrase-res-tr" lang="tr">{esc(l["tr"])}</span>' if l["tr"] else "")
                             + '</a></li>' for l in links) + "</ul></div>")
        num = clean(heading.group(1)) if heading else ""
        options.append(f'<option value="{esc(topic_id)}">{esc(title_tr)} ({cards})</option>')
        sections.append(
            f'<section class="phrase-topic-section" data-topic-id="{esc(topic_id)}">'
            f'<div class="phrase-topic-header"><h2>{esc(num)} {esc(title_tr)}</h2>'
            + (f'<span class="topic-sub">{esc(title_en)}</span>' if title_en else "")
            + f'<span class="topic-badge">{cards} ifade</span></div>'
            f'<div class="phrases-grid">{"".join(body)}</div>{link_html}</section>')
    return "\n".join(options), "\n".join(sections), total, filled_total, link_total, len(sections)


if __name__ == "__main__":
    _, _, total, filled, links, topics = build_phrases()
    print(f"{total} phrase cards in {topics} topics, {filled} completed, {links} links")
