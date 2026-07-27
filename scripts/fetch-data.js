#!/usr/bin/env node
// Fetches Coros health & activity data and writes to data/
// Used by: local server.js (on startup) + GitHub Actions (daily)

import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);
const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, '..', 'data');

mkdirSync(DATA_DIR, { recursive: true });

function getText(result) {
  try {
    let text = result?.content?.[0]?.text ?? '';
    if (text.startsWith('"') && text.endsWith('"')) text = JSON.parse(text);
    return text;
  } catch {
    return result?.content?.[0]?.text ?? '';
  }
}

async function callTool(toolName, args = {}) {
  const argsJson = JSON.stringify(args);
  const { stdout } = await execAsync(
    `coros-mcp call-tool --tool ${toolName} --arguments-json '${argsJson}'`
  );
  return JSON.parse(stdout);
}

function todayStr() {
  return new Date().toISOString().slice(0, 10).replace(/-/g, '');
}

function daysAgoStr(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10).replace(/-/g, '');
}

async function fetchHealth() {
  const today = todayStr();
  const [recovery, sleep, hr, stress] = await Promise.all([
    callTool('queryRecoveryStatus', {}),
    callTool('querySleepData', { startDate: today, endDate: today, days: 1 }),
    callTool('queryRestingHeartRate', { days: 3 }),
    callTool('queryStressLevel', { days: 1 }),
  ]);

  const data = {
    updatedAt: new Date().toISOString(),
    recovery: getText(recovery),
    sleep: getText(sleep),
    hr: getText(hr),
    stress: getText(stress),
  };

  writeFileSync(join(DATA_DIR, 'health.json'), JSON.stringify(data, null, 2));
  console.log('✓ health.json updated');
}

async function fetchActivities() {
  const end = todayStr();
  const start = daysAgoStr(30);

  const result = await callTool('querySportRecords', {
    startDate: start,
    endDate: end,
    sportTypeCodes: null,
    minDistanceKm: null,
    maxDistanceKm: null,
    minDurationMinutes: null,
    maxDurationMinutes: null,
    maxAveragePace: null,
    locationKeyword: null,
    limit: 20,
  });

  const data = {
    updatedAt: new Date().toISOString(),
    activities: getText(result),
  };

  writeFileSync(join(DATA_DIR, 'activities.json'), JSON.stringify(data, null, 2));
  console.log('✓ activities.json updated');
}

console.log('Fetching Coros data...');
await Promise.all([fetchHealth(), fetchActivities()]);
console.log('Done.');
