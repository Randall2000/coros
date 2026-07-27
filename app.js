// ── Config ───────────────────────────────────────────────────────────────────
const DATA_BASE = './data';       // relative path (works local + GitHub Pages)

// ── Helpers ───────────────────────────────────────────────────────────────────

function parseLines(text) {
  const out = {};
  if (!text) return out;
  for (const line of text.split('\n')) {
    const m = line.match(/^([^:]+):\s*(.+)$/);
    if (m) out[m[1].trim()] = m[2].trim();
  }
  return out;
}

function extractNumber(str) {
  if (!str) return null;
  const m = str.match(/\d+/);
  return m ? parseInt(m[0], 10) : null;
}

function fmt2(n) { return String(n).padStart(2, '0'); }
function isoDate(d) { return `${d.getFullYear()}-${fmt2(d.getMonth()+1)}-${fmt2(d.getDate())}`; }

// ── Countdown ─────────────────────────────────────────────────────────────────

function updateCountdown() {
  const race = new Date(RACE_DATE + 'T00:00:00');
  const now  = new Date();
  const days = Math.ceil((race - now) / 86400000);
  const el   = document.getElementById('countdown');
  el.textContent = days > 0 ? `🏁 距離比賽 ${days} 天` : days === 0 ? '🏁 今天比賽！' : `比賽結束 ${-days} 天`;
}

// ── Plan week detection ───────────────────────────────────────────────────────

function getCurrentWeekIdx() {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  for (let i = PLAN.length - 1; i >= 0; i--) {
    const start = new Date(PLAN[i].startDate + 'T00:00:00');
    if (today >= start) return i;
  }
  return 0;
}

function getWeekStatus(idx) {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const start = new Date(PLAN[idx].startDate + 'T00:00:00');
  const end   = new Date(start.getTime() + 7 * 86400000);
  if (today >= start && today < end) return 'current';
  if (today >= end) return 'past';
  return 'upcoming';
}

// ── Training day map ──────────────────────────────────────────────────────────
// Week starts on Sunday (plan.startDate). Training: Mon(A) Wed(B) Fri(C).

function buildTrainingDayMap() {
  const map = {}; // 'YYYY-MM-DD' → { type, session, week }
  for (const week of PLAN) {
    const sunday = new Date(week.startDate + 'T00:00:00');
    const mon    = new Date(sunday); mon.setDate(mon.getDate() + 1);
    const wed    = new Date(sunday); wed.setDate(wed.getDate() + 3);
    const fri    = new Date(sunday); fri.setDate(fri.getDate() + 5);
    const sessions = week.training;
    map[isoDate(mon)] = { type: 'A', session: sessions.find(s => s.day === 'A'), week };
    map[isoDate(wed)] = { type: 'B', session: sessions.find(s => s.day === 'B'), week };
    map[isoDate(fri)] = { type: 'C', session: sessions.find(s => s.day === 'C'), week };
  }
  return map;
}

const TRAINING_MAP = buildTrainingDayMap();

// ── Logged activity dates ─────────────────────────────────────────────────────
// Parsed from activities text: "2026-07-26" lines

function buildLoggedDates(activitiesText) {
  const dates = new Set();
  if (!activitiesText) return dates;
  const matches = activitiesText.matchAll(/(\d{4}-\d{2}-\d{2})/g);
  for (const m of matches) dates.add(m[1]);
  return dates;
}

let LOGGED_DATES = new Set();

// ── CALENDAR ──────────────────────────────────────────────────────────────────

let calYear  = new Date().getFullYear();
let calMonth = new Date().getMonth(); // 0-indexed
let selectedDate = null;

const MONTH_NAMES = ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'];

function calPrevMonth() { calMonth--; if (calMonth < 0) { calMonth = 11; calYear--; } renderCalendar(); }
function calNextMonth() { calMonth++; if (calMonth > 11) { calMonth = 0; calYear++; } renderCalendar(); }

