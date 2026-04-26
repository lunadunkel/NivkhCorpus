const params = new URLSearchParams(window.location.search);
const jobId = params.get("job_id");
let currentOffset = 0;
const PAGE_SIZE = 20;

document.getElementById("new-search").addEventListener("click", () => {
  sessionStorage.removeItem("search-form-data");
  window.location.href = "/";
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

async function fetchData(offset = 0) {
    try {
        const response = await fetch(`/get_output?job_id=${jobId}&offset=${offset}&limit=${PAGE_SIZE}`);
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
    currentOffset += data.results.length;
    updateShowMore(data.length);
});


document.getElementById('show-more').addEventListener('click', () => {
    fetchData(currentOffset).then(data => {
        if (!data) return;
        process_output(data.results);
        currentOffset += data.results.length;
        updateShowMore(data.length);
    });
});


function updateShowMore(total) {
    console.log(total, currentOffset);
    const btn = document.getElementById('show-more');
    btn.style.display = currentOffset < total ? 'block' : 'none';
}

function updateCounter(total) {
    const element = document.getElementById('documents');
    const str = total.toString();
    let word = " примеров";
    if (str.endsWith("1") && !str.endsWith("11")) {
        word = " пример";
    } else if (str.match(/[234]$/) && !str.match(/1[234]$/)) {
        word = " примера";
    }
    element.textContent = str + word;
}

function process_output(items, total) {
    const container = document.getElementById("all-documents");
    
    for (const [idx, item] of items.entries()) {
        const real_output = document.createElement("div");
        real_output.className = "real-output";

        const text_item = document.createElement("div");
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
        p_rus.textContent = item['russian_text'];
        rus.appendChild(p_rus);

        main_text.appendChild(nivkh);
        main_text.appendChild(rus);

        const add_info = document.createElement('div');
        add_info.className = "additional-info";
        add_info.textContent = "Посмотреть контекст";

        text_item.appendChild(top_item);
        text_item.appendChild(main_text);
        text_item.appendChild(add_info);
        real_output.appendChild(text_item);
        container.appendChild(real_output);
        updateShowMore(total);
    }
}