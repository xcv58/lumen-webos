// Exercise a fresh public profile, separately from the seeded UI fixtures.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {openBrowser} from './browser.mjs';

const browser = await openBrowser();
const errors = [], external = [];
const page = await browser.newPage({viewport: {width: 1920, height: 1080}});
page.on('pageerror', error => errors.push(error.message));
await page.route('https://**/*', route => { external.push(route.request().url()); return route.abort(); });
await page.addInitScript(() => {
 localStorage.clear();
 window.previewCalls = [];
 window.PalmServiceBridge = class {
  cancel() { this.cancelled = true; }
  call(uri, json) {
   const params = JSON.parse(json);
   window.previewCalls.push({uri, params});
   let result = {returnValue: false, errorText: 'Public profile fixture'};
   if (uri.endsWith('/getAppLoadStatus')) result = {returnValue: true, exist: true};
   if (uri.endsWith('/getAllInputStatus')) result = {returnValue: true, devices: []};
   setTimeout(() => { if (!this.cancelled && this.onservicecallback) this.onservicecallback(JSON.stringify(result)); }, 5);
  }
 };
});
try {
 await page.goto(process.env.TRIAL_URL || 'http://127.0.0.1:5187');
 await page.waitForFunction(() => document.querySelectorAll('.trial-row .tile').length >= 5);
 await page.waitForTimeout(2300);
 const config = await page.evaluate(() => JSON.parse(localStorage.getItem('launcher-config-v2')));
 assert.equal(config.useHomebrew, false);
 assert.equal(config.showWeather, false);
 assert.equal(config.navigationSounds, 'off');
 assert.equal(config.weatherCountry, '');
 assert.equal(config.weatherCity, '');
 assert.deepEqual(config.recentIds, []);
 assert.equal(await page.locator('.status__weather').count(), 0);
 const calls = await page.evaluate(() => window.previewCalls);
 assert(!calls.some(call => /listLaunchPoints|dd if=/.test(call.params.command || '')), 'Fresh profiles must not discover native apps/icons before opt-in');
 assert(!external.some(url => /ipwho\.is|open-meteo/.test(url)), 'Weather Off must not locate the TV');
 await page.keyboard.press('ArrowDown');
 await page.waitForFunction(() => document.querySelector('.trial-home').classList.contains('screen--lower'));
 await page.keyboard.press('Escape');
 await page.waitForFunction(() => !document.querySelector('.trial-home').classList.contains('screen--lower'));
 assert.deepEqual(errors, []);
 const result = {passed: true, checks: ['fresh app-discovery opt-in', 'weather Off without geolocation', 'navigation sounds Off', 'no seeded personal location/history', 'grid Down and Back'], errors};
 fs.writeFileSync('.trial-evidence/public-preview-results.json', JSON.stringify(result, null, 2));
 console.log(JSON.stringify(result));
} finally { await browser.close(); }
