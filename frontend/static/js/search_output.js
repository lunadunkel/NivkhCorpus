const params = new URLSearchParams(window.location.search);

document.addEventListener('click', (event) => {
    document.querySelectorAll('.dropdown[open]').forEach((dropdown) => {
        if (!dropdown.contains(event.target)) dropdown.open = false;
    });
    document.querySelectorAll('.filter[open]').forEach((filter) => {
        if (!filter.contains(event.target)) filter.open = false;
    });
});

document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    const dropdown = document.querySelector('.dropdown[open]');
    const filter = document.querySelector('.filter[open]');
    if (dropdown) {
        dropdown.open = false;
    }
    else if (filter) {
        filter.open = false;
    }
    else return;
    // dropdown.querySelector('.dropdown-toggle').focus();
});


const corpus = JSON.parse(document.getElementById("corpus-config").textContent);
const FILTER_ENDPOINT = `/${corpus.id}/search/update_filter`;

let controller = null;
let replacing = false;
let debounceTimer = null;

const jobId = params.get("job_id");
let currentOffset = 0;
const PAGE_SIZE = 20;

document.querySelector(".back_to_search").href = `/${corpus.id}?job_id=${encodeURIComponent(jobId)}`;

document.getElementById("new-search").addEventListener("click", () => {
  sessionStorage.removeItem("search-form-data");
  window.location.href = `/${corpus.id}`;
});


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


function collectFilters() {
    const filters = {};
    document.querySelectorAll('.dropdown input:checked').forEach((input) => {
        (filters[input.name] ??= []).push(input.value);
    });
    return filters;
}

function currentSort() {
    return document.querySelector('.filter input[name="sort"]:checked')?.value ?? 'default';
}

async function loadResults({ replace }) {
    if (!replace && replacing) return;

    controller?.abort();
    controller = new AbortController();
    replacing = replace;

    const params = new URLSearchParams({
        job_id: jobId,
        sort: currentSort(),
        offset: replace ? 0 : currentOffset,
    });

    try {
        const response = await fetch(`${FILTER_ENDPOINT}?${params}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(collectFilters()),
            signal: controller.signal,
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        if (replace) {
            updateCounter(data.length);
            document.getElementById("no-found-data").style.display = data.length === 0 ? "block" : "none";
        }
        process_output(data.results, data.length, { replace });
        replacing = false;
    } catch (err) {
        if (err.name === 'AbortError') return;
        replacing = false;
        console.error('Не удалось загрузить результаты:', err);
    }
}

document.querySelectorAll('.dropdown').forEach((dropdown) => {
    const counter = dropdown.querySelector('.dropdown-count');

    const updateDropdownCounter = () => {
        if (!counter) return;
        const count = dropdown.querySelectorAll('input:checked').length;
        counter.textContent = count;
        counter.hidden = count === 0;
    };

    dropdown.addEventListener('change', () => {
        updateDropdownCounter();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => loadResults({ replace: true }), 300);
    });
    updateDropdownCounter(); 
});

document.querySelectorAll('.filter input[name="sort"]').forEach((radio) => {
    radio.addEventListener('change', () => {
        radio.closest('.filter').open = false;
        clearTimeout(debounceTimer);
        loadResults({ replace: true });
    });
});

async function fetchData(offset = 0) {
    try {
        const response = await fetch(`/${corpus.id}/get_output?job_id=${jobId}&offset=${offset}&limit=${PAGE_SIZE}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error.message);
    }
}

// первая загрузка
fetchData(0).then(data => {
    if (!data) return;
    updateCounter(data.length);
    if (data.length === 0) {
        document.getElementById("no-found-data").style.display = "block";
        return;
    }
    process_output(data.results, data.length);
    showQueries(data.queries)
});


document.getElementById('show-more').addEventListener('click', () => 
    loadResults({ replace: false }));


function updateShowMore(total) {
    const btn = document.getElementById('show-more');
    btn.style.display = currentOffset < total ? 'block' : 'none';
}

function updateCounter(total) {
    const element = document.getElementById('documents');
    var prefix = "Найдено ";
    const str = total.toString();
    let word = " примеров";
    if (str.endsWith("1") && !str.endsWith("11")) {
        prefix = "Найден "
        word = " пример";
    } else if (str.match(/[234]$/) && !str.match(/1[234]$/)) {
        word = " примера";
    }
    element.textContent = prefix + str + word;
}

function updateCondition(total) {
    const element = document.getElementById('conditions');
    const str = total.toString();
    let word = " условий";
    if (str.endsWith("1") && !str.endsWith("11")) {
        word = " условия";
    } else if (str.match(/[234]$/) && !str.match(/1[234]$/)) {
        word = " условий";
    }
    element.textContent += " из " + str + " " + word;
}

