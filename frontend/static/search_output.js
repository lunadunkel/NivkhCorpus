document.getElementById("new-search").addEventListener("click", () => {
  sessionStorage.removeItem("search-form-data");
  window.location.href = "/";
});



async function fetchData() {
    try {
        const response = await fetch('/get_output');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
        // console.log('Fetched data:', data);
    } catch (error) {
        console.error('Fetch error:', error.message);
    }
    return data;
}

fetchData()
  .then(result =>  {
    process_output(result);
    })
  .catch((error) => console.error(error));

function process_output(data) {
    const documents_data = data["documents"];
    for (const item of documents_data) {
        const real_output = document.createElement("div");
        real_output.className = "real-output"

        const text_item = document.createElement("div");
        text_item.className = "text-item"

        const top_item = document.createElement("div");
        top_item.className = "top-base-container"

        const bold_title = document.createElement("div");
        bold_title.className = "bold-name";
        bold_title.textContent = item['id'] + '. '+ item['name']

        const bold_author = document.createElement("div");
        bold_author.className = "bold-name";
        bold_author.textContent = item['author']

        top_item.appendChild(bold_title);
        top_item.appendChild(bold_author);

        const main_text = document.createElement('div');
        main_text.classList = "main-text";

        const nivkh = document.createElement('div');
        nivkh.classList = "nivkh-text";

        const p_nivkh = document.createElement('p');
        p_nivkh.innerHTML = item['text'];

        nivkh.appendChild(p_nivkh);

        const rus = document.createElement('div');
        rus.classList = "rus-text";

        const p_rus = document.createElement('p');
        p_rus.textContent = item['translation'];

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

    const words_instances = data["words_instances"];
    console.log(words_instances);
    const element = document.getElementById('documents');
    const len_documents = documents_data.length.toString();
    element.textContent = documents_data.length;
    const instances = document.getElementById('instances');
    instances.textContent = words_instances;


}