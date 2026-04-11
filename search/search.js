/* =============================================
   OpenShelf — search.js
   ============================================= */
 
let currentBooks = [...BOOKS];
let savedSet = new Set(SAVED_IDS);
 
function renderResults(books) {
  const el = document.getElementById('result-list');
  const countEl = document.getElementById('result-count');
  countEl.textContent = books.length + ' listing' + (books.length !== 1 ? 's' : '') + ' found';
 
  if (books.length === 0) {
    el.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📭</div>
        <div class="empty-state-title">No results found</div>
        <div class="empty-state-text">Try a different title, course code, or author name.</div>
      </div>`;
    return;
  }
 
  el.innerHTML = books.map(b => {
    const isSaved = savedSet.has(b.id);
    return `
      <div class="result-card">
        <div class="result-cover" style="background:${b.bg}">${b.cover}</div>
        <div class="result-info">
          <div class="result-title">${b.title}</div>
          <div class="result-author">${b.author}</div>
          <div class="result-tags">
            <span class="pill pill-purple">${b.course}</span>
            <span class="pill ${conditionColor(b.condition)}">${b.condition}</span>
            ${b.isNew ? '<span class="badge-new">New</span>' : ''}
            ${b.hot  ? '<span class="badge-hot">Hot deal</span>' : ''}
          </div>
          <div class="result-seller">Listed by ${b.seller}</div>
        </div>
        <div class="result-price-col">
          <div>
            <div class="price-main">$${b.price}</div>
            <div class="price-orig">$${b.origPrice}</div>
          </div>
          <button
            class="result-save-btn ${isSaved ? 'saved-active' : ''}"
            onclick="toggleSave(event, ${b.id}, this)"
          >${isSaved ? '♥' : '♡'}</button>
        </div>
      </div>`;
  }).join('');
}
 
function toggleSave(e, id, btn) {
  e.stopPropagation();
  if (savedSet.has(id)) {
    savedSet.delete(id);
    btn.classList.remove('saved-active');
    btn.textContent = '♡';
    showToast('Removed from saved');
  } else {
    savedSet.add(id);
    btn.classList.add('saved-active');
    btn.textContent = '♥';
    showToast('Saved!');
  }
}
 
function doSearch(q) {
  const clearBtn = document.getElementById('clear-btn');
  clearBtn.classList.toggle('hidden', q.length === 0);
  q = q.toLowerCase().trim();
  currentBooks = BOOKS.filter(b =>
    b.title.toLowerCase().includes(q) ||
    b.course.toLowerCase().includes(q) ||
    b.author.toLowerCase().includes(q)
  );
  renderResults(currentBooks);
}
 
function clearSearch() {
  document.getElementById('search-input').value = '';
  document.getElementById('clear-btn').classList.add('hidden');
  currentBooks = [...BOOKS];
  renderResults(currentBooks);
  document.querySelectorAll('.tag').forEach(t => t.classList.remove('active-tag'));
  document.querySelector('.tag').classList.add('active-tag');
}
 
function quickSearch(el, tag) {
  document.querySelectorAll('.tag').forEach(t => t.classList.remove('active-tag'));
  el.classList.add('active-tag');
  const input = document.getElementById('search-input');
  input.value = tag;
  doSearch(tag);
}
 
function sortResults(v) {
  const condOrder = { 'Like new': 0, 'Good': 1, 'Highlighted': 2, 'Worn': 3 };
  if (v === 'price')     currentBooks.sort((a, b) => a.price - b.price);
  if (v === 'pricedesc') currentBooks.sort((a, b) => b.price - a.price);
  if (v === 'new')       currentBooks.sort((a, b) => b.isNew - a.isNew);
  if (v === 'cond')      currentBooks.sort((a, b) => condOrder[a.condition] - condOrder[b.condition]);
  renderResults(currentBooks);
}
 
renderResults(currentBooks);
