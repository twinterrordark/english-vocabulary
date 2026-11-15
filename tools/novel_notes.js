/* Public reader annotations. Only successful server writes are called shared.
   Drafts and the anonymous author's ownership capability stay on this device. */
const NovelNotes = {
  // Persistent service deployed and health-checked before enabling public notes.
  API: 'https://english-vocabulary-notes.twinterrordark.workers.dev',
  KEY: 'english-study-public-notes.v1',
  DRAFT_KEY: 'english-study-note-drafts.v1',
  counts: new Map(),
  book: null,
  bookKey: null,
  current: null,
  wordRun: 0,
  copy(tr, en) { return lang === 'tr' ? tr : en; },
  normalize(word) { return String(word || '').normalize('NFKC').toLowerCase().replace(/[’‘]/g, "'").replace(/[‐‑‒–—]/g, '-').replace(/\s+/g, ' ').trim(); },
  read(key, fallback) { try { return JSON.parse(Store.read(key) || 'null') || fallback; } catch (_) { return fallback; } },
  init() {
    if (!this.API) return;
    this.identity = this.read(this.KEY, {});
    if (!/^[a-f0-9]{64}$/.test(this.identity.token || '')) {
      const bytes = crypto.getRandomValues(new Uint8Array(32));
      this.identity = { token: [...bytes].map(b => b.toString(16).padStart(2, '0')).join(''), author: '', own: [] };
    }
    this.identity.own = Array.isArray(this.identity.own) ? this.identity.own.filter(id => typeof id === 'string').slice(-1000) : [];
    this.drafts = this.read(this.DRAFT_KEY, {});
    if (typeof this.drafts !== 'object' || Array.isArray(this.drafts)) this.drafts = {};
    this.persistIdentity();
    this.root = h('details', { class: 'novel-notes', id: 'novel-notes' });
    $('#novel-pop').append(this.root);
    // Keep the reader extension separate from its word lookup and translation.
    const render = Novel.renderPage, show = Novel.showWord, close = Novel.closePop;
    Novel.renderPage = function (...args) { const result = render.apply(this, args); NovelNotes.onPage(this.book); return result; };
    Novel.showWord = function (...args) { const result = show.apply(this, args); NovelNotes.openCurrent(); return result; };
    Novel.closePop = function (...args) { NovelNotes.closeCurrent(); return close.apply(this, args); };
    this.timer = setInterval(() => { if (this.visible()) this.refresh(); }, 30000);
    document.addEventListener('visibilitychange', () => { if (this.visible()) this.refresh(); });
    window.addEventListener('online', () => { if (this.visible()) this.refresh(); });
  },
  persistIdentity() { Store.write(this.KEY, JSON.stringify(this.identity)); },
  visible() { return !document.hidden && Router.current === 'novel' && Novel.book && !$('#novel-reader').hidden; },
  async request(path, method = 'GET', body) {
    if (navigator.onLine === false) throw new Error('offline');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(this.API + path, { method, signal: controller.signal, headers: body ? { 'content-type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
      let result; try { result = await response.json(); } catch (_) { throw new Error('network'); }
      if (!response.ok) throw new Error(response.status === 429 ? 'rate' : response.status === 403 ? 'owner' : 'network');
      return result;
    } catch (error) { throw error.message === 'rate' || error.message === 'owner' ? error : new Error(navigator.onLine === false ? 'offline' : 'network'); }
    finally { clearTimeout(timer); }
  },
  async onPage(book) {
    if (!book) return;
    if (this.book === book) { this.paint(); return; }
    this.closeCurrent();
    this.book = book; this.bookKey = null; this.counts = new Map(); this.paint();
    this.bookPromise = (async () => {
      const text = book.pages.map(page => page.map(p => p.replace(/^[\u2060\u2061]/, '')).join(' ')).join(' ').normalize('NFKC').replace(/\s+/g, ' ').trim();
      const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
      return [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, '0')).join('');
    })();
    try {
      const key = await this.bookPromise;
      if (this.book !== book) return;
      this.bookKey = key;
      await this.refresh();
    } catch (_) { /* A failed public index never blocks the book itself. */ }
  },
  async refresh() {
    const key = this.bookKey;
    if (!key || this.indexLoading === key) return;
    this.indexLoading = key;
    try {
      const result = await this.request('/api/notes/index?book=' + key);
      if (this.bookKey !== key) return;
      this.counts = new Map((Array.isArray(result.words) ? result.words : []).filter(row => typeof row.word === 'string' && Number.isInteger(row.count) && row.count > 0).map(row => [row.word, row.count]));
      this.paint();
      if (this.current && !$('#novel-pop').hidden) this.loadNotes();
    } catch (_) { /* Preserve last known highlights during a transient outage. */ }
    finally { if (this.indexLoading === key) this.indexLoading = null; }
  },
  paint() {
    if (!this.root) return;
    const phraseNotes = [...this.counts.keys()].some(word => word.includes(' '));
    for (const node of $$('#novel-text .nw')) {
      const key = this.normalize(node.textContent);
      const base = this.normalize(Novel.lookup(node.textContent)?.base || key);
      let count = this.counts.get(base) || this.counts.get(key) || 0;
      if (!count && phraseNotes) {
        const context = Novel.sentenceSpan(node);
        const tokens = Novel.phraseTokens(context.text);
        const tapped = tokens.findIndex(token => context.start + token.at === context.offset);
        const phrase = tapped >= 0 ? Novel.findPhrase(tokens, tapped) : null;
        count = phrase ? this.counts.get(this.normalize(phrase.phrase)) || 0 : 0;
      }
      node.classList.toggle('has-public-note', count > 0);
      if (count) node.title = this.copy(count + ' ortak not', count + ' shared notes');
      else node.removeAttribute('title');
    }
  },
  draftKey() { return this.current ? this.bookKey + ':' + this.current.word : ''; },
  keepDraft() {
    if (!this.current || !this.text || this.editing) return;
    const key = this.draftKey();
    if (this.text.value.trim()) this.drafts[key] = this.text.value.slice(0, 1000); else delete this.drafts[key];
    const keys = Object.keys(this.drafts); for (const old of keys.slice(0, Math.max(0, keys.length - 30))) delete this.drafts[old];
    Store.write(this.DRAFT_KEY, JSON.stringify(this.drafts));
  },
  closeCurrent() {
    this.keepDraft(); this.wordRun++; this.current = null; this.editing = null;
    this.root?.replaceChildren(); this.text = null;
  },
  async openCurrent() {
    this.closeCurrent();
    const selected = Novel.current;
    if (!selected || !Novel.book) { this.root.hidden = true; return; }
    this.root.hidden = false;
    const word = this.normalize(selected.review?.w || selected.word);
    if (!word || word.length > 100) return;
    const run = this.wordRun;
    this.current = { word, selected };
    this.summary = h('summary', { text: this.copy('Okur notları', 'Reader notes') });
    this.root.replaceChildren(this.summary, h('p', { class: 'hint', text: this.copy('Notlar yükleniyor…', 'Loading notes…') }));
    const book = this.book;
    let key;
    try { key = this.bookKey || await this.bookPromise; } catch (_) { return; }
    if (this.wordRun !== run || !this.current || this.book !== book) return;
    this.bookKey = key;
    this.root.open = (this.counts.get(word) || 0) > 0;
    this.list = h('ul', { class: 'novel-notes-list' });
    this.status = h('p', { class: 'hint', role: 'status', 'aria-live': 'polite' });
    this.author = h('input', { id: 'novel-note-author', type: 'text', maxlength: '40', autocomplete: 'nickname', value: typeof this.identity.author === 'string' ? this.identity.author : '' });
    this.text = h('textarea', { id: 'novel-note-body', maxlength: '1000', rows: '3', placeholder: this.copy('Bu kelime için bir açıklama veya örnek yaz…', 'Add an explanation or example for this word…') });
    this.text.value = typeof this.drafts[this.draftKey()] === 'string' ? this.drafts[this.draftKey()] : '';
    this.text.addEventListener('input', () => this.keepDraft());
    this.send = h('button', { type: 'submit', class: 'button small primary', text: this.copy('Notu paylaş', 'Share note') });
    this.cancel = h('button', { type: 'button', class: 'button small ghost', hidden: '', text: this.copy('Vazgeç', 'Cancel') });
    this.cancel.addEventListener('click', () => { this.editing = null; this.text.value = this.drafts[this.draftKey()] || ''; this.cancel.hidden = true; this.send.textContent = this.copy('Notu paylaş', 'Share note'); });
    const form = h('form', { class: 'novel-note-form' },
      h('label', { for: 'novel-note-author', text: this.copy('Takma ad (isteğe bağlı)', 'Nickname (optional)') }), this.author,
      h('label', { for: 'novel-note-body', text: this.copy('Notun', 'Your note') }), this.text,
      h('p', { class: 'hint', text: this.copy('Paylaştığın notu bu kitabı okuyan herkes görebilir.', 'Everyone reading this book can see a shared note.') }),
      h('div', { class: 'row' }, this.send, this.cancel));
    form.addEventListener('submit', event => { event.preventDefault(); this.save(); });
    this.root.replaceChildren(this.summary, this.list, this.status, form);
    await this.loadNotes();
  },
  async loadNotes() {
    if (!this.current || !this.bookKey || !this.list) return;
    const run = this.wordRun, request = this.listRun = (this.listRun || 0) + 1, word = this.current.word;
    try {
      const result = await this.request('/api/notes?book=' + this.bookKey + '&word=' + encodeURIComponent(word));
      if (this.wordRun !== run || this.listRun !== request) return;
      this.notes = (Array.isArray(result.notes) ? result.notes : []).filter(note => typeof note.id === 'string' && typeof note.body === 'string' && typeof note.author === 'string');
      this.counts.set(word, this.notes.length);
      if (!this.notes.length) this.counts.delete(word);
      this.summary.textContent = this.copy('Okur notları', 'Reader notes') + (this.notes.length ? ' (' + this.notes.length + ')' : ' · ' + this.copy('Not ekle', 'Add note'));
      this.status.textContent = this.notes.length ? '' : this.copy('Bu kelime için henüz ortak not yok.', 'No shared notes for this word yet.');
      this.list.replaceChildren(...this.notes.map(note => this.noteRow(note)));
      if (this.notes.length) this.root.open = true;
      this.paint();
    } catch (error) {
      if (this.wordRun === run && this.listRun === request) this.status.textContent = this.failure(error);
    }
  },
  noteRow(note) {
    const date = new Date(note.createdAt);
    const meta = h('div', { class: 'novel-note-meta' }, h('strong', { text: note.author || this.copy('Okur', 'Reader') }),
      Number.isNaN(date.getTime()) ? null : h('time', { dateTime: date.toISOString(), text: date.toLocaleDateString(lang === 'tr' ? 'tr-TR' : 'en-GB') }));
    const row = h('li', { 'data-note-id': note.id }, meta, h('p', { text: note.body }));
    if (this.identity.own.includes(note.id)) {
      const edit = h('button', { type: 'button', class: 'link-button', text: this.copy('Düzenle', 'Edit') });
      edit.addEventListener('click', () => { this.keepDraft(); this.editing = note.id; this.text.value = note.body; this.author.value = note.author; this.cancel.hidden = false; this.send.textContent = this.copy('Değişikliği kaydet', 'Save changes'); this.text.focus(); });
      const remove = h('button', { type: 'button', class: 'link-button', text: this.copy('Sil', 'Delete') });
      remove.addEventListener('click', () => this.remove(note.id));
      row.append(h('div', { class: 'row' }, edit, remove));
    }
    return row;
  },
  failure(error) {
    if (error.message === 'rate') return this.copy('Kısa sürede çok fazla not paylaşıldı. Biraz sonra tekrar dene.', 'Too many notes were shared. Please try again shortly.');
    if (error.message === 'owner') return this.copy('Bu not bu cihazdan değiştirilemiyor.', 'This device cannot change that note.');
    return this.copy('Ortak not servisine ulaşılamadı. Taslağın bu cihazda duruyor; henüz paylaşılmadı.', 'The shared notes service is unavailable. Your draft stays on this device and has not been shared.');
  },
  async save() {
    if (!this.current || this.busy) return;
    const body = this.text.value.trim();
    if (!body || body.length > 1000) { this.status.textContent = this.copy('1–1000 karakter arasında bir not yaz.', 'Write a note of 1–1000 characters.'); this.text.focus(); return; }
    const run = this.wordRun, word = this.current.word, book = this.bookKey, editing = this.editing;
    const author = this.author.value.trim().slice(0, 40) || this.copy('Okur', 'Reader');
    this.identity.author = author; this.persistIdentity(); this.keepDraft();
    this.busy = true; this.send.disabled = true;
    this.status.textContent = this.copy('Paylaşılıyor…', 'Sharing…');
    // Reuse this key after uncertain network results, preventing duplicate notes.
    this.pending = this.pending && this.pending.body === body && this.pending.word === word && this.pending.book === book ? this.pending : { book, word, body, id: crypto.randomUUID() };
    try {
      const result = await this.request(editing ? '/api/notes/' + encodeURIComponent(editing) : '/api/notes', editing ? 'PUT' : 'POST', { book, word, body, author, token: this.identity.token, requestId: this.pending.id });
      if (!result.note || typeof result.note.id !== 'string') throw new Error('network');
      this.identity.own = [...new Set([...this.identity.own, result.note.id])].slice(-1000); this.persistIdentity();
      delete this.drafts[book + ':' + word]; Store.write(this.DRAFT_KEY, JSON.stringify(this.drafts)); this.pending = null;
      if (this.wordRun === run) {
        this.text.value = ''; this.editing = null; this.cancel.hidden = true; this.send.textContent = this.copy('Notu paylaş', 'Share note');
        await this.loadNotes(); this.status.textContent = this.copy('Not paylaşıldı.', 'Note shared.');
      }
      await this.refresh();
    } catch (error) { if (this.wordRun === run) this.status.textContent = this.failure(error); }
    finally { this.busy = false; if (this.send && this.wordRun === run) this.send.disabled = false; }
  },
  async remove(id) {
    if (!this.current || this.busy) return;
    const confirmed = await confirmDialog({ title: this.copy('Not silinsin mi?', 'Delete this note?'), message: this.copy('Bu not diğer okurlardan da kaldırılacak.', 'This note will also disappear for other readers.'), confirmLabel: this.copy('Sil', 'Delete') });
    if (!confirmed) return;
    const run = this.wordRun;
    try {
      await this.request('/api/notes/' + encodeURIComponent(id), 'DELETE', { token: this.identity.token });
      this.identity.own = this.identity.own.filter(own => own !== id); this.persistIdentity();
      if (this.wordRun === run) await this.loadNotes();
      await this.refresh();
    } catch (error) { if (this.wordRun === run) this.status.textContent = this.failure(error); }
  }
};
