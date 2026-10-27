#!/usr/bin/env python3
"""Find and download free, word-relevant photos from Wikipedia / Wikimedia Commons.

No API key is needed. Every image keeps its author and licence for attribution.

  python tools/fetch_images.py candidates WORDS.json OUT.json
      For each word, look up the English Wikipedia article with the same title
      (following redirects) and record its lead image, the article title and
      the short description. Disambiguation pages are skipped.

  python tools/fetch_images.py download APPROVED.json
      APPROVED.json maps word -> {"file": "File:....jpg"}. Each file is
      downloaded as a 320 px thumbnail, saved as tools/images/<word>.webp,
      and its credit is written to tools/images/credits.json.

Relevance is decided by a human review of the candidate list (article title,
description and file name); images are never accepted just because a search
returned something.
"""
import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
IMAGE_DIR = HERE / "images"
USER_AGENT = "EnglishStudyBuild/1.0 (personal offline study page)"


def get_json(url: str, params: dict) -> dict:
    query = urllib.parse.urlencode({**params, "format": "json", "formatversion": "2"})
    # POST keeps long title lists out of the URL.
    request = urllib.request.Request(url, data=query.encode(), headers={"User-Agent": USER_AGENT})
    error = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                return json.load(response)
        except Exception as exc:
            error = exc
            time.sleep(5 + attempt * 10)
    raise RuntimeError(f"request failed: {url}: {error}")


def candidates(words_path: str, out_path: str) -> None:
    words = json.loads(Path(words_path).read_text(encoding="utf-8"))
    result = {}
    for start in range(0, len(words), 50):
        batch = words[start:start + 50]
        titles = {w[:1].upper() + w[1:]: w for w in batch}
        data = get_json("https://en.wikipedia.org/w/api.php", {
            "action": "query", "titles": "|".join(titles), "redirects": 1,
            "prop": "pageimages|pageprops|description", "piprop": "name", "ppprop": "disambiguation"})
        query = data.get("query", {})
        resolved = {t: t for t in titles}
        for step in query.get("normalized", []) + query.get("redirects", []):
            for original, current in list(resolved.items()):
                if current == step["from"]:
                    resolved[original] = step["to"]
        pages = {p["title"]: p for p in query.get("pages", [])}
        for original, title in resolved.items():
            page = pages.get(title, {})
            if page.get("missing") or "disambiguation" in page.get("pageprops", {}) or not page.get("pageimage"):
                continue
            result[titles[original]] = {"article": title, "description": page.get("description", ""), "file": "File:" + page["pageimage"]}
        time.sleep(1.5)
        print(f"{min(start + 50, len(words))}/{len(words)} words, {len(result)} candidates", flush=True)
    Path(out_path).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")


def commons(words_path: str, out_path: str) -> None:
    """Second pass: search Wikimedia Commons photos whose file name contains the word."""
    import re
    words = json.loads(Path(words_path).read_text(encoding="utf-8"))
    out_file = Path(out_path)
    result = json.loads(out_file.read_text(encoding="utf-8")) if out_file.exists() else {}
    for index, word in enumerate(words):
        if word in result or " " in word or len(word) < 3:
            continue
        data = get_json("https://commons.wikimedia.org/w/api.php", {
            "action": "query", "list": "search", "srnamespace": 6, "srlimit": 15,
            "srsearch": f'intitle:"{word}" filetype:bitmap'})
        stem = re.escape(word[:-1] if word.endswith("e") else word)
        pattern = re.compile(r"(?:^|[\s_\-(,])" + stem + r"[a-z]{0,4}(?:$|[\s_\-.),])", re.I)
        titles = [hit["title"] for hit in data.get("query", {}).get("search", [])
                  if pattern.search(hit["title"][5:]) and re.search(r"\.(jpe?g|png|webp)$", hit["title"], re.I)
                  and not re.search(r"logo|map|diagram|chart|graph|icon|symbol|flag_of|coat_of_arms|text|page|scan|plan\b", hit["title"], re.I)]
        result[word] = titles[:3]
        if index % 25 == 0:
            out_file.write_text(json.dumps(result, ensure_ascii=False, indent=0), encoding="utf-8")
            print(f"{index + 1}/{len(words)}", flush=True)
        time.sleep(0.4)
    out_file.write_text(json.dumps(result, ensure_ascii=False, indent=0), encoding="utf-8")


def strip_tags(text: str) -> str:
    import html
    import re
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", text or ""))).strip()


def download(approved_path: str) -> None:
    approved = json.loads(Path(approved_path).read_text(encoding="utf-8"))
    IMAGE_DIR.mkdir(exist_ok=True)
    credits_path = IMAGE_DIR / "credits.json"
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}
    files = {word: item["file"] for word, item in approved.items() if word not in credits}
    names = list(files.items())
    for start in range(0, len(names), 40):
        batch = names[start:start + 40]
        data = get_json("https://commons.wikimedia.org/w/api.php", {
            "action": "query", "titles": "|".join(f for _, f in batch), "prop": "imageinfo",
            "iiprop": "url|extmetadata", "iiurlwidth": 320})
        query = data.get("query", {})
        names_map = {n["from"]: n["to"] for n in query.get("normalized", [])}
        pages = {p["title"]: p for p in query.get("pages", [])}
        for word, file_title in batch:
            page = pages.get(names_map.get(file_title, file_title))
            info = (page or {}).get("imageinfo", [{}])[0]
            if not info.get("thumburl"):
                print("  no image info:", word, file_title)
                continue
            meta = info.get("extmetadata", {})
            licence = strip_tags(meta.get("LicenseShortName", {}).get("value", ""))
            if not licence:
                print("  no licence, skipped:", word)
                continue
            request = urllib.request.Request(info["thumburl"], headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    image = Image.open(io.BytesIO(response.read())).convert("RGB")
            except Exception as error:
                print("  download failed:", word, error)
                continue
            image.thumbnail((320, 240))
            image.save(IMAGE_DIR / f"{word}.webp", "WEBP", quality=55, method=6)
            credits[word] = {
                "file": file_title,
                "page": info.get("descriptionurl", ""),
                "author": strip_tags(meta.get("Artist", {}).get("value", ""))[:120] or "Unknown",
                "licence": licence,
            }
            time.sleep(0.3)
        credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        print(f"{min(start + 40, len(names))}/{len(names)} downloaded", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "candidates":
        candidates(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "commons":
        commons(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "download":
        download(sys.argv[2])
