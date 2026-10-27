import re

with open('650-english-textwork-mobile-v2.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Topics
topics = re.findall(r'<section class="topic" id="(topic-\d+)">(.*?)</section>', text, re.S)
print(f'Total topics: {len(topics)}')

blank_phrases = []
all_phrases = []

for topic_id, topic_html in topics:
    heading_m = re.search(r'<div class="topic-heading"><p>(.*?)</p><h2>(.*?)</h2>(?:<span>(.*?)</span>)?</div>', topic_html)
    p_num = heading_m.group(1) if heading_m else ''
    h2_tr = heading_m.group(2) if heading_m else ''
    sub_en = heading_m.group(3) if heading_m else ''
    
    phrases = re.findall(r'<li class="phrase"[^>]*>(.*?)</li>', topic_html, re.S)
    for p in phrases:
        en_m = re.search(r'<div class="english"[^>]*>(.*?)</div>', p, re.S)
        tr_m = re.search(r'<div class="turkish"[^>]*>(.*?)</div>', p, re.S)
        en = en_m.group(1).strip() if en_m else ''
        tr = tr_m.group(1).strip() if tr_m else ''
        all_phrases.append((topic_id, h2_tr, en, tr, p))
        if re.search(r'_{2,}', en) or re.search(r'_{2,}', tr):
            blank_phrases.append((topic_id, h2_tr, en, tr))

print(f'Total phrases: {len(all_phrases)}')
print(f'Blank phrases: {len(blank_phrases)}')

for t_id, h2, en, tr in blank_phrases[:20]:
    print(f'[{h2}]')
    print('  EN:', en)
    print('  TR:', tr)
