/* ═══════════════════════════════════════════════════════════════════════════
   Parent Eye - Main Application JavaScript
   ═══════════════════════════════════════════════════════════════════════════ */

// ─── State ───────────────────────────────────────────────────────────────────
let currentLang = localStorage.getItem('pc_lang') || 'en';
let currentUser = localStorage.getItem('pc_user') || null;
let userData = null;
let dashboardData = null;
let translations = {};
let subjectTranslations = {};
let marksTrendChart = null;

// Language codes for Web Speech API
const SPEECH_LANG_CODES = {
    en: 'en-US',
    te: 'te-IN',
    hi: 'hi-IN',
    ta: 'ta-IN'
};

// ─── Initialize ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    await loadTranslations(currentLang);

    // Check if on dashboard page and user is logged in
    if (window.location.pathname === '/dashboard') {
        if (!currentUser) {
            window.location.href = '/';
            return;
        }
        const dashSelect = document.getElementById('dashLangSelect');
        if (dashSelect) dashSelect.value = currentLang;
        loadDashboard();
    }
});


// ═══════════════════════════════════════════════════════════════════════════
//  LANGUAGE / TRANSLATION
// ═══════════════════════════════════════════════════════════════════════════

async function loadTranslations(lang) {
    try {
        const res = await fetch(`/api/translations/${lang}`);
        const data = await res.json();
        translations = data.ui;
        subjectTranslations = data.subjects;
        applyTranslations();
    } catch (err) {
        console.error('Failed to load translations:', err);
    }
}

function applyTranslations() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[key]) {
            el.textContent = translations[key];
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[key]) {
            el.placeholder = translations[key];
        }
    });

    // Login page specific
    const usernameLabel = document.getElementById('usernameLabel');
    if (usernameLabel) usernameLabel.textContent = translations.username || 'Username';

    const passwordLabel = document.getElementById('passwordLabel');
    if (passwordLabel) passwordLabel.textContent = translations.password || 'Password';

    const loginBtnText = document.getElementById('loginBtnText');
    if (loginBtnText) loginBtnText.textContent = translations.login_btn || 'Login';

    const demoHint = document.getElementById('demoHint');
    if (demoHint) demoHint.textContent = translations.demo_info || 'Demo: parent1 / pass123';

    const appTitle = document.getElementById('appTitle');
    if (appTitle) appTitle.textContent = translations.app_title || 'Parent Eye';

    // Update username/password placeholders
    const userInput = document.getElementById('username');
    if (userInput) userInput.placeholder = translations.username || 'Enter username';

    const passInput = document.getElementById('password');
    if (passInput) passInput.placeholder = translations.password || 'Enter password';

    // Update chatbot welcome message
    const chatWelcome = document.getElementById('chatWelcome');
    if (chatWelcome && translations.chatbot_welcome) {
        chatWelcome.innerHTML = translations.chatbot_welcome +
            '<div class="message-actions"><button class="msg-speak-btn" onclick="speakMessage(this.parentElement.parentElement)" title="Listen">🔊</button></div>';
    }

    // Update marks grid if dashboard is loaded
    if (dashboardData) {
        renderMarksGrid(dashboardData.marks);
        renderPredictions(dashboardData.predictions);
    }
}

function switchLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('pc_lang', lang);

    // Update login lang buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Update dashboard select
    const dashSelect = document.getElementById('dashLangSelect');
    if (dashSelect) dashSelect.value = lang;

    loadTranslations(lang);
}


// ═══════════════════════════════════════════════════════════════════════════
//  LOGIN
// ═══════════════════════════════════════════════════════════════════════════

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const loginBtn = document.getElementById('loginBtn');
    const errorMsg = document.getElementById('loginError');

    loginBtn.classList.add('loading');
    loginBtn.querySelector('span').textContent = '...';
    errorMsg.classList.remove('show');

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (data.success) {
            currentUser = username;
            userData = data.user;
            localStorage.setItem('pc_user', username);
            localStorage.setItem('pc_userData', JSON.stringify(data.user));

            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            errorMsg.textContent = data.error || 'Invalid credentials';
            errorMsg.classList.add('show');
            loginBtn.classList.remove('loading');
            loginBtn.querySelector('span').textContent = translations.login_btn || 'Login';
        }
    } catch (err) {
        errorMsg.textContent = 'Connection error. Please try again.';
        errorMsg.classList.add('show');
        loginBtn.classList.remove('loading');
        loginBtn.querySelector('span').textContent = translations.login_btn || 'Login';
    }
}


