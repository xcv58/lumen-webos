import fs from 'node:fs';
import {chromium} from 'playwright';
export async function openBrowser(){fs.mkdirSync('.trial-evidence',{recursive:true});return chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});}
export async function seedPreview(page){
 const seed=JSON.parse(fs.readFileSync(new URL('fixtures/preview-config.json',import.meta.url)));
 Object.assign(seed,{onboarded:true,acceptedUI:true,acceptedFrame:true});
 await page.addInitScript(seed=>{if(!localStorage.getItem('launcher-config-v2'))localStorage.setItem('launcher-config-v2',JSON.stringify(seed));},seed);
 await page.route('https://**/*',r=>r.abort());
}
