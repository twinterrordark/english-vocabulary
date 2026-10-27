import re
import sys
from blank_replacements import REPLACEMENTS

with open('650-english-textwork-mobile-v2.html', 'r', encoding='utf-8') as f:
    text = f.read()

topics = re.findall(r'<section class="topic" id="(topic-\d+)">(.*?)</section>', text, re.S)
unmatched = []

for topic_id, topic_html in topics:
    phrases = re.findall(r'<li class="phrase"[^>]*>(.*?)</li>', topic_html, re.S)
    for p in phrases:
        en_m = re.search(r'<div class="english"[^>]*>(.*?)</div>', p, re.S)
        tr_m = re.search(r'<div class="turkish"[^>]*>(.*?)</div>', p, re.S)
        en = en_m.group(1).strip() if en_m else ''
        tr = tr_m.group(1).strip() if tr_m else ''
        if re.search(r'_{2,}', en) or re.search(r'_{2,}', tr):
            if en not in REPLACEMENTS:
                unmatched.append((en, tr))

print(f'Unmatched count: {len(unmatched)}')
for u in unmatched:
    print('NOT FOUND:', u[0])