function closeContext(card) {
    card.querySelector(".segm-text").style.display = "none"
    card.querySelector(".additional-info").textContent = "Показать глоссы";
}

async function addContext(id, card) {
    const glossedText = card.querySelector(".gloss-wrapper");
    if (glossedText) {
        if (glossedText.checkVisibility()) {
            closeContext(card);
            return
        }
        else {
            card.querySelector(".segm-text").style.display = "flex";
            return
        };
    }

    const response = await fetch(`/${corpus.id}/search/doc_id=${encodeURIComponent(id)}`, {
    method: "POST"
    });

    const data = await response.json();


    const segmentation = data['segmentation'].split(" ");
    const glosses = data['glossing'].split(" ");

    const glossBlock = document.createElement("div");
    glossBlock.className = "gloss-wrapper";
    for (let i = 0; i < segmentation.length; i++) {
    const seg = document.createElement("div");
    seg.textContent = segmentation[i];
    seg.className = "nivkh-segm";

    const gloss = document.createElement("div");
    gloss.className = "rus-segm"
    gloss.textContent = glosses[i];

    const wordPair = document.createElement("div");
    wordPair.className = "word-pair";

    wordPair.appendChild(seg);
    wordPair.appendChild(gloss);

    glossBlock.appendChild(wordPair);
    }


    card.querySelector(".segm-text").appendChild(glossBlock);
    card.querySelector(".segm-text").style.display = "flex";
    card.querySelector(".additional-info").textContent = "Скрыть глоссы";
}

function showQueries(queries) {

    const box = document.getElementById("query-text");
    const show = document.getElementById("show-conditions");

    updateCondition(queries.length)

    queries.filter(Boolean).forEach(text => {
        const line = document.createElement("div");
        line.classList = "simple-buttons info";
        line.textContent = text;
        box.appendChild(line);
    });

    show.addEventListener('click', () => {
        if (box.checkVisibility()) {
            box.style.display = "none"
            show.textContent = "Показать условия"
        }
        else {
            box.style.display = "flex"
            show.textContent = "Скрыть условия"

        }
    })

}

function process_output(items, total, { replace = false } = {}) {
    const container = document.getElementById("all-documents");
    if (replace) {
        container.querySelectorAll('.real-output').forEach((el) => el.remove());
        currentOffset = 0;
    }
    
    for (const [idx, item] of items.entries()) {
        const real_output = document.createElement("div");
        real_output.className = "real-output";

        const text_item = document.createElement("div");
        text_item.dataset.id = item['_id'];
        text_item.className = "text-item";

        const top_item = document.createElement("div");
        top_item.className = "top-base-container";

        const bold_title = document.createElement("div");
        bold_title.className = "bold-name";
        bold_title.textContent = (currentOffset + idx + 1) + ') ' + item['title'];

        const bold_author = document.createElement("div");
        bold_author.className = "simple-name";
        bold_author.textContent = item['author'];

        top_item.appendChild(bold_title);
        top_item.appendChild(bold_author);

        const main_text = document.createElement('div');
        main_text.className = "main-text";

        const nivkh = document.createElement('div');
        nivkh.className = "nivkh-text";

        const p_nivkh = document.createElement('p');
        if (item['final_indexes']) {
            const words = item['text'].split(" ");
            for (const index of item['final_indexes']) {
                words[index] = `<b>${words[index]}</b>`;
            }
            p_nivkh.innerHTML = words.join(" ");
        } else {
            p_nivkh.innerHTML = item['text'];
        }

        nivkh.appendChild(p_nivkh);

        const rus = document.createElement('div');
        rus.className = "rus-text";

        const p_rus = document.createElement('p');
        p_rus.textContent = item['translation_text'];
        rus.appendChild(p_rus);


        const segmentation = document.createElement('div');
        segmentation.className = "segm-text";

        // const glossing = document.createElement('div');
        // glossing.className = "gloss-text";


        main_text.appendChild(nivkh);
        main_text.appendChild(segmentation);
        main_text.appendChild(rus);

        const add_info = document.createElement('div');
        add_info.className = "additional-info";
        add_info.textContent = "Показать глоссы";

        add_info.addEventListener("click", async() => {
            
            await addContext(item['_id'], real_output);
        })

        text_item.appendChild(top_item);
        text_item.appendChild(main_text);
        text_item.appendChild(add_info);
        real_output.appendChild(text_item);
        container.appendChild(real_output);
    }
    currentOffset += items.length;
    updateShowMore(total);
}

function exportResults(format) {
  const params = new URLSearchParams({ job_id: jobId, format });
  console.log(collectFilters())
  for (const [key, values] of Object.entries(collectFilters())) {
    values.forEach(v => params.append(key, v));    // append, чтобы мультивыбор не затирался
  }
  sort = currentSort()
  params.append("sort", sort)
  window.location.href = `/${corpus.id}/export?${params}`; 
}