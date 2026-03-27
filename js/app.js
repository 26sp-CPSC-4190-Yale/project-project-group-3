'use strict';

/* 1. CANVAS BACKGROUND */
(function initCanvas() {
  const canvas = document.getElementById('bgCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
  resize();
  window.addEventListener('resize', resize);
  
  const orbs = Array.from({ length: 6 }, () => ({
    x: Math.random() * window.innerWidth, y: Math.random() * window.innerHeight,
    r: 180 + Math.random() * 220, dx: (Math.random() - 0.5) * 0.35, dy: (Math.random() - 0.5) * 0.35,
    hue: Math.random() > 0.6 ? 35 : 20, alpha: 0.04 + Math.random() * 0.06
  }));
  const spines = Array.from({ length: 14 }, () => ({
    x: Math.random() * window.innerWidth, y: Math.random() * window.innerHeight,
    w: 5 + Math.random() * 9, h: 60 + Math.random() * 110,
    speed: 0.15 + Math.random() * 0.25, alpha: 0.03 + Math.random() * 0.06, rot: (Math.random() - 0.5) * 0.3
  }));

  if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function(x,y,w,h,r){
      this.beginPath(); this.moveTo(x+r,y); this.lineTo(x+w-r,y);
      this.quadraticCurveTo(x+w,y,x+w,y+r); this.lineTo(x+w,y+h-r);
      this.quadraticCurveTo(x+w,y+h,x+w-r,y+h); this.lineTo(x+r,y+h);
      this.quadraticCurveTo(x,y+h,x,y+h-r); this.lineTo(x,y+r);
      this.quadraticCurveTo(x,y,x+r,y); this.closePath();
    };
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    orbs.forEach(o => {
      const g = ctx.createRadialGradient(o.x,o.y,0,o.x,o.y,o.r);
      g.addColorStop(0, `hsla(${o.hue},80%,55%,${o.alpha})`);
      g.addColorStop(1, `hsla(${o.hue},80%,55%,0)`);
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(o.x,o.y,o.r,0,Math.PI*2); ctx.fill();
      o.x += o.dx; o.y += o.dy;
      if (o.x < -o.r) o.x = canvas.width+o.r;
      if (o.x > canvas.width+o.r) o.x = -o.r;
      if (o.y < -o.r) o.y = canvas.height+o.r;
      if (o.y > canvas.height+o.r) o.y = -o.r;
    });
    spines.forEach(s => {
      ctx.save(); ctx.translate(s.x, s.y); ctx.rotate(s.rot);
      ctx.fillStyle = `rgba(212,136,42,${s.alpha})`; ctx.roundRect(-s.w/2,-s.h/2,s.w,s.h,3); ctx.fill();
      ctx.restore(); s.y -= s.speed;
      if (s.y + s.h/2 < 0) { s.y = canvas.height + s.h; s.x = Math.random() * canvas.width; }
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

/* 2. TOAST */
const toast = (function() {
  const el = document.getElementById('toast'); let t = null;
  return function(msg, dur=3200) {
    el.textContent = msg; el.classList.add('show');
    clearTimeout(t); t = setTimeout(() => el.classList.remove('show'), dur);
  };
})();

/* 3. TAB SWITCHER */
(function initTabs() {
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.panel');
  const indicator = document.getElementById('tabIndicator');
  function switchTo(target) {
    tabs.forEach(t => { const on = t.dataset.target===target; t.classList.toggle('active',on); t.setAttribute('aria-selected',on); });
    panels.forEach(p => p.classList.toggle('active', p.id===`panel-${target}`));
    indicator.classList.toggle('right', target==='signup');
  }
  tabs.forEach(tab => tab.addEventListener('click', () => switchTo(tab.dataset.target)));
  document.querySelectorAll('[data-switch]').forEach(btn => btn.addEventListener('click', () => switchTo(btn.dataset.switch)));
})();

/* 4. PASSWORD TOGGLE */
document.querySelectorAll('.pw-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = document.getElementById(btn.dataset.target);
    const show = btn.querySelector('.eye-show'), hide = btn.querySelector('.eye-hide');
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';
    show.style.display = isHidden ? 'none' : '';
    hide.style.display = isHidden ? '' : 'none';
    btn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
  });
});

/* 5. VALIDATION HELPERS */
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
function setError(input, errEl, msg) { input.classList.add('is-error'); errEl.textContent = msg; errEl.classList.add('visible'); }
function clearError(input, errEl) { input.classList.remove('is-error'); errEl.classList.remove('visible'); }
function validateEmail(input, errEl) {
  const v = input.value.trim();
  if (!v) { setError(input,errEl,'Email is required.'); return false; }
  if (!EMAIL_RE.test(v)) { setError(input,errEl,'Enter a valid email address.'); return false; }
  clearError(input,errEl); return true;
}
function validatePassword(input, errEl) {
  const v = input.value;
  if (!v) { setError(input,errEl,'Password is required.'); return false; }
  if (v.length < 8) { setError(input,errEl,'Must be at least 8 characters.'); return false; }
  clearError(input,errEl); return true;
}
function validateRequired(input, errEl, label) {
  const v = input.value.trim();
  if (!v) { setError(input,errEl,`${label} is required.`); return false; }
  clearError(input,errEl); return true;
}
function live(input, errEl) { input.addEventListener('input', () => { if (input.classList.contains('is-error')) clearError(input,errEl); }); }

/* 6. PASSWORD STRENGTH */
(function() {
  const pw=document.getElementById('su-pw'), bar=document.getElementById('strengthBar'),
        fill=document.getElementById('strengthFill'), label=document.getElementById('strengthLabel');
  if (!pw) return;
  const levels=[{pct:0,color:'transparent',text:''},{pct:25,color:'#b84040',text:'Weak'},
                {pct:50,color:'#c9a227',text:'Fair'},{pct:75,color:'#4a8c5c',text:'Good'},{pct:100,color:'#2e7d52',text:'Strong'}];
  function score(p) {
    let s=0;
    if(p.length>=8)s++; if(p.length>=12)s++;
    if(/[A-Z]/.test(p)&&/[a-z]/.test(p))s++;
    if(/[0-9]/.test(p))s++; if(/[^A-Za-z0-9]/.test(p))s++;
    return Math.min(s,4);
  }
  pw.addEventListener('input', () => {
    if (!pw.value) { bar.classList.remove('visible'); return; }
    bar.classList.add('visible');
    const lvl = levels[score(pw.value)];
    fill.style.width=lvl.pct+'%'; fill.style.background=lvl.color;
    label.textContent=lvl.text; label.style.color=lvl.color;
  });
})();

/* 7. LOGIN FORM */
(function() {
  const form=document.getElementById('loginForm');
  const emailEl=document.getElementById('login-email'), emailErr=document.getElementById('login-email-err');
  const pwEl=document.getElementById('login-pw'), pwErr=document.getElementById('login-pw-err');
  const btn=document.getElementById('loginBtn');
  if (!form) return;
  live(emailEl,emailErr); live(pwEl,pwErr);
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (!validateEmail(emailEl,emailErr)|!validatePassword(pwEl,pwErr)) return;
    btn.disabled=true; btn.classList.add('loading');
    await new Promise(r=>setTimeout(r,1600));
    btn.disabled=false; btn.classList.remove('loading');
    toast('✓ Signed in — welcome back to OpenShelf!'); form.reset();
  });
})();

