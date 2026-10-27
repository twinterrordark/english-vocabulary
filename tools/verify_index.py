with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

checks = {
    'Phrases tab': 'data-route="phrases"' in text,
    'Phrases view section': 'data-view="phrases"' in text,
    'Phrases JS init': 'Phrases.init()' in text,
    'Phrase items': text.count('class="phrase-item"'),
    'Phrase answers': text.count('class="phrase-answers"'),
    'Phrase topic sections': text.count('phrase-topic-section'),
    'Total word cards': text.count('class="word-card"'),
    'Total word images': len(re.findall(r'<img [^>]*src="data:image/webp;base64,', text)),
    'Human audio API': 'api.dictionaryapi.dev' in text,
    'Google TTS': 'translate_tts' in text,
    'Warning removed': 'JavaScript çalıştırmayan' not in text,
    'Version': text[text.find('English Study · version')+len('English Study · version '):text.find('English Study · version')+len('English Study · version ')+8].strip(),
    'File size (MB)': f"{len(text.encode('utf-8')) / (1024*1024):.1f}",
}

for key, val in checks.items():
    print(f'{key}: {val}')
