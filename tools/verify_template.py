with open('tools/app_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('Phrases tab in nav:', 'data-route="phrases"' in text)
print('Phrases view section:', 'data-view="phrases"' in text)
print('Phrases CSS:', 'phrase-topic-section' in text)
print('Phrases JS:', 'const Phrases =' in text)
print('PHRASE_TOPIC_OPTIONS placeholder:', '<!--@PHRASE_TOPIC_OPTIONS@-->' in text)
print('PHRASES_HTML placeholder:', '<!--@PHRASES_HTML@-->' in text)
print('i18n phrases.title EN:', 'phrases.title' in text)
