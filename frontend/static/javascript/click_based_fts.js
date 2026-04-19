import { createDiv } from './create_div.js';

export function keyboardActivate(elem) {
    elem.addEventListener("change", function () {
        const selectedValue = elem.value;
        const frame = elem.closest(".main-searching-frame");
        const keyboards = frame.querySelectorAll(".letter-input");
        const keyboardButtons = frame.querySelectorAll(".keyboard");
        const grammContainer = frame.querySelectorAll('.basic-container')
        const selectedRadio = document.querySelector('input[name="search-type"]:checked');
        
        if (selectedValue === "nivkh") {
            keyboardButtons.forEach((btn) => (btn.style.display = "flex"));
            grammContainer.forEach((cont) => (cont.style.display = "flex"))
        } else if (selectedValue === "russian") {
            keyboardButtons.forEach((btn) => (btn.style.display = "none"));
            keyboards.forEach((kb) => (kb.style.display = "none"));
            if (selectedRadio.value == "token") {
                grammContainer.forEach((cont) => (cont.style.display = "none"))
            };
        }
    });

    if (elem.value) {
        elem.dispatchEvent(new Event("change"));
    }
}

export function actionKeyboard(elem) {
    const frame = elem.closest(".main-searching-frame");
    const keyboard = frame.querySelector(".letter-input");
    const displayValue = keyboard.style.display;

    if (!displayValue || displayValue === "none") {
        keyboard.style.display = "flex";
    } else {
        keyboard.style.display = "none";
    }
}


export function wordformButton(elem) {
	const id_value = elem.id.match(/\d+/)[0];
	document.getElementById("wordform-" + id_value).checked = true;
	document.getElementById("lemma-" + id_value).checked = false;
    const languageValue = document.getElementById("extension-" + id_value).value;
    if (languageValue == "russian") {
        document.getElementById("gram-feat-cont-" + id_value).style.display = "none";
    } else {
        document.getElementById("gram-feat-cont-" + id_value).style.display = "flex";
    };


	const placeholder = document.getElementById("correct_placeholder-" + id_value);
	placeholder.placeholder = "Найти по словоформе";
}

export function lemmaButton(elem) {
	const id_value = elem.id.match(/\d+/g)[0];

	document.getElementById("wordform-" + id_value).checked = false;
	document.getElementById("lemma-" + id_value).checked = true;
    document.getElementById("gram-feat-cont-" + id_value).style.display = "flex";

	const placeholder = document.getElementById("correct_placeholder-" + id_value);
	placeholder.placeholder = "Найти по лемме";
}

export class WordManager {
    #pos_id = 1;
    #limit = 10;
    #selector = ".main-searching-frame";
    #createDiv;

    constructor(createDiv) {
        this.#createDiv = createDiv;
    }

    get count() {
        return document.querySelectorAll(this.#selector).length;
    }

    add(target) {
        if (this.count >= this.#limit) {
            alert("Вы достигли лимита слов!");
            return;
        }
        const id_value = target.id.match(/\d+/)[0];
        const frame = createDiv(this.#pos_id++, this);
        console.log("adding new value", frame);
        document.getElementById("main-frame-" + id_value).after(frame);
    }

    remove(target) {
        const id_value = target.id.match(/\d+/)[0];
        document.getElementById("main-frame-" + id_value)?.remove();
    }
}