function renderCalendar() {
  const today = new Date(); today.setHours(0, 0, 0, 0);

  // Month label
  document.getElementById('calMonthLabel').textContent = `${calYear} / ${MONTH_NAMES[calMonth]}`;

  const firstDay = new Date(calYear, calMonth, 1);
  const lastDay  = new Date(calYear, calMonth + 1, 0);
  const startDow = (firstDay.getDay() + 6) % 7; // Mon=0 … Sun=6
  const totalCells = startDow + lastDay.getDate();
  const rows = Math.ceil(totalCells / 7);

  const container = document.getElementById('calDays');
  container.innerHTML = '';

  for (let i = 0; i < rows * 7; i++) {
    const dayNum = i - startDow + 1;
    const cell   = document.createElement('div');

    if (dayNum < 1 || dayNum > lastDay.getDate()) {
      cell.className = 'cal-day empty';
      container.appendChild(cell);
      continue;
    }

    const date    = new Date(calYear, calMonth, dayNum);
    const dateStr = isoDate(date);
    const isToday = date.getTime() === today.getTime();
    const isPast  = date < today;
    const training = TRAINING_MAP[dateStr];
    const logged   = LOGGED_DATES.has(dateStr);

    // Is this date in the current training week?
    const curIdx  = getCurrentWeekIdx();
    const curWeek = PLAN[curIdx];
    const weekStart = new Date(curWeek.startDate + 'T00:00:00');
    const weekEnd   = new Date(weekStart.getTime() + 7 * 86400000);
    const isCurrentWeek = date >= weekStart && date < weekEnd;

    let cls = 'cal-day';
    if (isToday)       cls += ' today';
    if (isPast)        cls += ' past-day';
    if (isCurrentWeek) cls += ' current-week-day';

    cell.className = cls;
    cell.setAttribute('role', 'button');
    cell.setAttribute('aria-label', `${calYear}年${calMonth+1}月${dayNum}日`);
    cell.tabIndex = 0;

    // Day number
    const numEl = document.createElement('div');
    numEl.className = 'cal-day-num';
    numEl.textContent = dayNum;
    cell.appendChild(numEl);

    // Training badge
    if (training) {
      const badge = document.createElement('span');
      badge.className = `cal-badge day-${training.type.toLowerCase()}`;
      if (training.week.deload) badge.classList.add('deload-badge');
      badge.textContent = training.type;
      cell.appendChild(badge);
    }

    // Dots row
    const dots = document.createElement('div');
    dots.className = 'cal-dots';
    if (logged) {
      const d = document.createElement('span');
      d.className = 'cal-dot-dot logged-dot';
      dots.appendChild(d);
    }
    if (training?.week?.deload) {
      const d = document.createElement('span');
      d.className = 'cal-dot-dot deload-dot';
      dots.appendChild(d);
    }
    if (dots.children.length) cell.appendChild(dots);

    // Click handler
    cell.addEventListener('click', () => showDayDetail(dateStr, dayNum, training, logged));
    cell.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') showDayDetail(dateStr, dayNum, training, logged); });

    container.appendChild(cell);
  }
}

function showDayDetail(dateStr, dayNum, training, logged) {
  const panel = document.getElementById('dayDetail');
  const [y, m, d] = dateStr.split('-');
  document.getElementById('dayDetailDate').textContent =
    `${y}年 ${parseInt(m)}月 ${parseInt(d)}日${training ? ' — W' + training.week.week : ''}`;

  const content = document.getElementById('dayDetailContent');
  content.innerHTML = '';

  if (training) {
    const week = training.week;
    const typeMap = { A: 'day-a-row run', B: 'day-b-row func', C: 'day-c-row sim' };
    for (const s of week.training) {
      const row = document.createElement('div');
      row.className = `detail-session ${typeMap[s.day] || ''}`;
      row.innerHTML = `
        <div class="detail-day-tag">DAY ${s.day}</div>
        <div>
          <div class="detail-name">${s.name}</div>
          <div class="detail-desc">${s.detail}</div>
        </div>`;
      content.appendChild(row);
    }
    if (week.deload) {
      const note = document.createElement('div');
      note.style.cssText = 'font-size:0.72rem;color:var(--cyan);margin-top:0.4rem;padding-top:0.4rem;border-top:1px solid var(--border)';
      note.textContent = '— 減量週：強度降低，讓身體充分恢復';
      content.appendChild(note);
    }
  } else {
    const el = document.createElement('div');
    el.style.cssText = 'font-size:0.78rem;color:var(--muted)';
    el.textContent = '本日無排定訓練';
    content.appendChild(el);
  }

  if (logged) {
    const el = document.createElement('div');
    el.style.cssText = 'font-size:0.72rem;color:var(--orange);margin-top:0.5rem;display:flex;align-items:center;gap:0.35rem';
    el.innerHTML = `<span style="font-size:0.6rem">●</span> Coros 有記錄本日活動`;
    content.appendChild(el);
  }

  panel.style.display = 'block';
}

// ── Today's Training ──────────────────────────────────────────────────────────

