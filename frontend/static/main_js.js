document.addEventListener("DOMContentLoaded", function () {
	const extension = document.getElementById("extension");

	extension.addEventListener("change", function () {
		const selectedValue = this.value;

		const keyboards = document.querySelectorAll(".letter-input");
		const keyboardButtons = document.querySelectorAll(".keyboard");

		if (selectedValue === "nivkh") {
			// показываем кнопки клавиатуры
			keyboardButtons.forEach((btn) => (btn.style.display = "flex"));
		} else if (selectedValue === "russian") {
			// скрываем кнопки и клавиатуры
			keyboardButtons.forEach((btn) => (btn.style.display = "none"));
			keyboards.forEach((kb) => (kb.style.display = "none"));
		}
	});

	if (extension.value) {
		extension.dispatchEvent(new Event("change"));
	}
});

document.addEventListener("DOMContentLoaded", function () {
	const add_frame = document.getElementById("add0");

	add_frame.addEventListener("click", function () {
		addWord(add_frame);
	});
});

document.addEventListener("DOMContentLoaded", function () {
	const modalButton = document.querySelectorAll(".select-features");
	modalButton.forEach((item) => {
		if (item.id.match("gram-chosen")) {
			item.addEventListener("click", function () {
				const id_value = item.id.match(/\d+/)[0];
				document.getElementById("pop-up" + id_value).showModal();
			});
		} else if (item.id.match("check-all")) {
			item.addEventListener("click", function () {
				add_feats = document.getElementById('add-feat' + item.id.match(/\d+/)[0])
				var checkboxes = add_feats.getElementsByTagName("input");
				for (var i=0; i < checkboxes.length; i++){
					if (checkboxes[i].type == 'checkbox')
						checkboxes[i].checked = true;
				}
			});
		}
	});
});

document.addEventListener('DOMContentLoaded', function() {
    const dialogs = document.querySelectorAll("dialog");
    dialogs.forEach((dialog) => {
        const button = dialog.querySelector('.modal-buttons');
		button.addEventListener('click', function() {
			const checkboxes = dialog.querySelectorAll('input[type="checkbox"]');
			checkboxes.forEach(checkbox => {
					checkbox.checked = true;
			})
		})
    })
});


// document.addEventListener('DOMContentLoaded', function() {
//     const checkboxes = document.querySelectorAll('.my-checkbox');
//     const button = document.getElementById('myButton');

//     function updateButtonState() {
//         let anyCheckboxChecked = false;
//         checkboxes.forEach(checkbox => {
//             if (checkbox.checked) {
//                 anyCheckboxChecked = true;
//             }
//         });
//         button.disabled = !anyCheckboxChecked;
//     }

//     // Initial state check
//     updateButtonState();

//     // Add event listener to each checkbox
//     checkboxes.forEach(checkbox => {
//         checkbox.addEventListener('change', updateButtonState);
//     });
// });


document.addEventListener("DOMContentLoaded", function () {
	const resetButton = document.querySelectorAll(".underline-button");
	resetButton.forEach((item) => {
		if (item.id.match("reset-features")) {
			item.addEventListener("click", function () {
				add_feats = document.getElementById('add-feat' + item.id.match(/\d+/)[0])
				var checkboxes = add_feats.getElementsByTagName("input");
				for (var i=0; i < checkboxes.length; i++){
					if (checkboxes[i].type == 'checkbox')
						checkboxes[i].checked = false;
				}
			});
		}
	});
});

document.addEventListener('DOMContentLoaded', function() {
	const dialogs = document.querySelectorAll("dialog");
	dialogs.forEach((dialog) => {
		const buttons = dialog.querySelectorAll('.modal-buton');

		buttons.forEach((button) => {
			button.addEventListener('click', function() {
				const checkboxes = dialog.querySelectorAll('input[type="image"]');
				checkboxes.forEach(checkbox => {
					if (checkbox.checked) {
						checkbox.checked = true;
					}
        		});	

			})
		})
	})
});


