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

    // группируем по переводу: несколько лемм -> один перевод
    const grouped = Object.values(
        words.reduce((acc, item) => {
            const key = item.translation;
            if (!acc[key]) {
                acc[key] = { translation: key, lemmas: [] };
            }
            acc[key].lemmas.push(...item.lemma.split(",").map(s => s.trim()));
            return acc;
        }, {})
    );

    // единый компаратор лемм
    const byLemma = (a, b) => {
        const c = a.localeCompare(b, "ru", { sensitivity: "base" });
        return c !== 0 ? c : a.length - b.length;
    };

    // 1) сортируем леммы ВНУТРИ каждой группы
    grouped.forEach(group => group.lemmas.sort(byLemma));

    // 2) сортируем САМИ группы по первой (наименьшей) лемме
    grouped.sort((g1, g2) => byLemma(g1.lemmas[0], g2.lemmas[0]));

    const mainItem = document.querySelector(".dictionary-list");
    for (const group of grouped) {
        const lemmas = group.lemmas.join(', ');
        const translation = group.translation;

        const lemmaGroup = document.createElement('div');
        lemmaGroup.classList = 'lemma';
        lemmaGroup.textContent = lemmas;

        const transGroup = document.createElement('div');
        transGroup.classList = 'translation';
        transGroup.textContent = translation;

        const wordItem = document.createElement('div');
        wordItem.classList = 'word-item';
        wordItem.appendChild(lemmaGroup);
        wordItem.appendChild(transGroup);

        mainItem.appendChild(wordItem);
    }
}

loadWords();