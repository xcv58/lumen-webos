"""Connect the accepted presentation to upstream state and keep upstream features."""
from pathlib import Path
import shutil
from webos5 import replace_once as sub


def apply(app: Path, root: Path) -> None:
    shutil.copytree(root / 'compat/ui', app / 'src/matched', dirs_exist_ok=True)
    shutil.copy2(root / 'compat/trial-idle-watch.sh', app / 'public/trial-idle-watch.sh')
    # Install the keyboard listener in the commit that reveals a new screen.
    # The browser regression exposed a first-Back race in upstream Control Center.
    keys = app / 'src/hooks/useKeys.ts'
    keys.write_text(keys.read_text().replace('useEffect', 'useLayoutEffect'))
    standby = app / 'src/components/StandBy.tsx'
    s = standby.read_text().replace('import {useEffect,', 'import {useEffect, useLayoutEffect,')
    s = sub(s, '\tuseEffect(() => {\n\t\tconst key = (e: KeyboardEvent)', '\tuseLayoutEffect(() => {\n\t\tconst key = (e: KeyboardEvent)')
    standby.write_text(s)
    path = app / 'src/lib/storage.ts'
    s = path.read_text()
    fields = '''
 acceptedUI: boolean;
 acceptedFrame: boolean;
 navigationSounds: 'off' | 'soft';
 recentMode: 'off' | 'other' | 'all';
 lastInput: string;
'''
    s = sub(s, 'export interface UserConfig {', 'export interface UserConfig {' + fields)
    s = sub(s, 'export const DEFAULT_CONFIG: UserConfig = {', "export const DEFAULT_CONFIG: UserConfig = {\n acceptedUI:true,acceptedFrame:true,navigationSounds:'off',recentMode:'off',lastInput:'',")
    s = sub(s, '\t\treturn {\n\t\t\tappIds:', "\t\treturn {\n acceptedUI:parsed.acceptedUI !== false,acceptedFrame:parsed.acceptedFrame !== false,\n navigationSounds:parsed.navigationSounds === 'soft' ? 'soft' : 'off',\n recentMode:parsed.recentMode === 'all' ? 'all' : parsed.recentMode === 'other' ? 'other' : 'off',\n lastInput:typeof parsed.lastInput === 'string' ? parsed.lastInput : '',\n\t\t\tappIds:")
    path.write_text(s)

    path = app / 'src/app.tsx'
    s = path.read_text()
    s = sub(s, 'useCallback, useEffect,', 'useCallback, useEffect, useLayoutEffect,')
    s = sub(s, "import {Home, type HomeRow}", "import {Home as UpstreamHome, type HomeRow}")
    s = sub(s, "import {ControlCenter, prefetchControls, type CenterAction}", "import {ControlCenter as UpstreamControlCenter, type CenterAction}")
    s = '''import {Home as MatchedHome} from './matched/screens/Home';
import {Layer} from './matched/components/Layer';
import {ControlCenter as MatchedControls} from './matched/components/ControlCenter';
import {InputsPanel} from './matched/components/InputsPanel';
import {PhotoFrame} from './matched/components/PhotoFrame';
import {useTrialIdle} from './matched/hooks/useTrialIdle';
import {isScenic, GRADIENTS, photoSource, refreshPhotos} from './matched/lib/photos';
import {setNavigationSoundMode,setNavigationSoundActive,stopNavigationSound} from './matched/lib/navigationSound';
import {setAcceptedBackdrop} from './lib/wallpaper';
import {readStatus} from './lib/status';
import './matched/theme/scoped.css';
''' + s
    s = sub(s, '\tconst [controls, setControls] = useState(false);', '''
 const [controls,setControls]=useState(false);
 const [upstreamControls,setUpstreamControls]=useState(false);
 const [inputsOpen,setInputsOpen]=useState(false),[inputsReturn,setInputsReturn]=useState(false);
 const [controlFocusInputs,setControlFocusInputs]=useState(false);
 const [photoFrame,setPhotoFrame]=useState(false),[network,setNetwork]=useState('');
 const Home=config.acceptedUI?MatchedHome:UpstreamHome;
 const navigationSoundMode=config.acceptedUI && !photoFrame ? config.navigationSounds:'off';
 useLayoutEffect(()=>{
  setNavigationSoundMode(navigationSoundMode);
  const hidden=()=>{if(document.hidden)stopNavigationSound();else setNavigationSoundMode(navigationSoundMode);};
  document.addEventListener('visibilitychange',hidden);
  return ()=>{setNavigationSoundMode('off');document.removeEventListener('visibilitychange',hidden);};
 },[navigationSoundMode]);
 const navigationActive=screen==='home'&&!photoFrame&&!(controls&&upstreamControls);
 useLayoutEffect(()=>{setNavigationSoundActive(navigationActive);return ()=>setNavigationSoundActive(false);},[navigationActive]);
 useEffect(()=>{let alive=true;readStatus().then(s=>{if(alive)setNetwork(s.network==='wifi'?'Wi-Fi':s.network==='ethernet'?'Ethernet':'');});return ()=>{alive=false;};},[]);
 useTrialIdle(config.acceptedFrame?config.idleMinutes:0,photoFrame,()=>{if(configRef.current.acceptedFrame)setPhotoFrame(true);},()=>setPhotoFrame(false));
''')
    # Hooks call callbacks later; configRef is initialized before those effects run.
    s = sub(s, '\tuseEffect(() => { setFavorites(config.favoriteWallpapers); setPicks(config.wallpaperPicks, config.wpNewOnLaunch); setWallpaper(config.wallpaper); }, [config.wallpaper, config.wallpaperPicks]);', '''
 useEffect(()=>setAcceptedBackdrop(config.acceptedUI),[config.acceptedUI]);
 useEffect(()=>{
  const apply=()=>{setFavorites(config.favoriteWallpapers);setPicks(config.wallpaperPicks,config.wpNewOnLaunch);setWallpaper(config.wallpaper,config.wpAutoMinutes);};
  apply();window.addEventListener('trial-photos-updated',apply);return ()=>window.removeEventListener('trial-photos-updated',apply);
 },[config.acceptedUI,config.wallpaper,config.wallpaperPicks,config.favoriteWallpapers,config.wpAutoMinutes]);
 useEffect(()=>{if(!isScenic(config.wallpaper))return;refreshPhotos(photoSource(config.wallpaper)).catch(()=>undefined);},[config.wallpaper]);
''')
    s = sub(s, "if (!config.idleMinutes || (config.videoWallpaper && !config.aerials))", "if (config.acceptedFrame || !config.idleMinutes || (config.videoWallpaper && !config.aerials))")
    s = sub(s, '\t}, [config.idleMinutes, config.videoWallpaper]);', '\t}, [config.acceptedFrame, config.idleMinutes, config.videoWallpaper, config.aerials, config.standBy, config.photoSaver]);')
    begin = s.index('\tconst rows: HomeRow[] = useMemo(')
    end = s.index('\n\tconst tabs: SettingsTab[]', begin)
    s = s[:begin] + '''
 const rows:HomeRow[]=useMemo(()=>{
  const count=config.acceptedUI?5:config.appsPerRow;
  const rows:HomeRow[]=[{id:ROW.apps,label:'Apps',items:homeTiles.slice(0,count),emptyText:'No apps selected — add some in Settings'}];
  if(config.acceptedUI){for(let i=count;i<homeTiles.length;i+=count)rows.push({id:ROW.dock+'-'+(i/count-1),label:'Apps',items:homeTiles.slice(i,i+count)});}
  else if(homeTiles.length>count)rows.push({id:ROW.dock,label:'More apps',items:homeTiles.slice(count)});
  const recent=recentApps.filter(a=>config.recentMode==='all'||config.appIds.indexOf(a.id)<0);
  if(config.acceptedUI?config.recentMode!=='off'&&recent.length>0:recentApps.length>0)rows.push({id:ROW.recent,label:'Recent',items:(config.acceptedUI?recent.slice(0,5):recentApps).map(appTile)});
  return rows;
 },[homeTiles,recentApps,config.acceptedUI,config.appsPerRow,config.recentMode,config.appIds]);
''' + s[end:]
    s = sub(s, 'const GROUP: Record<string, OptionGroup> = {', "const GROUP: Record<string, OptionGroup> = {\n 'accepted-ui':'appearance','navigation-sounds':'home','recent-mode':'home','advanced-controls':'system','photo-refresh':'wallpaper','app-switcher':'system',")
    # Additional option rows use upstream Settings and its normal choice pages.
    s = sub(s, "\t\tconst GROUP: Record<string, OptionGroup>", "\t\tconst GROUP: Record<string, OptionGroup>")
    s = sub(s, "\tconst optionBase: Omit<OptionItem, 'group' | 'choices' | 'choice'>[] = useMemo(() => [", "\tconst optionBase: Omit<OptionItem, 'group' | 'choices' | 'choice'>[] = useMemo(() => [\n {id:'accepted-ui',label:'Matched Home and panels',description:'Use the accepted five-column grid, rounded panels and volume pill. Turn off to compare upstream Home and Control Center.',value:config.acceptedUI},\n {id:'navigation-sounds',label:'Navigation sounds',description:'Immediate focus feedback on Home, Inputs and Control Center. Pointer and volume adjustments stay quiet.',value:config.navigationSounds==='soft',valueText:config.navigationSounds==='soft'?'Soft':'Off'},\n {id:'recent-mode',label:'Recent apps in grid',description:'Keep recent history while choosing which apps appear below Home.',value:config.recentMode!=='off',valueText:config.recentMode==='all'?'All recent':config.recentMode==='other'?'Not on Home':'Off'},\n {id:'advanced-controls',label:'More TV controls',description:'Upstream backlight, Eye Comfort, theme and TV controls.',value:false,valueText:'Open'},\n {id:'photo-refresh',label:'Refresh daily photos',description:'Refresh the bounded photo cache, retaining the last good offline collection.',value:false,valueText:'Refresh'},")
    s = sub(s, '], [config.weatherCountry, config.dockHide,', '], [config.acceptedUI,config.navigationSounds,config.recentMode,config.weatherCountry, config.dockHide,')
    s = sub(s, "{id:'advanced-controls',label:", "{id:'app-switcher',label:'App switcher',description:'Open upstream’s running-app switcher.',value:false,valueText:'Open'},\n {id:'advanced-controls',label:")
    s = sub(s, "if (id === OPTION.photoSaver) return {choices: ['Lumen Gallery or LG', 'Photos in Lumen', 'StandBy', 'Aerials'], choice: config.aerials ? 3 : config.standBy ? 2 : config.photoSaver ? 1 : 0};", "if (id === OPTION.photoSaver) return {choices: ['Lumen Gallery or LG', 'Photos in Lumen', 'StandBy', 'Aerials','Matched photo frame'], choice: config.acceptedFrame ? 4 : config.aerials ? 3 : config.standBy ? 2 : config.photoSaver ? 1 : 0};")
    # Existing memo dependencies must track the added screen and option values.
    s = sub(s, '}, [optionBase, config.weatherCountry,', '}, [optionBase, config.acceptedFrame,config.weatherCountry,')
    s = sub(s, ".filter((o) => [OPTION.clockX, OPTION.clockY, OPTION.pcX, OPTION.pcY].indexOf(o.id as never) < 0)", ".filter((o) => [OPTION.clockX, OPTION.clockY, OPTION.pcX, OPTION.pcY].indexOf(o.id as never) < 0 && (!config.acceptedUI || [OPTION.appsPerRow,OPTION.clockStyle,OPTION.clockColor,OPTION.clockSize,OPTION.clockLayout,OPTION.clockOrder,OPTION.clockLook,OPTION.clockWeight,OPTION.clockPos,OPTION.showDate,OPTION.focusStrength,OPTION.liquidDock,OPTION.liveGlass,OPTION.dockBlur].indexOf(o.id as never)<0))")
    s = sub(s, "if (item.key === 'screensaver') {", "if (item.key === 'screensaver') { if(configRef.current.acceptedFrame){setControls(false);setInputsOpen(false);setScreen('home');setPhotoFrame(true);return;}")
    s = sub(s, "if (item.key === 'controls') { setControls(true); return; }", "if (item.key === 'inputs' && configRef.current.acceptedUI){setInputsReturn(false);setInputsOpen(true);return;}\n\t\tif (item.key === 'controls') {setControlFocusInputs(false);setUpstreamControls(false);setControls(true);return;}")
    s = sub(s, 'if (_rowId === ROW.apps || _rowId === ROW.dock ||', "if (_rowId === ROW.apps || _rowId.indexOf(ROW.dock) === 0 ||")
    s = sub(s, "\t\telse if (optionId === OPTION.photoStart) setScreen(config.aerials ? 'aerials' : config.standBy ? 'standby' : 'photos');", "\t\telse if (optionId === OPTION.photoStart){if(config.acceptedFrame){setScreen('home');setPhotoFrame(true);}else setScreen(config.aerials?'aerials':config.standBy?'standby':'photos');}")
    s = sub(s, "else if (optionId === OPTION.photoSaver) updateConfig({...config, photoSaver: index === 1, standBy: index === 2, aerials: index === 3});", "else if (optionId === OPTION.photoSaver) updateConfig({...config,acceptedFrame:index===4,photoSaver:index===1,standBy:index===2,aerials:index===3});")
    anchor="\t\telse if (optionId === OPTION.showRecents)"
    s = sub(s, anchor, "\t\telse if(optionId==='accepted-ui')updateConfig({...config,acceptedUI:!config.acceptedUI});\n\t\telse if(optionId==='navigation-sounds')updateConfig({...config,navigationSounds:config.navigationSounds==='soft'?'off':'soft'});\n\t\telse if(optionId==='recent-mode')updateConfig({...config,recentMode:config.recentMode==='off'?'other':config.recentMode==='other'?'all':'off'});\n\t\telse if(optionId==='advanced-controls'){setScreen('home');setUpstreamControls(true);setControls(true);}\n\t\telse if(optionId==='photo-refresh')refreshPhotos(photoSource(config.wallpaper),true).then(()=>showToast('Photo collection updated')).catch(()=>showToast('Could not refresh photos','error'));\n"+anchor)
    s = sub(s, "else if(optionId==='advanced-controls'){", "else if(optionId==='app-switcher'){runningApps().then(ids=>setRunning(ids.sort())).catch(()=>undefined);setScreen('switcher');}\n\t\telse if(optionId==='advanced-controls'){")
    # Make daily photos and gradients regular entries in upstream's wallpaper picker.
    anchor='\t\t\tonPick: (key: string) =>'
    s = sub(s, anchor, anchor)  # Guard the insertion point against upstream drift.
    s = sub(s, "const entries: WallpaperEntry[] = [];", "const entries: WallpaperEntry[] = [{key:'tigris:daily',title:'Daily scenic photos',category:'Tigris'},{key:'tigris:anime',title:'Anime · SFW',category:'Tigris'},...Object.keys(GRADIENTS).map(name=>({key:'gradient:'+name,title:name.charAt(0).toUpperCase()+name.slice(1),category:'Tigris',tint:GRADIENTS[name]}))];")
    s = sub(s, "['Defaults', 'Favorites'].concat(WALLPAPER_CATEGORIES, 'All')", "['Defaults','Tigris','Favorites'].concat(WALLPAPER_CATEGORIES,'All')")
    s = sub(s, '<Home rows={rows}', '<Layer><Home rows={rows}')
    s = sub(s, "active={screen === 'home' && !controls}", "active={screen === 'home' && !controls && !inputsOpen && !photoFrame}")
    s = sub(s, 'perRow={config.appsPerRow} />', 'perRow={config.appsPerRow} /></Layer>')
    s = sub(s, '{controls && <ControlCenter', '{controls && (!config.acceptedUI || upstreamControls) && <UpstreamControlCenter')
    anchor='\t\t\t<Toast message={toast} />'
    s = sub(s, anchor, '''
 {controls && config.acceptedUI && !upstreamControls && <Layer><MatchedControls
  idleMinutes={config.idleMinutes} inputCount={shownInputs.length} network={network} focusInputs={controlFocusInputs}
  onIdleMinutes={minutes=>updateConfig({...configRef.current,idleMinutes:minutes})}
  onClose={()=>setControls(false)} onError={text=>showToast(text,'error')}
  onAction={action=>{setControls(false);if(action==='inputs'){setInputsReturn(true);setInputsOpen(true);return;}onActivate('menu',{key:action==='settings'?MISC.settings:action==='lg-home'?MISC.lgHome:'screensaver',label:action});}}
 /></Layer>}
 {inputsOpen && <Layer><InputsPanel inputs={shownInputs} sourceIds={config.sourceIds} lastInput={config.lastInput}
  onLastInput={id=>updateConfig({...configRef.current,lastInput:id})}
  onClose={()=>{setInputsOpen(false);if(inputsReturn){setControlFocusInputs(true);setControls(true);}}}
  onError={text=>showToast(text,'error')}/></Layer>}
 {photoFrame && <Layer><PhotoFrame selection={config.wallpaper} favorites={config.favoriteWallpapers} seconds={config.photoSeconds} showPeriod={config.showAmPm} onClose={()=>setPhotoFrame(false)}/></Layer>}
''' + anchor)
    # Non-matched upstream Home should not inherit accepted styling or tokens.
    s = s.replace('<Layer><Home rows={rows}', '<Layer enabled={config.acceptedUI}><Home rows={rows}')
    path.write_text(s)

    path = app / 'src/lib/wallpaper.ts'
    s = path.read_text()
    s = "import {bakeBackdrop} from '../matched/lib/glass';\nimport {currentPhoto,isScenic,GRADIENTS} from '../matched/lib/photos';\nlet acceptedBackdrop=true;\nexport function setAcceptedBackdrop(enabled:boolean):void {acceptedBackdrop=enabled;}\n" + s
    s = sub(s, "if (sel === 'picks') sel = choosePick();", "if (sel.indexOf('photo:')===0)return [sel.slice(6)].concat(fallback);\n\tif (sel === 'picks') sel = choosePick();")
    s = sub(s, 'function setBlur (shown: string | null): void {', '''function setBlur (shown: string | null): void {
 if(acceptedBackdrop && shown){
  const mine=token,image=new Image();image.onload=()=>{if(mine!==token)return;try{const b=bakeBackdrop(image);if(mine!==token)return;const style=document.documentElement.style;style.setProperty('--wp-blur',`url("${b.blur}")`);style.setProperty('--wp-bg',`url("${b.blur}")`);style.setProperty('--dock-glass',`url("${b.dock}")`);}catch{setLegacyBlur(shown);}};image.src=shown;return;
 }
 document.documentElement.style.removeProperty('--dock-glass');setLegacyBlur(shown);
}
function setLegacyBlur(shown:string|null):void {''')
    s = sub(s, 'export function setWallpaper (sel: string): void {', '''export function setWallpaper (sel: string, minutes=30): void {
 document.documentElement.classList.toggle('scenic',isScenic(sel)||sel.indexOf('gradient:')===0);
 if(sel.indexOf('gradient:')===0){++token;shown=null;shownCss='';shownCopies=null;released=false;const gradient=GRADIENTS[sel.slice(9)]||GRADIENTS.green;ensureElement().style.backgroundImage=gradient;document.documentElement.classList.add(HTML_CLASS);const style=document.documentElement.style;style.setProperty('--wp-blur',gradient);style.setProperty('--wp-bg',gradient);style.removeProperty('--dock-glass');return;}
 if(isScenic(sel)){const photo=currentPhoto(sel,minutes);sel=photo?'photo:'+photo.url:'local:0';}
''')
    path.write_text(s)

    # Add input naming/status improvements while retaining upstream's adapter contracts.
    source = (root / 'compat/input-status.ts').read_text()
    (app / 'src/lib/inputs.ts').write_text(source)
