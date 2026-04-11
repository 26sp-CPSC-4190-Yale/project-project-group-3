/* =============================================
   OpenShelf — messaging.js
   ============================================= */
 
let activeConvoId = null;
 
function renderConvoList(filter) {
  const el = document.getElementById('convo-list');
  let convos = CONVERSATIONS;
  if (filter) {
    const q = filter.toLowerCase();
    convos = convos.filter(c => c.name.toLowerCase().includes(q) || c.preview.toLowerCase().includes(q));
  }
 
  el.innerHTML = convos.map(c => `
    <div class="convo-item" onclick="openConvo(${c.id})">
      <div class="convo-avatar" style="background:${c.bg};color:${c.color}">${c.initials}</div>
      <div class="convo-body">
        <div class="convo-name">${c.name}</div>
        <div class="convo-preview">${c.preview}</div>
      </div>
      <div class="convo-right">
        <div class="convo-time">${c.time}</div>
        ${c.unread > 0 ? `<div class="unread-badge">${c.unread}</div>` : ''}
      </div>
    </div>
  `).join('');
}
 
function openConvo(id) {
  activeConvoId = id;
  const convo = CONVERSATIONS.find(c => c.id === id);
  convo.unread = 0;
 
  document.getElementById('list-view').classList.add('hidden');
  document.getElementById('chat-view').classList.remove('hidden');
 
  document.getElementById('chat-header').innerHTML = `
    <div class="chat-header-avatar" style="background:${convo.bg};color:${convo.color}">${convo.initials}</div>
    <div style="flex:1">
      <div class="chat-header-name">${convo.name}</div>
      <div class="chat-header-school">${convo.school}</div>
    </div>
    <div class="online-indicator"></div>
  `;
 
  renderMessages(convo);
}
 
function renderMessages(convo) {
  const el = document.getElementById('chat-messages');
  el.innerHTML = convo.messages.map(m => `
    <div class="msg-group ${m.side}">
      <div class="msg-bubble ${m.side}">${m.text}</div>
      <div class="msg-time ${m.side}">${m.time}</div>
    </div>
  `).join('');
  el.scrollTop = el.scrollHeight;
}
 
function sendMessage() {
  const input = document.getElementById('chat-input');
  const text  = input.value.trim();
  if (!text || activeConvoId === null) return;
 
  const convo = CONVERSATIONS.find(c => c.id === activeConvoId);
  const now   = new Date();
  const time  = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0');
 
  convo.messages.push({ side: 'me', text, time });
  input.value = '';
  renderMessages(convo);
}
 
function showList() {
  document.getElementById('chat-view').classList.add('hidden');
  document.getElementById('list-view').classList.remove('hidden');
  renderConvoList();
}
 
function filterConvos(q) {
  renderConvoList(q);
}
 
renderConvoList();
