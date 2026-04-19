const params = new URLSearchParams(window.location.search);
const jobId = params.get("job_id");

document.getElementById("new-search").addEventListener("click", () => {
  sessionStorage.removeItem("search-form-data");
  window.location.href = "/";
});



async function fetchData() {
    try {
        const response = await fetch(`/get_output?job_id=${jobId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();

    } catch (error) {
        console.error('Fetch error:', error.message);
    }
}

fetchData()
  .then(result =>  {
    process_output(result);
    })
  .catch((error) => console.error(error));

function process_output(data) {
    if (data.length == 0) {
      const placeholder = document.getElementById("no-found-data");
      placeholder.style.display = "block";
    };

    for (const [idx, item] of data.entries()) {
        // console.log(item['final_indexes']);
        const real_output = document.createElement("div");
        real_output.className = "real-output"

        const text_item = document.createElement("div");
        text_item.className = "text-item"

        const top_item = document.createElement("div");
        top_item.className = "top-base-container"

        const bold_title = document.createElement("div");
        bold_title.className = "bold-name";
        bold_title.textContent = idx + 1 + ') '+ item['title']

        const bold_author = document.createElement("div");
        bold_author.className = "simple-name";
        bold_author.textContent = item['author']

        top_item.appendChild(bold_title);
        top_item.appendChild(bold_author);

        const main_text = document.createElement('div');
        main_text.classList = "main-text";

        const nivkh = document.createElement('div');
        nivkh.classList = "nivkh-text";

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
        rus.classList = "rus-text";

        const p_rus = document.createElement('p');
        p_rus.textContent = item['russian_text'];

        rus.appendChild(p_rus);

        main_text.appendChild(nivkh);
        main_text.appendChild(rus);

        const add_info = document.createElement('div');
        add_info.classList = "additional-info";
        add_info.textContent = "Посмотреть контекст"

        text_item.appendChild(top_item);
        text_item.appendChild(main_text);
        text_item.appendChild(add_info);
        text_item.appendChild(add_info);
        real_output.appendChild(text_item);

        const all_info = document.getElementById("output-info");
        all_info.appendChild(real_output);
    }

    const element = document.getElementById('documents');
    const len_documents = data.length.toString();
    let word = " примеров";
    let regexp = /[234]$/gi;

    if (len_documents.endsWith("1")) {
      word = " пример"
    } else if (len_documents.match(regexp)) {
      word = " примера"
    }
    element.textContent = len_documents + word;

}