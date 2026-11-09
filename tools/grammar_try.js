/* Small, authored comparisons inside existing lessons. No progress or network side effects. */
const GrammarTry = {
  lessons: {
    'tn:2': {
      states: [
        { label: 'Alışkanlık', en: 'She [reads] every evening.', tr: 'Her akşam kitap okur.', why: 'Düzenli alışkanlık anlatılıyor; şu anda okuduğu söylenmiyor.', kind: 'habit', caption: 'Tekrar eden düzen' },
        { label: 'Şu anda', en: 'She [is reading] now.', tr: 'Şu anda kitap okuyor.', why: 'Konuşma anında devam eden okuma eylemi öne çıkıyor.', kind: 'now', caption: 'Şimdi sürüyor' }
      ],
      question: 'Elif şu anda elindeki kitabı okuyor. Özellikle o anda süren eylemi hangi cümle anlatır?',
      answer: 1,
      explanation: 'Is reading, şu anda devam eden eylemi gösterir. Reads every evening ise düzenli alışkanlıktır; o saniyede ne yaptığını söylemez.'
    },
    'tn:5': {
      states: [
        { label: 'Bitmiş olay', en: 'I [read] the report last night.', tr: 'Dün gece raporu okudum.', why: 'Okuma, bitmiş bir geçmiş olay olarak sunuluyor.', kind: 'past', caption: 'Geçmişteki olay' },
        { label: 'O anda sürüyordu', en: 'I [was reading] the report at nine last night.', tr: 'Dün gece dokuzda raporu okuyordum.', why: 'Dokuzdaki okuma süreci gösteriliyor; ne zaman bitirildiği belirtilmiyor.', kind: 'past-process', caption: 'Dokuzda sürüyordu' }
      ],
      question: 'Dün gece saat dokuzdaki sahneyi anlatıyorsun: raporu okuma işinin tam içindeydin. Hangi cümle bu bakışı verir?',
      answer: 1,
      explanation: 'Was reading geçmişteki belirli anda sürmekte olan işi gösterir. Read last night ise okumayı geçmişte gerçekleşen olay olarak sunar.'
    },
    'tn:8': {
      states: [
        { label: 'Bitmiş geçmiş zaman', en: 'I [lost] my key yesterday.', tr: 'Dün anahtarımı kaybettim.', why: 'Kaybetme olayı bitmiş bir güne yerleştiriliyor. Anahtarın şu anki durumu bu cümlede açıklanmıyor.', kind: 'past', caption: 'Dün gerçekleşen olay' },
        { label: 'Şimdiyle bağlantı', en: "I [have lost] my key, so I can't open the door.", tr: 'Anahtarımı kaybettim; bu yüzden kapıyı açamıyorum.', why: 'Geçmişteki kayıp, bugünkü kapıyı açamama sorununa bağlanıyor.', kind: 'result', caption: 'Geçmiş olay → şimdiki sonuç' }
      ],
      question: 'Kaybetme olayını özellikle bitmiş bir geçmiş güne, yani düne yerleştirmek istiyorsun. Hangi cümle uygundur?',
      answer: 0,
      explanation: 'Yesterday bitmiş geçmiş zaman verir; bu cümlede lost ile past simple kullanılır. Have lost örneği ise belirli bir geçmiş gün söylemeden şimdiki sonucu öne çıkarır.'
    }
  },
  marked(text) {
    const span = h('span', { lang: 'en' });
    for (const part of text.split(/(\[[^\]]+\])/)) span.append(part.startsWith('[') ? h('mark', { text: part.slice(1, -1) }) : part);
    return span;
  },
  diagram(state) {
    const wrap = h('div', { class: 'gtry-timeline', role: 'img', 'aria-label': state.caption + '. ' + state.why });
    const track = h('div', { class: 'gtry-track', 'aria-hidden': 'true' });
    track.append(h('span', { class: 'gtry-axis' }), h('span', { class: 'gtry-now' }));
    if (state.kind === 'habit') {
      for (const at of [12, 28, 44, 60, 76]) track.append(h('span', { class: 'gtry-dot', style: 'left:' + at + '%' }));
    } else if (state.kind === 'now') track.append(h('span', { class: 'gtry-process gtry-process-now' }));
    else if (state.kind === 'past-process') {
      track.append(h('span', { class: 'gtry-process gtry-process-past' }), h('span', { class: 'gtry-reference', text: 'Dokuzda' }));
    } else {
      track.append(h('span', { class: 'gtry-dot', style: 'left:30%' }));
      if (state.kind === 'result') track.append(h('span', { class: 'gtry-result' }));
    }
    wrap.append(h('p', { class: 'gtry-caption', text: state.caption }), track,
      h('div', { class: 'gtry-axis-labels', 'aria-hidden': 'true' }, h('span', { text: 'Geçmiş' }), h('span', { text: 'Şimdi' })));
    return wrap;
  },
  create(topicId, lessonIndex) {
    const lesson = this.lessons[topicId + ':' + lessonIndex];
    if (!lesson) return null;
    const details = h('details', { class: 'gtry', lang: 'tr' }, h('summary', { text: 'Örnek üzerinde dene' }));
    let panel = null, selected = 0;
    const explore = () => {
      panel.replaceChildren();
      const controls = h('div', { class: 'gtry-controls', role: 'group', 'aria-label': 'Anlatım biçimi' });
      const output = h('div', { class: 'gtry-output', 'aria-live': 'polite' });
      const render = () => {
        const state = lesson.states[selected];
        for (const button of controls.children) button.setAttribute('aria-pressed', String(Number(button.dataset.state) === selected));
        output.replaceChildren(h('p', { class: 'gtry-sentence' }, this.marked(state.en)), h('p', { class: 'gtry-tr', lang: 'tr', text: state.tr }),
          this.diagram(state), h('p', { class: 'gtry-why', text: state.why }));
      };
      lesson.states.forEach((state, index) => {
        const button = h('button', { type: 'button', 'data-state': index, text: state.label });
        button.addEventListener('click', () => { selected = index; render(); });
        controls.append(button);
      });
      const quizButton = h('button', { type: 'button', class: 'button small', 'data-gtry-quiz': '', text: 'Duruma göre seç' });
      quizButton.addEventListener('click', () => quiz());
      panel.append(controls, output, quizButton);
      render();
    };
    const quiz = () => {
      const title = h('h3', { tabindex: '-1', text: 'Şimdi sen seç' });
      const options = h('div', { class: 'gtry-options' });
      const feedback = h('p', { class: 'gtry-feedback', role: 'status', tabindex: '-1', hidden: true });
      lesson.states.forEach((state, index) => {
        const button = h('button', { type: 'button', 'data-answer': index }, this.marked(state.en));
        button.addEventListener('click', () => {
          const right = index === lesson.answer;
          feedback.hidden = false;
          feedback.className = 'gtry-feedback ' + (right ? 'is-right' : 'is-wrong');
          feedback.textContent = (right ? 'Doğru. ' : 'Bu durumda diğer anlatım uygun. ') + lesson.explanation;
          for (const option of options.children) option.disabled = true;
          feedback.focus();
        });
        options.append(button);
      });
      const back = h('button', { type: 'button', class: 'button small ghost', text: 'Örneklere dön' });
      back.addEventListener('click', () => { explore(); panel.querySelector('button').focus(); });
      panel.replaceChildren(title, h('p', { text: lesson.question }), options, feedback, back);
      title.focus();
    };
    details.addEventListener('toggle', () => {
      if (!details.open || panel) return;
      panel = h('div', { class: 'gtry-body' });
      details.append(panel);
      explore();
    });
    return details;
  }
};
