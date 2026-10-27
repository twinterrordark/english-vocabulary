import json
import html

with open('tools/phrases_data.json', 'r', encoding='utf-8') as f:
    topics = json.load(f)

def esc(s):
    return html.escape(s or '', quote=True)

topic_options = []
phrases_html_blocks = []

total_phrases = 0
for t in topics:
    t_id = t['id']
    num = t['num']
    title_tr = t['titleTr']
    title_en = t['titleEn']
    phrases = t['phrases']
    if not phrases:
        continue
    
    topic_options.append(f'<option value="{esc(t_id)}">{esc(title_tr)} ({len(phrases)})</option>')
    
    cards = []
    for p in phrases:
        total_phrases += 1
        p_id = p['id']
        en = p['en']
        tr = p['tr']
        recip = p.get('reciprocal')
        answers = p.get('answers', [])
        
        search_blob = (en + ' ' + tr + ' ' + title_tr + ' ' + (title_en or '')).lower()
        
        ans_html = []
        if answers:
            ans_html.append('<div class="phrase-answers">')
            for a in answers:
                ans_html.append(
                    f'<div class="phrase-answer-item {esc(a["type"])}">'
                    f'<span class="phrase-ans-sign" aria-hidden="true">{esc(a["sign"])}</span>'
                    f'<div class="phrase-ans-content">'
                    f'<span class="phrase-ans-en">{esc(a["en"])}</span>'
                    f'<span class="phrase-ans-tr">{esc(a["tr"])}</span>'
                    f'</div></div>'
                )
            ans_html.append('</div>')
            
        recip_html = f'<div class="phrase-recip">💬 {esc(recip)}</div>' if recip else ''
        
        card = (
            f'<article class="phrase-item" data-id="{esc(p_id)}" data-topic="{esc(t_id)}" data-search="{esc(search_blob)}">'
            f'<div class="phrase-item-top">'
            f'<div class="phrase-en" lang="en">{esc(en)}</div>'
            f'<button type="button" class="phrase-speak-btn" data-action="speak-phrase" data-text="{esc(en)}" aria-label="Telaffuzu dinle">'
            f'<svg class="icon" aria-hidden="true"><use href="#i-sound"/></svg>'
            f'</button>'
            f'</div>'
            f'<p class="phrase-tr" lang="tr">{esc(tr)}</p>'
            f'{recip_html}'
            f'{"".join(ans_html)}'
            f'</article>'
        )
        cards.append(card)
        
    section = (
        f'<section class="phrase-topic-section" data-topic-id="{esc(t_id)}">'
        f'<div class="phrase-topic-header">'
        f'<h2>{esc(num)} {esc(title_tr)}</h2>'
        f'{f"<span class=\"topic-sub\">{esc(title_en)}</span>" if title_en else ""}'
        f'<span class="topic-badge">{len(phrases)} ifade</span>'
        f'</div>'
        f'<div class="phrases-grid">{"".join(cards)}</div>'
        f'</section>'
    )
    phrases_html_blocks.append(section)

print(f"Generated HTML for {len(topic_options)} topics and {total_phrases} phrases.")
print(f"Total HTML size: {sum(len(b) for b in phrases_html_blocks) / 1024:.1f} KB")