function renderTodayCard() {
  const idx  = getCurrentWeekIdx();
  const week = PLAN[idx];

  document.getElementById('todayBadge').textContent = `W${week.week}`;
  document.getElementById('todayPhase').textContent = week.phase;
  document.getElementById('todayTheme').textContent = week.theme;
  const deloadEl = document.getElementById('todayDeload');
  deloadEl.style.display = week.deload ? 'inline-flex' : 'none';

  const sessionsEl = document.getElementById('todaySessions');
  sessionsEl.innerHTML = week.training.map(s => `
    <div class="session-row ${s.type}">
      <div class="session-day">DAY ${s.day}</div>
      <div>
        <div class="session-name">${s.name}</div>
        <div class="session-detail">${s.detail}</div>
      </div>
    </div>
  `).join('');
}

// ── Plan Table ────────────────────────────────────────────────────────────────

const PHASE_COLORS = { '基礎期': 'var(--phase-1)', '增量期': 'var(--phase-2)', '專項期': 'var(--phase-3)', '減量期': 'var(--phase-4)' };

function fmtDateShort(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return `${d.getMonth()+1}/${d.getDate()}`;
}

function renderPlanTable() {
  const tbody = document.getElementById('planBody');
  let lastPhase = null;

  tbody.innerHTML = PLAN.map((week, idx) => {
    const status = getWeekStatus(idx);
    let phaseRow = '';

    if (week.phase !== lastPhase) {
      lastPhase = week.phase;
      const color = PHASE_COLORS[week.phase] || 'white';
      phaseRow = `<tr class="phase-row">
        <td colspan="7"><span class="phase-dot" style="background:${color}"></span>${week.phase}</td>
      </tr>`;
    }

    const rowClass = [
      status === 'current' ? 'current-week' : '',
      status === 'past'    ? 'past-week'    : '',
      week.deload          ? 'deload-week'  : '',
    ].filter(Boolean).join(' ');

    const badgeCls   = status === 'current' ? 'current' : status === 'past' ? 'done' : 'upcoming';
    const badgeTxt   = status === 'current' ? '▶ 本週' : status === 'past' ? '✓' : '–';
    const endDate    = new Date(new Date(week.startDate + 'T00:00:00').getTime() + 6 * 86400000);
    const endStr     = `${endDate.getMonth()+1}/${endDate.getDate()}`;

    return phaseRow + `
      <tr class="${rowClass}">
        <td><div class="week-num">W${week.week}</div></td>
        <td><div class="week-date">${fmtDateShort(week.startDate)}–${endStr}</div></td>
        <td><span class="status-badge ${badgeCls}">${badgeTxt}</span></td>
        <td style="font-size:0.7rem;max-width:160px">${week.theme}</td>
        ${week.training.map(s => `<td><div class="train-name">${s.name}</div><div class="train-detail">${s.detail}</div></td>`).join('')}
      </tr>`;
  }).join('');

  tbody.innerHTML += `
    <tr style="background:rgba(249,115,22,0.08);border-top:2px solid var(--orange)">
      <td colspan="7" style="text-align:center;padding:1rem;font-family:var(--font-head);font-weight:800;font-size:0.95rem;letter-spacing:0.12em;color:var(--orange)">
        🏁 HYROX 比賽日 — 2027/3/13
      </td>
    </tr>`;
}

// ── Health Data (from data/health.json) ───────────────────────────────────────

async function loadHealth() {
  try {
    const res  = await fetch(`${DATA_BASE}/health.json?t=${Date.now()}`);
    if (!res.ok) throw new Error('no file');
    const data = await res.json();
    applyHealth(data);
    if (data.updatedAt) updateSyncTime(new Date(data.updatedAt));
  } catch {
    // Fallback to local API server if running
    try {
      const res  = await fetch('/api/health');
      const data = await res.json();
      applyHealth(data);
      updateSyncTime(new Date());
    } catch {
      ['recovery','sleep','hr','stress'].forEach(k => {
        document.getElementById(`sub-${k}`).textContent = '無資料';
      });
    }
  }
}

