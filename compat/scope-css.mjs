import fs from 'node:fs';
import postcss from '../app/node_modules/postcss/lib/postcss.mjs';
const base=new URL('ui/theme/',import.meta.url);
const root=postcss.parse(fs.readFileSync(new URL('global.css',base),'utf8')+'\n'+fs.readFileSync(new URL('trial.css',base),'utf8'));
root.walkAtRules('font-face',r=>r.remove()); // Use the existing upstream font asset.
root.walkRules(rule=>{
 if(rule.parent.type==='atrule' && /keyframes/.test(rule.parent.name))return;
 const selectors=postcss.list.comma(rule.selector).flatMap(selector=>{
  if(['html','body','#root'].includes(selector.trim()))return [];
  if(/#wpimage|#bgvideo/.test(selector))return [selector];
  const html=/^(html\S*)\s+(.+)$/.exec(selector);
  return [html?html[1]+' .matched-ui '+html[2]:'.matched-ui '+selector];
 });
 if(!selectors.length)rule.remove();else rule.selector=selectors.join(',');
});
root.append('.matched-ui {position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;} .matched-ui > * {pointer-events:auto;}');
fs.writeFileSync(new URL('../app/src/matched/theme/scoped.css',import.meta.url),root.toString());
