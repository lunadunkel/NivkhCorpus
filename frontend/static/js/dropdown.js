// document.addEventListener('click', (event) => {
//     document.querySelectorAll('.dropdown[open]').forEach((dropdown) => {
//         if (!dropdown.contains(event.target)) dropdown.open = false;
//     });
// });

// document.addEventListener('keydown', (event) => {
//     if (event.key !== 'Escape') return;
//     const dropdown = document.querySelector('.dropdown[open]');
//     if (!dropdown) return;
//     dropdown.open = false;
//     dropdown.querySelector('.dropdown-toggle').focus();
// });

// const FILTER_ENDPOINT = `/${corpus.id}/search/update_filter`;

// function collectFilters() {
//     const filters = {};
//     document.querySelectorAll('.dropdown input:checked').forEach((input) => {
//         (filters[input.name] ??= []).push(input.value);
//     });
//     return filters;
// }

// let controller = null;
// let debounceTimer = null;

// async function loadResults({ replace }) {
//     if (!replace && replacing) return; // пока применяется фильтр, «показать ещё» ждёт

//     controller?.abort();
//     controller = new AbortController();
//     replacing = replace;

//     const params = new URLSearchParams({
//         job_id: jobId,
//         offset: replace ? 0 : currentOffset,
//     });

//     try {
//         const response = await fetch(`${FILTER_ENDPOINT}?${params}`, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify(collectFilters()),
//             signal: controller.signal,
//         });
//         if (!response.ok) throw new Error(`HTTP ${response.status}`);
//         const data = await response.json();
//         process_output(data.results, data.length, { replace });
//         replacing = false;
//     } catch (err) {
//         if (err.name === 'AbortError') return;
//         replacing = false;
//         console.error('Не удалось загрузить результаты:', err);
//     }
// }

// function scheduleSend() {
//     clearTimeout(debounceTimer);
//     debounceTimer = setTimeout(() => loadResults({ replace: true }), 300);
// }

// document.querySelectorAll('.dropdown').forEach((dropdown) => {
//     const counter = dropdown.querySelector('.dropdown-count');

//     const updateCounter = () => {
//         if (!counter) return;
//         const count = dropdown.querySelectorAll('input:checked').length;
//         counter.textContent = count;
//         counter.hidden = count === 0;
//     };

//     dropdown.addEventListener('change', () => {
//         updateCounter();
//         scheduleSend();
//     });
//     updateCounter();
// });