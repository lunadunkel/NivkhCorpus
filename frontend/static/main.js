import { WordManager, keyboardActivate, actionKeyboard, lemmaButton, wordformButton } from './javascript/click_based_fts.js';
import { createDiv } from './javascript/create_div.js';

const lang = window.location.pathname.split("/")[1];

document.querySelectorAll('a[href*="{lang}"]').forEach(link => {
    const href = link.getAttribute("href");
    link.setAttribute("href", href.replace("{lang}", lang));
});

export const manager = new WordManager(createDiv);


document.addEventListener("DOMContentLoaded", function () {
	// добавление из template поискового окна для первого элемента
	const frame = createDiv("0", manager);
	const parentFrame = document.getElementById("search-frame");
	parentFrame.appendChild(frame);
    document.getElementById("closure-0").style.display = "none";

});

document.addEventListener("input", (e) => {
  if (e.target.closest(".main-searching-frame")) {
    const hint = document.getElementById("search-hint");
    if (hint) hint.classList.remove("is-visible");
  }
});

let hintTimer = null;

function showSearchHint(message) {
  const hint = document.getElementById("search-hint");
  if (!hint) return;
  hint.textContent = message;
  hint.classList.add("is-visible");
  clearTimeout(hintTimer);
  hintTimer = setTimeout(() => {
    hint.classList.remove("is-visible");
  }, 3000); // само гаснет через 3 c
}

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
		showSearchHint("Введите хотя бы одно поле для поиска.");
		return;
	}

	document.getElementById("text-search").style.display = "none";
	document.getElementById("loader").style.display = "block";
	document.getElementById("search").style.opacity = "0.8";

	console.log("Отправка данных:", allData);

	try {
		console.log(lang);
		const response = await fetch(`/${lang}/search`, {
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

		window.location.href = `/${lang}/search_output?job_id=${result.job_id}`;


	} catch (error) {
		console.error("Ошибка при запросе:", error);
	}
});

document.getElementById("reset").addEventListener("click", () => {
	const forms = document.querySelectorAll(".main-searching-frame");
 
	forms.forEach(form => {
		form.reset();
 
		form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
			cb.checked = false;
		});
 
		const langSelect = form.querySelector('select[name="language-select"]');
		if (langSelect) {
			langSelect.dispatchEvent(new Event("change", { bubbles: true }));
		}
	});
 
	const textSearch = document.getElementById("text-search");
	const loader = document.getElementById("loader");
	const searchBtn = document.getElementById("search");
	if (textSearch) textSearch.style.display = "";
	if (loader) loader.style.display = "none";
	if (searchBtn) searchBtn.style.opacity = "";
});