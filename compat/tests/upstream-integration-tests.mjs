import fs from 'node:fs';
import assert from 'node:assert/strict';
import {openBrowser,seedPreview} from './browser.mjs';
const b=await openBrowser(),p=await b.newPage({viewport:{width:1920,height:1080}}),checks=[],errors=[];
p.on('pageerror',e=>errors.push(e.message));await seedPreview(p);
const row=label=>p.locator('.slist__row').filter({has:p.getByText(label,{exact:true})});
const backHome=async()=>{for(let i=0;i<5&&await p.locator('.screen--settings').count();i++)await p.keyboard.press('Escape');};
const settings=async()=>{await p.locator('.topbar .pill').nth(1).click();await p.locator('[data-control=settings]').click();};
try {
 await p.goto(process.env.TRIAL_URL||'http://127.0.0.1:5191');await p.waitForSelector('.trial-home');await settings();
 await row('System').click();await row('More TV controls').click();await p.waitForSelector('.panel--cc .cc__mod');await p.keyboard.press('Escape');
 assert(await p.locator('.trial-home').count());await p.locator('.topbar .pill').nth(1).click();assert(await p.locator('.panel--accepted-cc').count());await p.keyboard.press('Escape');
 checks.push('upstream TV controls remain accessible and return to matched Home/panels');
 await settings();await row('Appearance').click();await row('Matched Home and panels').click();await backHome();
 assert.equal(await p.locator('.trial-home').count(),0);await p.locator('.topbar .pill').nth(1).click();await p.waitForSelector('.panel--cc .cc__mod');
 await p.locator('.cc__circle').nth(3).click();await row('Appearance').click();await row('Matched Home and panels').click();await backHome();assert(await p.locator('.trial-home').count());
 checks.push('upstream presentation can be selected and switched back without losing settings');
 await settings();await row('Screensaver').click();await row('Screensaver type').click();await row('StandBy').click();await backHome();
 await p.locator('.topbar .pill').nth(1).click();await p.locator('[data-control=photo]').click();await p.getByText('Start now',{exact:true}).click();await p.waitForSelector('.sb');await p.keyboard.press('ArrowRight');assert(await p.locator('.sb--analog').count());await p.keyboard.press('Escape');
 checks.push('upstream StandBy selection, analog navigation and Back work from matched Control Center');
 assert.deepEqual(errors,[]);
}finally{fs.writeFileSync('.trial-evidence/upstream-integration-results.json',JSON.stringify({checks,errors},null,2));console.log(JSON.stringify({checks,errors}));await b.close();}
