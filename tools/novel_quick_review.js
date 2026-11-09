/* Optional, local-only retrieval practice for words saved on the current book page.
   This module never changes Review's schedule, learned state or XP. */
const NovelQuickReview = {
  KEY: 'english-study-novel-quick.v1',
  LIMIT: 240,
  records: [],
  context: null,
  session: null,
  init(options) {
    this.options = options;
    this.session = null;
    if (!this.root) {
      this.root = this.el('section', { class: 'novel-quick-review', hidden: true, 'aria-label': this.label('region') });
      options.article.insertAdjacentElement('afterend', this.root);
    }
    try {
      const stored = JSON.parse(options.store.read(this.KEY) || '[]');
      this.records = this.sanitize(stored);
    } catch (_) { this.records = []; }
    this.render();
    return this;
  },
  label(key, values = {}) {
    const tr = !this.options || !this.options.language || this.options.language() === 'tr';
    const strings = tr ? {
      region: 'Bu sayfadan kısa tekrar', title: 'Bu sayfadan kısa tekrar',
      note: '{n} kayıtlı kelime veya kalıp · yaklaşık 1 dakika', start: 'Kısa tekrar yap',
      progress: '{i} / {n}', prompt: 'Boşlukları cümledeki biçimiyle tamamla.',
      word: 'Eksik kelime veya kalıp', input: 'Cümledeki biçimi yaz…',
      help: 'Birden fazla boşluk varsa kelimeleri soldan sağa, aralarına boşluk koyarak yaz.',
      check: 'Kontrol et', reveal: 'Cevabı göster', next: 'Sonraki', finish: 'Bitir',
      correct: 'Doğru! Kelimeyi bağlamında hatırladın.', wrong: 'Bu cümlede kullanılan biçim aşağıda.',
      empty: 'Önce bir cevap yaz veya “Cevabı göster”i seç.',
      done: 'Kısa tekrar tamamlandı', score: '{n} sorudan {c} tanesini yardımsız hatırladın.',
      again: 'Bir daha dene', close: 'Okumaya dön', answer: 'Cümlenin tamamı'
    } : {
      region: 'Quick review from this page', title: 'Quick review from this page',
      note: '{n} saved words or phrases · about 1 minute', start: 'Quick review',
      progress: '{i} / {n}', prompt: 'Complete the gaps with the forms used in this sentence.',
      word: 'Missing word or phrase', input: 'Type the form used here…',
      help: 'For several gaps, type the missing words from left to right, separated by spaces.',
      check: 'Check', reveal: 'Show answer', next: 'Next', finish: 'Finish',
      correct: 'Correct! You recalled the word in its context.', wrong: 'The form used in this sentence is shown below.',
      empty: 'Type an answer first, or choose “Show answer”.',
      done: 'Quick review complete', score: 'You recalled {c} of {n} without help.',
      again: 'Try again', close: 'Back to reading', answer: 'Complete sentence'
    };
    return (strings[key] || key).replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? ''));
  },
  el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (value == null || value === false) continue;
      if (key === 'text') node.textContent = value;
      else node.setAttribute(key, value === true ? '' : String(value));
    }
    for (const child of children.flat()) if (child != null && child !== false) node.append(child instanceof Node ? child : String(child));
    return node;
  },
  /* Each target must exactly cover a real token. This rejects arbitrary substrings,
     stale offsets, empty targets and targets that would remove the whole context. */
  clean(item) {
    if (!item || typeof item !== 'object' || typeof item.book !== 'string' || !item.book || item.book.length > 400
      || !Number.isInteger(item.page) || item.page < 0 || typeof item.id !== 'string' || !/^n:[^\s].{0,118}$/.test(item.id)
      || typeof item.word !== 'string' || !item.word.trim() || item.word.length > 80
      || typeof item.meaning !== 'string' || !item.meaning.trim() || item.meaning.length > 500
      || typeof item.sentence !== 'string' || item.sentence.length < 8 || item.sentence.length > 1600
      || !/[.!?…]["'”’)\]]*$/.test(item.sentence.trim())
      || !Array.isArray(item.ranges) || !item.ranges.length || item.ranges.length > 8
      || item.ranges.some(range => !range || typeof range !== 'object')) return null;
    const tokens = [...item.sentence.matchAll(/[\p{L}\p{N}]+(?:['’\-‐‑][\p{L}]+)*/gu)]
      .map(match => ({ start: match.index, end: match.index + match[0].length }));
    const ranges = item.ranges.map(range => ({ start: range.start, end: range.end })).sort((a, b) => a.start - b.start);
    if (ranges.some((range, i) => !Number.isInteger(range.start) || !Number.isInteger(range.end)
      || !tokens.some(token => token.start === range.start && token.end === range.end)
      || (i && range.start < ranges[i - 1].end))) return null;
    if (tokens.length < 3 || tokens.length - ranges.length < 2) return null;
    const answer = ranges.map(range => item.sentence.slice(range.start, range.end)).join(' ');
    if (!answer.trim()) return null;
    return { book: item.book, page: item.page, id: item.id, word: item.word.trim(), meaning: item.meaning.trim(),
      sentence: item.sentence, ranges, at: Number.isFinite(item.at) ? item.at : Date.now() };
  },
  sanitize(records) {
    if (!Array.isArray(records)) return [];
    const unique = new Map();
    for (const record of records.slice(-this.LIMIT * 2)) {
      const item = this.clean(record);
      if (!item) continue;
      const key = JSON.stringify([item.book, item.page, item.id]);
      unique.delete(key);
      unique.set(key, item);
    }
    return [...unique.values()].slice(-this.LIMIT);
  },
  snapshot() { return this.sanitize(this.records); },
  restore(records) {
    this.records = this.sanitize(records);
    this.session = null;
    this.persist();
    this.render();
  },
  clear() { this.restore([]); },
  persist() {
    this.records = this.sanitize(this.records);
    try { this.options.store.write(this.KEY, JSON.stringify(this.records)); } catch (_) { /* Practice remains usable without storage. */ }
  },
  /* Call after rendering a reader page. Saving never opens the practice automatically. */
  onPage(context) {
    this.context = context && typeof context.book === 'string' && Number.isInteger(context.page)
      ? { book: context.book, page: context.page } : null;
    this.session = null;
    this.render();
  },
  /* Call only for a word clicked in #novel-text, after Review's saved state changes.
     `ranges` are offsets into the full English sentence, including split particles. */
  saved(payload, on = true) {
    if (!this.options || !payload || typeof payload.id !== 'string') return;
    if (!on) {
      this.records = this.records.filter(item => item.id !== payload.id);
      this.persist();
      this.session = null;
      this.render();
      return;
    }
    const item = this.clean({ ...payload, at: Date.now() });
    if (!item) return;
    this.records = this.records.filter(record => !(record.book === item.book && record.page === item.page && record.id === item.id));
    this.records.push(item);
    this.persist();
    this.session = null;
    this.render();
  },
  eligible() {
    if (!this.context || !this.options) return [];
    return this.records.filter(item => {
      if (item.book !== this.context.book || item.page !== this.context.page) return false;
      try { return Boolean(this.options.isSaved(item.id)) && (!this.options.matchesPage || this.options.matchesPage(item)); } catch (_) { return false; }
    }).slice(-3);
  },
  hide() {
    this.context = null;
    this.session = null;
    if (this.root) this.root.hidden = true;
  },
  button(text, action, primary = false) {
    const button = this.el('button', { type: 'button', class: 'nqr-button' + (primary ? ' is-primary' : ''), text });
    button.addEventListener('click', action);
    return button;
  },
  render() {
    if (!this.root) return;
    this.root.setAttribute('aria-label', this.label('region'));
    const items = this.eligible();
    this.root.hidden = !items.length;
    if (!items.length) { this.session = null; this.root.replaceChildren(); return; }
    if (this.session) { this.renderQuestion(); return; }
    this.root.replaceChildren(
      this.el('div', { class: 'nqr-launch-copy' }, this.el('h3', { text: this.label('title') }), this.el('p', { text: this.label('note', { n: items.length }) })),
      this.button(this.label('start'), () => this.start(), true));
  },
  start() {
    const items = this.eligible();
    if (!items.length) { this.render(); return; }
    if (this.options.onOpen) this.options.onOpen();
    this.session = { items: items.map(item => ({ ...item })), at: 0, correct: 0, answered: false };
    this.renderQuestion();
  },
  sentence(item, reveal = false) {
    const node = this.el('p', { class: 'nqr-sentence', id: 'nqr-sentence', lang: 'en' });
    let from = 0;
    for (const range of item.ranges) {
      node.append(item.sentence.slice(from, range.start));
      const text = item.sentence.slice(range.start, range.end);
      node.append(reveal ? this.el('mark', { text }) : this.el('span', { class: 'nqr-gap', text: '_____' }));
      from = range.end;
    }
    node.append(item.sentence.slice(from));
    return node;
  },
  renderQuestion() {
    const session = this.session;
    if (!session) { this.render(); return; }
    const item = session.items[session.at];
    const input = this.el('input', { id: 'nqr-answer', type: 'text', autocomplete: 'off', autocapitalize: 'off', spellcheck: 'false',
      placeholder: this.label('input'), 'aria-describedby': 'nqr-sentence nqr-meaning nqr-help', lang: 'en' });
    const feedback = this.el('p', { class: 'nqr-feedback', 'aria-live': 'polite' });
    const actions = this.el('div', { class: 'nqr-actions' });
    const submit = this.el('button', { type: 'submit', class: 'nqr-button is-primary', text: this.label('check') });
    const form = this.el('form', { class: 'nqr-form' },
      this.el('label', { for: 'nqr-answer', text: this.label('word') }), input,
      this.el('p', { id: 'nqr-help', class: 'nqr-help', text: this.label('help') }), feedback, actions);
    const answer = item.ranges.map(range => item.sentence.slice(range.start, range.end)).join(' ');
    const respond = reveal => {
      if (session !== this.session || session.answered) return;
      if (!reveal && !input.value.trim()) { feedback.textContent = this.label('empty'); input.focus(); return; }
      const right = !reveal && this.normal(input.value) === this.normal(answer);
      if (right) session.correct++;
      session.answered = true;
      input.readOnly = true;
      feedback.textContent = this.label(right ? 'correct' : 'wrong');
      feedback.className = 'nqr-feedback ' + (right ? 'is-correct' : 'is-answer');
      form.querySelectorAll('button').forEach(button => { button.disabled = true; });
      const model = this.sentence(item, true);
      model.removeAttribute('id');
      actions.replaceChildren(this.el('div', { class: 'nqr-model' }, this.el('p', { class: 'nqr-help', text: this.label('answer') }), model),
        this.button(this.label(session.at + 1 === session.items.length ? 'finish' : 'next'), () => this.next(), true));
      actions.querySelector('button').focus({ preventScroll: true });
    };
    form.addEventListener('submit', event => { event.preventDefault(); respond(false); });
    actions.append(submit, this.button(this.label('reveal'), () => respond(true)));
    this.root.replaceChildren(
      this.el('div', { class: 'nqr-question-head' }, this.el('h3', { text: this.label('prompt') }),
        this.el('span', { text: this.label('progress', { i: session.at + 1, n: session.items.length }) })),
      this.sentence(item), this.el('p', { class: 'nqr-meaning', id: 'nqr-meaning', lang: 'tr', text: item.meaning }), form,
      this.button(this.label('close'), () => this.close()));
    input.focus({ preventScroll: true });
  },
  normal(value) { return value.normalize('NFKC').replace(/’/g, "'").replace(/[‐‑]/g, '-').toLocaleLowerCase('en').trim().replace(/\s+/g, ' '); },
  next() {
    const session = this.session;
    if (!session || !session.answered) return;
    if (++session.at < session.items.length) { session.answered = false; this.renderQuestion(); return; }
    this.root.replaceChildren(this.el('h3', { text: this.label('done') }),
      this.el('p', { class: 'nqr-result', 'aria-live': 'polite', text: this.label('score', { c: session.correct, n: session.items.length }) }),
      this.el('div', { class: 'nqr-actions' }, this.button(this.label('again'), () => this.start(), true), this.button(this.label('close'), () => this.close())));
    this.root.querySelector('button').focus({ preventScroll: true });
  },
  close() {
    this.session = null;
    this.render();
    this.root.querySelector('button')?.focus({ preventScroll: true });
  }
};
