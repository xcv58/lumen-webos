import fs from 'node:fs';
export async function seedTV(page){
const seed=JSON.parse(fs.readFileSync(new URL('fixtures/preview-config.json',import.meta.url)));
const baseline=JSON.parse(fs.readFileSync(new URL('fixtures/webos5-controls.json',import.meta.url)));
 await page.addInitScript(({seed,baseline})=>{
  if(!localStorage.getItem('launcher-config-v2'))localStorage.setItem('launcher-config-v2',JSON.stringify({...seed,useHomebrew:false,showWeather:false,wallpaper:'local:0',idleMinutes:0}));
  window.tvFixture={volume:22,muted:false,picture:'normal',sound:'aiSound',sleepMinutes:0,audioDelay:0,failNext:false,freezeNextPicture:false,writes:[],inputs:baseline.inputs};
  window.PalmServiceBridge=class {
   cancel(){this.cancelled=true;}
   call(uri,json){
    this.cancelled=false;const p=JSON.parse(json),tv=window.tvFixture;let r={returnValue:true},delay=10;
    if(uri.endsWith('/getAppLoadStatus'))r.exist=true;
    else if(uri.endsWith('/getAllInputStatus'))r=tv.inputs;
    else if(uri.endsWith('/getVolume')){r={returnValue:true,volume:tv.volume,muteStatus:tv.muted};delay=tv.audioDelay;}
    else if(uri.endsWith('/setVolume')){tv.writes.push({field:'volume',value:p.volume});tv.volume=p.volume;tv.muted=false;}
    else if(uri.endsWith('/setMuted')){tv.muted=p.muted;tv.writes.push({field:'muted',value:p.muted});}
    else if(uri.endsWith('/getRemainTime'))r.sleepTimeSecond=tv.sleepMinutes*60;
    else if(uri.endsWith('/timer/sleep/add')){tv.sleepMinutes=p.sleepTimeMinute;tv.writes.push({field:'sleep',value:p.sleepTimeMinute});}
    else if(uri.endsWith('/getStatus'))r={returnValue:true,wifi:{state:'connected'}};
    else if(uri.includes('applicationManager/launch')){tv.writes.push({field:'launch',value:p.id});}
    else if(uri.endsWith('/exec')){
     const c=p.command||'';let inner={returnValue:true};
     const field=c.includes('pictureMode')?'picture':c.includes('soundMode')?'sound':null;
     if(c.includes('tvReservationAgent/timer/sleep/getRemainTime')){inner.sleepTimeMinute=tv.sleepMinutes?tv.sleepMinutes-1:0;inner.sleepTimeSecond=tv.sleepMinutes?58:0;}
     else if(c.includes('tvReservationAgent/timer/sleep/add')){const n=JSON.parse(c.match(/'([^']+)'$/)[1]).sleepTimeMinute;tv.sleepMinutes=n;tv.writes.push({field:'sleep',value:n});}
     else if(field&&c.includes('/getSystemSettingDesc'))inner.results=[{values:{arrayExt:(field==='picture'?['normal','cinema','hdrVivid','evil;command']:['standard','movie','aiSound']).map(value=>({value,active:true,visible:value!=='hdrVivid'}))}}];
     else if(field&&c.includes('/getSystemSettings')){inner.settings={[field+'Mode']:tv[field]};if(tv.freezeNextPicture&&field==='picture'){tv.freezeNextPicture=false;delay=1800;}}
     else if(field&&c.includes('/setSystemSettings')){
      const match=c.match(/'([^']+)'$/);const mode=JSON.parse(match[1]).settings[field+'Mode'];
      tv.writes.push({field,value:mode});
      if(tv.failNext){tv.failNext=false;inner={returnValue:false,errorText:'Fixture refusal'};}else tv[field]=mode;
     }else {inner={returnValue:false,errorText:'Not used by panel tests'};}
     r={returnValue:true,stdoutString:JSON.stringify(inner)};
    }else r={returnValue:false,errorText:'Unsupported test call'};
    if(tv.refuseReads&&(uri.endsWith('/getVolume')||uri.endsWith('/getRemainTime')||uri.endsWith('/exec')&&((p.command||'').includes('/getSystemSetting')||(p.command||'').includes('/sleep/getRemainTime'))))r=uri.endsWith('/exec')?{returnValue:true,stdoutString:JSON.stringify({returnValue:false,errorText:'Read unavailable'})}:{returnValue:false,errorText:'Read unavailable'};
    setTimeout(()=>{if(!this.cancelled&&this.onservicecallback)this.onservicecallback(JSON.stringify(r));},delay);
   }
  };
 },{seed,baseline});

}
