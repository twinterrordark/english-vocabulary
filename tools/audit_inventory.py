"""Read-only accounting of the entire built HTML and embedded content."""
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
text = subprocess.run(['git', 'show', 'HEAD:index.html'], cwd=root, capture_output=True, check=True).stdout.decode('utf-8') if '--git-baseline' in sys.argv else (root / 'index.html').read_text(encoding='utf-8')
sizes, counts = collections.Counter(), collections.Counter()
for mime, payload in re.findall(r'data:((?:image|font)/[\w.+-]+);base64,([A-Za-z0-9+/=]+)', text):
    sizes[mime] += len(payload)
    counts[mime] += 1
scripts = re.findall(r'<script([^>]*)>([\s\S]*?)</script>', text)
inventory = {'bytes': len(text.encode()), 'sha256': hashlib.sha256(text.encode()).hexdigest(),
    'data_uri_encoded_chars': dict(sizes), 'data_uri_counts': dict(counts),
    'scripts': [{'attributes': attrs.strip(), 'bytes': len(code.encode())} for attrs, code in scripts],
    'word_cards': text.count('class="word-card"')}
inventory['word_card_markup_sha256'] = hashlib.sha256(''.join(re.findall(r'<article class="word-card"[\s\S]*?</article>', text)).encode()).hexdigest()
inventory['embedded_images_sha256'] = hashlib.sha256(''.join(re.findall(r'data:image/[\w.+-]+;base64,[A-Za-z0-9+/=]+', text)).encode()).hexdigest()
for key in ['vocab-data', 'sentence-data', 'phrase-data', 'work-data', 'novel-dict', 'grammar-data']:
    data = json.loads(next(code for attrs, code in scripts if f'id="{key}"' in attrs))
    inventory[key] = {'entries': len(data), 'sha256': hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
out = root / 'audits' / '2026-11-09'
out.mkdir(parents=True, exist_ok=True)
phase = sys.argv[1] if len(sys.argv) > 1 else 'baseline'
(out / phase).mkdir(exist_ok=True)
(out / phase / 'inventory.json').write_text(json.dumps(inventory, indent=2), encoding='utf-8')
print(json.dumps(inventory, indent=2))
