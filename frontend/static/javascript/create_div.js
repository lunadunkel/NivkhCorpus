import {actionKeyboard, keyboardActivate, wordformButton, lemmaButton} from './click_based_fts.js';



function bindEvents(root, value, manager) {

     let gramState = {}; // состояние чекбоксов для этого фрейма

    const v = value;
    const dialog = root.querySelector("#pop-up-" + v);

    const select = root.querySelector("#extension-" + value);
    keyboardActivate(select);

    root.querySelector("#add-" + value).addEventListener("click", function(e) {
        e.preventDefault();
        manager.add(this);
    });

    root.querySelector("#closure-" + value).addEventListener("click", function(e) {
        e.preventDefault();
        manager.remove(this);
    });

    root.querySelector("#wordform-" + value).addEventListener("click", function() {
        wordformButton(this);
    });

    root.querySelector("#lemma-" + value).addEventListener("click", function() {
        lemmaButton(this);
    });

    root.querySelector("#nivkh_keyboard-" + value).addEventListener("click", function(e) {
        e.preventDefault();
        actionKeyboard(this);
    });

    root.querySelector("#gram-chosen-" + value).addEventListener("click", function(e) {
        root.querySelector("#pop-up-" + value).showModal();
    });

    root.querySelector("#close-modal-" + value).addEventListener("click", function(e) {
        if (Object.keys(gramState).length === 0) {
            dialog.querySelectorAll('input[type="checkbox"]')
                .forEach(cb => cb.checked = false);
        } else {
            dialog.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                const key = cb.name + "__" + cb.value;
                if (key in gramState) cb.checked = gramState[key];
            });
        }
        dialog.close()
        // root.querySelector("#pop-up-" + value).close();
        // const checkboxes = root.querySelectorAll('input[type="checkbox"]');
        // checkboxes.forEach(checkbox => {
        //     checkbox.checked = false;
        // })
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
        gramState = {};
        dialog.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                gramState[cb.name + "__" + cb.value] = cb.checked;
        });

        const gramQuery = {}
        const checkboxes = root.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            const categoryName = checkbox.name;
            if (checkbox.checked && categoryName && checkbox.value !== 'all') { // вот здесь
                const categoryValue = checkbox.value;
                if (!(categoryName in gramQuery)) {
                    gramQuery[categoryName] = [];
                }
                gramQuery[categoryName].push(categoryValue);
            };
        });
        root.querySelector("#pop-up-" + value).close();
        const parts = [];
        for (const [name, values] of Object.entries(gramQuery)) {
            // let part;
            let part = values.length > 1 ? `(${values.join('|')})` : values[0];
            // } else {
            //     const key = name.replace('[]', '');
            //     const vals = values.map(v => `${key}=${v}`);
            //     part = vals.length > 1 ? `(${vals.join('|')})` : vals[0];
            // }
            parts.push(part);
        }
        root.querySelector("#regex-" + value).value = parts.join(' & ');

        root.querySelector("#pop-up-" + value).close(); // это уже было
        console.log(gramQuery);
    });

    dialog.querySelectorAll(".feature-block").forEach((block) => {
        const selectAll = block.querySelector("h4 > label > input");
        selectAll.addEventListener("click", function() {
            block.querySelectorAll("label > input[type='checkbox']")
                .forEach(cb => cb.checked = selectAll.checked);
        });
    });

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
    console.log("adding", value);
    const template = document.getElementById("search-frame-template");
    const clone = template.content.cloneNode(true);
    const root = clone.firstElementChild;

    updateIds(root, "0", String(value));
    bindEvents(root, value, manager);
    return root;
}