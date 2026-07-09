let currentResults = [];
const input = document.getElementById('correct_placeholder-0'); 
const indexEl = document.querySelector('.alpha-index'); 
const resultsEl = document.getElementById('dict-results');
const langSelect = document.getElementById('extension-0');

document.addEventListener('DOMContentLoaded', () => {
  keyboardActivate(document.getElementById('extension-0'));
});

resultsEl.style.display = 'none';

let fuse;
let activeIndex = -1;

fetch('/search/dictionary')
  .then(response => response.json())
  .then(words => {
    fuse = new Fuse(words, {
      keys: [
        {name: 'lemma', weight: 2},
        {name: 'translation', weight: 1}
      ],
      threshold: 0.5,
      ignoreLocation: false,
      minMatchCharLength: 1
    });

    if (input.value.trim() !== '') runSearch(input.value);
  })
  .catch(err => console.error('Не удалось загрузить словарь:', err));

function buildQuery(q) {
  return langSelect.value === 'russian'
    ? {translation: q }
    : {lemma: q };
}

input.addEventListener('input', (e) => runSearch(e.target.value));
langSelect.addEventListener('change', () => runSearch(input.value));

const clickZone = document.querySelectorAll(".idx-row");

// clickZone.forEach(selectedZone => {
//   selectedZone.addEventListener('click', async () => {
//     const selectedLetter = selectedZone.firstElementChild.textContent;

//     try {
//         const response = await fetch(`/list?letter=${selectedLetter}`);
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         return await response.json();
//     } catch (error) {
//         console.error('Fetch error:', error.message);
//     }
//   })
// })

clickZone.forEach(selectedZone => {
    selectedZone.addEventListener("click", () => {
        const letter = selectedZone.firstElementChild.textContent.trim();
        window.location.href = `/dictionary/${encodeURIComponent(letter)}`;
    });
});


function normalizeApostrophe(s) {
  return s.replace(/['\u2018\u02BC\u0060\u00B4]/g, '\u2019');
}


function runSearch(rawQuery) {
  const q = normalizeApostrophe(rawQuery.trim());
  // const q = rawQuery.trim();
  if (q === '') {                      
    resultsEl.innerHTML = '';
    resultsEl.style.display = 'none';
    return;
  }
  if (!fuse) return;                   

  const hits = fuse.search(buildQuery(q));
  render(hits);
}

function render(hits) {
  activeIndex = -1;

  const groups = new Map();
  for (const hit of hits) {
    const { _id, lemma, translation } = hit.item;

    if (!groups.has(translation)) {
        groups.set(translation, {
            lemmas: [],
            ids: []
        });
    }

    const group = groups.get(translation);
    group.lemmas.push(lemma);
    group.ids.push(_id);
  }

  const top5 = [...groups.entries()].slice(0, 5);
  currentResults = top5;

  const isRu = langSelect.value === 'russian';

  resultsEl.innerHTML = top5.map(([translation, group], index) => {
    const lemmaText = group.lemmas.join(', ');

    const [first, second] = isRu
      ? [translation, lemmaText]   // русский поиск: перевод первым
      : [lemmaText, translation];  // нивхский поиск: лемма первой

    return `<li class="dict-entry" data-index="${index}">
              <span class="entry-lemma">${first}</span>
              <span class="entry-tr">${second}</span>
            </li>`;
  }).join('');

  const liCount = resultsEl.querySelectorAll('li').length;
  const focused = document.activeElement === input;
  resultsEl.style.display = (liCount > 0 && focused) ? '' : 'none';
}

function select(li) {
  const index = Number(li.dataset.index);
  const [, group] = currentResults[index];
  const id = group.ids[0];
  resultsEl.style.display = 'none';
  activeIndex = -1;
  window.location.href = `/dictionary/word?id=${encodeURIComponent(id)}`;
}

input.addEventListener('focus', () => {
  if (input.value.trim() !== '') runSearch(input.value); 
});
input.addEventListener('blur', () => {
  resultsEl.style.display = 'none';     
  activeIndex = -1;
});

resultsEl.addEventListener('mousedown', (e) => e.preventDefault());
resultsEl.addEventListener('click', (e) => {
  const li = e.target.closest('li');    
  if (li) select(li);
});
 
resultsEl.addEventListener('mouseover', (e) => {
  const li = e.target.closest('li');
  if (!li) return;
  const items = resultsEl.querySelectorAll('li');
  activeIndex = [...items].indexOf(li);
  highlight(items, false);
});

input.addEventListener('keydown', (e) => {
  const items = resultsEl.querySelectorAll('li');
  if (!items.length) return;            
  const n = items.length;

  if (e.key === 'ArrowDown') {
    e.preventDefault();                 
    activeIndex = activeIndex < 0 ? 0 : (activeIndex + 1) % n;
    highlight(items);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    activeIndex = activeIndex < 0 ? n - 1 : (activeIndex - 1 + n) % n;
    highlight(items);
  } else if (e.key === 'Enter') {
    if (activeIndex >= 0) {
      e.preventDefault();
      select(items[activeIndex]);
    }
  }
});

function highlight(items) {
  items.forEach((li, i) => li.classList.toggle('is-active', i === activeIndex));
  if (activeIndex >= 0) {
    items[activeIndex].scrollIntoView({ block: 'nearest' });
  }
}

function keyboardActivate(select) {
  const frame = select.closest('.final-form');
  const keyboardBtn = frame.querySelector('.keyboard');       // #nivkh_keyboard-0
  const keyboardPanel = frame.querySelector('.letter-input');  // #keyboard-0
  const input = frame.querySelector('.input-panel');           // #correct_placeholder-0

  // видимость иконки клавиатуры в зависимости от языка
  function applyLanguage() {
    if (select.value === 'nivkh') {
      keyboardBtn.style.display = 'flex';
    } else {
      keyboardBtn.style.display = 'none';
      keyboardPanel.style.display = 'none';  // на русском панель закрыта
    }
  }

  select.addEventListener('change', applyLanguage);
  applyLanguage();  // начальное состояние

  // клик по иконке — тоггл панели
  keyboardBtn.addEventListener('click', () => {
    const isOpen = keyboardPanel.style.display === 'flex';
    keyboardPanel.style.display = isOpen ? 'none' : 'flex';
  });

  // клик по букве — вставляем символ в инпут в позицию курсора
  keyboardPanel.addEventListener('click', (e) => {
    const key = e.target.closest('.letters');
    if (!key) return;

    const ch = key.textContent;
    const start = input.selectionStart ?? input.value.length;
    const end = input.selectionEnd ?? input.value.length;

    input.value = input.value.slice(0, start) + ch + input.value.slice(end);

    // возвращаем фокус и ставим курсор после вставленного символа
    input.focus();
    const pos = start + ch.length;
    input.setSelectionRange(pos, pos);

    // триггерим input, чтобы сработал поиск в dictionary.js
    input.dispatchEvent(new Event('input', { bubbles: true }));
  });
}
