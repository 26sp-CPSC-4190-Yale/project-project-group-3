'use strict';

(function initCanvas() {
  const canvas = document.getElementById('bgCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const sparks = Array.from({ length: 28 }, () => ({
    x: Math.random(),
    y: Math.random(),
    r: Math.random() * 2.4 + 0.8,
    dx: (Math.random() - 0.5) * 0.0007,
    dy: (Math.random() - 0.5) * 0.0005
  }));

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const gradient = ctx.createRadialGradient(
      canvas.width * 0.78,
      canvas.height * 0.18,
      0,
      canvas.width * 0.78,
      canvas.height * 0.18,
      canvas.width * 0.72
    );
    gradient.addColorStop(0, 'rgba(212, 136, 42, 0.18)');
    gradient.addColorStop(1, 'rgba(15, 13, 11, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    sparks.forEach((spark) => {
      spark.x += spark.dx;
      spark.y += spark.dy;

      if (spark.x < 0 || spark.x > 1) spark.dx *= -1;
      if (spark.y < 0 || spark.y > 1) spark.dy *= -1;

      ctx.beginPath();
      ctx.fillStyle = 'rgba(241, 209, 160, 0.22)';
      ctx.arc(spark.x * canvas.width, spark.y * canvas.height, spark.r, 0, Math.PI * 2);
      ctx.fill();
    });

    requestAnimationFrame(draw);
  }

  resize();
  window.addEventListener('resize', resize);
  requestAnimationFrame(draw);
})();

(function initTabs() {
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.panel');
  const indicator = document.getElementById('tabIndicator');
  if (!tabs.length || !indicator) return;

  function activateTab(target) {
    tabs.forEach((tab, index) => {
      const active = tab.dataset.target === target;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', String(active));
      if (active) {
        indicator.style.transform = `translateX(${index * 100}%)`;
      }
    });

    panels.forEach((panel) => {
      panel.classList.toggle('active', panel.id === `panel-${target}`);
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => activateTab(tab.dataset.target));
  });
})();

(function initPasswordToggles() {
  const toggles = document.querySelectorAll('.pw-toggle');
  toggles.forEach((toggle) => {
    toggle.addEventListener('click', () => {
      const input = document.getElementById(toggle.dataset.target);
      if (!input) return;

      const showing = input.type === 'text';
      input.type = showing ? 'password' : 'text';
      toggle.textContent = showing ? 'Show' : 'Hide';
    });
  });
})();

(function initForms() {
  const toast = document.getElementById('toast');
  const logoutButton = document.getElementById('logoutButton');

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('visible');
    window.clearTimeout(showToast.timeoutId);
    showToast.timeoutId = window.setTimeout(() => {
      toast.classList.remove('visible');
    }, 2600);
  }

  function setError(id, message) {
    const el = document.getElementById(id);
    if (el) el.textContent = message || '';
  }

  async function sendJson(url, payload) {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Request failed.');
    }
    return data;
  }

  document.querySelectorAll('[data-toast]').forEach((button) => {
    button.addEventListener('click', () => showToast(button.dataset.toast));
  });

  if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
      try {
        const response = await fetch('/logout', { method: 'POST' });
        const data = await response.json();
        window.location.href = data.redirect_url || '/';
      } catch (error) {
        showToast('Could not log out right now.');
      }
    });
  }

  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const email = document.getElementById('login-email')?.value.trim() || '';
      const password = document.getElementById('login-pw')?.value.trim() || '';
      setError('login-email-err', email ? '' : 'Enter your email.');
      setError('login-pw-err', password ? '' : 'Enter your password.');
      if (!email || !password) return;

      try {
        const data = await sendJson('/api/login', { email, password });
        showToast(data.message || 'Signed in.');
        window.setTimeout(() => {
          window.location.href = data.redirect_url || '/search';
        }, 300);
      } catch (error) {
        setError('login-pw-err', error.message);
      }
    });
  }

  const signupForm = document.getElementById('signupForm');
  if (signupForm) {
    signupForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const required = [
        ['su-fname', 'su-fname-err', 'Enter your first name.'],
        ['su-lname', 'su-lname-err', 'Enter your last name.'],
        ['su-email', 'su-email-err', 'Enter your email.'],
        ['su-pw', 'su-pw-err', 'Enter a password.'],
        ['su-confirm', 'su-confirm-err', 'Confirm your password.']
      ];

      let invalid = false;
      required.forEach(([inputId, errorId, message]) => {
        const value = document.getElementById(inputId)?.value.trim() || '';
        setError(errorId, value ? '' : message);
        invalid = invalid || !value;
      });

      const pw = document.getElementById('su-pw')?.value || '';
      const confirm = document.getElementById('su-confirm')?.value || '';
      const terms = document.getElementById('terms');
      setError('su-confirm-err', pw && confirm && pw !== confirm ? 'Passwords do not match.' : '');
      setError('terms-err', terms?.checked ? '' : 'Accept the prototype terms to continue.');
      if (invalid || pw !== confirm || !terms?.checked) return;

      try {
        const data = await sendJson('/api/signup', {
          first_name: document.getElementById('su-fname')?.value.trim(),
          last_name: document.getElementById('su-lname')?.value.trim(),
          email: document.getElementById('su-email')?.value.trim(),
          password: pw
        });
        showToast(data.message || 'Account created.');
        window.setTimeout(() => {
          window.location.href = data.redirect_url || '/search';
        }, 300);
      } catch (error) {
        setError('su-email-err', error.message);
      }
    });
  }
})();
