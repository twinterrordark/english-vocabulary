import re
import json

with open('650-english-textwork-mobile-v2.html', 'r', encoding='utf-8') as f:
    text = f.read()

topics = re.findall(r'<section class="topic" id="(topic-\d+)">(.*?)</section>', text, re.S)

blank_items = []
for topic_id, topic_html in topics:
    h2_m = re.search(r'<h2>(.*?)</h2>', topic_html)
    topic_title = h2_m.group(1) if h2_m else ''
    phrases = re.findall(r'<li class="phrase"[^>]*>(.*?)</li>', topic_html, re.S)
    for p in phrases:
        en_m = re.search(r'<div class="english"[^>]*>(.*?)</div>', p, re.S)
        tr_m = re.search(r'<div class="turkish"[^>]*>(.*?)</div>', p, re.S)
        en = en_m.group(1).strip() if en_m else ''
        tr = tr_m.group(1).strip() if tr_m else ''
        if re.search(r'_{2,}', en) or re.search(r'_{2,}', tr):
            blank_items.append({'topic': topic_title, 'en': en, 'tr': tr})

with open('tools/all_blanks.json', 'w', encoding='utf-8') as f:
    json.dump(blank_items, f, ensure_ascii=False, indent=2)

print(f'Wrote {len(blank_items)} blanks to tools/all_blanks.json')
