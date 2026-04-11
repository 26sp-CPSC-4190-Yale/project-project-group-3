/* =============================================
   OpenShelf — saved.js
   ============================================= */
 
let savedIds = new Set(SAVED_IDS);
let currentFilter = 'all';
const YALE_COURSES = ['CPSC', 'MATH', 'CHEM', 'ENGL', 'PHYS', 'ECON', 'MB&B'];
 
function getSavedBooks() {
  let books = BOOKS.filter(b => savedIds.has(b.id));
  if (currentFilter === 'cheap')   books = books.filter(b => b.price < 20);
  if (currentFilter === 'likenew') books = books.filter(b => b.condition === 'Like new');
  if (currentFilter === 'yale')    books = books.filter(b => YALE_COURSES.some(c => b.course.startsWith(c)));
  return books;
}
 
function renderSaved() {
  const books = getSavedBooks();
  const grid  = document.getElementById('saved-grid');
  const count = document.getElementById('saved-count');
 
  count.textContent = savedIds.size + ' book' + (savedIds.size !== 1 ? 's' : '') + ' saved';
 
  if (books.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:span 2">
        <div class="empty-state-icon">💔</div>
        <div class="empty-state-title">Nothing here yet</div>
        <div class="empty-state-text">Save books from the search page to see them here.</div>
      </div>`;
    return;
  }
 
  grid.innerHTML = books.map(b => `
    <div class="saved-card">
      <div class="saved-cover" style="background:${b.bg}">${b.cover}</div>
      <div class="saved-body">
        <div class="saved-book-title">${b.title}</div>
        <div class="saved-course">${b.course}</div>
        <div class="saved-price-row">
          <div>
            <div class="price-main">$${b.price}</div>
            <div class="price-orig">$${b.origPrice}</div>
          </div>
          <button class="saved-remove-btn" onclick="removeBook(event,${b.id})">♥</button>
        </div>
      </div>
    </div>
  `).join('');
}
 
function removeBook(e, id) {
  e.stopPropagation();
  savedIds.delete(id);
  renderSaved();
  showToast('Removed from saved');
}
 
function filterSaved(el, type) {
  document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active-chip'));
  el.classList.add('active-chip');
  currentFilter = type;
  renderSaved();
}
 
renderSaved();
