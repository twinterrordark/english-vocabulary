"""Example sentences by word type from Tatoeba, into tools/work/extra_sentences.json.

Usage: python tools/work/extra_sentences.py <folder with tur.txt> [<nltk data folder>]
tur.txt comes from https://www.manythings.org/anki/tur-eng.zip (Tatoeba, CC BY 2.0 FR).
Words get sentences for the types they do not have yet. A type counts only when the tagger finds
it in at least 2 sentences and at least 10% of the word's sentences, as taggers make mistakes."""
import heapq
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
OUT = HERE / "extra_sentences.json"
PER_WORD = 40
PER_TYPE = 2
TOKEN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
AVOID = re.compile(r"\b(kill\w*|murder\w*|suicide|rape\w*|sex\w*|naked|nude|whore|bitch\w*|fuck\w*|shit\w*|damn\w*|ass|asshole|drunk|nazi\w*|hitler|terroris\w*|penis|breast\w*|virgin|porn\w*)\b", re.I)
TYPE_OF = {"NN": "n", "NNS": "n", "VB": "v", "VBD": "v", "VBG": "v", "VBN": "v", "VBP": "v", "VBZ": "v", "JJ": "adj", "JJR": "adj", "JJS": "adj", "RB": "adv", "RBR": "adv", "RBS": "adv"}
FILLERS = {"a", "an", "the", "his", "her", "my", "your", "their", "our", "its", "this", "that"}
WN_OF = {"n": wn.NOUN, "v": wn.VERB, "adj": wn.ADJ, "adv": wn.ADV}


def targets() -> tuple[set, set]:
    work = set()
    for name in ("ai_it", "industrial_design", "business", "exam_words"):
        for line in (HERE / f"{name}.txt").read_text(encoding="utf-8").splitlines():
            if "|" in line and not line.startswith("#"):
                work.add(line.split("|")[0].strip().lower())
    main = set()
    for path in sorted((TOOLS / "sentences").glob("*.json")):
        main.update(word.strip().lower() for word in json.loads(path.read_text(encoding="utf-8")))
    return main, work


def main() -> None:
    source = Path(sys.argv[1])
    if len(sys.argv) > 2:
        nltk.data.path.insert(0, sys.argv[2])
    lemmatize = WordNetLemmatizer().lemmatize
    main_words, work_words = targets()
    wanted = main_words | work_words
    single = {word for word in wanted if " " not in word}
    phrases = defaultdict(list)
    for word in wanted - single:
        parts = TOKEN.findall(word)
        if len(parts) > 1:
            phrases[parts[0]].append(parts)

    cache: dict[str, set] = {}

    def bases(token: str) -> set:
        if token not in cache:
            cache[token] = {token} | {lemmatize(token, pos) for pos in (wn.NOUN, wn.VERB, wn.ADJ, wn.ADV)}
        return cache[token]

    # Short, plain sentences first; Tom and Mary are everywhere, so a little later.
    heaps: dict[str, list] = defaultdict(list)
    seen: set[str] = set()
    pairs = []
    for line in (source / "tur.txt").read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        en, tr = parts[0].strip(), parts[1].strip()
        if en in seen or AVOID.search(en) or len(en) > 130:
            continue
        tokens = [token.lower() for token in TOKEN.findall(en)]
        if not 4 <= len(tokens) <= 20:
            continue
        seen.add(en)
        pairs.append((en, tr))
        rank = abs(len(tokens) - 8) + (3 if re.search(r"\b(Tom|Mary)\b", en) else 0)
        hits = set()
        bare = [token for token in tokens if token not in FILLERS]
        for at, token in enumerate(tokens):
            for base in bases(token):
                if base in single:
                    hits.add(base)
                if token in FILLERS:
                    continue
                for phrase in phrases.get(base, ()):
                    place = sum(1 for earlier in tokens[:at] if earlier not in FILLERS)
                    if bare[place + 1:place + len(phrase)] == [part.lower() for part in phrase[1:] if part.lower() not in FILLERS]:
                        hits.add(" ".join(phrase).lower())
        for word in hits:
            item = (-rank, len(pairs) - 1)
            if len(heaps[word]) < PER_WORD:
                heapq.heappush(heaps[word], item)
            else:
                heapq.heappushpop(heaps[word], item)
    print("sentences:", len(pairs), "words with candidates:", len(heaps), "of", len(wanted))

    tags: dict[int, list] = {}
    existing = defaultdict(set)
    for path in sorted((TOOLS / "sentences").glob("*.json")):
        for word, groups in json.loads(path.read_text(encoding="utf-8")).items():
            existing[word.strip().lower()].update(groups)

    out: dict[str, dict] = {}
    for count, (word, heap) in enumerate(sorted(heaps.items()), 1):
        found = defaultdict(list)
        for _, index in sorted(heap, key=lambda item: -item[0]):
            en, tr = pairs[index]
            if " " in word:
                found["phr"].append((en, tr))
                continue
            if index not in tags:
                tags[index] = nltk.pos_tag(TOKEN.findall(en))
            for token, tag in tags[index]:
                kind = TYPE_OF.get(tag)
                if kind and word == lemmatize(token.lower(), WN_OF[kind]):
                    found[kind].append((en, tr))
                    break
                if kind and word == token.lower():
                    usable = next((k for k in (kind, "adj", "n", "adv") if wn.synsets(word, WN_OF[k])), None) or next((k for k in ("v",) if wn.morphy(word, wn.VERB)), None)
                    if usable:
                        found[usable].append((en, tr))
                    break
        total = sum(len(items) for items in found.values())
        groups = {}
        for kind, items in found.items():
            real = kind == "phr" or wn.synsets(word.replace(" ", "_"), WN_OF[kind]) or (kind == "v" and wn.morphy(word, wn.VERB))
            # Short common words are tagged wrongly often, so a second type needs more proof.
            enough = len(items) >= 2 and len(items) / total >= 0.1
            alone = len(found) == 1 and word in work_words
            if kind not in existing[word] and real and (enough or alone):
                groups[kind] = [list(pair) for pair in items[:PER_TYPE]]
        if groups:
            out[word] = groups
        if count % 500 == 0:
            print(count, "/", len(heaps), flush=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    done_work = sum(word in out for word in work_words)
    print("written words:", len(out), "work words with sentences:", done_work, "of", len(work_words), "main words with a new type:", sum(word in out for word in main_words))
    print("sentences:", sum(len(items) for groups in out.values() for items in groups.values()), "bytes:", OUT.stat().st_size)


if __name__ == "__main__":
    main()