function applyHealth(data) {
  // Recovery
  const recText = data.recovery ?? '';
  const recM = recText.match(/Recovery[:\s]*(\d+)%/i);
  if (recM) {
    const pct = parseInt(recM[1], 10);
    document.getElementById('val-recovery').textContent = pct + '%';
    const levelM = recText.match(/Level[:\s]*(.+)/i);
    document.getElementById('sub-recovery').textContent = levelM ? levelM[1].trim() : '';
    const card = document.getElementById('card-recovery');
    card.classList.add(pct >= 70 ? 'good' : pct >= 40 ? 'warn' : 'bad');
  }

  // Sleep
  const sleepM = (data.sleep ?? '').match(/Sleep Score[:\s]*(\d+)/i);
  if (sleepM) {
    const score = parseInt(sleepM[1], 10);
    document.getElementById('val-sleep').textContent = score;
    const durM = (data.sleep ?? '').match(/Main Sleep[:\s]*([\dhm\s]+)/i);
    document.getElementById('sub-sleep').textContent = durM ? durM[1].trim() : (score >= 80 ? '良好' : score >= 60 ? '尚可' : '不足');
    document.getElementById('card-sleep').classList.add(score >= 80 ? 'good' : score >= 60 ? 'warn' : 'bad');
  }

  // HR
  const hrLines = (data.hr ?? '').split('\n').filter(l => /\d+\s*bpm/i.test(l) && !/No data/i.test(l));
  const hrM = hrLines.length > 0 ? hrLines[0].match(/(\d+)\s*bpm/i) : null;
  if (hrM) {
    const hr = parseInt(hrM[1], 10);
    document.getElementById('val-hr').textContent = hr;
    document.getElementById('sub-hr').textContent = 'bpm 靜止心率';
    document.getElementById('card-hr').classList.add(hr < 60 ? 'good' : hr < 75 ? 'warn' : 'bad');
  }

  // Stress
  const stressM = (data.stress ?? '').match(/Average Stress[:\s]*(\d+)/i);
  if (stressM) {
    const s = parseInt(stressM[1], 10);
    document.getElementById('val-stress').textContent = s;
    const labelM = (data.stress ?? '').match(/Average Stress[:\s]*\d+\s*\(([^)]+)\)/i);
    document.getElementById('sub-stress').textContent = labelM ? labelM[1] : (s < 30 ? '低壓' : s < 60 ? '中等' : '高壓');
    document.getElementById('card-stress').classList.add(s < 30 ? 'good' : s < 60 ? 'warn' : 'bad');
  }
}

// ── Activities (from data/activities.json) ────────────────────────────────────

async function loadActivities() {
  const el = document.getElementById('activityContent');
  try {
    const res  = await fetch(`${DATA_BASE}/activities.json?t=${Date.now()}`);
    if (!res.ok) throw new Error('no file');
    const data = await res.json();
    applyActivities(data.activities ?? '');
    LOGGED_DATES = buildLoggedDates(data.activities ?? '');
    renderCalendar();
  } catch {
    try {
      const res  = await fetch('/api/activities');
      const data = await res.json();
      applyActivities(data.activities ?? '');
      LOGGED_DATES = buildLoggedDates(data.activities ?? '');
      renderCalendar();
    } catch {
      el.textContent = '無法載入 Coros 資料';
    }
  }
}

function applyActivities(text) {
  const el = document.getElementById('activityContent');
  const clean = text.replace(/={3,}/g, '').replace(/\n{3,}/g, '\n\n').trim();
  el.textContent = clean || '近期無訓練紀錄';
}

// ── Sync time ─────────────────────────────────────────────────────────────────

function updateSyncTime(date = new Date()) {
  const hh = fmt2(date.getHours()), mm = fmt2(date.getMinutes());
  document.getElementById('syncTime').textContent = `更新 ${hh}:${mm}`;
}

async function forceRefresh() {
  const btn = document.getElementById('syncBtn');
  btn.disabled = true;
  btn.querySelector('svg').style.animation = 'spin 1s linear infinite';

  // Try local server refresh
  try { await fetch('/api/refresh', { method: 'POST' }); } catch {}

  await Promise.all([loadHealth(), loadActivities()]);
  updateSyncTime();

  btn.disabled = false;
  btn.querySelector('svg').style.animation = '';
}

// ── Init ──────────────────────────────────────────────────────────────────────

// Add spin keyframe
const style = document.createElement('style');
style.textContent = '@keyframes spin{to{transform:rotate(360deg)}}';
document.head.appendChild(style);

updateCountdown();
setInterval(updateCountdown, 60000);

renderTodayCard();
renderCalendar();
renderPlanTable();

// Scroll current week into view
setTimeout(() => {
  const row = document.querySelector('.plan-table tr.current-week');
  if (row) row.scrollIntoView({ behavior: 'smooth', block: 'center' });
}, 400);

// Load data
Promise.all([loadHealth(), loadActivities()]);

// Auto-refresh every 5 min
setInterval(() => {
  loadHealth();
  loadActivities();
}, 5 * 60 * 1000);
