// Фильтр по таблицам справки: <input data-filter="CSS-селектор строк">.
// Строки, в которых нет введённого текста, скрываются.
for (const input of document.querySelectorAll("[data-filter]")) {
    const rows = [...document.querySelectorAll(input.dataset.filter)];
    const empty = input.parentElement.querySelector(".ref-empty");

    input.addEventListener("input", () => {
        const query = input.value.trim().toLowerCase();
        let shown = 0;
        for (const row of rows) {
            const hit = !query || row.textContent.toLowerCase().includes(query);
            row.hidden = !hit;
            if (hit) shown += 1;
        }
        if (empty) empty.hidden = shown > 0;
    });
}
