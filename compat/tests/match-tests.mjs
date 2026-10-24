import fs from 'node:fs';
import assert from 'node:assert/strict';
import {openBrowser} from './browser.mjs';
import {seedTV} from './fixture.mjs';
const browser=await openBrowser(),checks=[],errors=[];
const styles=['borderRadius','borderColor','backgroundColor','backgroundOrigin','backgroundPosition','boxShadow','color','fontSize','lineHeight','paddingLeft','paddingRight'];
const metrics=async(page,selector)=>page.locator(selector).first().evaluate((e,props)=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {x:r.x,y:r.y,width:r.width,height:r.height,...Object.fromEntries(props.map(p=>[p,s[p]]))};},styles);
const compare=async(selector)=>{
 const [a,b]=await Promise.all(pages.map(p=>metrics(p,selector)));
 for(const k of Object.keys(a)){if(typeof a[k]==='number')assert(Math.abs(a[k]-b[k])<.1,selector+' '+k+' '+a[k]+' != '+b[k]);else assert.equal(b[k],a[k],selector+' '+k);}
};
const pages=[];
try{
 for(const [index,url] of ['http://127.0.0.1:5192','http://127.0.0.1:5191'].entries()){
  const page=await browser.newPage({viewport:{width:1920,height:1080}});pages.push(page);page.on('pageerror',e=>errors.push(e.message));
  await page.route('https://**/*',r=>r.abort());await seedTV(page);
  await page.addInitScript(()=>{const D=Date;window.Date=class extends D{constructor(...args){super(...(args.length?args:[1792849260000]));}static now(){return 1792849260000;}};});
  const painting=fs.readFileSync('app/public/wallpapers/default-0.jpg');
  await page.route('**/wallpapers/default-0.jpg',r=>r.fulfill({contentType:'image/jpeg',body:painting}));
  await page.goto(url);await page.waitForFunction(()=>document.querySelectorAll('.trial-row .tile').length>5);await page.waitForTimeout(1500);
  await page.screenshot({path:'.trial-evidence/match-'+index+'-home.png'});
 }
 for(const selector of ['.trial-rows','.trial-row .tile__box','.trial-row .tile__label','.trial-home .status','.trial-home .clock__time','.topbar .pill'])await compare(selector);
 checks.push('Home card, grid, clock and toolbar geometry/colors match accepted 0.3.13');
 for(const p of pages){await p.keyboard.press('ArrowDown');await p.waitForTimeout(500);}
 await compare('.trial-row .tile--focused .tile__box');checks.push('expanded grid matches accepted geometry');
 for(const p of pages){await p.keyboard.press('Escape');await p.locator('.topbar .pill').first().click();await p.waitForSelector('.input-card');}
 for(const selector of ['.panel--surface','.input-card','.surface__head','.input-card__name'])await compare(selector);
 checks.push('Inputs surface, corners, border highlights and cards match accepted design');
 for(const [i,p] of pages.entries()){await p.screenshot({path:'.trial-evidence/match-'+i+'-inputs.png'});await p.keyboard.press('Escape');await p.locator('.topbar .pill').nth(1).click();await p.waitForFunction(()=>document.querySelector('.cc__num').textContent==='22');await p.waitForTimeout(250);}
 for(const selector of ['.panel--surface','.cc__slider','.cc__fill','.cc__slidertext','.cc__audio','[data-control=sound]'])await compare(selector);
 checks.push('Control Center, volume pill, bright-left fill and focus styling match accepted design');
 for(const [i,p] of pages.entries()){await p.screenshot({path:'.trial-evidence/match-'+i+'-controls.png'});await p.locator('[data-control=photo]').click();await p.getByText('Start now',{exact:true}).click();await p.waitForSelector('.photo-frame__image');await p.waitForTimeout(2200);await p.screenshot({path:'.trial-evidence/match-'+i+'-photos.png'});}
 for(const selector of ['.photo-frame__clock','.photo-frame__clock .clock','.photo-frame__caption'])await compare(selector);
 checks.push('photo frame clock and caption match accepted design');
 assert.deepEqual(errors,[]);
}finally{fs.writeFileSync('.trial-evidence/match-results.json',JSON.stringify({checks,errors},null,2));console.log(JSON.stringify({checks,errors}));await browser.close();}