// ═══════════════════════════════════════════════════════════════════════════
//  DASHBOARD
// ═══════════════════════════════════════════════════════════════════════════

async function loadDashboard() {
    try {
        userData = JSON.parse(localStorage.getItem('pc_userData') || '{}');

        // Set parent name
        const parentName = document.getElementById('parentName');
        if (parentName) parentName.textContent = userData.name || 'Parent';

        const res = await fetch(`/api/dashboard?user=${currentUser}&lang=${currentLang}`);
        dashboardData = await res.json();

        renderStudentInfo(dashboardData.student);
        renderMarksGrid(dashboardData.marks);
        renderAttendance(dashboardData);
        renderMarksTrendChart(dashboardData.marks_history);
        renderPredictions(dashboardData.predictions);
        renderNotifications(dashboardData.notifications);
        renderRemarks(dashboardData.remarks);

    } catch (err) {
        console.error('Failed to load dashboard:', err);
    }
}

function renderStudentInfo(student) {
    const grid = document.getElementById('studentInfoGrid');
    if (!grid) return;

    const fields = [
        { key: 'child_name', value: student.name },
        { key: 'class', value: student.class },
        { key: 'section', value: student.section },
        { key: 'roll_no', value: student.roll_no },
        { key: 'school', value: student.school }
    ];

    grid.innerHTML = fields.map(f => `
        <div class="info-item">
            <div class="label">${translations[f.key] || f.key}</div>
            <div class="value">${f.value}</div>
        </div>
    `).join('');
}

function renderMarksGrid(marks) {
    const grid = document.getElementById('marksGrid');
    if (!grid) return;

    grid.innerHTML = Object.entries(marks).map(([subject, mark]) => {
        const colorClass = mark >= 85 ? 'mark-excellent' :
            mark >= 70 ? 'mark-good' :
                mark >= 50 ? 'mark-average' : 'mark-poor';
        const barColor = mark >= 85 ? 'var(--success)' :
            mark >= 70 ? 'var(--primary-light)' :
                mark >= 50 ? 'var(--warning)' : 'var(--danger)';

        const translatedSubject = subjectTranslations[subject] || subject;

        return `
            <div class="mark-card">
                <div class="subject-name">${translatedSubject}</div>
                <div class="mark-value ${colorClass}">${mark}</div>
                <div class="mark-label">${translations.mark || 'Marks'}</div>
                <div class="mark-bar" style="width: ${mark}%; background: ${barColor};"></div>
            </div>
        `;
    }).join('');
}

function renderAttendance(data) {
    const stats = document.getElementById('attendanceStats');
    if (!stats) return;

    const attClass = data.attendance >= 85 ? 'good' :
        data.attendance >= 70 ? 'warn' : 'danger';

    stats.innerHTML = `
        <div class="stat-item">
            <div class="stat-value ${attClass}">${data.attendance}%</div>
            <div class="stat-label">${translations.attendance || 'Attendance'}</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color: var(--primary-light)">${data.total_classes}</div>
            <div class="stat-label">${translations.total_classes || 'Total Classes'}</div>
        </div>
        <div class="stat-item">
            <div class="stat-value" style="color: var(--accent-light)">${data.attended_classes}</div>
            <div class="stat-label">${translations.attended || 'Attended'}</div>
        </div>
    `;

    // Animate attendance bar
    setTimeout(() => {
        const bar = document.getElementById('attendanceBar');
        if (bar) bar.style.width = data.attendance + '%';
    }, 300);
}

