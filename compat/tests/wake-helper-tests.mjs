import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';

const source=fs.readFileSync(new URL('../tv/on-power.sh',import.meta.url),'utf8');
const home='com.webos.app.home',trial='local.lumen.upstreamtrial';
const tests=[
 {name:'Home waits eight seconds and opens the new trial once',expected:1,minTime:608},
 {name:'accepted launcher upgrades on safe wake',front:'local.lumen.trial',expected:1},
 {name:'already in trial needs no launch',front:trial,expected:0},
 ...[1,2,3,4].map(n=>({name:`HDMI ${n} preserved at startup`,front:`com.webos.app.hdmi${n}`,expected:0})),
 {name:'AV input preserved',front:'com.webos.app.externalinput.av1',expected:0},
 {name:'other apps preserved',front:'netflix',expected:0},
 {name:'Home appears before HDMI during console wake',fronts:[home,home,'com.webos.app.hdmi3'],expected:0},
 {name:'CEC wake never opens launcher even over LG Home',reason:'hdmiCec',expected:0},
 {name:'any unknown wake reason fails closed',reason:'newReason',expected:0},
 {name:'wake reason read failure fails closed',reasonError:true,expected:0},
 {name:'foreground read failure never launches blindly',frontError:true,expected:0},
 {name:'foreground readiness restarts grace period',fronts:['','',home],expected:1,minTime:612},
 {name:'connected network wake uses same Home guard',reason:'wakeOnWiFi',expected:1},
 {name:'local power button uses same Home guard',reason:'localKey',expected:1},
 {name:'late HDMI switch cancels final check',lateFront:'com.webos.app.hdmi2',expected:0},
 {name:'late CEC reason cancels final check',lateReason:'hdmiCec',expected:0},
 {name:'standby then HDMI wake preserves game',states:['Active','Suspend','Suspend',...Array(10).fill('Active')],fronts:[trial,trial,trial,...Array(10).fill('com.webos.app.hdmi3')],expected:0},
 {name:'standby then Home wake opens once',states:['Active','Suspend','Suspend',...Array(10).fill('Active')],expected:1,minTime:614},
 {name:'long suspended gap preserves HDMI',advance:[45],front:'com.webos.app.hdmi3',expected:0},
 {name:'screensaver return never steals focus',states:['Active','Screen Saver','Active',...Array(10).fill('Active')],expected:0},
 {name:'screen off return never steals focus',states:['Active','Screen Off','Active',...Array(10).fill('Active')],expected:0},
 {name:'power error never acts as standby',states:['Active','error',...Array(12).fill('Active')],expected:1},
 {name:'launch failure retries are bounded at three',failLaunch:true,expected:3},
 {name:'API readiness window is bounded',frontError:true,count:30,expected:0},
 {name:'other foreground cancels whole wake even if Home returns',fronts:[home,'netflix',home],expected:0},
];
const results=[];
for(const test of tests){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'lumen-safe-wake-'));
 try {
  for(const sub of ['bin','app','base'])fs.mkdirSync(path.join(dir,sub));
  const data=path.join(dir,'state.json'),uptime=path.join(dir,'uptime');
  fs.writeFileSync(data,JSON.stringify({...test,index:0,uptime:600,launches:[],frontCalls:0,reasonCalls:0}));
  fs.writeFileSync(uptime,'600.00 0.00\n');
  const mock=`#!${process.execPath}
const fs=require('fs');const data=${JSON.stringify(data)},dir=${JSON.stringify(dir)};
const s=JSON.parse(fs.readFileSync(data));const last=(a,f)=>a? a[Math.min(s.index,a.length-1)]:f;
let out={returnValue:true};const cmd=process.argv.join(' ');
if(process.argv[1].endsWith('/sleep')){
 s.uptime+=(s.advance||[])[s.index]||2;s.index++;s.frontCalls=0;s.reasonCalls=0;
 fs.writeFileSync(dir+'/uptime',s.uptime+'.00 0.00\\n');
 if(s.index>=(s.states?.length||s.count||14))fs.rmdirSync(dir+'/app');
}else if(cmd.includes('getPowerState')){
 const state=last(s.states,'Active');out=state==='error'?{returnValue:false}:{returnValue:true,state};
}else if(cmd.includes('getForegroundAppInfo')){
 s.frontCalls++;out=s.frontError?{returnValue:false}:{returnValue:true,appId:s.frontCalls>1&&s.lateFront?s.lateFront:last(s.fronts,s.front||${JSON.stringify(home)})};
}else if(cmd.includes('getPowerOnReason')){
 s.reasonCalls++;out=s.reasonError?{returnValue:false}:{returnValue:true,reason:s.reasonCalls>1&&s.lateReason?s.lateReason:(s.reason||'remoteKey')};
}else if(cmd.includes('applicationManager/launch')){
 const payload=JSON.parse(process.argv.at(-1));if(payload.id!==${JSON.stringify(trial)})throw new Error('Wrong launch target');
 s.launches.push(s.uptime);out={returnValue:!s.failLaunch};
}else throw new Error('Unexpected command '+cmd);
fs.writeFileSync(data,JSON.stringify(s));console.log(JSON.stringify(out));
`;
  for(const name of ['luna-send','sleep'])fs.writeFileSync(path.join(dir,'bin',name),mock,{mode:0o755});
  const script=source.replace('PATH=/bin:/sbin:/usr/bin:/usr/sbin','PATH='+dir+'/bin:/bin:/sbin:/usr/bin:/usr/sbin')
   .replace('BASE=/var/lib/lumen-trial-launcher','BASE='+dir+'/base')
   .replace('APPDIR=/media/developer/apps/usr/palm/applications/$APP','APPDIR='+dir+'/app')
   .replace('LOCK=/tmp/lumen-trial-launcher.lock','LOCK='+dir+'/lock')
   .replace('/proc/uptime',uptime);
  const file=path.join(dir,'test.sh');fs.writeFileSync(file,script);
  const result=spawnSync('/bin/sh',[file],{encoding:'utf8',timeout:15000});
  assert.equal(result.status,0,result.stderr);
  const final=JSON.parse(fs.readFileSync(data));assert.equal(final.launches.length,test.expected,test.name+'\n'+result.stdout);
  if(test.minTime)assert(final.launches[0]>=test.minTime,test.name+' grace period');
  assert(!fs.existsSync(path.join(dir,'lock')),'PID lock must be cleaned up');
  results.push({name:test.name,passed:true,launches:final.launches.length});
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
}
console.log(JSON.stringify({passed:true,results},null,2));
