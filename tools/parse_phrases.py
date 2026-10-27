import re
import json
import html
from blank_replacements import REPLACEMENTS

with open('650-english-textwork-mobile-v2.html', 'r', encoding='utf-8') as f:
    text = f.read()

topics_raw = re.findall(r'<section class="topic" id="(topic-\d+)">(.*?)</section>', text, re.S)

def clean(s):
    if not s:
        return ""
    # strip tags and unescape html
    t = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()

def fill_blank(en, tr):
    if en in REPLACEMENTS:
        return REPLACEMENTS[en]
    # Check 34,999
    if '34,999' in en and 'How many' in en:
        return (
            "When talking about numbers or amounts: 'How many books do you have?'",
            "Sayılardan veya miktarlardan bahsederken: 'Kaç tane kitabın var?'"
        )
    return en, tr

topics_data = []
total_phrases = 0
total_filled = 0

for t_id, t_html in topics_raw:
    heading_m = re.search(r'<div class="topic-heading"><p>(.*?)</p><h2>(.*?)</h2>(?:<span>(.*?)</span>)?</div>', t_html)
    num = clean(heading_m.group(1)) if heading_m else ''
    title_tr = clean(heading_m.group(2)) if heading_m else ''
    title_en = clean(heading_m.group(3)) if heading_m else ''
    
    # Topic 1 is just links to external books, we can still include it or keep it as reference
    phrases_raw = re.findall(r'<li class="phrase"[^>]*>(.*?)</li>', t_html, re.S)
    phrases = []
    
    for p_html in phrases_raw:
        en_m = re.search(r'<div class="english"[^>]*>(.*?)</div>', p_html, re.S)
        tr_m = re.search(r'<div class="turkish"[^>]*>(.*?)</div>', p_html, re.S)
        recip_m = re.search(r'<div class="reciprocal-question"[^>]*>(.*?)</div>', p_html, re.S)
        
        raw_en = en_m.group(1).strip() if en_m else ''
        raw_tr = tr_m.group(1).strip() if tr_m else ''
        recip = clean(recip_m.group(1)) if recip_m else None
        
        filled_en, filled_tr = fill_blank(raw_en, raw_tr)
        if filled_en != raw_en:
            total_filled += 1
            
        en_clean = clean(filled_en)
        tr_clean = clean(filled_tr)
        
        # Answers
        answers = []
        ans_items = re.findall(r'<div class="answer-example\s*([^"]*)">(.*?)</div>\s*</div>', p_html, re.S)
        for cls, a_html in ans_items:
            sign = '+' if 'positive' in cls or '+' in a_html else ('-' if 'negative' in cls or '−' in a_html else '•')
            ans_en_m = re.search(r'<div class="answer-en"[^>]*>(.*?)</div>', a_html, re.S)
            ans_tr_m = re.search(r'<div class="answer-tr"[^>]*>(.*?)</div>', a_html, re.S)
            ans_en = clean(ans_en_m.group(1)) if ans_en_m else ''
            ans_tr = clean(ans_tr_m.group(1)) if ans_tr_m else ''
            if ans_en:
                answers.append({
                    'type': 'negative' if 'negative' in cls else ('neutral' if 'neutral' in cls else 'positive'),
                    'sign': sign,
                    'en': ans_en,
                    'tr': ans_tr
                })
        
        if en_clean or tr_clean:
            phrases.append({
                'id': f"p{total_phrases + 1}",
                'en': en_clean,
                'tr': tr_clean,
                'reciprocal': recip,
                'answers': answers
            })
            total_phrases += 1

    topics_data.append({
        'id': t_id,
        'num': num,
        'titleTr': title_tr,
        'titleEn': title_en,
        'phrases': phrases
    })

print(f"Extracted {len(topics_data)} topics with {total_phrases} phrases.")
print(f"Filled blanks in {total_filled} phrases.")

with open('tools/phrases_data.json', 'w', encoding='utf-8') as f:
    json.dump(topics_data, f, ensure_ascii=False, indent=2)

print("Saved to tools/phrases_data.json successfully!")
