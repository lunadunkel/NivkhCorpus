const letter = decodeURIComponent(window.location.pathname.split("/").pop());

document.title = `Слова на букву ${letter}`;

const goUpBtn = document.querySelector('.go-up');

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        goUpBtn.style.display = 'flex';
    } else {
        goUpBtn.style.display = 'none';
    }
});

goUpBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

async function loadWords() {
    const smallLetter = letter.toLowerCase();
    const response = await fetch(`/dictionary/list/${encodeURIComponent(smallLetter)}`);
    const words = await response.json();

    // группируем по переводу: несколько лемм -> один перевод, СОХРАНЯЯ id
    const grouped = Object.values(
        words.reduce((acc, item) => {
            const key = item.translation;
            if (!acc[key]) {
                acc[key] = { translation: key, lemmas: [], ids: [] };
            }
            acc[key].lemmas.push(...item.lemma.split(",").map(s => s.trim()));
            acc[key].ids.push(item._id);   // сохраняем id леммы
            return acc;
        }, {})
    );

    const byLemma = (a, b) => {
        const c = a.localeCompare(b, "ru", { sensitivity: "base" });
        return c !== 0 ? c : a.length - b.length;
    };

    grouped.forEach(group => group.lemmas.sort(byLemma));
    grouped.sort((g1, g2) => byLemma(g1.lemmas[0], g2.lemmas[0]));

    const mainItem = document.querySelector(".dictionary-list");

    grouped.forEach((group, index) => {
        const lemmas = group.lemmas.join(', ');
        const translation = group.translation;

        const lemmaGroup = document.createElement('div');
        lemmaGroup.className = 'lemma';
        lemmaGroup.textContent = lemmas;

        const transGroup = document.createElement('div');
        transGroup.className = 'translation';
        transGroup.textContent = translation;

        const wordItem = document.createElement('div');
        wordItem.className = 'word-item';
        wordItem.dataset.index = index;          // data-index, как на главной
        wordItem.appendChild(lemmaGroup);
        wordItem.appendChild(transGroup);

        mainItem.appendChild(wordItem);
    });

    // клик по группе -> страница леммы по id первой леммы группы
    mainItem.addEventListener('click', (e) => {
        const item = e.target.closest('.word-item');
        if (!item) return;
        const group = grouped[Number(item.dataset.index)];
        const id = group.ids[0];
        window.location.href = `/dictionary/word?id=${encodeURIComponent(id)}`;
    });
}

loadWords();