function renderMarksTrendChart(marksHistory) {
    const canvas = document.getElementById('marksTrendChart');
    if (!canvas) return;

    if (marksTrendChart) marksTrendChart.destroy();

    const subjects = Object.keys(marksHistory);
    const colors = [
        '#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'
    ];

    const datasets = subjects.map((subject, i) => ({
        label: subjectTranslations[subject] || subject,
        data: marksHistory[subject],
        borderColor: colors[i % colors.length],
        backgroundColor: colors[i % colors.length] + '20',
        tension: 0.4,
        fill: false,
        pointRadius: 5,
        pointHoverRadius: 7,
        borderWidth: 2
    }));

    const maxLen = Math.max(...subjects.map(s => marksHistory[s].length));
    const labels = Array.from({ length: maxLen }, (_, i) => `${translations.semester || 'Test'} ${i + 1}`);

    marksTrendChart = new Chart(canvas, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 12 },
                        padding: 16,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 15, 26, 0.9)',
                    titleFont: { family: 'Inter' },
                    bodyFont: { family: 'Inter' },
                    padding: 12,
                    cornerRadius: 8,
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#64748b', font: { family: 'Inter' } }
                },
                y: {
                    min: 40,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#64748b', font: { family: 'Inter' } }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function renderPredictions(predictions) {
    const grid = document.getElementById('predictionGrid');
    if (!grid) return;

    grid.innerHTML = Object.entries(predictions).map(([subject, pred]) => {
        const translatedSubject = subjectTranslations[subject] || subject;
        const trendKey = pred.trend || 'stable';
        const trendLabel = translations[trendKey] || trendKey;

        return `
            <div class="pred-card">
                <div class="pred-subject">${translatedSubject}</div>
                <div class="pred-value">${pred.predicted_mark}%</div>
                <span class="pred-trend trend-${trendKey}">${trendLabel}</span>
            </div>
        `;
    }).join('');
}

function renderNotifications(notifications) {
    const list = document.getElementById('notifList');
    if (!list) return;

    const icons = {
        exam: { icon: '📝', cls: 'notif-exam' },
        meeting: { icon: '🤝', cls: 'notif-meeting' },
        achievement: { icon: '🏆', cls: 'notif-achievement' }
    };

    list.innerHTML = notifications.map(n => {
        const { icon, cls } = icons[n.type] || icons.exam;
        return `
            <div class="notification-item">
                <div class="notif-icon ${cls}">${icon}</div>
                <div class="notif-content">
                    <div class="notif-msg">${n.message}</div>
                    <div class="notif-date">${n.date}</div>
                </div>
            </div>
        `;
    }).join('');
}

function renderRemarks(remarks) {
    const el = document.getElementById('remarksText');
    if (el) el.textContent = remarks;
}


// ═══════════════════════════════════════════════════════════════════════════
//  CUSTOM PREDICTION
// ═══════════════════════════════════════════════════════════════════════════

async function customPredict() {
    const input = document.getElementById('customMarksInput').value.trim();
    const resultDiv = document.getElementById('predictResult');
    const resultText = document.getElementById('predictResultText');

    if (!input) return;

    const marks = input.split(',').map(m => parseFloat(m.trim())).filter(m => !isNaN(m));

    if (marks.length < 2) {
        resultText.innerHTML = '⚠️ Please enter at least 2 marks separated by commas.';
        resultDiv.classList.add('show');
        return;
    }

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ past_marks: marks })
        });

        const data = await res.json();

        if (data.predicted_mark !== null) {
            const trendLabel = translations[data.trend] || data.trend;
            resultText.innerHTML = `
                <strong>${translations.predicted_mark || 'Predicted Mark'}:</strong> <span style="color: var(--accent-light); font-size: 20px; font-weight: 700;">${data.predicted_mark}%</span><br>
                <strong>${translations.trend || 'Trend'}:</strong> <span class="pred-trend trend-${data.trend}" style="display:inline-block; margin-top:4px;">${trendLabel}</span><br>
                <strong>${translations.confidence || 'Confidence'}:</strong> ${data.confidence}%
            `;
        } else {
            resultText.innerHTML = '⚠️ ' + (data.error || 'Unable to predict');
        }
        resultDiv.classList.add('show');
    } catch (err) {
        resultText.innerHTML = '❌ Error making prediction. Please try again.';
        resultDiv.classList.add('show');
    }
}


// ═══════════════════════════════════════════════════════════════════════════
//  CHATBOT
// ═══════════════════════════════════════════════════════════════════════════