document.addEventListener("DOMContentLoaded", function () {
	const dialogs = document.querySelectorAll("dialog");

	dialogs.forEach(dialog => {
		const closeButton = dialog.querySelector('input[type="image"]');
		if (closeButton) {
			closeButton.addEventListener("click", function (e) {
				e.preventDefault();
				dialog.close();
			});
		}
	});
});

document.getElementById("search").addEventListener("click", async () => {
  const forms = document.querySelectorAll(".main-searching-frame");
  const allData = [];

  forms.forEach(form => {
    const formData = new FormData(form);
    const formObj = {};
    for (const [key, value] of formData.entries()) {
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

document.addEventListener("DOMContentLoaded", function (e) {
	// e.preventDefault();
	const featureBlock = document.querySelectorAll(".feature-block");
	featureBlock.forEach((block) => {
			const selectAll = block.querySelector('h4 > label > input');
			selectAll.addEventListener('click', function(e){
				// e.preventDefault();
				var checkboxes = block.querySelectorAll("label > input");
				if (selectAll.checked == true) {
					for (var i=0; i < checkboxes.length; i++) {
						if (checkboxes[i].type == 'checkbox') {
							checkboxes[i].checked = true;
						};
					};
				}
				else {
					for (var i=0; i < checkboxes.length; i++) {
						if (checkboxes[i].type == 'checkbox') {
							checkboxes[i].checked = false;
						}
					};
				}
			});

			const resetButton = document.querySelector(".simple-buttons");
			if (resetButton) {
				resetButton.addEventListener("click", function (e) {
					e.preventDefault();
					const checkboxes = block.querySelectorAll('input[type="checkbox"]');
					checkboxes.forEach((cb) => {
						cb.checked = false;
        			});
      		});
    	}

	});
});


function actionKeyboard(elem) {
	const id_value = elem.id.match(/\d+/)[0];
	const keyboard = document.getElementById("keyboard" + id_value);
	const displayValue = keyboard.style.display;
	if (!displayValue || displayValue == "none") {
		keyboard.style.display = "flex";
		const letterInput = keyboard.querySelectorAll(".letters");

		letterInput.forEach((item) => {
			item.addEventListener("click", function (e) {
				e.preventDefault();
				const selectedLetter = item.textContent;
				const trueValue = document.getElementById(
					"correct_placeholder" + id_value
				);
				trueValue.value += selectedLetter;
			});
		});
	} else if (displayValue == "flex") {
		keyboard.style.display = "none";
	}
}

function updateIds(root, oldIndex, newIndex) {
	const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);

	while (walker.nextNode()) {
		const el = walker.currentNode;

		if (el.id && el.id.includes(oldIndex)) {
			el.id = el.id.replace(oldIndex, newIndex);
		}

		if (el.htmlFor && el.htmlFor.includes(oldIndex)) {
			el.htmlFor = el.htmlFor.replace(oldIndex, newIndex);
		}

		// Переписываем name (если нужно уникализировать input'ы)
		if (el.name && el.name.includes(oldIndex)) {
			el.name = el.name.replace(oldIndex, newIndex);
		}
	}
}

var count = 1;
var pos_id = 1;

function addWord(target) {
	const id_value = target.id.match(/\d+/)[0];
	if (count >= 10) {
		alert("Вы достигли лимита слов!");
	}
	count += 1;

	const additional_frame = createDiv(pos_id);
	pos_id += 1;

	const prevDiv = document.getElementById("main-frame" + id_value);

	prevDiv.after(additional_frame);
}

function closeWord(target) {
	const id_value = target.id.match(/\d+/)[0];
	count -= 1;
	const deleteDiv = document.getElementById("main-frame" + id_value);
	deleteDiv.remove();
}

function closeContainer(target) {
	const matches = [...target.id.matchAll(/\d+/g)];
	// count -= 1;
	if (matches[1][0] == "0") {
		const deleteDiv = document.getElementById("gram-feat-cont" + matches[0][0]);
		deleteDiv.style.display = "none";
	} else if (matches[1][0] == "1") {
		const deleteDiv = document.getElementById("add-feat-cont" + matches[0][0]);
		deleteDiv.style.display = "none";
	}
}

function wordformButton(elem) {
	const id_value = elem.id.match(/\d+/)[0];
	document.getElementById("wordform" + id_value).checked = true;
	document.getElementById("lemma" + id_value).checked = false;

	const placeholder = document.getElementById("correct_placeholder" + id_value);
	placeholder.placeholder = "Найти по словоформе";
}

function lemmaButton(elem) {
	const id_value = elem.id.match(/\d/g);
	document.getElementById("wordform" + id_value).checked = false;
	document.getElementById("lemma" + id_value).checked = true;

	const placeholder = document.getElementById("correct_placeholder" + id_value);
	placeholder.placeholder = "Найти по лемме";
}

function createDiv(value) {
	const newSearchFrame = document.createElement("form");
	newSearchFrame.id = "main-frame" + value;
	newSearchFrame.className = "main-searching-frame";

	// Блок "Искать:"
	const newSearchOrder = document.createElement("div");
	newSearchOrder.className = "search-order";
	newSearchOrder.textContent = "Искать:";

	const newCheckboxes = document.createElement("div");
	newCheckboxes.className = "checkboxes";

	// Чекбокс "До"
	const newDivBefore = document.createElement("div");
	const newBeforeCheckbox = document.createElement("input");
	newBeforeCheckbox.name = 'order[]';
	newBeforeCheckbox.type = "checkbox";
	newBeforeCheckbox.id = "before" + value;
	newBeforeCheckbox.value = 'before';
	newBeforeCheckbox.name = "search-order1";
	const newBeforeLabel = document.createElement("label");
	newBeforeLabel.htmlFor = newBeforeCheckbox.id;
	newBeforeLabel.textContent = "До";

	newDivBefore.appendChild(newBeforeCheckbox);
	newDivBefore.appendChild(newBeforeLabel);
	newCheckboxes.appendChild(newDivBefore);

	// Чекбокс "После"
	const newDivAfter = document.createElement("div");
	const newAfterCheckbox = document.createElement("input");
	newAfterCheckbox.type = "checkbox";
	newAfterCheckbox.value = 'after';
	newAfterCheckbox.name = 'order[]';
	newAfterCheckbox.name = "search-order";
	newAfterCheckbox.id = "after" + value;
	const newAfterLabel = document.createElement("label");
	newAfterLabel.htmlFor = newAfterCheckbox.id;
	newAfterLabel.textContent = "После";

	newDivAfter.appendChild(newAfterCheckbox);
	newDivAfter.appendChild(newAfterLabel);
	newCheckboxes.appendChild(newDivAfter);

	newSearchOrder.appendChild(newCheckboxes);
	newSearchFrame.appendChild(newSearchOrder);

	// Радио кнопки (Словоформа / Лемма)
	const newSelection = document.createElement("div");
	newSelection.classList = "search-selection-info";

	const newControl = document.createElement("div");
	newControl.classList = "segmented-control";

	const newRadioWordform = document.createElement("input");
	newRadioWordform.type = "radio";
	newRadioWordform.id = "wordform" + value;
	newRadioWordform.name = "search-type" + value;
	newRadioWordform.value = 'wordform';
	newRadioWordform.addEventListener("click", function (e) {
		wordformButton(newRadioWordform);
	});
	newRadioWordform.checked = true;

	const newRadioWordformLabel = document.createElement("label");
	newRadioWordformLabel.htmlFor = newRadioWordform.id;
	newRadioWordformLabel.textContent = "Словоформа";

	newControl.appendChild(newRadioWordform);
	newControl.appendChild(newRadioWordformLabel);

	const newRadioLemma = document.createElement("input");
	newRadioLemma.type = "radio";
	newRadioLemma.id = "lemma" + value;
	newRadioLemma.name = "search-type" + value;
	newRadioLemma.value = 'lemma'
	newRadioLemma.addEventListener("click", function () {
		lemmaButton(newRadioLemma);
	});

	const newRadioLemmaLabel = document.createElement("label");
	newRadioLemmaLabel.htmlFor = newRadioLemma.id;
	newRadioLemmaLabel.textContent = "Лемма";

	newControl.appendChild(newRadioLemma);
	newControl.appendChild(newRadioLemmaLabel);
	newSelection.appendChild(newControl);

	// Кнопки добавления и закрытия
	const newRegulation = document.createElement("div");
	newRegulation.classList = "regulation-adding";

	const newAdd = document.createElement("div");
	newAdd.classList = "add-word";

	const newAddImg = document.createElement("input");
	newAddImg.id = "add" + value;
	newAddImg.type = "image";
	newAddImg.setAttribute("src", "/static/images/add.svg");
	newAddImg.onclick = function (e) {
		e.preventDefault();
		addWord(newAddImg);
	};
	// newAddImg.style.width = "20px";
	// newAddImg.style.height = "20px";

	newAdd.appendChild(newAddImg);
	newRegulation.appendChild(newAdd);

	const newClose = document.createElement("div");
	newClose.classList = "close-word";
	const newCloseImg = document.createElement("input");
	newCloseImg.id = "closure" + value;
	newCloseImg.type = "image";
	newCloseImg.setAttribute("src", "/static/images/close.svg");

	newClose.addEventListener('mouseover', (e) => {
		e.preventDefault();
        newClose.style.backgroundColor = 'var(--100)';
        newClose.style.transform = "all 0.2s ease-out";
    });

	newClose.addEventListener('mouseouut', () => {
        newClose.style.backgroundColor = "";
        newClose.style.transform = "all 0.2s ease-out";
    });

	newCloseImg.onclick = function (e) {
		e.preventDefault();
		closeWord(newCloseImg);
	};
	newCloseImg.style.width = "20px";
	newCloseImg.style.height = "20px";

	newClose.appendChild(newCloseImg);
	newRegulation.appendChild(newClose);
	newSelection.appendChild(newRegulation);
	newSearchFrame.appendChild(newSelection);

	// Поле поиска
	const newSearchInput = document.createElement("div");
	newSearchInput.classList = "searching-input";

	const newInputField = document.createElement("input");
	newInputField.id = "correct_placeholder" + value;
	newInputField.classList = "input-panel";
	newInputField.type = "search";
	newInputField.name = "input_word" + value;
	newInputField.placeholder = "Найти по словоформе";

	newSearchInput.appendChild(newInputField);

	// Кнопка клавиатуры
	const newKeyboardContainer = document.createElement("div");
	newKeyboardContainer.classList = "keyboard-container";

	const newKeyboardButton = document.createElement("input");
	newKeyboardButton.id = "nivkh_keyboard" + value;
	newKeyboardButton.classList = "keyboard";
	newKeyboardButton.type = "image";
	newKeyboardButton.setAttribute("src", "/static/images/keyboard.svg");
	newKeyboardButton.addEventListener("click", function (e) {
		e.preventDefault();
		actionKeyboard(newKeyboardButton);
	});

	newKeyboardContainer.appendChild(newKeyboardButton);
	newSearchInput.appendChild(newKeyboardContainer);
	newSearchFrame.appendChild(newSearchInput);

	// Копия клавиатуры
	const LetterInput = document.getElementById("keyboard0");
	const newLetterInput = LetterInput.cloneNode(true);
	updateIds(newLetterInput, "0", value);

	newLetterInput
		.querySelectorAll("[style]")
		.forEach((el) => el.removeAttribute("style"));
	newLetterInput.style.display = "none";
	newLetterInput.id = "keyboard" + value;

	newSearchFrame.appendChild(newLetterInput);

	// Первый блок (Грамматические признаки)
	const newBasicContainer1 = document.createElement("div");
	newBasicContainer1.classList = "basic-container";
	newBasicContainer1.id = "gram-feat-cont" + value;

	const newTopContainer1 = document.createElement("div");
	newTopContainer1.classList = "top-base-container";
	const newTitle1 = document.createElement("div");
	newTitle1.textContent = "Грамматические признаки";

	newTopContainer1.appendChild(newTitle1);

	const newAddSelections1 = document.createElement("div");
	newAddSelections1.classList = "additional-selections";

	const newSelectFeatures = document.createElement("div");
	newSelectFeatures.classList = "select-features";
	newSelectFeatures.textContent = "Выбрать";
	newSelectFeatures.id = "gram-chosen" + value;
	newSelectFeatures.addEventListener("click", function (e) {
		e.preventDefault();
		document.getElementById("pop-up" + value).showModal();
	});

	newAddSelections1.appendChild(newSelectFeatures);

	// маленькие кнопки
	const newSmallButtons1 = document.createElement("div");
	newSmallButtons1.classList = "small-extra-buttons";

	const newQuestion1 = document.createElement("input");
	newQuestion1.id = "question0_" + value;
	newQuestion1.type = "image";
	newQuestion1.setAttribute("src", "/static/images/question_mark.svg");
	newQuestion1.addEventListener("click", function (e) {
		e.preventDefault();
	});
	newQuestion1.style.width = "10px";
	newQuestion1.style.height = "10px";

	newSmallButtons1.appendChild(newQuestion1);
	newAddSelections1.appendChild(newSmallButtons1);

	const newCloseSmall1 = document.createElement("div");
	newCloseSmall1.classList = "small-extra-buttons";

	const newCloseInput1 = document.createElement("input");
	newCloseInput1.id = "close_container" + value + "_" + "0";
	newCloseInput1.type = "image";
	newCloseInput1.setAttribute("src", "/static/images/close.svg");
	newCloseInput1.style.width = "10px";
	newCloseInput1.style.height = "10px";
	newCloseInput1.addEventListener("click", function (e) {
		e.preventDefault();
		closeContainer(newCloseInput1);
	});

	newCloseSmall1.appendChild(newCloseInput1);
	newAddSelections1.appendChild(newCloseSmall1);

	newTopContainer1.appendChild(newAddSelections1);
	newBasicContainer1.appendChild(newTopContainer1);

	const newRegexInput = document.createElement("input");
	newRegexInput.type = "text";
	newRegexInput.id = "regex" + value;

	newBasicContainer1.appendChild(newRegexInput);
	newSearchFrame.appendChild(newBasicContainer1);

	// Второй блок (Дополнительные признаки)
	const newBasicContainer2 = document.createElement("div");
	newBasicContainer2.classList = "basic-container";
	newBasicContainer2.id = "add-feat-cont" + value;

	const newTopContainer2 = document.createElement("div");
	newTopContainer2.classList = "top-base-container";

	const newTitle2 = document.createElement("div");
	newTitle2.textContent = "Дополнительные признаки";

	newTopContainer2.appendChild(newTitle2);


	const newAddSelections2 = document.createElement("div");
	newAddSelections2.classList = "additional-selections";


	const newSelectFeaturesAdd2 = document.createElement("div");
	newSelectFeaturesAdd2.classList = "select-features";
	newSelectFeaturesAdd2.id = "check-all" + value;
	newSelectFeaturesAdd2.textContent = 'Выбрать все';

	newSelectFeaturesAdd2.addEventListener("click", function (e) {
		e.preventDefault();
		add_feats = document.getElementById('add-feat' + value)
		var checkboxes = add_feats.getElementsByTagName("input");
			for (var i=0; i < checkboxes.length; i++){
				if (checkboxes[i].type == 'checkbox') {
					checkboxes[i].checked = true;
				}
			}
	});

	newAddSelections2.appendChild(newSelectFeaturesAdd2);


	const newSmallButtons2 = document.createElement("div");
	newSmallButtons2.classList = "small-extra-buttons";

	const newQuestion2 = document.createElement("input");
	newQuestion2.id = "question1_" + value;
	newQuestion2.type = "image";
	newQuestion2.setAttribute("src", "/static/images/question_mark.svg");
	newQuestion2.addEventListener("click", function (e) {
		e.preventDefault();
	});
	newQuestion2.style.width = "10px";
	newQuestion2.style.height = "10px";

	newSmallButtons2.appendChild(newQuestion2);
	newAddSelections2.appendChild(newSmallButtons2);

	const newCloseSmall2 = document.createElement("div");
	newCloseSmall2.classList = "small-extra-buttons";

	const newCloseInput2 = document.createElement("input");
	newCloseInput2.id = "close_container" + value + "_" + "1";
	newCloseInput2.type = "image";
	newCloseInput2.setAttribute("src", "/static/images/close.svg");
	newCloseInput2.style.width = "10px";
	newCloseInput2.style.height = "10px";
	newCloseInput2.addEventListener("click", function (e) {
		e.preventDefault();
		closeContainer(newCloseInput2);
	});

	newCloseSmall2.appendChild(newCloseInput2);
	newAddSelections2.appendChild(newCloseSmall2);

	newTopContainer2.appendChild(newAddSelections2);
	newBasicContainer2.appendChild(newTopContainer2);

	const firstWrapper = document.createElement("div");
	firstWrapper.classList = "additional-wrapper";

	const secondWrapper = document.createElement("div");
	secondWrapper.classList = "features-wrapper";

	const oldSelect = document.getElementById("add-feat0");
	const newSelect = oldSelect.cloneNode(true);
	newSelect.id = "add-feat" + value;
	updateIds(newSelect, "0", value);

	// снимаем checked у всех input внутри newSelect
	for (let elem of newSelect.children) {
		const checkboxes = elem.getElementsByTagName("input");
		for (let checkbox of checkboxes) {
			checkbox.checked = false;
		}
	}

	secondWrapper.appendChild(newSelect);
	firstWrapper.appendChild(secondWrapper);

	newBasicContainer2.appendChild(firstWrapper);

	const newAdditionalContent = document.createElement('div');
	newAdditionalContent.classList = "additional-content";

	const newResetButton = document.createElement('button');
	newResetButton.type = 'button';
	newResetButton.classList = "underline-button";
	newResetButton.id = "reset-features" + value;
	newResetButton.textContent = "Сбросить";

	newResetButton.addEventListener("click", function (e) {
		e.preventDefault();
		var checkboxes = newSelect.getElementsByTagName("input");
		for (var i=0; i < checkboxes.length; i++){
			if (checkboxes[i].type == 'checkbox')
				checkboxes[i].checked = false;
		}
	});

	newAdditionalContent.appendChild(newResetButton);
	newBasicContainer2.appendChild(newAdditionalContent);

	newSearchFrame.appendChild(newBasicContainer2);

	const oldDialog = document.getElementById("pop-up0");
	const newDialog = oldDialog.cloneNode(true);
	newDialog.id = "pop-up" + value;
	updateIds(newDialog, "0", value);

	const allNewCheckboxes = newDialog.querySelectorAll('input[type="checkbox"]');
	allNewCheckboxes.forEach(checkbox => {
		checkbox.checked = false
	});

	newResetButtonDialog = newDialog.querySelector('.modal-top > .left-buttons > .simple-buttons');
	newResetButtonDialog.addEventListener("click", function () {

		var checkboxes = newDialog.getElementsByTagName("input");
		for (var i=0; i < checkboxes.length; i++){
			if (checkboxes[i].type == 'checkbox')
				checkboxes[i].checked = false;
		}
	});

	for (let elem of newDialog.children) {
		const checkboxes = elem.getElementsByTagName("input");

		for (let checkbox of checkboxes) {
			if (checkbox.value === 'all') {
				checkbox.addEventListener('change', () => {
					const baseName = checkbox.name.replace('[]', '');
					const related = elem.querySelectorAll(`input[name="${baseName}[]"]`);

					for (let r of related) {
						r.checked = checkbox.checked;
					}
				});
			}
		}
	}
	const selectAllCheckDialog =  newDialog.querySelector('.modal-buttons');

	selectAllCheckDialog.addEventListener("click", function() {
		const checkboxes = newDialog.getElementsByTagName("input");
		for (let checkbox of checkboxes) {
			checkbox.checked = true;
		}
	});

	const closeButton = newDialog.querySelector('input[type="image"]');
	if (closeButton) {
		closeButton.addEventListener("click", function (e) {
			e.preventDefault();
				newDialog.close();
		});
	}
	newSearchFrame.appendChild(newDialog);

	return newSearchFrame;
} 

document.addEventListener("DOMContentLoaded", (e) => {
	e.preventDefault();
  	document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", event => {
      event.preventDefault();
    });
  });
});