import re

with open('tools/app_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. CSS
phrases_css = """
/* ---------- Phrases (Everyday Conversation) ---------- */
.phrases-container { display: flex; flex-direction: column; gap: var(--space-5); margin-top: var(--space-3); }
.phrase-topic-section { display: flex; flex-direction: column; gap: var(--space-3); scroll-margin-top: 80px; }
.phrase-topic-header { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: var(--space-2); padding-bottom: var(--space-2); border-bottom: 2px solid var(--primary); }
.phrase-topic-header h2 { font-size: 1.25rem; margin: 0; color: var(--primary); }
.phrase-topic-header .topic-sub { color: var(--muted); font-size: .9rem; font-weight: 500; }
.phrase-topic-header .topic-badge { font-size: .75rem; font-weight: 700; padding: 2px 8px; border-radius: 999px; background: var(--primary-soft); color: var(--primary); }
.phrases-grid { display: grid; grid-template-columns: 1fr; gap: var(--space-3); }
@media (min-width: 768px) { .phrases-grid { grid-template-columns: 1fr 1fr; } }
.phrase-item { display: flex; flex-direction: column; gap: var(--space-2); padding: var(--space-4); background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow); transition: transform .15s ease, border-color .15s ease; }
.phrase-item:hover { border-color: var(--primary); }
.phrase-item-top { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--space-2); }
.phrase-en { font-size: 1.05rem; font-weight: 600; color: var(--text); line-height: 1.4; flex: 1; }
.phrase-speak-btn { flex-shrink: 0; color: var(--primary); background: var(--primary-soft); border: none; border-radius: 50%; width: 34px; height: 34px; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; transition: background .15s ease, transform .1s ease; }
.phrase-speak-btn:hover { background: var(--primary); color: #fff; transform: scale(1.08); }
.phrase-speak-btn svg { width: 18px; height: 18px; }
.phrase-tr { font-size: .95rem; color: #b71c1c; font-weight: 500; margin: 0; line-height: 1.4; }
[data-theme="dark"] .phrase-tr { color: #ef9a9a; }
.phrase-recip { font-size: .88rem; color: var(--accent-text); background: var(--primary-soft); padding: var(--space-2) var(--space-3); border-radius: var(--radius-s); font-weight: 500; }
.phrase-answers { display: flex; flex-direction: column; gap: 6px; margin-top: var(--space-1); padding-top: var(--space-2); border-top: 1px dashed var(--line); }
.phrase-answer-item { display: grid; grid-template-columns: 24px 1fr; gap: 6px; padding: 6px 10px; border-radius: var(--radius-s); font-size: .88rem; }
.phrase-answer-item.positive { background: var(--success-soft); border-left: 3px solid var(--success); }
.phrase-answer-item.negative { background: var(--error-soft); border-left: 3px solid var(--error); }
.phrase-answer-item.neutral { background: var(--surface-2); border-left: 3px solid var(--muted); }
.phrase-ans-sign { font-weight: 900; font-size: 1.05rem; text-align: center; }
.phrase-answer-item.positive .phrase-ans-sign { color: var(--success); }
.phrase-answer-item.negative .phrase-ans-sign { color: var(--error); }
.phrase-answer-item.neutral .phrase-ans-sign { color: var(--muted); }
.phrase-ans-content { display: flex; flex-direction: column; gap: 2px; }
.phrase-ans-en { font-weight: 600; color: var(--text); }
.phrase-ans-tr { color: var(--muted); font-size: .82rem; }
"""
text = text.replace('</style>', phrases_css + '\n</style>', 1)

# 2. SVG icon
svg_chat = '<symbol id="i-chat" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></symbol>'
text = text.replace('</svg>', svg_chat + '\n</svg>', 1)

# 3. Tabs nav
old_tabs = '<a href="#words" data-route="words"><svg class="icon" aria-hidden="true"><use href="#i-words"/></svg><span data-i18n="nav.words">Words</span></a>'
new_tabs = old_tabs + '\n    <a href="#phrases" data-route="phrases"><svg class="icon" aria-hidden="true"><use href="#i-chat"/></svg><span data-i18n="nav.phrases">Phrases</span></a>'
text = text.replace(old_tabs, new_tabs, 1)

# 4. Home Mode-Grid
old_mode = '<li><a class="mode-card" href="#words"><svg class="icon" aria-hidden="true"><use href="#i-words"/></svg><div><strong data-i18n="nav.words">Words</strong><span data-i18n="mode.words">Search the list, open example sentences for each word type and mark words you know.</span></div></a></li>'
new_mode = old_mode + '\n      <li><a class="mode-card" href="#phrases"><svg class="icon" aria-hidden="true"><use href="#i-chat"/></svg><div><strong data-i18n="nav.phrases">Phrases</strong><span data-i18n="mode.phrases">41 everyday topics and 1,127 practical conversation patterns.</span></div></a></li>'
text = text.replace(old_mode, new_mode, 1)

# 5. Section Phrases View
phrases_section = """
  <!-- Phrases / Daily Conversation -->
  <section class="view" data-view="phrases" aria-labelledby="phrases-title">
    <div class="view-head">
      <h1 id="phrases-title" tabindex="-1" data-i18n="phrases.title">Daily Phrases</h1>
      <p class="lead" data-i18n="phrases.lead">41 günlük yaşam konusu, 1.127 pratik İngilizce ifade ve B1 cevap örnekleri.</p>
    </div>
    <div class="panel toolbar js-only" role="search">
      <div class="field search-field">
        <label for="phrase-search" data-i18n="phrases.search">Search Phrases</label>
        <input id="phrase-search" type="search" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search" placeholder="İfade veya Türkçe anlam ara…" data-i18n-placeholder="phrases.searchPh">
      </div>
      <div class="field status-field">
        <label for="phrase-topic-select" data-i18n="phrases.topicLabel">Topic</label>
        <select id="phrase-topic-select">
          <option value="all" data-i18n="phrases.allTopics">Tüm Konular (41 Konu)</option>
          <!--@PHRASE_TOPIC_OPTIONS@-->
        </select>
      </div>
    </div>
    <div class="row js-only">
      <p id="phrase-count" class="result-count" aria-live="polite">1127 ifade gösteriliyor</p>
    </div>
    <div id="phrases-list" class="phrases-container">
      <!--@PHRASES_HTML@-->
    </div>
  </section>
"""
old_view_end = '    <div class="more-row js-only"><button type="button" class="button" id="word-more" hidden></button></div>\n  </section>'
text = text.replace(old_view_end, old_view_end + '\n' + phrases_section, 1)

# 6. i18n
# en additions
en_add = """    'nav.phrases': 'Phrases',
    'phrases.title': 'Everyday Conversation Phrases',
    'phrases.lead': '41 daily life topics, 1,127 practical English expressions with B1 answers.',
    'phrases.search': 'Search English or Turkish',
    'phrases.searchPh': 'Search phrase or Turkish meaning…',
    'phrases.topicLabel': 'Topic',
    'phrases.allTopics': 'All Topics (41 Topics)',
    'mode.phrases': '41 everyday topics and 1,127 practical conversation patterns.',
"""
text = text.replace("'nav.home': 'Home',", en_add + "    'nav.home': 'Home',", 1)

# tr additions
tr_add = """    'nav.phrases': 'İfadeler',
    'phrases.title': 'Günlük Konuşma İfadeleri',
    'phrases.lead': '41 günlük yaşam konusu, 1.127 pratik İngilizce ifade ve B1 cevap örnekleri.',
    'phrases.search': 'İfade veya Türkçe ara',
    'phrases.searchPh': 'İfade veya Türkçe anlam ara…',
    'phrases.topicLabel': 'Konu',
    'phrases.allTopics': 'Tüm Konular (41 Konu)',
    'mode.phrases': '41 günlük yaşam konusu ve 1.127 pratik konuşma kalıbı.',
"""
text = text.replace("'card.photo': 'Görsel',", tr_add + "    'card.photo': 'Görsel',", 1)

# 7. JS Routes, Phrases Object, Modules, Init
text = text.replace("const ROUTES = ['home', 'words', 'quiz', 'reading', 'settings'];",
                    "const ROUTES = ['home', 'words', 'phrases', 'quiz', 'reading', 'settings'];", 1)

phrases_js = """
/* ---------- 7l. Phrases (Everyday Conversation) ---------- */
const Phrases = {
  activeTopic: 'all',
  query: '',
  timer: 0,
  init() {
    const search = $('#phrase-search');
    if (search) {
      search.addEventListener('input', () => {
        clearTimeout(this.timer);
        this.timer = setTimeout(() => {
          this.query = normalize(search.value.trim());
          this.filter();
        }, 150);
      });
      search.addEventListener('keydown', event => { if (event.key === 'Enter') search.blur(); });
    }
    const topicSelect = $('#phrase-topic-select');
    if (topicSelect) {
      topicSelect.addEventListener('change', e => {
        this.activeTopic = e.target.value;
        this.filter();
      });
    }
    const list = $('#phrases-list');
    if (list) {
      list.addEventListener('click', event => {
        const btn = event.target.closest('[data-action="speak-phrase"]');
        if (btn) {
          const text = btn.dataset.text;
          if (text) Speech.speak(text);
        }
      });
    }
  },
  onShow() {},
  filter() {
    const q = this.query;
    const topic = this.activeTopic;
    let visibleCount = 0;
    const items = $$('#phrases-list .phrase-item');
    for (const card of items) {
      const cardTopic = card.dataset.topic;
      const cardSearch = card.dataset.search || '';
      const matchTopic = topic === 'all' || cardTopic === topic;
      const matchQuery = !q || cardSearch.indexOf(q) >= 0;
      const show = matchTopic && matchQuery;
      card.hidden = !show;
      if (show) visibleCount++;
    }
    for (const sec of $$('#phrases-list .phrase-topic-section')) {
      const visibleChildren = $$('.phrase-item:not([hidden])', sec);
      sec.hidden = visibleChildren.length === 0;
    }
    const countEl = $('#phrase-count');
    if (countEl) {
      countEl.textContent = (lang === 'tr' ? (visibleCount + ' ifade gösteriliyor') : (visibleCount + ' phrases shown'));
    }
  }
};
"""
old_quiz_marker = '/* ---------- 7m. Quiz ---------- */'
text = text.replace(old_quiz_marker, phrases_js + '\n' + old_quiz_marker, 1)

# MODULES and init
text = text.replace('const MODULES = { home: Home, words: Words, quiz: Quiz, reading: Reading, settings: Settings };',
                    'const MODULES = { home: Home, words: Words, phrases: Phrases, quiz: Quiz, reading: Reading, settings: Settings };', 1)

text = text.replace('Home.init(); Words.init(); Quiz.init(); Settings.init();',
                    'Home.init(); Words.init(); Phrases.init(); Quiz.init(); Settings.init();', 1)

with open('tools/app_template.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated tools/app_template.html successfully!")
