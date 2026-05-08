(async () => {
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  if (!input || !results) return;

  let shlokas = [];

  try {
    const res = await fetch('./search.json');
    shlokas = await res.json();
  } catch {
    return;
  }

  function match(shloka, query) {
    const q = query.toLowerCase();
    return (
      shloka.title.toLowerCase().includes(q) ||
      shloka.source.toLowerCase().includes(q) ||
      shloka.shloka.toLowerCase().includes(q) ||
      shloka.tags.some(t => t.toLowerCase().includes(q)) ||
      shloka.translation_languages.some(l => l.toLowerCase().includes(q))
    );
  }

  function render(hits) {
    results.innerHTML = '';
    if (!hits.length) {
      results.hidden = true;
      return;
    }
    hits.slice(0, 8).forEach(s => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = s.url;
      a.innerHTML =
        `<span>${s.title}</span>` +
        `<span class="search-result-source">${s.source}</span>`;
      li.appendChild(a);
      results.appendChild(li);
    });
    results.hidden = false;
  }

  input.addEventListener('input', () => {
    const q = input.value.trim();
    render(q.length >= 2 ? shlokas.filter(s => match(s, q)) : []);
  });

  document.addEventListener('click', e => {
    if (!input.contains(e.target) && !results.contains(e.target)) {
      results.hidden = true;
    }
  });

  input.addEventListener('focus', () => {
    if (input.value.trim().length >= 2) results.hidden = false;
  });
})();