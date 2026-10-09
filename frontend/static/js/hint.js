let hintTimer = null;

export function showSearchHint(message, ms = 3000) {
  const hint = document.getElementById("search-hint");
  if (!hint) return;
  hint.textContent = message;
  hint.classList.add("is-visible");
  clearTimeout(hintTimer);
  hintTimer = setTimeout(() => {
    hint.classList.remove("is-visible");
  }, ms); // само гаснет
}