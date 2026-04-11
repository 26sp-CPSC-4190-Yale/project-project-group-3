/* =============================================
   OpenShelf — home.js
   ============================================= */
 
const MY_LISTINGS = [
  { title:"Organic Chemistry, 9th Ed.",      course:"CHEM 220", price:45, condition:"Good",     cover:"⚗️", bg:"#E1F5EE" },
  { title:"Calculus: Early Transcendentals", course:"MATH 115", price:30, condition:"Like new", cover:"📐", bg:"#FAEEDA" },
  { title:"Introduction to Algorithms",      course:"CPSC 365", price:22, condition:"Highlighted",cover:"💻",bg:"#EEEDFE" },
];
 
const ACTIVITIES = [
  { text:"Someone saved your <strong>Organic Chemistry</strong> listing", time:"2 hours ago",   color:"#7F77DD" },
  { text:"New message from <strong>Marcus T.</strong> about Algorithms",   time:"Yesterday",     color:"#1D9E75" },
  { text:"Price drop alert — <strong>Physics for Scientists</strong> is now $18", time:"2 days ago", color:"#EF9F27" },
  { text:"<strong>Jordan L.</strong> wants to buy your Calculus book",    time:"3 days ago",    color:"#D4537E" },
];
 
function renderListings() {
  const el = document.getElementById('listings-list');
  el.innerHTML = MY_LISTINGS.map(b => `
    <div class="listing-row">
      <div class="listing-cover" style="background:${b.bg}">${b.cover}</div>
      <div class="listing-info">
        <div class="listing-title">${b.title}</div>
        <div class="listing-meta">${b.course} &nbsp;·&nbsp; <span class="pill ${conditionColor(b.condition)}">${b.condition}</span></div>
      </div>
      <div class="listing-price">$${b.price}</div>
    </div>
  `).join('');
}
 
function renderActivity() {
  const el = document.getElementById('activity-list');
  el.innerHTML = ACTIVITIES.map(a => `
    <div class="activity-item">
      <div class="act-dot" style="background:${a.color}"></div>
      <div>
        <div class="act-text">${a.text}</div>
        <div class="act-time">${a.time}</div>
      </div>
    </div>
  `).join('');
}
 
function renderHotDeals() {
  const el = document.getElementById('hot-scroll');
  const hot = BOOKS.filter(b => b.hot || b.price < 20).slice(0, 6);
  el.innerHTML = hot.map(b => `
    <div class="hot-card" onclick="window.location.href='../search/search.html'">
      <div class="hot-cover" style="background:${b.bg}">${b.cover}</div>
      <div class="hot-title">${b.title}</div>
      <div class="hot-price">$${b.price}</div>
      <div class="hot-course">${b.course}</div>
    </div>
  `).join('');
}
 
function showListModal()  { document.getElementById('list-modal').classList.remove('hidden'); }
function hideListModal()  { document.getElementById('list-modal').classList.add('hidden'); }
 
function submitListing(e) {
  e.preventDefault();
  hideListModal();
  showToast('Listing posted successfully!');
}
 
renderListings();
renderActivity();
renderHotDeals();
 
