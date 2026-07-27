// 32-Week Hyrox Training Plan
// Race: 2027-03-13 | Start: 2026-07-27 | 3 days/week
// Equipment: Rowing machine, dumbbells, wall balls, TRX, treadmill/track

const RACE_DATE = '2027-03-13';
const PLAN_START = '2026-07-27';

const CIRCUIT_BASE = '划船機 400m・Burpee Broad Jump 8m×4・啞鈴弓步 15m・Wall Balls 12 下・TRX 划船 10 下・農夫走 20m';
const CIRCUIT_MID  = '划船機 500m・Burpee Broad Jump 10m×4・啞鈴弓步 20m・Wall Balls 15 下・TRX 划船 12 下・農夫走 30m';
const CIRCUIT_HEAVY= '划船機 600m・Burpee Broad Jump 12m×4・啞鈴弓步 25m・Wall Balls 20 下・TRX 划船 15 下・農夫走 40m';
const CIRCUIT_PEAK = '划船機 800m・Burpee Broad Jump 15m×4・啞鈴弓步 30m・Wall Balls 25 下・戰繩 90 秒・農夫走 50m';

const PLAN = [
  // ── Phase 1: 基礎期 (Week 1–8) ──────────────────────────────────
  {
    week: 1, startDate: '2026-07-27', phase: '基礎期', deload: false,
    theme: '動作入門，熟悉所有 Hyrox 站項',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 跑步', detail: '輕鬆跑 4km，目標配速 6:15/km，全程能說話為準' },
      { day: 'B', type: 'func', name: 'Hyrox 入門電路', detail: `3 輪，輪間休息 90 秒：${CIRCUIT_BASE}` },
      { day: 'C', type: 'sim',  name: '入門模擬', detail: '跑 3km → 電路 2 輪 → 跑 1km（感受複合疲勞）' },
    ],
  },
  {
    week: 2, startDate: '2026-08-03', phase: '基礎期', deload: false,
    theme: '建立有氧底子，動作穩定性',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 跑步', detail: '輕鬆跑 5km，配速 6:15/km' },
      { day: 'B', type: 'func', name: 'Hyrox 入門電路', detail: `3 輪，輪間休息 90 秒：${CIRCUIT_BASE}` },
      { day: 'C', type: 'sim',  name: '入門模擬', detail: '跑 3km → 電路 2 輪 → 跑 2km' },
    ],
  },
  {
    week: 3, startDate: '2026-08-10', phase: '基礎期', deload: false,
    theme: '略微提升重量，維持動作品質',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 跑步', detail: '輕鬆跑 5km，配速 6:10/km' },
      { day: 'B', type: 'func', name: '電路（加重）', detail: `3 輪，休息 75 秒：${CIRCUIT_MID}` },
      { day: 'C', type: 'sim',  name: '模擬 + 跑步', detail: '跑 4km → 電路 2 輪 → 跑 1km' },
    ],
  },
  {
    week: 4, startDate: '2026-08-17', phase: '基礎期', deload: true,
    theme: '減量恢復週',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 3km，配速隨意，享受跑步' },
      { day: 'B', type: 'func', name: '輕量電路', detail: '2 輪，休息 2 分鐘，重量降 20%：' + CIRCUIT_BASE },
      { day: 'C', type: 'sim',  name: '輕鬆模擬', detail: '跑 2km → 電路 1 輪 → 跑 1km' },
    ],
  },
  {
    week: 5, startDate: '2026-08-24', phase: '基礎期', deload: false,
    theme: '增加電路輪數，引入 1km 模擬節奏',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 跑步', detail: '輕鬆跑 6km，配速 6:10/km' },
      { day: 'B', type: 'func', name: '電路 4 輪', detail: `4 輪，休息 75 秒：${CIRCUIT_MID}` },
      { day: 'C', type: 'sim',  name: '1km 模擬節奏', detail: '1km 跑 → 站項 → 1km 跑 → 站項（3 組），休息 3 分鐘/組' },
    ],
  },
  {
    week: 6, startDate: '2026-08-31', phase: '基礎期', deload: false,
    theme: '穩固基礎，輕度加強',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 跑步', detail: '輕鬆跑 6km，配速 6:05/km' },
      { day: 'B', type: 'func', name: '電路 4 輪（加重）', detail: `4 輪，休息 70 秒：${CIRCUIT_HEAVY}` },
      { day: 'C', type: 'sim',  name: '1km 模擬節奏', detail: '1km 跑 → 站項 → 1km 跑 → 站項（3 組），休息 2.5 分/組' },
    ],
  },
  {
    week: 7, startDate: '2026-09-07', phase: '基礎期', deload: false,
    theme: '接近基礎期峰值',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 跑步', detail: '輕鬆跑 7km，配速 6:00/km' },
      { day: 'B', type: 'func', name: '電路 4 輪（高重）', detail: `4 輪，休息 60 秒：${CIRCUIT_HEAVY}` },
      { day: 'C', type: 'sim',  name: '1km 模擬節奏', detail: '1km 跑 → 站項 → 1km 跑 → 站項（4 組），休息 2 分/組' },
    ],
  },
  {
    week: 8, startDate: '2026-09-14', phase: '基礎期', deload: true,
    theme: '基礎期末減量週',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 4km，純 Zone 2 恢復' },
      { day: 'B', type: 'func', name: '輕量電路', detail: '2 輪，休息 2 分：' + CIRCUIT_BASE },
      { day: 'C', type: 'sim',  name: '輕鬆模擬', detail: '1km 跑 → 站項（3 組），輕鬆完成即可' },
    ],
  },

  // ── Phase 2: 增量期 (Week 9–18) ────────────────────────────────
  {
    week: 9, startDate: '2026-09-21', phase: '增量期', deload: false,
    theme: '拉長跑量，開始中等強度電路',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 長跑', detail: '跑 8km，配速 6:00/km，保持輕鬆對話' },
      { day: 'B', type: 'func', name: '電路 5 輪', detail: `5 輪，休息 75 秒：${CIRCUIT_HEAVY}` },
      { day: 'C', type: 'sim',  name: '1km 模擬', detail: '1km 跑 → 站項（4 組），休息 2 分/組' },
    ],
  },
  {
    week: 10, startDate: '2026-09-28', phase: '增量期', deload: false,
    theme: '強化複合耐力',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 長跑', detail: '跑 8km，配速 5:55/km' },
      { day: 'B', type: 'func', name: '電路 5 輪（加重）', detail: `5 輪，休息 70 秒：${CIRCUIT_HEAVY}` },
      { day: 'C', type: 'sim',  name: '1km 模擬', detail: '1km 跑 → 站項（4 組），休息 90 秒/組' },
    ],
  },
  {
    week: 11, startDate: '2026-10-05', phase: '增量期', deload: false,
    theme: '拉長單次訓練總量',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 長跑', detail: '跑 9km，配速 5:55/km' },
      { day: 'B', type: 'func', name: '電路 5 輪（重）', detail: `5 輪，休息 65 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '1km 模擬加量', detail: '1km 跑 → 站項（5 組），休息 90 秒/組' },
    ],
  },
  {
    week: 12, startDate: '2026-10-12', phase: '增量期', deload: true,
    theme: '增量期中減量',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 5km，Zone 2 恢復' },
      { day: 'B', type: 'func', name: '輕量電路', detail: '3 輪，休息 2 分：' + CIRCUIT_MID },
      { day: 'C', type: 'sim',  name: '輕鬆模擬', detail: '1km 跑 → 站項（3 組），輕鬆配速' },
    ],
  },
  {
    week: 13, startDate: '2026-10-19', phase: '增量期', deload: false,
    theme: '引入高強度電路',
    training: [
      { day: 'A', type: 'run',  name: 'Zone 2 長跑', detail: '跑 9km，配速 5:50/km' },
      { day: 'B', type: 'func', name: '電路 5 輪（高強）', detail: `5 輪，休息 60 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '1km 模擬', detail: '1km 跑 → 站項（5 組），休息 75 秒/組' },
    ],
  },
  {
    week: 14, startDate: '2026-10-26', phase: '增量期', deload: false,
    theme: '達到增量期跑步峰值',
    training: [
      { day: 'A', type: 'run',  name: '10km 長跑', detail: '跑 10km，配速 5:45–6:00/km' },
      { day: 'B', type: 'func', name: '電路 6 輪', detail: `6 輪，休息 60 秒：${CIRCUIT_HEAVY}` },
      { day: 'C', type: 'sim',  name: '1km 模擬', detail: '1km 跑 → 站項（5 組），休息 60 秒/組' },
    ],
  },
  {
    week: 15, startDate: '2026-11-02', phase: '增量期', deload: false,
    theme: '引入節奏跑片段',
    training: [
      { day: 'A', type: 'run',  name: '節奏跑', detail: '10km：前後各 2km 輕鬆配速，中間 6km 節奏跑（約 5:30/km）' },
      { day: 'B', type: 'func', name: '電路 6 輪（重）', detail: `6 輪，休息 55 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '1km 模擬加量', detail: '1km 跑 → 站項（6 組），休息 60 秒/組' },
    ],
  },
  {
    week: 16, startDate: '2026-11-09', phase: '增量期', deload: true,
    theme: '增量期末減量',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 5km，Zone 2 恢復' },
      { day: 'B', type: 'func', name: '輕量電路', detail: '3 輪，休息 2 分：' + CIRCUIT_MID },
      { day: 'C', type: 'sim',  name: '輕鬆模擬', detail: '1km 跑 → 站項（3 組）' },
    ],
  },
  {
    week: 17, startDate: '2026-11-16', phase: '增量期', deload: false,
    theme: '鞏固增量期成果',
    training: [
      { day: 'A', type: 'run',  name: '10km 跑', detail: '跑 10km，含 4km 節奏段（5:20/km）' },
      { day: 'B', type: 'func', name: '電路 6 輪（重）', detail: `6 輪，休息 55 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '1km 模擬', detail: '1km 跑 → 站項（6 組），全力配速' },
    ],
  },
  {
    week: 18, startDate: '2026-11-23', phase: '增量期', deload: false,
    theme: '增量期收尾，準備進入專項期',
    training: [
      { day: 'A', type: 'run',  name: '10km + 節奏', detail: '跑 10km，含 5km 節奏段（5:15/km）' },
      { day: 'B', type: 'func', name: '電路 6 輪', detail: `6 輪，休息 50 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '6 組全力模擬', detail: '1km 跑 → 站項（6 組），組間休息 45 秒' },
    ],
  },

  // ── Phase 3: 專項期 (Week 19–27) ────────────────────────────────
  {
    week: 19, startDate: '2026-11-30', phase: '專項期', deload: false,
    theme: '引入間歇跑，模擬比賽心率',
    training: [
      { day: 'A', type: 'run',  name: '間歇跑', detail: '5×1km，目標配速 5:00/km，組間慢跑 90 秒' },
      { day: 'B', type: 'func', name: '重量電路 5 輪', detail: `5 輪，休息 50 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '完整模擬 6 組', detail: '1km 跑 → 站項（6 組），全力完成' },
    ],
  },
  {
    week: 20, startDate: '2026-12-07', phase: '專項期', deload: true,
    theme: '專項期中減量',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 5km Zone 2，好好恢復' },
      { day: 'B', type: 'func', name: '輕量電路', detail: '3 輪，休息 2 分：' + CIRCUIT_MID },
      { day: 'C', type: 'sim',  name: '輕鬆模擬', detail: '1km 跑 → 站項（3 組）' },
    ],
  },
  {
    week: 21, startDate: '2026-12-14', phase: '專項期', deload: false,
    theme: '完整 Hyrox 模擬訓練',
    training: [
      { day: 'A', type: 'run',  name: '間歇跑', detail: '5×1km，目標 4:55/km，組間慢跑 75 秒' },
      { day: 'B', type: 'func', name: '重量電路 5 輪', detail: `5 輪，休息 45 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '完整模擬 7 組', detail: '1km 跑 → 站項（7 組），組間不休息' },
    ],
  },
  {
    week: 22, startDate: '2026-12-21', phase: '專項期', deload: false,
    theme: '節奏跑 + 模擬強化',
    training: [
      { day: 'A', type: 'run',  name: '節奏跑', detail: '7km 節奏跑（5:10/km），前後各 1km 熱身收操' },
      { day: 'B', type: 'func', name: '重量電路 5 輪', detail: `5 輪，休息 45 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '完整模擬 7 組', detail: '1km 跑 → 站項（7 組），穩定配速' },
    ],
  },
  {
    week: 23, startDate: '2026-12-28', phase: '專項期', deload: false,
    theme: '接近完整比賽量',
    training: [
      { day: 'A', type: 'run',  name: '間歇跑', detail: '5×1km，目標 4:50/km，組間慢跑 60 秒' },
      { day: 'B', type: 'func', name: '電路 6 輪', detail: `6 輪，休息 45 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '完整模擬 8 組', detail: '1km 跑 → 站項（8 組）— 全比賽量！' },
    ],
  },
  {
    week: 24, startDate: '2027-01-04', phase: '專項期', deload: true,
    theme: '新年恢復週',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 5km Zone 2，讓身體恢復' },
      { day: 'B', type: 'func', name: '輕量電路', detail: '3 輪，休息 2 分：' + CIRCUIT_MID },
      { day: 'C', type: 'sim',  name: '輕鬆模擬', detail: '1km 跑 → 站項（4 組）' },
    ],
  },
  {
    week: 25, startDate: '2027-01-11', phase: '專項期', deload: false,
    theme: '進入衝刺期',
    training: [
      { day: 'A', type: 'run',  name: '間歇跑', detail: '6×1km，目標 4:50/km，組間慢跑 60 秒' },
      { day: 'B', type: 'func', name: '電路 6 輪（重）', detail: `6 輪，休息 40 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '全 Hyrox 模擬', detail: '1km×8 跑 + 8 站項，模擬正式比賽' },
    ],
  },
  {
    week: 26, startDate: '2027-01-18', phase: '專項期', deload: false,
    theme: '穩定高強度，建立信心',
    training: [
      { day: 'A', type: 'run',  name: '節奏跑', detail: '8km 節奏跑（5:05/km）' },
      { day: 'B', type: 'func', name: '電路 6 輪（重）', detail: `6 輪，休息 40 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '全 Hyrox 模擬', detail: '1km×8 跑 + 8 站項，穩定完成' },
    ],
  },
  {
    week: 27, startDate: '2027-01-25', phase: '專項期', deload: false,
    theme: '專項期最後衝刺',
    training: [
      { day: 'A', type: 'run',  name: '間歇跑', detail: '6×1km，目標 4:45/km — 最高強度!' },
      { day: 'B', type: 'func', name: '電路 5 輪（重）', detail: `5 輪，休息 45 秒：${CIRCUIT_PEAK}` },
      { day: 'C', type: 'sim',  name: '全 Hyrox 模擬（全力）', detail: '1km×8 跑 + 8 站項，計時！這是你的最佳參考成績' },
    ],
  },

  // ── Phase 4: 減量期 (Week 28–32) ────────────────────────────────
  {
    week: 28, startDate: '2027-02-01', phase: '減量期', deload: false,
    theme: '開始降量，維持強度',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 6km，Zone 2，不要硬撐' },
      { day: 'B', type: 'func', name: '電路 4 輪（60%）', detail: '量減 40%，強度維持：' + CIRCUIT_HEAVY },
      { day: 'C', type: 'sim',  name: '4 組模擬', detail: '1km 跑 → 站項（4 組），保持感覺' },
    ],
  },
  {
    week: 29, startDate: '2027-02-08', phase: '減量期', deload: false,
    theme: '繼續降量',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 5km Zone 2' },
      { day: 'B', type: 'func', name: '電路 3 輪（50%）', detail: '量減 50%：' + CIRCUIT_MID },
      { day: 'C', type: 'sim',  name: '3 組模擬', detail: '1km 跑 → 站項（3 組）' },
    ],
  },
  {
    week: 30, startDate: '2027-02-15', phase: '減量期', deload: false,
    theme: '接近賽前狀態',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 4km Zone 2' },
      { day: 'B', type: 'func', name: '電路 2 輪（40%）', detail: '量減 60%，維持動作感：' + CIRCUIT_BASE },
      { day: 'C', type: 'sim',  name: '2 組模擬', detail: '1km 跑 → 站項（2 組），感受比賽配速' },
    ],
  },
  {
    week: 31, startDate: '2027-02-22', phase: '減量期', deload: false,
    theme: '賽前兩週，養精蓄銳',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆跑', detail: '跑 3km，輕鬆感受腳感' },
      { day: 'B', type: 'func', name: '動作確認', detail: '極輕量：每個站項做 1 輪，確認動作不生疏' },
      { day: 'C', type: 'sim',  name: '比賽配速感受', detail: '1km 跑（比賽配速） + 2 個站項，找到比賽感覺' },
    ],
  },
  {
    week: 32, startDate: '2027-03-01', phase: '減量期', deload: false,
    theme: '賽前一週，靜養備戰 🏁',
    training: [
      { day: 'A', type: 'run',  name: '輕鬆慢跑', detail: '跑 2km，純放鬆，不追配速' },
      { day: 'B', type: 'func', name: '熱身動作', detail: '15 分鐘輕鬆熱身，感受每個動作，不追求強度' },
      { day: 'C', type: 'sim',  name: '靜養 / 伸展', detail: '休息或輕鬆伸展，保存體力迎接比賽日' },
    ],
  },
];
