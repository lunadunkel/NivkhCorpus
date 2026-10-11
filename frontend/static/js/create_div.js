import {actionKeyboard, keyboardActivate, wordformButton, lemmaButton} from './click_based_fts.js';
import { showSearchHint } from './hint.js';

const corpusId = JSON.parse(document.getElementById("corpus-config").textContent).id;


function bindEvents(root, value, manager) {

    const v = value;
    const dialog = root.querySelector("#pop-up-" + v);
    const regex = root.querySelector("#regex-" + value);
    const boxes = () => dialog.querySelectorAll('input[type="checkbox"]');
    let saved = []; // галочки на момент открытия модала

    // Строка, по которой сейчас отмечены галочки, и ошибка её разбора.
    let synced = { text: "", error: "" };
    let pending = null; // разбор, который ещё ждёт ответа сервера

    // Галочки -> строка. После «Применить» и при восстановлении формы.
    function refreshText() {
        return fetch(`/${corpusId}/search/preview`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formToObject(root)),
        })
            .then(r => r.json())
            .then(data => {
                regex.value = data.text;
                synced = { text: data.text, error: "" };
            });
    }

    // Строка -> галочки. Возвращает текст ошибки или "".
    // Зовётся при уходе из поля и перед каждым поиском (main.js): поиск
    // сверяет то, что написано прямо сейчас, и не зависит от того, успел ли
    // сработать change. Ищется всегда по галочкам, строка лишь их отмечает.
    function syncText() {
        const text = regex.value.trim();
        if (text === synced.text) return Promise.resolve(synced.error);
        if (pending?.text !== text) {
            const promise = parseText(text).finally(() => {
                if (pending?.text === text) pending = null;
            });
            pending = { text, promise };
        }
        return pending.promise;
    }

    async function parseText(text) {
        let checked = {};
        let canonical = "";
        if (text) {
            const response = await fetch(`/${corpusId}/search/checkboxes`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            });
            const data = await response.json();
            // пока ждали ответ, строку успели поменять — разбираем новую
            if (regex.value.trim() !== text) return syncText();
            if (!response.ok) {
                // галочки не трогаем; «Найти» не пустит, пока строку не исправят
                synced = { text, error: data.error };
                showSearchHint(data.error);
                return data.error;
            }
            checked = data.checked;
            canonical = data.text;
        }
        // пустая строка снимает все галочки, без запроса к серверу
        boxes().forEach(cb => {
            cb.checked = (checked[cb.name] ?? []).includes(cb.value);
        });
        regex.value = canonical;
        synced = { text: canonical, error: "" };
        return "";
    }

    root.syncText = syncText;
    regex.addEventListener("change", syncText);
    regex.addEventListener("input", () => {
        if (!regex.value.trim()) syncText();
    });
    regex.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault(); // иначе Enter отправит <form> и перезагрузит страницу
            regex.blur();       // blur вызовет change
        }
    });

    const select = root.querySelector("#extension-" + value);
    keyboardActivate(select);

    const trueValue = root.querySelector("#correct_placeholder-" + value);
    const closeButton = root.querySelector("#closure-" + value);

    function toggleClearButton() {
        closeButton.style.display = trueValue.value !== "" ? "flex" : "none";
    }

    trueValue.addEventListener("input", toggleClearButton);

    // не даём кнопке забрать фокус у инпута до клика
    closeButton.addEventListener("mousedown", (e) => e.preventDefault());

    closeButton.addEventListener("click", function (e) {
        e.preventDefault();
        trueValue.value = "";
        trueValue.focus();
        trueValue.dispatchEvent(new Event("input", { bubbles: true }));
    });

    toggleClearButton();

    root.querySelector("#add-" + value).addEventListener("click", function(e) {
        e.preventDefault();
        manager.add(this);
    });

    root.querySelector("#remove-" + value).addEventListener("click", function(e) {
        e.preventDefault();
        manager.remove(this);
    });

    root.querySelector("#wordform-" + value).addEventListener("click", function() {
        wordformButton(this);
    });

    root.querySelector("#lemma-" + value).addEventListener("click", function() {
        lemmaButton(this);
    });

    root.querySelector("#kbd-" + value).addEventListener("click", function(e) {
        e.preventDefault();
        actionKeyboard(this);
    });

    root.querySelector("#gram-chosen-" + value).addEventListener("click", function(e) {
        saved = [...boxes()].map(cb => cb.checked);
        dialog.showModal();
    });

    // закрыли без «Применить» (крестик или Esc) — возвращаем, как было
    const restore = () => boxes().forEach((cb, i) => cb.checked = saved[i]);
    dialog.addEventListener("cancel", restore);

    const letters = root.querySelectorAll(".letters");
    letters.forEach((item) => {
        item.addEventListener("click", function (e) {
            const selectedLetter = item.textContent;
            const trueValue = root.querySelector(
                "#correct_placeholder-" + value
            );
            trueValue.value += selectedLetter;
            trueValue.dispatchEvent(new Event("input", { bubbles: true }));
        });
    });

    root.querySelector("#close-modal-" + value).addEventListener("click", function(e) {
        restore();
        dialog.close();
    });

    root.querySelector('#check-categories-' + value).addEventListener('click', function () {
        const checkboxes = root.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        })
    });

    root.querySelector("#reset-categories-" + value).addEventListener('click', function() {
        const checkboxes = root.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        })
    });

    root.querySelector("#checked-categories-" + value).addEventListener('click', function() {
        dialog.close();
        // галочки теперь главнее строки: пока /preview не ответил, старая
        // строка считается разобранной, чтобы «Найти» не перебил галочки ею
        synced = { text: regex.value.trim(), error: "" };
        refreshText();
    });

    dialog.querySelectorAll(".feature-block").forEach((block) => {
        const selectAll = block.querySelector("h4 > label > input");
        if (selectAll) {
            selectAll.addEventListener("click", function() {
            block.querySelectorAll("label > input[type='checkbox']")
                .forEach(cb => cb.checked = selectAll.checked);
        });

        }
    });

}

