import { WordManager, keyboardActivate, actionKeyboard, lemmaButton, wordformButton } from './javascript/click_based_fts.js';
import { createDiv } from './javascript/create_div.js';

export const manager = new WordManager(createDiv);

document.addEventListener("DOMContentLoaded", function () {
	// добавление из template поискового окна для первого элемента
	const frame = createDiv("0", manager);
	const parentFrame = document.getElementById("search-frame");
	parentFrame.appendChild(frame);
    document.getElementById("closure-0").style.display = "none";

});


document.getElementById("search").addEventListener("click", async () => {
	const forms = document.querySelectorAll(".main-searching-frame");
	const allData = [];
	let hasAnyValue = false;

	forms.forEach(form => {
		const formData = new FormData(form);
		const formObj = {};

		for (const [key, value] of formData.entries()) {
			if (key === "language-select" || /^search-type\d*$/.test(key)) {
				formObj[key] = value;
				continue;
			}

			if (value.trim() !== "") {
				console.log(value);
				hasAnyValue = true;
			}

			if (formObj[key] !== undefined) {
				if (Array.isArray(formObj[key])) {
					formObj[key].push(value);
				} else {
					formObj[key] = [formObj[key], value];
				}
			} else {
				formObj[key] = value;
			}
		}

		allData.push(formObj);
	});

	if (!hasAnyValue) {
		alert("Введите хотя бы одно поле для поиска.");
		return;
	}

	console.log("Отправка данных:", allData);

	try {
		const response = await fetch("/search", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(allData)
		});

		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(`HTTP ${response.status}: ${errorText}`);
		}

		const result = await response.json();
		console.log("Успешный ответ от сервера:", result);

		window.location.href = "search_output.html";

	} catch (error) {
		console.error("Ошибка при запросе:", error);
	}
});