// Murmel Chat Widget
// Vanilla JS, keine Abhängigkeiten

(function() {
  // Allgemeine Sprüche (auf allen Seiten)
  const QUOTES_GENERAL = [
    "Verdopple niemals deinen Einsatz... es sei denn, du tust es.",
    "Das Haus gewinnt immer. Ich bin das Haus 🏠",
    "Hast du schon mal Münzen in einen Brunnen geworfen? Hier ist es dasselbe, nur teurer.",
    "Glück ist, wenn du aufhörst, bevor das Pech kommt.",
    "Ich hab schon Leute kommen und gehen sehen. Meistens gehen sie.",
    "Ein kluger Spieler weiß, wann er aufhören muss. Ein cleverer Spieler weiß, wann er anfängt.",
    "Chips sind nur Plastik... bis sie es nicht mehr sind.",
    "Heute dein Glückstag? Murmel sagt: vielleicht 🎲",
    "Ich sage nichts. Ich bin nur ein Biber.",
    "Cash out early, cash out often. Das ist mein Motto.",
    "Streng dich an! 😤",
    "Das Casino schläft nie! 🃏",
    "Murmel beobachtet dich... 👀",
    "Heute ist dein Glückstag!",
    "Verdopple oder nichts! 🎰"
  ];

  // Nur auf dem Hauptmenü (index.html)
  const QUOTES_INDEX = [
    "Was spielen wir heute? 🎮",
    "Ich tippe auf Blackjack heute!",
    "Das Chicken wartet auf dich! 🐔"
  ];

  const isIndexPage = /\/(index\.html)?$/.test(window.location.pathname)
    && !window.location.pathname.includes('admin');

  let lastQuote = null;

  const API_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "https://finndev.me";

  let isOpen = false;
  let quoteTimeout = null;
  let bubbleTimeout = null;
  let stateTimer = null;
  let returnTimer = null;

  // State classes on SVG root: si=idle, sw=wink, sg=grimace, sl=laugh, ss=surprised
  const ALL_STATES    = ['si','sw','sg','sl','ss'];
  const SPECIAL_STATES = ['sw','sg','sl','ss'];

  // ─────────────────────────────────────────────
  //  Inline SVG (alle Klassen mit m- Prefix um
  //  Konflikte mit der Seite zu vermeiden)
  // ─────────────────────────────────────────────
  const MURMEL_SVG = `<svg class="si" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150" width="56" height="56" style="pointer-events:none;display:block">
  <defs>
    <radialGradient id="m-gFur" cx="40%" cy="28%" r="68%">
      <stop offset="0%"   stop-color="#C08848"/>
      <stop offset="55%"  stop-color="#9B6C32"/>
      <stop offset="100%" stop-color="#6B4018"/>
    </radialGradient>
    <radialGradient id="m-gMuz" cx="48%" cy="38%" r="62%">
      <stop offset="0%"   stop-color="#E0B878"/>
      <stop offset="100%" stop-color="#B88840"/>
    </radialGradient>
    <radialGradient id="m-gEye" cx="38%" cy="32%" r="68%">
      <stop offset="0%"   stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#E8E8EC"/>
    </radialGradient>
    <radialGradient id="m-gJkt" cx="38%" cy="30%" r="70%">
      <stop offset="0%"   stop-color="#2A2840"/>
      <stop offset="100%" stop-color="#111020"/>
    </radialGradient>
    <style>
      /* Wipp-Animation läuft immer */
      .m-c { animation: m-bob 2.7s ease-in-out infinite; }
      @keyframes m-bob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }

      /* Alle Gesichter standardmäßig unsichtbar */
      .m-fi,.m-fw,.m-fg,.m-fl,.m-fs { opacity:0; }

      /* Zustand via Klasse auf SVG-Root */
      .si .m-fi { opacity:1; }
      .sw .m-fw { opacity:1; }
      .sg .m-fg { opacity:1; }
      .sl .m-fl { opacity:1; }
      .ss .m-fs { opacity:1; }

      /* Zwinkern: Wimpern pulsieren */
      .sw .m-wl { animation: m-lash 1.3s ease-in-out infinite; }
      @keyframes m-lash { 0%,100%{opacity:1} 50%{opacity:0.3} }

      /* Überrascht: kurzer Pop-Bounce */
      .ss .m-fs {
        transform-box:fill-box; transform-origin:50% 100%;
        animation: m-pop 0.45s ease-out;
      }
      @keyframes m-pop {
        0%{transform:scale(0.88)} 55%{transform:scale(1.08)}
        80%{transform:scale(0.96)} 100%{transform:scale(1)}
      }

      /* Lachen: Kopf-Wackeln */
      .sl .m-fl {
        transform-box:fill-box; transform-origin:50% 100%;
        animation: m-shk 0.17s linear infinite;
      }
      @keyframes m-shk {
        0%,100%{transform:rotate(0deg)}
        25%{transform:rotate(-1.8deg)}
        75%{transform:rotate(1.8deg)}
      }
    </style>
  </defs>

  <g class="m-c">
    <!-- Ohren -->
    <ellipse cx="44"  cy="34" rx="16" ry="17" fill="url(#m-gFur)"/>
    <ellipse cx="106" cy="34" rx="16" ry="17" fill="url(#m-gFur)"/>
    <ellipse cx="44"  cy="35" rx="9"  ry="10" fill="url(#m-gMuz)" opacity="0.75"/>
    <ellipse cx="106" cy="35" rx="9"  ry="10" fill="url(#m-gMuz)" opacity="0.75"/>
    <!-- Smoking-Körper -->
    <ellipse cx="75" cy="127" rx="33" ry="21" fill="url(#m-gJkt)"/>
    <ellipse cx="65" cy="116" rx="10" ry="7"   fill="#30304A" opacity="0.7"/>
    <ellipse cx="87" cy="120" rx="7"  ry="4.5" fill="#30304A" opacity="0.45"/>
    <!-- Weißes Hemd -->
    <path d="M71.5,112 Q75,107 78.5,112 L80.5,128 Q75,131 69.5,128Z" fill="#EEEAE2"/>
    <circle cx="75" cy="117.5" r="1.6" fill="#C4C0BC"/>
    <circle cx="75" cy="123"   r="1.6" fill="#C4C0BC"/>
    <!-- Fliege -->
    <path d="M75,110 L65,104 L65,116Z" fill="#8A0022"/>
    <path d="M75,110 L85,104 L85,116Z" fill="#8A0022"/>
    <ellipse cx="75" cy="110" rx="4.5" ry="5.5" fill="#640018"/>
    <ellipse cx="72" cy="107" rx="3"   ry="2"   fill="#AA2038" opacity="0.55"/>
    <!-- Pfoten -->
    <ellipse cx="43"  cy="122" rx="12" ry="8" fill="url(#m-gFur)"/>
    <ellipse cx="107" cy="122" rx="12" ry="8" fill="url(#m-gFur)"/>
    <path d="M35,126 Q36,131 37.5,129"  stroke="#5A3018" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <path d="M43,129 L43,133"           stroke="#5A3018" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <path d="M51,126 Q50,131 48.5,129"  stroke="#5A3018" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <path d="M99,126 Q100,131 101.5,129" stroke="#5A3018" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <path d="M107,129 L107,133"          stroke="#5A3018" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <path d="M115,126 Q114,131 112.5,129" stroke="#5A3018" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <!-- Kopf -->
    <circle cx="75" cy="65" r="44" fill="url(#m-gFur)"/>
    <!-- Maul-Bereich -->
    <ellipse cx="75" cy="78" rx="27" ry="20" fill="url(#m-gMuz)"/>
    <!-- Wangen-Rouge -->
    <circle cx="48"  cy="82" r="11" fill="#E07070" opacity="0.22"/>
    <circle cx="102" cy="82" r="11" fill="#E07070" opacity="0.22"/>
    <!-- Nase -->
    <ellipse cx="75"   cy="77.5" rx="7"   ry="5" fill="#3A1806"/>
    <ellipse cx="72.5" cy="75.8" rx="3.2" ry="2" fill="#6A3818" opacity="0.6"/>

    <!-- ── IDLE ── -->
    <g class="m-fi">
      <circle cx="60" cy="61" r="11" fill="url(#m-gEye)"/>
      <circle cx="90" cy="61" r="11" fill="url(#m-gEye)"/>
      <circle cx="61.5" cy="62.5" r="6.5" fill="#180800"/>
      <circle cx="91.5" cy="62.5" r="6.5" fill="#180800"/>
      <circle cx="64"   cy="59.5" r="2.5" fill="white"/>
      <circle cx="94"   cy="59.5" r="2.5" fill="white"/>
      <circle cx="59.5" cy="65"   r="1.4" fill="white" opacity="0.6"/>
      <circle cx="89.5" cy="65"   r="1.4" fill="white" opacity="0.6"/>
      <path d="M50,52 Q60,46 70,51"  stroke="#4A2810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M80,51 Q90,46 100,52" stroke="#4A2810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M63,87 Q75,97 87,87"  stroke="#3A1806" stroke-width="2.8" fill="none" stroke-linecap="round"/>
    </g>

    <!-- ── ZWINKERN ── -->
    <g class="m-fw">
      <circle cx="60" cy="61" r="11" fill="url(#m-gEye)"/>
      <circle cx="61.5" cy="62.5" r="6.5" fill="#180800"/>
      <circle cx="64"   cy="59.5" r="2.5" fill="white"/>
      <path d="M79.5,61 Q90,69.5 100.5,61" stroke="#180800" stroke-width="4" fill="none" stroke-linecap="round"/>
      <g class="m-wl">
        <path d="M82,64 L80,68.5"   stroke="#180800" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M90,68 L90,73"     stroke="#180800" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M98,64 L100,68.5"  stroke="#180800" stroke-width="1.8" stroke-linecap="round"/>
      </g>
      <path d="M50,52 Q60,46 70,51"  stroke="#4A2810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M80,47 Q90,42 100,47" stroke="#4A2810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M63,87 Q76,98 89,85"  stroke="#3A1806" stroke-width="2.8" fill="none" stroke-linecap="round"/>
    </g>

    <!-- ── GRIMASSE ── -->
    <g class="m-fg">
      <circle cx="60" cy="61" r="11" fill="url(#m-gEye)"/>
      <circle cx="90" cy="61" r="11" fill="url(#m-gEye)"/>
      <circle cx="62"   cy="64.5" r="6.5" fill="#180800"/>
      <circle cx="92"   cy="64.5" r="6.5" fill="#180800"/>
      <circle cx="64.5" cy="62"   r="2.3" fill="white"/>
      <circle cx="94.5" cy="62"   r="2.3" fill="white"/>
      <path d="M49,58 Q60,53.5 71,58"  stroke="#9B6C32" stroke-width="7" fill="none"/>
      <path d="M79,58 Q90,53.5 101,58" stroke="#9B6C32" stroke-width="7" fill="none"/>
      <path d="M50,50 Q60,44 70,49"  stroke="#4A2810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M80,49 Q90,44 100,50" stroke="#4A2810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M60,85 Q75,97 90,85 Q86,79 75,78 Q64,79 60,85Z" fill="#3A1806"/>
      <rect x="65"   y="84.5" width="10" height="6.5" rx="2.2" fill="#EEEAE2"/>
      <rect x="76.5" y="84.5" width="10" height="6.5" rx="2.2" fill="#EEEAE2"/>
      <ellipse cx="75" cy="96"  rx="11" ry="8.5" fill="#CC3358"/>
      <path d="M75,87.5 L75,101" stroke="#AA1840" stroke-width="1.8"/>
      <ellipse cx="75" cy="101" rx="5"  ry="3"   fill="#BB2848"/>
    </g>

    <!-- ── LACHEN ── -->
    <g class="m-fl">
      <path d="M49,62 Q60,52 71,62"   stroke="#180800" stroke-width="4.5" fill="none" stroke-linecap="round"/>
      <path d="M79,62 Q90,52 101,62"  stroke="#180800" stroke-width="4.5" fill="none" stroke-linecap="round"/>
      <path d="M49,63 L45.5,69.5"    stroke="#180800" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M71,63 L74.5,69.5"    stroke="#180800" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M79,63 L75.5,69.5"    stroke="#180800" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M101,63 L104.5,69.5"  stroke="#180800" stroke-width="1.8" stroke-linecap="round"/>
      <path d="M50,49 Q60,43 70,48"  stroke="#4A2810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M80,48 Q90,43 100,49" stroke="#4A2810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M55,82 Q75,108 95,82 Q89,75 75,74 Q61,75 55,82Z" fill="#3A1806"/>
      <ellipse cx="75" cy="96" rx="15" ry="10" fill="#BB2840"/>
      <rect x="61"   y="82" width="11" height="6" rx="2.2" fill="#EEEAE2"/>
      <rect x="73.5" y="82" width="11" height="6" rx="2.2" fill="#EEEAE2"/>
      <circle cx="43"  cy="80" r="14" fill="#E87070" opacity="0.32"/>
      <circle cx="107" cy="80" r="14" fill="#E87070" opacity="0.32"/>
    </g>

    <!-- ── ÜBERRASCHT ── -->
    <g class="m-fs">
      <circle cx="60" cy="59" r="14" fill="url(#m-gEye)"/>
      <circle cx="90" cy="59" r="14" fill="url(#m-gEye)"/>
      <circle cx="61.5" cy="60.5" r="8.5" fill="#180800"/>
      <circle cx="91.5" cy="60.5" r="8.5" fill="#180800"/>
      <circle cx="65"   cy="57"   r="4"   fill="white"/>
      <circle cx="95"   cy="57"   r="4"   fill="white"/>
      <circle cx="57.5" cy="64"   r="2.2" fill="white" opacity="0.65"/>
      <circle cx="87.5" cy="64"   r="2.2" fill="white" opacity="0.65"/>
      <path d="M46,43 Q60,36 72,42"   stroke="#4A2810" stroke-width="3.5" fill="none" stroke-linecap="round"/>
      <path d="M78,42 Q90,36 104,43"  stroke="#4A2810" stroke-width="3.5" fill="none" stroke-linecap="round"/>
      <line x1="64" y1="35" x2="64" y2="40.5" stroke="#7A4820" stroke-width="2.2" stroke-linecap="round"/>
      <line x1="86" y1="35" x2="86" y2="40.5" stroke="#7A4820" stroke-width="2.2" stroke-linecap="round"/>
      <ellipse cx="75" cy="88" rx="9"   ry="10" fill="#3A1806"/>
      <ellipse cx="75" cy="86" rx="5.5" ry="4"  fill="#6A3020" opacity="0.35"/>
    </g>
  </g>
</svg>`;

  // Styles injizieren
  const styleTag = document.createElement("style");
  styleTag.textContent = `
    #murmel-button {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 62px;
      height: 62px;
      border-radius: 50%;
      background-color: #1a1a1a;
      border: 3px solid #f0c040;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(240, 192, 64, 0.3);
      z-index: 9999;
      transition: box-shadow 0.3s ease, transform 0.3s ease;
      padding: 0;
      overflow: hidden;
    }
    #murmel-button:hover {
      box-shadow: 0 6px 20px rgba(240, 192, 64, 0.5);
      transform: scale(1.05);
    }
    #murmel-bubble {
      position: fixed;
      bottom: 100px;
      right: 24px;
      background-color: #f5f5f0;
      color: #0f0f0f;
      border: 2px solid #f0c040;
      border-radius: 12px;
      padding: 12px 16px;
      max-width: 220px;
      font-size: 13px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.4;
      z-index: 9998;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      animation: fadeInOut 6s ease-in-out;
      word-wrap: break-word;
    }
    #murmel-bubble::after {
      content: '';
      position: absolute;
      bottom: -12px;
      right: 20px;
      width: 0; height: 0;
      border-left: 12px solid transparent;
      border-right: 0px solid transparent;
      border-top: 12px solid #f0c040;
    }
    @keyframes fadeInOut {
      0%   { opacity: 0; transform: translateY(10px); }
      10%  { opacity: 1; transform: translateY(0); }
      90%  { opacity: 1; transform: translateY(0); }
      100% { opacity: 0; transform: translateY(10px); }
    }
    #murmel-window {
      position: fixed;
      bottom: 100px;
      right: 24px;
      width: 380px;
      height: 600px;
      background-color: #0f0f0f;
      border: 2px solid #2a2a2a;
      border-radius: 12px;
      display: none;
      flex-direction: column;
      z-index: 9999;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    #murmel-window.open {
      display: flex;
      animation: slideUp 0.3s ease;
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(20px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    #murmel-header {
      background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
      border-bottom: 1px solid #2a2a2a;
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 10px 10px 0 0;
    }
    #murmel-header-title {
      color: #f0c040;
      font-size: 16px;
      font-weight: 600;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    #murmel-close-btn {
      background: none;
      border: none;
      color: #f0c040;
      font-size: 20px;
      cursor: pointer;
      padding: 0;
      width: 28px; height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: color 0.2s;
    }
    #murmel-close-btn:hover { color: #ffdb58; }
    #murmel-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background-color: #0f0f0f;
    }
    #murmel-messages::-webkit-scrollbar { width: 6px; }
    #murmel-messages::-webkit-scrollbar-track { background: #1a1a1a; border-radius: 10px; }
    #murmel-messages::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 10px; }
    #murmel-messages::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }
    .murmel-message { display: flex; gap: 8px; align-items: flex-start; }
    .murmel-message.user { justify-content: flex-end; }
    .murmel-bubble {
      padding: 12px 14px;
      border-radius: 12px;
      font-size: 14px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.4;
      max-width: 70%;
      word-wrap: break-word;
    }
    .murmel-bubble.murmel-from-user {
      background-color: #f0c040;
      color: #0f0f0f;
      border: 1px solid #d4a520;
    }
    .murmel-bubble.murmel-from-murmel {
      background-color: #1a1a1a;
      color: #f5f5f0;
      border: 1px solid #2a2a2a;
    }
    .murmel-typing { font-size: 18px; animation: blink 1.4s infinite; }
    @keyframes blink {
      0%,20%,50%,80%,100% { opacity: 1; }
      40% { opacity: 0.4; }
      60% { opacity: 0.7; }
    }
    #murmel-input-area {
      border-top: 1px solid #2a2a2a;
      padding: 12px;
      display: flex;
      gap: 8px;
      background-color: #0f0f0f;
      border-radius: 0 0 10px 10px;
    }
    #murmel-input {
      flex: 1;
      background-color: #1a1a1a;
      border: 1px solid #2a2a2a;
      color: #f5f5f0;
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 13px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      transition: border-color 0.2s;
    }
    #murmel-input:focus {
      outline: none;
      border-color: #f0c040;
      box-shadow: 0 0 8px rgba(240, 192, 64, 0.2);
    }
    #murmel-send-btn {
      background-color: #f0c040;
      color: #0f0f0f;
      border: none;
      border-radius: 8px;
      padding: 10px 16px;
      cursor: pointer;
      font-weight: 600;
      font-size: 13px;
      transition: all 0.2s;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    #murmel-send-btn:hover {
      background-color: #ffdb58;
      box-shadow: 0 2px 8px rgba(240, 192, 64, 0.3);
    }
    #murmel-send-btn:active  { transform: scale(0.95); }
    #murmel-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  `;
  document.head.appendChild(styleTag);

  // ── Button mit SVG ──
  const button = document.createElement("button");
  button.id = "murmel-button";
  button.innerHTML = MURMEL_SVG;
  document.body.appendChild(button);

  const svgEl = button.querySelector("svg");

  // ── Zustand setzen ──
  function setMurmelState(cls) {
    ALL_STATES.forEach(c => svgEl.classList.remove(c));
    svgEl.classList.add(cls);
  }

  // ── Zufälliger Zustandswechsel alle 15–30 Sekunden ──
  function scheduleNextState() {
    if (stateTimer) clearTimeout(stateTimer);
    const delay = 15000 + Math.random() * 15000;
    stateTimer = setTimeout(() => {
      if (!isOpen) {
        const next = SPECIAL_STATES[Math.floor(Math.random() * SPECIAL_STATES.length)];
        setMurmelState(next);
        // Nach 3–5 Sekunden zurück zu Idle
        if (returnTimer) clearTimeout(returnTimer);
        returnTimer = setTimeout(() => {
          if (!isOpen) setMurmelState('si');
        }, 3000 + Math.random() * 2000);
      }
      scheduleNextState();
    }, delay);
  }

  // ── Chat-Fenster ──
  const chatWindow = document.createElement("div");
  chatWindow.id = "murmel-window";

  const header = document.createElement("div");
  header.id = "murmel-header";

  const titleEl = document.createElement("div");
  titleEl.id = "murmel-header-title";
  titleEl.textContent = "🦫 Murmel";

  const closeBtn = document.createElement("button");
  closeBtn.id = "murmel-close-btn";
  closeBtn.textContent = "✕";
  closeBtn.type = "button";

  header.appendChild(titleEl);
  header.appendChild(closeBtn);

  const messagesContainer = document.createElement("div");
  messagesContainer.id = "murmel-messages";

  const inputArea = document.createElement("div");
  inputArea.id = "murmel-input-area";

  const input = document.createElement("input");
  input.id = "murmel-input";
  input.type = "text";
  input.placeholder = "Deine Frage...";
  input.autocomplete = "off";

  const sendBtn = document.createElement("button");
  sendBtn.id = "murmel-send-btn";
  sendBtn.textContent = "Senden";
  sendBtn.type = "button";

  inputArea.appendChild(input);
  inputArea.appendChild(sendBtn);
  chatWindow.appendChild(header);
  chatWindow.appendChild(messagesContainer);
  chatWindow.appendChild(inputArea);
  document.body.appendChild(chatWindow);

  // ── Sprechblase ──
  const bubble = document.createElement("div");
  bubble.id = "murmel-bubble";
  bubble.style.display = "none";
  document.body.appendChild(bubble);

  // ── Hilfsfunktionen ──
  function showBubble() {
    const pool = isIndexPage
      ? [...QUOTES_GENERAL, ...QUOTES_INDEX]
      : QUOTES_GENERAL;
    // Kein doppelter Spruch hintereinander
    let candidates = pool.filter(q => q !== lastQuote);
    if (!candidates.length) candidates = pool;
    const quote = candidates[Math.floor(Math.random() * candidates.length)];
    lastQuote = quote;

    bubble.textContent = quote;
    // Animation neu starten (Element klonen damit keyframe neu triggert)
    bubble.style.display = "none";
    void bubble.offsetWidth;
    bubble.style.display = "block";
    if (bubbleTimeout) clearTimeout(bubbleTimeout);
    bubbleTimeout = setTimeout(() => { bubble.style.display = "none"; }, 6000);
  }

  function scheduleNextBubble() {
    if (quoteTimeout) clearTimeout(quoteTimeout);
    const delay = 50000 + Math.random() * 10000; // 50–60 Sekunden
    quoteTimeout = setTimeout(() => {
      if (!isOpen) showBubble();
      scheduleNextBubble();
    }, delay);
  }

  function addMessage(text, isUser) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "murmel-message" + (isUser ? " user" : "");
    const bbl = document.createElement("div");
    bbl.className = "murmel-bubble " + (isUser ? "murmel-from-user" : "murmel-from-murmel");
    bbl.textContent = text;
    msgDiv.appendChild(bbl);
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function showTyping() {
    const msgDiv = document.createElement("div");
    msgDiv.className = "murmel-message";
    msgDiv.id = "murmel-typing-indicator";
    const bbl = document.createElement("div");
    bbl.className = "murmel-bubble murmel-from-murmel";
    const t = document.createElement("div");
    t.className = "murmel-typing";
    t.textContent = "...";
    bbl.appendChild(t);
    msgDiv.appendChild(bbl);
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function removeTyping() {
    const el = document.getElementById("murmel-typing-indicator");
    if (el) el.remove();
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    addMessage(text, true);
    input.value = "";
    sendBtn.disabled = true;
    showTyping();
    try {
      const res = await fetch(`${API_URL}/ask_murmel`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text })
      });
      removeTyping();
      if (!res.ok) {
        addMessage("Murmel schläft gerade 💤", false);
      } else {
        const data = await res.json();
        addMessage(data.answer || "Murmel schläft gerade 💤", false);
      }
    } catch {
      removeTyping();
      addMessage("Murmel schläft gerade 💤", false);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  function toggleChat() {
    isOpen = !isOpen;
    if (isOpen) {
      chatWindow.classList.add("open");
      if (quoteTimeout)  clearTimeout(quoteTimeout);
      if (bubbleTimeout) clearTimeout(bubbleTimeout);
      if (stateTimer)    clearTimeout(stateTimer);
      if (returnTimer)   clearTimeout(returnTimer);
      setMurmelState('si');
      bubble.style.display = "none";
      input.focus();
    } else {
      chatWindow.classList.remove("open");
      scheduleNextBubble();
      scheduleNextState();
    }
  }

  // ── Events ──
  button.addEventListener("click", toggleChat);
  closeBtn.addEventListener("click", toggleChat);
  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  // ── Start ──
  setMurmelState('si');
  scheduleNextBubble();
  scheduleNextState();
})();
