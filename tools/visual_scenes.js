/* Small, offline meaning scenes. Kept closed and unrendered until requested.
   Public API: create(family, initial, { lang }), forWord(word, options),
   forGrammar(topicId, lessonIndex, unit, options), relabel(lang, container).
   Factories return <details> or null. */
const VisualScenes = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  let serial = 0;
  const languageUpdaters = new WeakMap();
  const COPY = {
    tr: { try: 'Görerek dene', transfer: 'ödünç almak / vermek', position: 'nesnelerin konumu', search: 'aramak / bulmak',
      choose: 'Gösterilecek anlam', bookDirection: 'Kitap Ada’dan Bora’ya gidiyor.', cutaway: 'Kutunun içi gösteriliyor',
      box: 'kutu', ball: 'top', key: 'anahtar', bag: 'çanta', perspective: 'Bu sahneye karşıdan bakıyoruz.' },
    en: { try: 'See the meaning', transfer: 'borrow / lend', position: 'where things are', search: 'look for / find',
      choose: 'Meaning to show', bookDirection: 'The book goes from Ada to Bora.', cutaway: 'Inside the box is shown',
      box: 'box', ball: 'ball', key: 'key', bag: 'bag', perspective: 'We are looking at this scene from the front.' }
  };
  const STATES = {
    transfer: {
      borrow: { label: 'borrow', en: 'Bora [borrows] a book from Ada.', tr: 'Bora, Ada’dan bir kitap [ödünç alır].',
        note: 'Alan kişi Bora öznedir. Kitap Ada’dan Bora’ya gider.', noteEn: 'Bora, the person receiving the book, is the subject. The book goes from Ada to Bora.' },
      lend: { label: 'lend', en: 'Ada [lends] her book to Bora.', tr: 'Ada kitabını Bora’ya [ödünç verir].',
        note: 'Veren kişi Ada öznedir. Kitabın yönü değişmez; cümledeki bakış açısı değişir.', noteEn: 'Ada, the person giving the book, is the subject. The direction stays the same; the sentence changes perspective.' }
    },
    position: {
      in: { label: 'in', en: 'The ball is [in] the box.', tr: 'Top kutunun [içinde].',
        note: 'Top kutunun iç alanındadır. Görmek için kutunun içini açık gösteriyoruz.', noteEn: 'The ball is inside the box. The box is shown open so that we can see inside.' },
      on: { label: 'on', en: 'The ball is [on] the box.', tr: 'Top kutunun [üstünde].',
        note: 'Top kutunun üst yüzeyine temas eder.', noteEn: 'The ball touches the top surface of the box.' },
      under: { label: 'under', en: 'The ball is [under] the box.', tr: 'Top kutunun [altında].',
        note: 'Top, kutudan daha aşağıdaki konumdadır.', noteEn: 'The ball is in a lower position, underneath the box.' },
      between: { label: 'between', en: 'The ball is [between] the boxes.', tr: 'Top kutuların [arasında].',
        note: 'İki kutu var; top bu ikisinin arasındaki boşluktadır.', noteEn: 'There are two boxes. The ball is in the space between them.' },
      behind: { label: 'behind', en: 'The ball is [behind] the box.', tr: 'Top kutunun [arkasında].',
        note: 'Bu bakış açısından kutu topun bir bölümünü kapatır.', noteEn: 'From this viewpoint, the box hides part of the ball.' },
      'in front of': { label: 'in front of', en: 'The ball is [in front of] the box.', tr: 'Top kutunun [önünde].',
        note: 'Bu bakış açısından top kutunun önünü kısmen kapatır.', noteEn: 'From this viewpoint, the ball partly covers the front of the box.' }
    },
    search: {
      'look for': { label: 'look for', en: 'Ada is [looking for] her key.', tr: 'Ada anahtarını [arıyor].',
        note: 'Arama sürüyor; anahtarı bulduğu henüz söylenmiyor.', noteEn: 'The search is in progress. This does not say that she has found the key.' },
      find: { label: 'find', en: 'Ada has [found] her key.', tr: 'Ada anahtarını [buldu].',
        note: 'Aramanın sonucu var: anahtar artık bulundu. Find fiilinin V3 biçimi found’dur.', noteEn: 'There is a result: the key has been found. Found is the past participle of find.' }
    }
  };

  function el(tag, attrs, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs || {})) {
      if (key === 'text') node.textContent = value;
      else node.setAttribute(key, String(value));
    }
    for (const child of children.flat()) if (child != null) node.append(child);
    return node;
  }
  function svgEl(tag, attrs, ...children) {
    const node = document.createElementNS(NS, tag);
    for (const [key, value] of Object.entries(attrs || {})) node.setAttribute(key, String(value));
    for (const child of children) node.append(child);
    return node;
  }
  function marked(text, language, className) {
    const node = el('p', { class: className, lang: language });
    for (const part of text.split(/(\[[^\]]+\])/)) node.append(part.startsWith('[') ? el('mark', { text: part.slice(1, -1) }) : part);
    return node;
  }
  function text(x, y, value, attrs = {}) {
    const node = svgEl('text', { x, y, 'text-anchor': 'middle', ...attrs });
    node.textContent = value;
    return node;
  }
  function person(x, name, active) {
    return svgEl('g', { class: 'vs-person' + (active ? ' is-active' : '') },
      svgEl('circle', { cx: x, cy: 77, r: 20, class: 'vs-person-head' }),
      svgEl('path', { d: `M ${x - 30} 165 L ${x - 25} 122 Q ${x} 100 ${x + 25} 122 L ${x + 30} 165 Z`, class: 'vs-person-body' }),
      text(x, 203, name));
  }
  function keyShape(x, y, active = true) {
    return svgEl('g', { class: active ? 'vs-key is-found' : 'vs-key' },
      svgEl('circle', { cx: x, cy: y, r: 11 }),
      svgEl('path', { d: `M ${x + 11} ${y} H ${x + 45} M ${x + 33} ${y} V ${y + 10} M ${x + 43} ${y} V ${y + 8}` }));
  }
  function box(x, y, width = 130, height = 96, cutaway = false) {
    return svgEl('g', { class: 'vs-box' + (cutaway ? ' is-cutaway' : '') },
      svgEl('rect', { x, y, width, height, rx: 5 }),
      svgEl('path', { d: `M ${x} ${y + 23} H ${x + width}` }));
  }
  function ball(x, y) { return svgEl('circle', { cx: x, cy: y, r: 19, class: 'vs-ball' }); }

  function drawing(family, mode, language, id) {
    const copy = COPY[language];
    const state = STATES[family][mode];
    const title = svgEl('title', { id: id + '-title' });
    title.textContent = state.en.replace(/[\[\]]/g, '');
    const desc = svgEl('desc', { id: id + '-desc' });
    desc.textContent = language === 'en' ? state.noteEn : state.note;
    const svg = svgEl('svg', { viewBox: '0 0 420 250', class: 'vs-drawing', role: 'img',
      'aria-labelledby': id + '-title ' + id + '-desc', 'data-scene-state': mode }, title, desc);
    if (family === 'transfer') {
      const marker = svgEl('marker', { id: id + '-arrow', viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto' },
        svgEl('path', { d: 'M 0 0 L 10 5 L 0 10 Z', class: 'vs-arrow-head' }));
      svg.append(svgEl('defs', {}, marker), person(75, 'Ada', mode === 'lend'), person(345, 'Bora', mode === 'borrow'),
        svgEl('path', { d: 'M 122 151 H 297', class: 'vs-transfer-arrow', 'marker-end': 'url(#' + id + '-arrow)' }),
        svgEl('rect', { x: 184, y: 99, width: 46, height: 34, rx: 3, class: 'vs-book' }),
        svgEl('path', { d: 'M 207 99 V 133', class: 'vs-book-spine' }));
    } else if (family === 'position') {
      if (mode === 'in') {
        svg.append(box(145, 90, 130, 118, true), ball(210, 155), text(210, 235, copy.cutaway, { class: 'vs-annotation' }));
      } else if (mode === 'on') {
        svg.append(box(145, 120), ball(210, 101));
      } else if (mode === 'under') {
        svg.append(box(145, 48, 130, 94), ball(210, 191));
      } else if (mode === 'between') {
        svg.append(box(53, 105, 102, 105), box(265, 105, 102, 105), ball(210, 160));
      } else if (mode === 'behind') {
        svg.append(ball(210, 121), box(145, 121));
      } else {
        svg.append(box(145, 121), ball(210, 142));
      }
    } else {
      svg.append(person(75, 'Ada', true),
        svgEl('path', { d: 'M 255 102 V 83 Q 285 54 315 83 V 102', class: 'vs-bag-handle' }),
        svgEl('rect', { x: 240, y: 100, width: 90, height: 91, rx: 12, class: 'vs-bag' }),
        text(285, 224, copy.bag));
      if (mode === 'look for') {
        svg.append(svgEl('circle', { cx: 180, cy: 105, r: 22, class: 'vs-search-glass' }),
          svgEl('path', { d: 'M 195 121 L 219 145', class: 'vs-search-glass' }),
          text(285, 153, '?', { class: 'vs-question' }));
      } else {
        svg.append(keyShape(162, 120), text(190, 181, copy.key));
      }
    }
    return svg;
  }

  function create(family, initial, options = {}) {
    if (!STATES[family]) return null;
    let language = options.lang === 'en' ? 'en' : 'tr';
    let copy = COPY[language];
    const keys = Object.keys(STATES[family]);
    let selected = keys.includes(initial) ? initial : keys[0];
    const id = 'vs-' + (++serial);
    const root = el('details', { class: 'vs-scene', 'data-visual-scene': family });
    const summary = el('summary', { text: copy.try + ': ' + copy[family] });
    root.append(summary);
    let body = null;
    function render() {
      if (!body) { body = el('div', { class: 'vs-content' }); root.append(body); }
      const controls = el('div', { class: 'vs-controls', role: 'group', 'aria-label': copy.choose });
      for (const key of keys) {
        const button = el('button', { type: 'button', class: 'vs-choice', 'data-scene-choice': key,
          'aria-pressed': String(selected === key), text: STATES[family][key].label });
        button.addEventListener('click', () => {
          selected = key;
          render();
          // Keep keyboard focus on the same choice after replacing the scene.
          [...root.querySelectorAll('[data-scene-choice]')].find(item => item.dataset.sceneChoice === key)?.focus({ preventScroll: true });
        });
        controls.append(button);
      }
      const state = STATES[family][selected];
      const stage = el('div', { class: 'vs-stage' }, drawing(family, selected, language, id));
      const output = el('div', { class: 'vs-output', 'aria-live': 'polite', 'aria-atomic': 'true' },
        marked(state.en, 'en', 'vs-sentence'), marked(state.tr, 'tr', 'vs-translation tr-support'),
        el('p', { class: 'vs-note', text: language === 'en' ? state.noteEn : state.note }));
      body.replaceChildren(controls, stage, output);
      if (family === 'transfer') body.append(el('p', { class: 'vs-caption', text: copy.bookDirection }));
      if (family === 'position' && /^(behind|in front of)$/.test(selected)) body.append(el('p', { class: 'vs-caption', text: copy.perspective }));
    }
    root.addEventListener('toggle', () => { if (root.open && !body) render(); });
    // Word cards have their own tap-to-learn handler. Scene choices must stay local.
    root.addEventListener('click', event => event.stopPropagation());
    root.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') event.stopPropagation(); });
    languageUpdaters.set(root, next => {
      language = next === 'en' ? 'en' : 'tr';
      copy = COPY[language];
      summary.textContent = copy.try + ': ' + copy[family];
      if (body) render();
    });
    return root;
  }

  function forWord(raw, options = {}) {
    const key = String(raw || '').trim().toLowerCase().replace(/\s+/g, ' ');
    for (const [family, states] of Object.entries(STATES)) if (states[key]) return create(family, key, options);
    return null;
  }
  function forGrammar(topicId, lessonIndex, unit, options = {}) {
    if (topicId === 'pp' && lessonIndex === 1) return create('position', 'in', options);
    return unit && unit.title ? forWord(unit.title, options) : null;
  }
  function relabel(language, container = document) {
    for (const scene of container.querySelectorAll('.vs-scene')) languageUpdaters.get(scene)?.(language);
  }
  return { create, forWord, forGrammar, relabel };
})();
