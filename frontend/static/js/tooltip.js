document.addEventListener('DOMContentLoaded', () => {
  const dialog = document.getElementById('pop-up-0');
  const tip = document.getElementById('tooltip-0');

  if (!dialog) { console.error('не найден #pop-up-0'); return; }
  if (!tip)    { console.error('не найден #tooltip-0 — добавь div.tooltip в dialog'); return; }

  let showTimer = null;

  function positionTip(target) {
    const r = target.getBoundingClientRect();
    tip.style.left = (r.left + r.width / 2) + 'px';
    tip.style.top = r.top + 'px';
  }

  dialog.addEventListener('mouseover', (e) => {
    const target = e.target.closest('[data-tooltip]');
    if (!target) return;
    tip.textContent = target.dataset.tooltip;
    clearTimeout(showTimer);
    showTimer = setTimeout(() => {
      positionTip(target);
      tip.classList.add('is-visible');
    }, 700);
  });

  dialog.addEventListener('mouseout', (e) => {
    if (!e.target.closest('[data-tooltip]')) return;
    clearTimeout(showTimer);
    tip.classList.remove('is-visible');
  });

  dialog.querySelector('.gram-scroll-container')?.addEventListener('scroll', () => {
    clearTimeout(showTimer);
    tip.classList.remove('is-visible');
  });
});