/* Guided study: real practice events, never navigation clicks or elapsed page time. */
const Study = {
  KEY: 'english-study-plan.v1',
  LEVELS: ['A2', 'B1', 'B2', 'C1'],
  TIMES: [15, 30, 45],
  state: null,
  run: null,
  recording: null,
  recToken: 0,
  copy(tr, en) { return lang === 'tr' ? tr : en; },
  button(text, action, attrs = {}) {
    const node = h('button', { type: 'button', class: 'button', ...attrs, text });
    node.addEventListener('click', action);
    return node;
  },
  wordCount(text) { return (String(text).match(/[A-Za-z]+(?:['’-][A-Za-z]+)*/g) || []).length; },
  sentenceCount(text) { return String(text).split(/[.!?]+(?:\s|$)|\n+/).filter(part => this.wordCount(part) >= 3).length; },
  init() {
    this.grammarIds = new Set(Grammar.topics.flatMap(topic => topic.units.map(unit => unit.id)));
    this.readingKeys = new Set(READINGS.flatMap(passage => passage.questions.map((_, i) => passage.id + ':' + i)));
    let raw;
    try { raw = JSON.parse(Store.read(this.KEY) || 'null'); } catch (_) { /* fresh plan */ }
    this.state = this.sanitize(raw) || { version: 1, prefs: { minutes: 30, level: this.LEVELS.includes(progress.settings.path) ? progress.settings.path : 'A2' }, days: {} };
    this.day();
    window.addEventListener('pagehide', () => { if (this.draftTimer) this.save(); });
  },
  sanitize(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw) || raw.version !== 1) return null;
    const prefs = raw.prefs || {};
    const out = { version: 1, prefs: { minutes: this.TIMES.includes(prefs.minutes) ? prefs.minutes : 30, level: this.LEVELS.includes(prefs.level) ? prefs.level : 'A2' }, days: {} };
    const ids = (list, valid, max = 100) => Array.isArray(list) ? [...new Set(list.filter(id => typeof id === 'string' && valid(id)))].slice(0, max) : [];
    const validWord = id => BY_ID.has(id);
    for (const [date, saved] of Object.entries(raw.days || {}).filter(([date]) => /^\d{4}-\d{2}-\d{2}$/.test(date)).sort().slice(-60)) {
      if (!saved || typeof saved !== 'object' || Array.isArray(saved)) continue;
      const config = saved.config;
      const validConfig = config && this.LEVELS.includes(config.level) && this.TIMES.includes(config.minutes)
        && READINGS.some(passage => passage.id === config.passage)
        && (!config.grammar || this.grammarIds.has(config.grammar))
        && ['reviewTarget', 'recallTarget', 'writingTarget', 'speechTarget'].every(key => Number.isInteger(config[key]) && config[key] >= 0 && config[key] <= 200);
      const day = { date, config: validConfig ? { level: config.level, minutes: config.minutes, passage: config.passage, grammar: config.grammar || null,
        reviewTarget: config.reviewTarget, recallTarget: config.recallTarget, writingTarget: config.writingTarget, speechTarget: config.speechTarget } : null,
        reviewed: ids(saved.reviewed, id => /^[wgn]:[^\x00-\x1f]{1,180}$/.test(id)),
        grammar: ids(saved.grammar, id => this.grammarIds.has(id)), reading: {}, listened: ids(saved.listened, id => READINGS.some(p => p.id === id), 30),
        writing: typeof saved.writing === 'string' ? saved.writing.slice(0, 6000) : '', written: saved.written === true,
        spoken: Number.isFinite(saved.spoken) ? Math.min(600, Math.max(0, saved.spoken)) : 0,
        tutor: ids(saved.tutor, line => line.length <= 1000 && this.wordCount(line) >= 5, 20), pool: ids(saved.pool, validWord, 10), hints: ids(saved.hints, validWord, 10), recall: {} };
      for (const [key, value] of Object.entries(saved.reading || {})) if (this.readingKeys.has(key) && typeof value === 'boolean') day.reading[key] = value;
      for (const [id, value] of Object.entries(saved.recall || {}).slice(0, 60)) {
        if (validWord(id) && value && typeof value === 'object') day.recall[id] = { first: value.first === true, correct: value.correct === true, attempts: Math.min(100, Math.max(1, Number.isInteger(value.attempts) ? value.attempts : 1)) };
      }
      out.days[date] = day;
    }
    return out;
  },
  snapshot() { return JSON.parse(JSON.stringify(this.state)); },
  restore(raw) {
    const next = this.sanitize(raw);
    if (!next) return false;
    this.away(); this.discardRecording(); this.state = next; this.run = null; this.day(); this.save();
    if (Router.current === 'home') this.renderHome();
    if (Router.current === 'study') this.onShow();
    return true;
  },
  clear() {
    this.away(); this.discardRecording(); this.state.days = {}; this.run = null; this.day(); this.save();
    if (Router.current === 'home') this.renderHome();
  },
  save() {
    clearTimeout(this.draftTimer); this.draftTimer = null;
    const keys = Object.keys(this.state.days).sort();
    for (const key of keys.slice(0, -60)) delete this.state.days[key];
    Store.write(this.KEY, JSON.stringify(this.state));
  },
  queueSave() { clearTimeout(this.draftTimer); this.draftTimer = setTimeout(() => this.save(), 350); },
  grammarPick(level) {
    const core = ['bs', 'tn', 'nn', 'aj', 'pp', 'md', 'ps', 'cn', 'rs', 'gi'];
    const ceiling = { A1: 0, A2: 1, B1: 2, B2: 3, C1: 4 }[level];
    const topics = Grammar.topics.filter(topic => core.includes(topic.id));
    if (Grammar.lastTopic) topics.sort((a, b) => Number(b.id === Grammar.lastTopic) - Number(a.id === Grammar.lastTopic));
    for (const topic of topics) {
      const index = topic.units.findIndex((unit, i) => !Grammar.learned[unit.id] && (i === 0 || Grammar.learned[topic.units[i - 1].id])
        && ({ A1: 0, A2: 1, B1: 2, B2: 3 }[topic.lessons[unit.lesson].level] ?? 0) <= ceiling);
      if (index >= 0) return topic.units[index].id;
    }
    return null;
  },
  plan() {
    const { minutes, level } = this.state.prefs;
    let passages = READINGS.filter(p => p.level === level || (level === 'B2' && p.level === 'B1–B2'));
    if (!passages.length) passages = READINGS;
    const due = Review.due().length;
    return { minutes, level, passage: passages[Review.today() % passages.length].id, grammar: this.grammarPick(level),
      reviewTarget: Math.min(minutes === 15 ? 4 : minutes === 30 ? 8 : 12, due || Review.newWords(level).length),
      recallTarget: minutes === 15 ? 3 : minutes === 30 ? 5 : 8,
      writingTarget: Math.round(({ A2: 25, B1: 45, B2: 65, C1: 85 }[level]) * (minutes === 15 ? .7 : minutes === 45 ? 1.2 : 1)),
      speechTarget: minutes === 15 ? 30 : minutes === 30 ? 60 : 90 };
  },
  day() {
    const date = dateKey(new Date());
    let day = this.state.days[date];
    if (!day) day = this.state.days[date] = { date, config: null, reviewed: [], grammar: [], reading: {}, listened: [], writing: '', written: false, spoken: 0, tutor: [], pool: [], hints: [], recall: {} };
    if (!day.config) { day.config = this.plan(); this.save(); }
    return day;
  },
  passage() { return READINGS.find(passage => passage.id === this.day().config.passage) || READINGS[0]; },
  grammarUnit(id) {
    for (const topic of Grammar.topics) { const index = topic.units.findIndex(unit => unit.id === id); if (index >= 0) return { topic, unit: topic.units[index], index }; }
    return null;
  },
  noteReview(id) { const day = this.day(); if (!day.reviewed.includes(id) && day.reviewed.length < 100) { day.reviewed.push(id); this.save(); } },
  noteGrammar(id) { const day = this.day(); if (!day.grammar.includes(id) && day.grammar.length < 30) { day.grammar.push(id); this.save(); } },
  noteReading(id, index, correct) { this.day().reading[id + ':' + index] = Boolean(correct); this.save(); },
  noteListening(id) { const day = this.day(); if (!day.listened.includes(id)) { day.listened.push(id); this.save(); } },
  noteTutor(text) { const day = this.day(); const clean = text.trim().slice(0, 1000); if (this.wordCount(clean) >= 5 && !day.tutor.includes(clean) && day.tutor.length < 20) { day.tutor.push(clean); this.save(); } },
  steps() {
    const day = this.day(), config = day.config, passage = this.passage();
    const grammar = this.grammarUnit(config.grammar);
    const read = passage.questions.filter((_, i) => day.reading[passage.id + ':' + i]).length;
    const recalled = day.pool.filter(id => day.recall[id]?.correct).length;
    const output = (day.written && this.wordCount(day.writing) >= config.writingTarget && this.sentenceCount(day.writing) >= 3) || day.spoken >= config.speechTarget || day.tutor.length >= 2;
    const mins = config.minutes === 15 ? [3, 3, 4, 3, 2] : config.minutes === 30 ? [6, 6, 7, 7, 4] : [9, 9, 11, 11, 5];
    return [
      { id: 'review', title: this.copy('Önce hatırla', 'Recall first'), note: this.copy(`${Math.min(day.reviewed.length, config.reviewTarget)}/${config.reviewTarget} farklı kartı yanıtladın`, `${Math.min(day.reviewed.length, config.reviewTarget)}/${config.reviewTarget} different cards answered`),
        done: day.reviewed.length >= config.reviewTarget, href: Review.due().length ? '#review' : '#review/learn/' + config.level },
      { id: 'grammar', title: this.copy('Bir yapıyı öğren ve dene', 'Learn and test one structure'), note: grammar ? grammar.unit.title : this.copy('Temel derslerin tamamı çalışıldı', 'Core lessons already completed'),
        done: !grammar || day.grammar.includes(config.grammar), href: grammar ? '#grammar/' + grammar.topic.id + '/' + grammar.index : '#grammar' },
      { id: 'input', title: this.copy('Dinle, oku, anlamını kontrol et', 'Listen, read and check meaning'), note: passage.title + ` · ${read}/${passage.questions.length}`, done: read === passage.questions.length, href: '#reading/' + passage.id },
      { id: 'output', title: this.copy('Kendi cümlelerinle anlat', 'Express it in your own words'), note: this.copy(`${config.writingTarget}+ kelime yaz veya ${config.speechTarget} sn sesli anlat`, `Write ${config.writingTarget}+ words or speak for ${config.speechTarget} seconds`), done: output, href: '#study/output' },
      { id: 'recall', title: this.copy('Seçeneksiz hatırlama kontrolü', 'Recall without answer options'), note: this.copy(`${recalled}/${config.recallTarget} kelime yardımsız hatırlandı`, `${recalled}/${config.recallTarget} words recalled without hints`), done: recalled >= config.recallTarget, href: '#study/recall' }
    ].map((step, i) => ({ ...step, minutes: mins[i] }));
  },
  renderHome() {
    const root = $('#study-home');
    if (!root || !this.state) return;
    const day = this.day(), steps = this.steps(), done = steps.filter(step => step.done).length;
    const next = steps.find(step => !step.done);
    const minutes = h('select', { id: 'study-minutes' }, this.TIMES.map(n => h('option', { value: n, text: this.copy(`${n} dakika`, `${n} minutes`) })));
    minutes.value = this.state.prefs.minutes;
    const level = h('select', { id: 'study-level' }, this.LEVELS.map(value => h('option', { value, text: value })));
    level.value = this.state.prefs.level;
    const change = () => { this.discardRecording(); this.state.prefs = { minutes: Number(minutes.value), level: level.value }; day.config = this.plan(); day.pool = []; this.run = null; this.save(); this.renderHome(); };
    minutes.addEventListener('change', change); level.addEventListener('change', change);
    root.replaceChildren(
      h('div', { class: 'study-heading' }, h('div', {}, h('span', { class: 'eyebrow', text: this.copy('GENEL İNGİLİZCE', 'GENERAL ENGLISH') }), h('h2', { text: this.copy('Bugün ne çalışacağım?', 'What should I study today?') })), h('span', { class: 'chip level', text: `${day.config.level} · ${day.config.minutes} ${this.copy('dk', 'min')}` })),
      h('p', { class: 'lead', text: this.copy('Hatırla, anla ve kendi cümlelerini üret. Her adım seni gerçekten yaptığın çalışmaya göre yönlendirir.', 'Recall, understand and produce your own sentences. Each step follows the practice you actually do.') }),
      h('a', { id: 'study-next', class: 'button primary study-start', href: next ? next.href : '#study/recall', text: next ? this.copy('Sıradaki: ', 'Next: ') + next.title : this.copy('Bugünkü tur tamam · kısa tekrar yap', 'Daily round complete · practise again') }),
      h('div', { class: 'study-meter' }, h('span', { id: 'study-progress-text', text: this.copy(`${done}/5 adım tamamlandı`, `${done}/5 steps completed`) }), h('span', { text: this.copy('Süreler yaklaşık', 'Times are approximate') })),
      h('progress', { value: done, max: 5, 'aria-label': this.copy('Günlük öğrenme adımları', 'Daily learning steps') }),
      h('ol', { class: 'study-steps' }, steps.map((step, i) => h('li', { class: 'study-step' + (step.done ? ' is-done' : next?.id === step.id ? ' is-next' : ''), 'data-study-step': step.id },
        h('span', { class: 'study-step-number', 'aria-hidden': 'true', text: step.done ? '✓' : i + 1 }),
        h('span', { class: 'study-step-text' }, h('strong', { text: step.title }), h('small', { text: step.note }), h('small', { text: `${step.minutes} ${this.copy('dk', 'min')}` })),
        h('a', { href: step.href, 'aria-label': step.title }, icon('next'))))),
      h('details', { class: 'study-options' }, h('summary', { text: this.copy('Süreyi ve kelime yolunu ayarla', 'Choose your time and vocabulary path') }),
        h('div', { class: 'study-fields' }, h('label', { class: 'field', for: 'study-minutes' }, this.copy('Günlük süre', 'Daily time'), minutes), h('label', { class: 'field', for: 'study-level' }, this.copy('Kelime yolu', 'Vocabulary path'), level)),
        h('p', { class: 'study-note', text: this.copy('A2–C1 seçimi bir çalışma tercihidir, seviye sınavı değildir. Bugün yaptığın çalışmalar korunur.', 'A2–C1 is a study preference, not a placement test. Today’s practice is retained.') })),
      h('p', { class: 'study-note', text: this.copy('Bir adımı açmak tamamlamak değildir. Sayaçlar verilen yanıtlar, ders testi ve kendi üretiminle ilerler.', 'Opening a step does not complete it. Answers, lesson tests and your own output move the counters.') }));
    root.insertBefore(root.querySelector('.study-options'), $('#study-next'));
  },
  onShow() {
    this.away();
    const mode = location.hash.split('/')[1];
    $('#study-title').textContent = mode === 'recall' ? this.copy('Cevabı kendin hatırla', 'Retrieve the answer yourself') : this.copy('Kendi cümlelerinle anlat', 'Express it in your own words');
    if (mode === 'recall') this.renderRecall(); else this.renderOutput();
  },
  task() {
    const passage = this.passage();
    return passage.task || { en: 'Summarise the text in your own words. Connect it to your own life and explain one opinion with a reason.', tr: 'Metni kendi cümlelerinle özetle. Kendi hayatınla bağlantı kur ve bir görüşünü nedeniyle açıkla.', frames: ['The text is about…', 'In my experience…', 'I think… because…'] };
  },
  prompt() {
    const task = this.task();
    return h('div', { class: 'study-prompt' }, h('p', { class: 'eyebrow', text: this.passage().title }), h('p', { lang: 'en', text: task.en }),
      lang === 'tr' ? h('p', { lang: 'tr', class: 'hint', text: task.tr }) : null,
      h('ul', {}, task.frames.map(text => h('li', { lang: 'en', text }))));
  },
  renderOutput() {
    const day = this.day();
    const box = $('#study-app');
    const speak = location.hash.split('/')[1] === 'speak';
    const text = h('textarea', { id: 'study-writing', lang: 'en', rows: 7, maxlength: 6000, placeholder: this.copy('Örnek cümleleri kopyalamadan İngilizce anlat…', 'Write in English without copying the example sentences…') });
    text.value = day.writing;
    const count = h('p', { class: 'hint', id: 'study-writing-count' });
    const update = () => { day.writing = text.value; day.written = false; count.textContent = this.copy(`${this.wordCount(text.value)}/${day.config.writingTarget} kelime · en az 3 cümle`, `${this.wordCount(text.value)}/${day.config.writingTarget} words · at least 3 sentences`); this.queueSave(); };
    text.addEventListener('input', update);
    count.textContent = this.copy(`${this.wordCount(text.value)}/${day.config.writingTarget} kelime · en az 3 cümle`, `${this.wordCount(text.value)}/${day.config.writingTarget} words · at least 3 sentences`);
    const feedback = h('p', { class: 'study-feedback', id: 'study-writing-feedback', role: 'status' });
    const save = this.button(this.copy('Yazma çalışmamı kaydet', 'Save my writing practice'), () => {
      if (this.wordCount(text.value) < day.config.writingTarget || this.sentenceCount(text.value) < 3 || new Set((text.value.toLowerCase().match(/[a-z]+/g) || [])).size < 8) {
        feedback.textContent = this.copy(`En az ${day.config.writingTarget} kelime ve 3 anlamlı cümle yaz. Bir fikir, örnek ve neden eklemeyi dene.`, `Write at least ${day.config.writingTarget} words and 3 sentences. Include an idea, an example and a reason.`); text.focus(); return;
      }
      day.writing = text.value; day.written = true; this.save();
      feedback.textContent = this.copy('Yazma çalışman kaydedildi. Bu, dilbilgisi puanı değildir; geri bildirimle gözden geçirebilirsin.', 'Writing practice saved. This is not a grammar score; you can now review it with feedback.');
    }, { class: 'button primary', id: 'study-writing-save' });
    const grammar = this.button(this.copy('Yazımı geri bildirimle incele', 'Review my writing with feedback'), () => {
      if (!text.value.trim()) { text.focus(); return; }
      const id = 'study-' + day.date;
      let story = Writer.stories.find(item => item.id === id);
      if (!story) { story = { id }; Writer.stories.push(story); }
      Object.assign(story, { title: this.passage().title, text: text.value, updated: Date.now() }); Writer.save();
      location.hash = '#grammar/write/' + id;
    }, { id: 'study-writing-review' });
    box.replaceChildren(h('a', { class: 'study-return', href: '#reading/' + this.passage().id, text: this.copy('← Metne ve dinlemeye dön', '← Return to the text and listening') }),
      h('nav', { class: 'study-mode', 'aria-label': this.copy('Anlatım biçimi', 'Output mode') },
        h('a', { class: 'button' + (!speak ? ' primary' : ''), href: '#study/output', 'aria-current': !speak ? 'page' : null, text: this.copy('Yazılı anlatım', 'Writing') }),
        h('a', { class: 'button' + (speak ? ' primary' : ''), href: '#study/speak', 'aria-current': speak ? 'page' : null, text: this.copy('Sesli anlatım', 'Speaking') })), this.prompt(),
      h('section', { class: 'panel', hidden: speak }, h('h2', { text: this.copy('Yazılı anlatım', 'Writing practice') }), h('label', { for: 'study-writing', text: this.copy('Kendi İngilizce metnin', 'Your own English text') }), text, count, h('div', { class: 'row' }, save, grammar), feedback),
      h('section', { class: 'panel', hidden: !speak }, h('h2', { text: this.copy('Sesli anlatım', 'Speaking practice') }),
        h('p', { text: this.copy(`Aynı konuyu ${day.config.speechTarget} saniye kendi cümlelerinle anlat. Kaydını dinle; sonra aynı fikri daha rahat anlatmayı dene. Yazma ve sesli anlatımdan biri üretim adımını tamamlar.`, `Explain the same topic for ${day.config.speechTarget} seconds. Listen back, then try expressing it more smoothly. Either writing or speaking completes the output step.`) }),
        h('div', { id: 'study-record', class: 'study-record' }),
        h('p', { class: 'study-note', text: this.copy('Ses kaydı bu sekmede kalır ve gönderilmez. Konuşma süresi telaffuz ya da yeterlilik puanı değildir.', 'The recording stays in this tab and is not uploaded. Speaking time is not a pronunciation or proficiency score.') }),
        h('a', { class: 'button', href: '#tutor', text: this.copy('İstersen yapay zekâ öğretmeniyle konuş (çevrim içi)', 'Or talk to the AI teacher (online)') })),
      h('a', { class: 'button primary study-start', href: '#home', text: this.copy('Günlük yoluma dön', 'Return to my daily path') }));
    this.renderRecorder();
  },
  renderRecorder(message = '') {
    const root = $('#study-record');
    if (!root) return;
    const time = h('span', { class: 'study-record-time', id: 'study-record-time', role: 'timer', 'aria-label': this.copy('Konuşma süresi', 'Speaking time'), text: '0:00' });
    const start = this.button(this.copy('Mikrofonla kaydet', 'Record with microphone'), () => this.startRecorder(), { id: 'study-record-start' });
    const stop = this.button(this.copy('Kaydı durdur', 'Stop recording'), () => this.stopRecorder(), { id: 'study-record-stop', hidden: true });
    const status = h('p', { id: 'study-record-status', role: 'status', text: message });
    root.replaceChildren(time, h('div', { class: 'row' }, start, stop), status);
    const recording = this.recording;
    if (recording && recording.date === this.day().date && recording.url) {
      const audio = h('audio', { controls: true, src: recording.url, 'aria-label': this.copy('Kendi ses kaydın', 'Your recording') });
      const target = this.day().config.speechTarget;
      const finish = this.button(this.copy('Kaydımı dinledim · çalışmayı kaydet', 'I listened back · save practice'), () => {
        if (recording.seconds < target || !recording.heard) return;
        this.day().spoken = Math.max(this.day().spoken, recording.seconds); this.save();
        status.textContent = this.copy('Sesli anlatım çalışman kaydedildi. Aynı fikri daha akıcı anlatmak için yeniden deneyebilirsin.', 'Speaking practice saved. Try expressing the same idea more fluently in another recording.');
      }, { id: 'study-record-save', disabled: !recording.heard || recording.seconds < target });
      audio.addEventListener('timeupdate', () => { if (audio.currentTime >= Math.min(5, recording.seconds / 2)) { recording.heard = true; finish.disabled = recording.seconds < target; } });
      time.textContent = this.formatTime(recording.seconds);
      status.textContent = recording.seconds < target ? this.copy(`Bu kayıt ${recording.seconds} saniye. Hedef ${target} saniye; yeniden deneyebilirsin.`, `This recording is ${recording.seconds} seconds; the target is ${target}. Try again.`) : this.copy('Kaydının en az 5 saniyesini dinle, sonra çalışmanı kaydet.', 'Listen to at least 5 seconds, then save your practice.');
      root.append(audio, finish);
    }
  },
  formatTime(seconds) { return Math.floor(seconds / 60) + ':' + String(Math.floor(seconds % 60)).padStart(2, '0'); },
  async startRecorder() {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) { this.renderRecorder(this.copy('Bu tarayıcıda ses kaydı kullanılamıyor. Yazma alıştırmasıyla devam edebilirsin.', 'Recording is unavailable in this browser. You can complete the writing activity instead.')); return; }
    if (this.recorder && this.recorder.state !== 'inactive') return;
    const token = ++this.recToken;
    $('#study-record-start').disabled = true;
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (token !== this.recToken || Router.current !== 'study') { stream.getTracks().forEach(track => track.stop()); return; }
      this.discardRecording(); this.stream = stream;
      const generation = this.recordGeneration;
      const recorder = this.recorder = new MediaRecorder(stream);
      const chunks = [], started = performance.now(), date = this.day().date;
      recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = () => {
        clearInterval(this.recordTimer); stream.getTracks().forEach(track => track.stop());
        if (generation !== this.recordGeneration) return;
        const seconds = Math.floor((performance.now() - started) / 1000);
        const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
        this.recording = blob.size ? { date, seconds, url: URL.createObjectURL(blob), heard: false } : null;
        if (Router.current === 'study' && location.hash.split('/')[1] !== 'recall') this.renderRecorder();
      };
      recorder.onerror = () => { this.stopRecorder(); this.renderRecorder(this.copy('Kayıt alınamadı. Yazma alıştırmasıyla devam edebilirsin.', 'Recording failed. You can continue with writing.')); };
      recorder.start();
      $('#study-record-stop').hidden = false;
      $('#study-record-status').textContent = this.copy('Kaydediliyor…', 'Recording…');
      this.recordTimer = setInterval(() => {
        const seconds = Math.floor((performance.now() - started) / 1000);
        const timer = $('#study-record-time'); if (timer) timer.textContent = this.formatTime(seconds);
        if (seconds >= 180) this.stopRecorder();
      }, 500);
    } catch (_) {
      if (stream) stream.getTracks().forEach(track => track.stop());
      if (token === this.recToken && Router.current === 'study') this.renderRecorder(this.copy('Mikrofon açılamadı. Tarayıcı iznini kontrol edebilir veya yazmayla devam edebilirsin.', 'The microphone could not be opened. Check browser permission or continue with writing.'));
    }
  },
  stopRecorder() {
    clearInterval(this.recordTimer);
    if (this.recorder && this.recorder.state !== 'inactive') this.recorder.stop();
    if (this.stream) this.stream.getTracks().forEach(track => track.stop());
  },
  discardRecording() {
    this.recordGeneration = (this.recordGeneration || 0) + 1;
    if (this.recording?.url) URL.revokeObjectURL(this.recording.url);
    this.recording = null;
  },
  away() {
    if (this.draftTimer) this.save();
    this.recToken++;
    this.stopRecorder();
    const audio = $('#study-record audio'); if (audio) audio.pause();
  },
  prepareRecall() {
    const day = this.day();
    if (!day.pool.length) {
      const level = day.config.level;
      const reviewed = day.reviewed.filter(id => id.startsWith('w:')).map(id => id.slice(2));
      const mistakes = Object.entries(Review.state.cards).filter(([id, card]) => id.startsWith('w:') && card[4] > 0 && (card[3] < 3 || card[0] <= Review.today()))
        .sort((a, b) => b[1][4] - a[1][4]).map(([id]) => id.slice(2));
      const source = [...mistakes.slice(0, 2), ...reviewed, ...mistakes.slice(2), ...learnedSet, ...VOCAB.filter(entry => entry.level === level).map(entry => entry.id), ...VOCAB.map(entry => entry.id)];
      const seen = new Set();
      day.pool = [...new Set(source)].filter(id => {
        const entry = BY_ID.get(id); if (!entry || !entry.meaning || seen.has(normalize(entry.word))) return false;
        seen.add(normalize(entry.word)); return true;
      }).slice(0, day.config.recallTarget);
      day.config.recallTarget = day.pool.length;
      this.save();
    }
    if (!this.run || this.run.date !== day.date) this.run = { date: day.date, queue: day.pool.filter(id => !day.recall[id]?.correct).sort((a, b) => (day.recall[a]?.attempts || 0) - (day.recall[b]?.attempts || 0)), hinted: false, locked: false };
  },
  renderRecall() {
    this.prepareRecall();
    const day = this.day(), run = this.run, root = $('#study-app');
    const correct = day.pool.filter(id => day.recall[id]?.correct).length;
    const first = day.pool.filter(id => day.recall[id]?.first).length;
    if (!run.queue.length) {
      root.replaceChildren(h('section', { class: 'panel' }, h('h2', { text: this.copy('Hatırlama turu tamamlandı', 'Recall round complete') }),
        h('p', { text: this.copy(`${correct}/${day.pool.length} kelimeyi yardımsız yazdın. İlk denemede yardımsız doğru: ${first}/${day.pool.length}.`, `${correct}/${day.pool.length} words retrieved without hints. Correct on the first unassisted attempt: ${first}/${day.pool.length}.`) }),
        h('p', { class: 'hint', text: this.copy('Bu sonuç bugünkü alıştırmaya aittir. Kalıcılık için sonraki günlerde yeniden hatırla.', 'This result describes today’s practice. Retrieve the words again on later days for longer-term retention.') }),
        h('a', { class: 'button primary', href: '#home', text: this.copy('Günlük yoluma dön', 'Return to my daily path') }),
        this.button(this.copy('Bir tur daha', 'Another round'), () => { this.run = { date: day.date, queue: [...day.pool], hinted: false, locked: false }; this.renderRecall(); })));
      return;
    }
    const entry = BY_ID.get(run.queue[0]);
    run.hinted = day.hints.includes(entry.id); run.locked = false;
    const label = h('label', { for: 'study-answer', text: this.copy('Bu kartın İngilizce kelimesini veya ifadesini yaz', 'Type the English word or phrase practised on this card') });
    const input = h('input', { id: 'study-answer', type: 'text', lang: 'en', autocomplete: 'off', autocapitalize: 'off', spellcheck: 'false', enterkeyhint: 'done' });
    const feedback = h('div', { id: 'study-recall-feedback', role: 'status' });
    const hint = h('p', { class: 'hint', id: 'study-recall-hint', hidden: !run.hinted, text: run.hinted ? entry.word[0] + '…' : '' });
    const form = h('form', { class: 'study-recall-form' }, label, input,
      h('div', { class: 'row' }, h('button', { type: 'submit', class: 'button primary', id: 'study-check', text: this.copy('Kontrol et', 'Check answer') }),
        this.button(this.copy('İlk harf ipucu', 'First-letter hint'), () => { if (run.locked) return; run.hinted = true; if (!day.hints.includes(entry.id)) day.hints.push(entry.id); this.save(); hint.hidden = false; hint.textContent = entry.word[0] + '…'; input.focus(); }, { id: 'study-hint' })), hint);
    form.addEventListener('submit', event => {
      event.preventDefault();
      if (run.locked) return;
      if (!input.value.trim()) { feedback.textContent = this.copy('Önce bir cevap yaz.', 'Write an answer first.'); input.focus(); return; }
      run.locked = true;
      const clean = value => value.normalize('NFKC').toLowerCase().replace(/[’‘]/g, "'").replace(/[.!?,;:]+$/g, '').trim().replace(/\s+/g, ' ');
      const matches = clean(input.value) === clean(entry.word), passed = matches && !run.hinted;
      const old = day.recall[entry.id];
      day.recall[entry.id] = { first: old ? old.first : passed, attempts: (old?.attempts || 0) + 1, correct: passed };
      day.hints = day.hints.filter(id => id !== entry.id);
      run.queue.shift();
      if (!passed) {
        for (const id of day.pool) { if (run.queue.length >= 2) break; if (id !== entry.id && !run.queue.includes(id)) run.queue.push(id); }
        run.queue.push(entry.id);
      }
      if (!passed) {
        Review.add('w:' + entry.id, 1);
        if (!matches) Review.state.cards['w:' + entry.id][4] += 1;
        Review.save();
      }
      this.save();
      for (const button of $$('button', form)) button.disabled = true;
      input.disabled = true;
      const example = entry.example || sentencesFor(entry).flatMap(([, pairs]) => pairs)[0]?.[0];
      feedback.className = 'study-recall-feedback ' + (passed ? 'is-correct' : 'is-wrong');
      feedback.replaceChildren(h('h2', { text: passed ? this.copy('Yardımsız hatırladın', 'Recalled without hints') : matches ? this.copy('İpucuyla buldun; biraz sonra yeniden dene', 'Found with a hint; try again shortly') : this.copy('Modeli incele; biraz sonra yeniden hatırla', 'Study the model, then retrieve it again shortly') }),
        h('p', { lang: 'en' }, h('strong', { text: entry.word }), ' — ', entry.meaning), example ? h('p', { lang: 'en', text: example }) : null,
        this.button(this.copy('Sonraki kelime', 'Next word'), () => this.renderRecall(), { class: 'button primary', id: 'study-recall-next' }));
      $('#study-recall-next').focus();
    });
    root.replaceChildren(h('p', { class: 'hint', text: this.copy(`${correct}/${day.pool.length} yardımsız hatırlama · yanlışlar birkaç kelime sonra yeniden gelir`, `${correct}/${day.pool.length} unassisted recalls · missed words return after other words`) }),
      h('section', { class: 'panel' }, h('h2', { text: this.copy('Türkçe anlamından İngilizcesini hatırla', 'Retrieve the English from its Turkish meaning') }),
        h('p', { class: 'study-recall-meaning', lang: 'tr', text: entry.meaning }), form, feedback),
      h('a', { class: 'study-return', href: '#home', text: this.copy('Günlük yoluma dön', 'Return to my daily path') }));
    input.focus({ preventScroll: true });
  }
};