function formToObject(form) {
    const obj = {};
    for (const [key, value] of new FormData(form).entries()) {
        if (obj[key] === undefined) obj[key] = value;
        else if (Array.isArray(obj[key])) obj[key].push(value);
        else obj[key] = [obj[key], value];
    }
    return obj;
}

export function fillFrame(root, data) {
    const index = root.id.match(/\d+$/)[0];
    const values = name => [].concat(data[name] ?? []);

    const select = root.querySelector("#extension-" + index);
    if (data["language-select"]) {
        select.value = data["language-select"];
        select.dispatchEvent(new Event("change"));
    }
    const type = data["search-type"] === "token" ? "#wordform-" : "#lemma-";
    root.querySelector(type + index).click();

    const word = root.querySelector("#correct_placeholder-" + index);
    word.value = data["input_word"] ?? "";
    word.dispatchEvent(new Event("input", { bubbles: true }));

    let checked = false;
    root.querySelectorAll('dialog input[type="checkbox"][name]').forEach(cb => {
        cb.checked = values(cb.name).includes(cb.value);
        checked ||= cb.checked;
    });

    // «Применить» соберёт строку из галочек через /preview
    if (checked) root.querySelector("#checked-categories-" + index).click();
}


function updateIds(root, oldIndex, newIndex) {
    // обрабатываем сам корневой элемент
    if (root.id && root.id.includes(oldIndex)) {
        root.id = root.id.replace(new RegExp(oldIndex + '$'), newIndex);
    }

    // затем всех потомков
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
    while (walker.nextNode()) {
        const el = walker.currentNode;
        if (el.id && el.id.includes(oldIndex)) {
            el.id = el.id.replace(new RegExp(oldIndex + '$'), newIndex);
        }
        if (el.htmlFor && el.htmlFor.includes(oldIndex)) {
            el.htmlFor = el.htmlFor.replace(new RegExp(oldIndex + '$'), newIndex);
        }
    }
};

export function createDiv(value, manager) {
    const template = document.getElementById("search-frame-template");
    const clone = template.content.cloneNode(true);
    const root = clone.firstElementChild;

    updateIds(root, "0", String(value));
    bindEvents(root, value, manager);
    return root;
}