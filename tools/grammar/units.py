"""Grammar topics split into learning units, the steps of a topic's learning path.

A lesson marked "mode": "items" gives one unit per example (one conjunction,
one phrasal verb); its label reads "term = meaning". Any other lesson is a
single unit (one verb with its meanings, one relative clause lesson).
Example sentences from the novels are kept in book_examples.json under the
unit's id. Used by build_index.py and book_candidates.py.
"""
import re


def slug(text):
    text = text.translate(str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def units(topic_id, topic):
    result, seen = [], {}
    for index, lesson in enumerate(topic["lessons"]):
        if lesson.get("mode") == "items":
            parts = [(example, *example[2].split(" = ", 1)) for example in lesson["examples"]]
        else:
            parts = [(None, lesson["title"], "")]
        for example, title, meaning in parts:
            key = slug(title.split(" + ")[0] if example else title)
            seen[key] = seen.get(key, 0) + 1
            unit = {
                "id": f"{topic_id}:{key}" + (f"-{seen[key]}" if seen[key] > 1 else ""),
                "lesson": index,
                "title": title,
                "meaning": meaning,
                "examples": [example[:2]] if example else lesson["examples"],
            }
            result.append(unit)
    return result