function toggleChat() {
    const widget = document.getElementById('chatWidget');
    widget.classList.toggle('open');
    document.getElementById('chatBadge').style.display = 'none';

    if (widget.classList.contains('open')) {
        document.getElementById('chatInput').focus();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    // Add user message
    addChatMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    const typing = document.getElementById('typingIndicator');
    typing.classList.add('show');
    scrollChat();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                user: currentUser || 'parent1',
                lang: currentLang
            })
        });

        const data = await res.json();
        typing.classList.remove('show');

        // Add bot response
        addChatMessage(data.response, 'bot');

    } catch (err) {
        typing.classList.remove('show');
        addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

function addChatMessage(text, sender) {
    const container = document.getElementById('chatMessages');
    const typing = document.getElementById('typingIndicator');

    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender}`;
    msgDiv.textContent = text;

    if (sender === 'bot') {
        const actions = document.createElement('div');
        actions.className = 'message-actions';
        actions.innerHTML = '<button class="msg-speak-btn" onclick="speakMessage(this.parentElement.parentElement)" title="Listen">🔊</button>';
        msgDiv.appendChild(actions);
    }

    container.insertBefore(msgDiv, typing);
    scrollChat();
}

function scrollChat() {
    const container = document.getElementById('chatMessages');
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 50);
}


// ═══════════════════════════════════════════════════════════════════════════
//  TEXT-TO-SPEECH
// ═══════════════════════════════════════════════════════════════════════════

function speakMessage(msgElement) {
    // Get text content without the button text
    const text = msgElement.childNodes[0].textContent.trim();
    if (!text) return;

    // Try browser's built-in TTS first (works offline, supports all 4 languages)
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = SPEECH_LANG_CODES[currentLang] || 'en-US';
        utterance.rate = 0.9;
        utterance.pitch = 1;

        // Try to find a voice for the language
        const voices = window.speechSynthesis.getVoices();
        const langCode = SPEECH_LANG_CODES[currentLang];
        const matchingVoice = voices.find(v => v.lang.startsWith(langCode.split('-')[0]));
        if (matchingVoice) {
            utterance.voice = matchingVoice;
        }

        window.speechSynthesis.speak(utterance);
    } else {
        // Fallback: use server-side gTTS
        speakViaServer(text, currentLang);
    }
}

async function speakViaServer(text, lang) {
    try {
        const res = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, lang })
        });

        if (res.ok) {
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            audio.play();
            audio.onended = () => URL.revokeObjectURL(url);
        }
    } catch (err) {
        console.error('TTS error:', err);
    }
}


// ═══════════════════════════════════════════════════════════════════════════
//  SPEECH-TO-TEXT (Voice Input)
// ═══════════════════════════════════════════════════════════════════════════

let recognition = null;
let isRecording = false;

function toggleVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
        return;
    }

    const voiceBtn = document.getElementById('voiceBtn');

    if (isRecording) {
        // Stop recording
        if (recognition) recognition.stop();
        isRecording = false;
        voiceBtn.classList.remove('recording');
        return;
    }

    // Start recording
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = SPEECH_LANG_CODES[currentLang] || 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        isRecording = true;
        voiceBtn.classList.add('recording');
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('chatInput').value = transcript;
        isRecording = false;
        voiceBtn.classList.remove('recording');

        // Auto-send after voice input
        sendMessage();
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isRecording = false;
        voiceBtn.classList.remove('recording');
    };

    recognition.onend = () => {
        isRecording = false;
        voiceBtn.classList.remove('recording');
    };

    recognition.start();
}


// ═══════════════════════════════════════════════════════════════════════════
//  LOGOUT
// ═══════════════════════════════════════════════════════════════════════════

function handleLogout() {
    localStorage.removeItem('pc_user');
    localStorage.removeItem('pc_userData');
    currentUser = null;
    userData = null;
    window.location.href = '/';
}


// ═══════════════════════════════════════════════════════════════════════════
//  VOICE LOADING
// ═══════════════════════════════════════════════════════════════════════════

// Ensure voices are loaded (some browsers load them async)
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
    };
}
