const id = new URLSearchParams(location.search).get('id');

// кнопка «наверх», как на странице буквы
const goUpBtn = document.querySelector('.go-up');
if (goUpBtn) {
    window.addEventListener('scroll', () => {
        goUpBtn.style.display = window.scrollY > 300 ? 'flex' : 'none';
    });
    goUpBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// UD-теги частей речи -> русские подписи; неизвестный код показываем как есть
const POS_RU = {
    NOUN: 'сущ.',
    VERB: 'глаг.',
    NUM: 'числ.',
    CLASS: 'классиф.',
    Q: 'вопр. слово',
    ADV: 'нареч.',
    INTJ: 'междом.',
    PROPN: 'имя собств.',
    PRON: 'мест.',
    DISC: 'дискурс. слово',
    X: 'прочее',
};

function posLabel(pos) {
    if (!pos) return '';
    return POS_RU[pos] || pos;
}

const byLemma = (a, b) => {
    const c = a.lemma.localeCompare(b.lemma, "ru", { sensitivity: "base" });
    return c !== 0 ? c : a.lemma.length - b.lemma.length;
};

async function loadWord() {
    const list = document.querySelector('.dictionary-list');

    if (!id) {
        list.textContent = 'Не найдено';
        return;
    }

    let data;
    try {
        const res = await fetch(`/dictionary/group?id=${encodeURIComponent(id)}`);
        if (!res.ok) {
            list.textContent = 'Не найдено';
            return;
        }
        data = await res.json();
    } catch (err) {
        console.error('Не удалось загрузить значение:', err);
        list.textContent = 'Не найдено';
        return;
    }

    document.title = data.translation;

    const lemmas = [...data.documents].sort(byLemma);

    for (const doc of lemmas) {
        const item = document.createElement('div');
        item.className = 'word-item';

        const head = document.createElement('div');
        head.className = 'lemma';
        head.textContent = doc.lemma;

        const pos = posLabel(doc.POS);
        if (pos) {
            const posEl = document.createElement('span');
            posEl.className = 'pos';
            posEl.textContent = pos;
            head.appendChild(posEl);
        }
        item.appendChild(head);

        // перевод
        const transEl = document.createElement('div');
        transEl.className = 'translation';
        transEl.textContent = data.translation;
        item.appendChild(transEl);

        if (doc.ex) {
            const exBlock = document.createElement('div');
            exBlock.className = 'example';

            const exNivkh = document.createElement('div');
            exNivkh.className = 'example-nivkh';
            exNivkh.textContent = doc.ex;
            exBlock.appendChild(exNivkh);

            if (doc.tr) {
                const exRus = document.createElement('div');
                exRus.className = 'example-rus';
                exRus.textContent = doc.tr;
                exBlock.appendChild(exRus);
            }
            item.appendChild(exBlock);
        }

        list.appendChild(item);
    }
}

loadWord();
