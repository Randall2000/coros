import express from 'express';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 3737;
const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 min

app.use(express.static(__dirname));

app.post('/api/refresh', async (req, res) => {
  try {
    syncData();
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

function syncData() {
  console.log('[sync] Fetching Coros data...');
  execSync(`node ${join(__dirname, 'scripts/fetch-data.js')}`, { stdio: 'inherit' });
}

// Initial sync on startup
try {
  syncData();
} catch (e) {
  console.warn('[sync] Initial fetch failed:', e.message);
}

// Auto-refresh every 5 min
setInterval(() => {
  try { syncData(); } catch (e) { console.warn('[sync] Auto-refresh failed:', e.message); }
}, REFRESH_INTERVAL);

app.listen(PORT, () => {
  console.log(`\n🏃 Hyrox 備賽儀表板已啟動`);
  console.log(`👉 http://localhost:${PORT}\n`);
});