/* 8. SIGNUP FORM */
(function() {
  const form=document.getElementById('signupForm');
  const fn=document.getElementById('su-fname'), fnErr=document.getElementById('su-fname-err');
  const ln=document.getElementById('su-lname'), lnErr=document.getElementById('su-lname-err');
  const em=document.getElementById('su-email'), emErr=document.getElementById('su-email-err');
  const pw=document.getElementById('su-pw'),   pwErr=document.getElementById('su-pw-err');
  const cf=document.getElementById('su-confirm'),cfErr=document.getElementById('su-confirm-err');
  const tc=document.getElementById('terms'),   tcErr=document.getElementById('terms-err');
  const btn=document.getElementById('signupBtn');
  if (!form) return;
  live(fn,fnErr); live(ln,lnErr); live(em,emErr); live(pw,pwErr); live(cf,cfErr);
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const ok1=validateRequired(fn,fnErr,'First name');
    const ok2=validateRequired(ln,lnErr,'Last name');
    const ok3=validateEmail(em,emErr);
    const ok4=validatePassword(pw,pwErr);
    let ok5=true;
    if (!cf.value) { setError(cf,cfErr,'Please confirm your password.'); ok5=false; }
    else if (cf.value!==pw.value) { setError(cf,cfErr,'Passwords do not match.'); ok5=false; }
    else clearError(cf,cfErr);
    let ok6=true;
    if (!tc.checked) { tcErr.textContent='You must agree to continue.'; tcErr.classList.add('visible'); ok6=false; }
    else tcErr.classList.remove('visible');
    tc.addEventListener('change',()=>{ if(tc.checked)tcErr.classList.remove('visible'); },{once:true});
    if (!ok1||!ok2||!ok3||!ok4||!ok5||!ok6) return;
    btn.disabled=true; btn.classList.add('loading');
    await new Promise(r=>setTimeout(r,1800));
    btn.disabled=false; btn.classList.remove('loading');
    toast('🎉 Welcome to OpenShelf! Your account is ready.'); form.reset();
    document.getElementById('strengthBar').classList.remove('visible');
  });
})();

/* 9. FORGOT PASSWORD */
document.getElementById('forgotLink')?.addEventListener('click', e => {
  e.preventDefault(); toast('📧 Password reset link sent to your email.');
});
