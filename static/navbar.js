(function () {
  if (window.location.pathname.endsWith('login.html')) return;

  const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://finndev.me';

  const THRESHOLDS  = [0, 500, 2000, 5000, 10000, 20000, 50000, 100000, 250000, 500000, 1000000];
  const LEVEL_TABLE = [
    { level: 1,  gold: 500,     bonus: 250,    feature: 'Dice & Blackjack' },
    { level: 2,  gold: 2000,    bonus: 1000,   feature: 'Slots + Leaderboard' },
    { level: 3,  gold: 5000,    bonus: 2500,   feature: 'Autospin + höherer Daily' },
    { level: 4,  gold: 10000,   bonus: 5000,   feature: 'Chicken Road' },
    { level: 5,  gold: 20000,   bonus: 10000,  feature: 'Input Bet' },
    { level: 6,  gold: 50000,   bonus: 25000,  feature: '—' },
    { level: 7,  gold: 100000,  bonus: 50000,  feature: '—' },
    { level: 8,  gold: 250000,  bonus: 125000, feature: 'Roulette' },
    { level: 9,  gold: 500000,  bonus: 250000, feature: 'Poker' },
    { level: 10, gold: 1000000, bonus: 500000, feature: '🏆 Gold Winner Badge' },
  ];

  // ── CSS ──
  const style = document.createElement('style');
  style.textContent = `
    #buzz-navbar {
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 9000;
      height: 60px;
      background: #17171c;
      border-bottom: 1px solid #2a2a32;
      display: flex;
      align-items: center;
      padding: 0 1.25rem;
      gap: 1rem;
      box-shadow: 0 2px 12px rgba(0,0,0,0.5);
    }

    .nv-logo {
      font-size: 1.2rem;
      font-weight: 700;
      color: #c9952a;
      text-decoration: none;
      letter-spacing: 0.04em;
      white-space: nowrap;
      flex-shrink: 0;
    }
    .nv-logo span { color: #e8e8ee; }

    .nv-level-wrap {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      min-width: 0;
    }
    .nv-level-inner {
      display: flex;
      align-items: center;
      gap: 0.55rem;
      padding: 0.28rem 0.85rem;
      border-radius: 999px;
      border: 1px solid #2a2a32;
      background: #111118;
      transition: border-color 0.2s, background 0.2s;
      max-width: 320px;
      width: 100%;
    }
    .nv-level-wrap:hover .nv-level-inner {
      border-color: #c9952a;
      background: #1a1a22;
    }
    .nv-level-num {
      font-size: 0.75rem;
      font-weight: 700;
      color: #c9952a;
      white-space: nowrap;
      flex-shrink: 0;
    }
    .nv-progress-track {
      flex: 1;
      height: 6px;
      background: #2a2a32;
      border-radius: 999px;
      overflow: hidden;
      min-width: 50px;
    }
    .nv-progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #c9952a, #e8b84b);
      border-radius: 999px;
      transition: width 0.5s ease;
    }
    .nv-progress-xp {
      font-size: 0.68rem;
      color: #7a7a8c;
      white-space: nowrap;
      flex-shrink: 0;
    }

    .nv-right {
      display: flex;
      align-items: center;
      gap: 0.45rem;
      flex-shrink: 0;
    }
    .nv-nav { display: flex; gap: 0; }
    .nv-nav a {
      color: #7a7a8c;
      text-decoration: none;
      font-size: 0.82rem;
      padding: 0.3rem 0.6rem;
      border-radius: 8px;
      transition: color 0.15s, background 0.15s;
      white-space: nowrap;
    }
    .nv-nav a:hover { color: #e8e8ee; background: #2a2a32; }

    .nv-wallet {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      background: #2a2a32;
      border: 1px solid #3a3a46;
      padding: 0.28rem 0.75rem;
      border-radius: 999px;
      font-size: 0.8rem;
      white-space: nowrap;
    }
    .nv-wallet-amount { color: #e8b84b; font-weight: 700; }

    .nv-logout {
      font-size: 0.8rem;
      color: #c9952a;
      cursor: pointer;
      background: #17171c;
      border: 1px solid #a57820;
      padding: 0.28rem 0.75rem;
      border-radius: 999px;
      font-weight: 600;
      white-space: nowrap;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
    }
    .nv-logout:hover { background: #c9952a; color: #0d0d0f; border-color: #c9952a; }

    /* ── Level Modal ── */
    #nv-modal-overlay {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 9999;
      background: rgba(0,0,0,0.75);
      align-items: center;
      justify-content: center;
    }
    #nv-modal-overlay.open { display: flex; }

    #nv-modal {
      background: #17171c;
      border: 1px solid #2a2a32;
      border-radius: 16px;
      padding: 1.75rem 1.5rem 1.5rem;
      width: 100%;
      max-width: 640px;
      max-height: 88vh;
      overflow-y: auto;
      box-shadow: 0 24px 64px rgba(0,0,0,0.9), 0 0 0 1px rgba(201,149,42,0.07);
      position: relative;
      margin: 1rem;
    }
    #nv-modal h2 {
      font-size: 1.15rem;
      font-weight: 700;
      color: #e8b84b;
      margin-bottom: 0.25rem;
      font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .nv-modal-sub {
      font-size: 0.8rem;
      color: #7a7a8c;
      margin-bottom: 1.25rem;
      font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .nv-modal-close {
      position: absolute;
      top: 1rem; right: 1rem;
      background: none;
      border: none;
      color: #7a7a8c;
      font-size: 1.2rem;
      cursor: pointer;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      line-height: 1;
      transition: color 0.15s, background 0.15s;
    }
    .nv-modal-close:hover { color: #e8e8ee; background: #2a2a32; }

    #nv-level-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.84rem;
      font-family: 'Segoe UI', system-ui, sans-serif;
    }
    #nv-level-table th {
      text-align: left;
      font-size: 0.7rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #7a7a8c;
      padding: 0.35rem 0.6rem;
      border-bottom: 1px solid #2a2a32;
    }
    #nv-level-table td {
      padding: 0.5rem 0.6rem;
      border-bottom: 1px solid #1e1e25;
      color: #e8e8ee;
      vertical-align: middle;
    }
    #nv-level-table tr.nv-row-current td {
      background: rgba(201,149,42,0.09);
    }
    #nv-level-table tr.nv-row-current td:first-child {
      border-left: 3px solid #c9952a;
      padding-left: calc(0.6rem - 3px);
    }
    #nv-level-table tr.nv-row-locked td { color: #3e3e4e; }
    #nv-level-table tr:last-child td { border-bottom: none; }

    /* ── Hamburger & Mobile Menu ── */
    .nv-hamburger {
      display: none;
      background: none;
      border: none;
      color: #7a7a8c;
      cursor: pointer;
      padding: 0.3rem 0.4rem;
      border-radius: 6px;
      line-height: 1;
      transition: color 0.15s, background 0.15s;
      flex-shrink: 0;
      align-items: center;
      justify-content: center;
    }
    .nv-hamburger:hover { color: #e8e8ee; background: #2a2a32; }

    #nv-mobile-menu {
      display: none;
      position: fixed;
      top: 60px; left: 0; right: 0;
      background: #1a1a22;
      border-bottom: 1px solid #2a2a32;
      z-index: 8998;
      padding: 0.4rem 0.75rem 0.65rem;
      flex-direction: column;
      box-shadow: 0 8px 24px rgba(0,0,0,0.55);
    }
    #nv-mobile-menu.open { display: flex; }
    #nv-mobile-menu a {
      color: #7a7a8c;
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      padding: 0.65rem 0.75rem;
      border-radius: 8px;
      transition: color 0.15s, background 0.15s;
      display: block;
    }
    #nv-mobile-menu a:hover { color: #e8e8ee; background: #2a2a32; }

    @media (max-width: 768px) {
      html, body { overflow-x: hidden; }
      #buzz-navbar { padding: 0 0.6rem; gap: 0.35rem; }
      .nv-logo { font-size: 0.95rem; }
      .nv-level-inner { padding: 0.2rem 0.5rem; gap: 0.3rem; max-width: none; }
      .nv-progress-xp { display: none; }
      .nv-nav { display: none; }
      .nv-hamburger { display: flex; }
      .nv-wallet { padding: 0.22rem 0.5rem; font-size: 0.73rem; gap: 0.25rem; }
      .nv-logout { padding: 0.22rem 0.5rem; font-size: 0.73rem; }
    }
    @media (max-width: 400px) {
      .nv-level-num { font-size: 0.68rem; }
      .nv-wallet-amount { font-size: 0.73rem; }
    }
  `;
  document.head.appendChild(style);

  // ── Navbar HTML ──
  const header = document.createElement('header');
  header.id = 'buzz-navbar';
  header.innerHTML = `
    <a class="nv-logo" href="/static/index.html">🃏 Buzz<span>Casino</span></a>
    <div class="nv-level-wrap" id="nv-level-btn" title="Level-Übersicht öffnen">
      <div class="nv-level-inner">
        <span class="nv-level-num" id="nv-level-num">Lv. 0</span>
        <div class="nv-progress-track">
          <div class="nv-progress-fill" id="nv-progress-fill" style="width:0%"></div>
        </div>
        <span class="nv-progress-xp" id="nv-progress-xp">— / —</span>
      </div>
    </div>
    <div class="nv-right">
      <nav class="nv-nav">
        <a href="/static/index.html#games">Games</a>
        <a href="/static/leaderboard.html">Leaderboard</a>
        <a href="/static/shop.html">Shop</a>
        <a href="/static/settings.html">Settings</a>
      </nav>
      <div class="nv-wallet">
        <span>💰</span>
        <span class="nv-wallet-amount" id="nv-balance">—</span>
      </div>
      <button class="nv-logout" id="nv-logout">Logout</button>
      <button class="nv-hamburger" id="nv-hamburger" aria-label="Menü öffnen">☰</button>
    </div>
  `;
  document.body.prepend(header);
  document.body.style.paddingTop = '60px';

  // ── Mobile Menu ──
  const mobileMenu = document.createElement('div');
  mobileMenu.id = 'nv-mobile-menu';
  mobileMenu.innerHTML = `
    <a href="/static/index.html#games">Games</a>
    <a href="/static/leaderboard.html">Leaderboard</a>
    <a href="/static/shop.html">Shop</a>
    <a href="/static/settings.html">Settings</a>
  `;
  document.body.insertBefore(mobileMenu, document.body.children[1] || null);

  // ── Modal HTML ──
  const overlay = document.createElement('div');
  overlay.id = 'nv-modal-overlay';
  overlay.innerHTML = `
    <div id="nv-modal">
      <button class="nv-modal-close" id="nv-modal-close">✕</button>
      <h2>⭐ Level-Übersicht</h2>
      <p class="nv-modal-sub" id="nv-modal-sub">Dein aktuelles Level: 0</p>
      <table id="nv-level-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Level</th>
            <th>Gold benötigt</th>
            <th>Bonus Coins</th>
            <th>Feature / Unlock</th>
          </tr>
        </thead>
        <tbody id="nv-level-tbody"></tbody>
      </table>
    </div>
  `;
  document.body.appendChild(overlay);

  // ── Helpers ──
  function fmt(n) { return Number(n).toLocaleString('de-DE'); }

  function updateDisplay(balance, level, totalGold) {
    document.getElementById('nv-balance').textContent = fmt(balance);
    document.getElementById('nv-level-num').textContent = 'Lv. ' + level;
    document.getElementById('nv-modal-sub').textContent =
      'Dein aktuelles Level: ' + level + '  |  Gesamt verdient: ' + fmt(totalGold) + ' Gold';

    if (level >= 10) {
      document.getElementById('nv-progress-fill').style.width = '100%';
      document.getElementById('nv-progress-xp').textContent = 'MAX';
    } else {
      const cur    = THRESHOLDS[level] || 0;
      const nxt    = THRESHOLDS[level + 1] || 1;
      const earned = Math.max(0, totalGold - cur);
      const needed = nxt - cur;
      const pct    = Math.min(100, (earned / needed) * 100);
      document.getElementById('nv-progress-fill').style.width = pct + '%';
      document.getElementById('nv-progress-xp').textContent   = fmt(earned) + ' / ' + fmt(needed);
    }

    const tbody = document.getElementById('nv-level-tbody');
    tbody.innerHTML = LEVEL_TABLE.map(row => {
      const reached   = level >= row.level;
      const isCurrent = level === row.level;
      const status    = reached ? '✅' : '🔒';
      const cls = isCurrent ? 'nv-row-current' : (reached ? '' : 'nv-row-locked');
      return `<tr class="${cls}">
        <td>${status}</td>
        <td><strong>${row.level}</strong></td>
        <td>${fmt(row.gold)}</td>
        <td>${fmt(row.bonus)}</td>
        <td>${row.feature}</td>
      </tr>`;
    }).join('');
  }

  // ── Initial display from localStorage ──
  const storedLevel = parseInt(localStorage.getItem('level') || '0', 10);
  const storedGold  = parseInt(localStorage.getItem('total_gold_earned') || '0', 10);
  updateDisplay(0, storedLevel, storedGold);

  // ── Fetch fresh data ──
  const username = localStorage.getItem('username');
  if (username) {
    fetch(`${API_URL}/get_balance?username=${encodeURIComponent(username)}`)
      .then(r => r.json())
      .then(data => {
        if (data.id_banned) {
          localStorage.clear();
          window.location.href = '/static/login.html';
          return;
        }
        const lvl  = data.level  ?? storedLevel;
        const gold = data.total_gold_earned ?? storedGold;
        localStorage.setItem('level', lvl);
        localStorage.setItem('total_gold_earned', gold);
        updateDisplay(data.balance ?? 0, lvl, gold);
      })
      .catch(() => {});
  }

  // ── Modal open/close ──
  document.getElementById('nv-level-btn').addEventListener('click', () => {
    overlay.classList.add('open');
  });
  document.getElementById('nv-modal-close').addEventListener('click', () => {
    overlay.classList.remove('open');
  });
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.classList.remove('open');
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') overlay.classList.remove('open');
  });

  // ── Hamburger ──
  document.getElementById('nv-hamburger').addEventListener('click', e => {
    e.stopPropagation();
    mobileMenu.classList.toggle('open');
  });
  document.addEventListener('click', e => {
    if (!e.target.closest('#buzz-navbar') && !e.target.closest('#nv-mobile-menu')) {
      mobileMenu.classList.remove('open');
    }
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') mobileMenu.classList.remove('open');
  });

  // ── Logout ──
  document.getElementById('nv-logout').addEventListener('click', () => {
    localStorage.removeItem('username');
    window.location.href = '/static/login.html';
  });
  window.updateDisplay = updateDisplay;
})();
