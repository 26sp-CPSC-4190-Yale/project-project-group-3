/* =============================================
   OpenShelf — data.js
   Shared data used across all pages
   ============================================= */
 
const BOOKS = [
  { id:1,  title:"Introduction to Algorithms",          author:"Cormen et al.",      course:"CPSC 365", price:22, origPrice:85, condition:"Highlighted", seller:"Ayushi D.",  cover:"💻", bg:"#EEEDFE", isNew:false, hot:true  },
  { id:2,  title:"Organic Chemistry, 9th Ed.",           author:"McMurry",            course:"CHEM 220", price:45, origPrice:120,condition:"Good",        seller:"Taylor R.",  cover:"⚗️", bg:"#E1F5EE", isNew:true,  hot:false },
  { id:3,  title:"Calculus: Early Transcendentals",      author:"Stewart",            course:"MATH 115", price:30, origPrice:95, condition:"Like new",    seller:"Ayushi D.",  cover:"📐", bg:"#FAEEDA", isNew:false, hot:false },
  { id:4,  title:"Molecular Biology of the Cell",        author:"Alberts et al.",     course:"MB&B 300", price:38, origPrice:75, condition:"Good",        seller:"Priya S.",   cover:"🧬", bg:"#FBEAF0", isNew:false, hot:false },
  { id:5,  title:"Physics for Scientists, Vol. 1",       author:"Serway",             course:"PHYS 180", price:18, origPrice:65, condition:"Worn",        seller:"Jordan L.",  cover:"🔭", bg:"#E6F1FB", isNew:true,  hot:true  },
  { id:6,  title:"Principles of Economics",              author:"Mankiw",             course:"ECON 115", price:15, origPrice:60, condition:"Like new",    seller:"Marcus T.",  cover:"🌍", bg:"#EAF3DE", isNew:false, hot:false },
  { id:7,  title:"The Elements of Style",                author:"Strunk & White",     course:"ENGL 114", price:8,  origPrice:18, condition:"Good",        seller:"Sam K.",     cover:"📜", bg:"#FAECE7", isNew:false, hot:true  },
  { id:8,  title:"Computer Networks: Top-Down Approach", author:"Kurose & Ross",      course:"CPSC 434", price:28, origPrice:80, condition:"Like new",    seller:"Alex P.",    cover:"🖥️", bg:"#EEEDFE", isNew:true,  hot:false },
  { id:9,  title:"Linear Algebra Done Right",            author:"Axler",              course:"MATH 225", price:18, origPrice:55, condition:"Like new",    seller:"Dana M.",    cover:"📊", bg:"#E1F5EE", isNew:false, hot:false },
  { id:10, title:"The Great Gatsby",                     author:"F. Scott Fitzgerald", course:"ENGL 120",price:6,  origPrice:15, condition:"Good",        seller:"Riley B.",   cover:"📖", bg:"#FBEAF0", isNew:false, hot:false },
  { id:11, title:"Microeconomics",                       author:"Pindyck & Rubinfeld",course:"ECON 121", price:20, origPrice:70, condition:"Highlighted", seller:"Chris W.",   cover:"📈", bg:"#FAEEDA", isNew:true,  hot:false },
  { id:12, title:"Genetics: From Genes to Genomes",      author:"Hartwell et al.",    course:"MB&B 250", price:35, origPrice:90, condition:"Like new",    seller:"Neha R.",    cover:"🔬", bg:"#EAF3DE", isNew:false, hot:true  },
];
 
const CONVERSATIONS = [
  {
    id:1, name:"Marcus T.", initials:"MT", color:"#7F77DD", bg:"#EEEDFE",
    school:"Yale University", unread:2, time:"2m ago",
    preview:"Is the Algorithms book still available?",
    messages:[
      {side:"them", text:"Hey! Is the Introduction to Algorithms book still available?",   time:"10:32 AM"},
      {side:"me",   text:"Yes it is! It has some highlighting but nothing too heavy.",     time:"10:35 AM"},
      {side:"them", text:"Perfect — would you take $20 for it?",                          time:"10:36 AM"},
      {side:"them", text:"I need it by Thursday if possible",                             time:"10:36 AM"},
    ]
  },
  {
    id:2, name:"Priya S.", initials:"PS", color:"#1D9E75", bg:"#E1F5EE",
    school:"Yale University", unread:0, time:"1h ago",
    preview:"Can you do $25 for the calc book?",
    messages:[
      {side:"them", text:"Hi! I saw your Calculus listing. Can you do $25?",              time:"9:14 AM"},
      {side:"me",   text:"I could do $27 — it's basically brand new.",                    time:"9:20 AM"},
      {side:"them", text:"Deal! Can we meet at Bass tomorrow?",                           time:"9:22 AM"},
    ]
  },
  {
    id:3, name:"Jordan L.", initials:"JL", color:"#D85A30", bg:"#FAECE7",
    school:"Southern CT State", unread:0, time:"Yesterday",
    preview:"You: Sounds good, see you Friday!",
    messages:[
      {side:"them", text:"Do you have the Physics book for PHYS 180?",                    time:"Tue 3:10 PM"},
      {side:"me",   text:"Just listed it — it's $18. Interested?",                       time:"Tue 3:15 PM"},
      {side:"them", text:"Yes! Let's meet Friday afternoon",                              time:"Tue 3:17 PM"},
      {side:"me",   text:"Sounds good, see you Friday!",                                  time:"Tue 3:18 PM"},
    ]
  },
  {
    id:4, name:"Sam K.", initials:"SK", color:"#BA7517", bg:"#FAEEDA",
    school:"Yale University", unread:0, time:"2 days ago",
    preview:"Does it have the access code?",
    messages:[
      {side:"them", text:"Does the Organic Chem book have the access code?",              time:"Mon 11:00 AM"},
      {side:"me",   text:"Unfortunately no, the code was already used.",                  time:"Mon 11:05 AM"},
      {side:"them", text:"Ah ok, thanks for letting me know!",                            time:"Mon 11:06 AM"},
    ]
  },
];
 
const SAVED_IDS = [1, 3, 4, 5, 7, 8, 9];
 
function showToast(msg) {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    t.className = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}
 
function getInitials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0,2).toUpperCase();
}
 
function conditionColor(c) {
  if (c === 'Like new') return 'pill-teal';
  if (c === 'Good')     return 'pill-green';
  if (c === 'Highlighted') return 'pill-amber';
  return 'pill-coral';
}
