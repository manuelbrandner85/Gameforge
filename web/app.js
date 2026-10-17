'use strict';
/* GAMEFORGE 2.0 – Oberfläche. Alle angezeigten Daten stammen aus dem lokalen Backend (REST). */

// ------------------------------------------------------------------ Grundlagen
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const short=(s,n=160)=>{s=String(s||'');return s.length>n?s.slice(0,n-1)+'…':s};
const size=n=>n>1024**3?(n/1024**3).toFixed(2)+' GB':n>1024**2?(n/1024**2).toFixed(1)+' MB':(n/1024).toFixed(1)+' KB';
const when=s=>{if(!s)return '–';const d=new Date(s);return isNaN(d)?String(s).slice(0,16).replace('T',' '):d.toLocaleString('de-DE',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'})};
const day=s=>{if(!s)return '–';const d=new Date(s);return isNaN(d)?String(s).slice(0,10):d.toLocaleDateString('de-DE')};
const enc=encodeURIComponent;
const local={get(k,d){try{const v=localStorage.getItem('gf.'+k);return v===null?d:v}catch{return d}},set(k,v){try{localStorage.setItem('gf.'+k,v)}catch{}}};

const ICONS={
 home:'<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9.5 21v-6h5v6"/>',
 games:'<rect x="2" y="7" width="20" height="12" rx="4"/><path d="M7 11v4M5 13h4"/><circle cx="16" cy="12" r=".8"/><circle cx="18" cy="14.5" r=".8"/>',
 studio:'<path d="M12 3l1.9 4.6 4.6 1.9-4.6 1.9L12 16l-1.9-4.6L5.5 9.5l4.6-1.9z"/><path d="M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"/>',
 production:'<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
 archive:'<rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 9v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9"/><path d="M10 13h4"/>',
 chat:'<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-5.1A8 8 0 1 1 21 12z"/>',
 plus:'<path d="M12 5v14M5 12h14"/>',download:'<path d="M12 4v11"/><path d="m7 10 5 5 5-5"/><path d="M5 20h14"/>',
 upload:'<path d="M12 20V9"/><path d="m7 14 5-5 5 5"/><path d="M5 4h14"/>',check:'<path d="m5 12.5 4.5 4.5L19 7.5"/>',
 x:'<path d="M6 6l12 12M18 6 6 18"/>',alert:'<path d="M12 3.5 2.5 20h19z"/><path d="M12 10v4.5M12 17.2h.01"/>',
 refresh:'<path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 5v6h-6"/>',play:'<path d="M7 4.5v15l12-7.5z"/>',
 folder:'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
 users:'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.2a6.5 6.5 0 0 1 3.5 5.8"/>',
 cube:'<path d="M12 2.5 21 7v10l-9 4.5L3 17V7z"/><path d="M3 7l9 4.5L21 7M12 11.5v10"/>',send:'<path d="M4 12 20 4l-4 16-4-7z"/><path d="m12 13 8-9"/>',
 book:'<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11"/>',
 image:'<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 16-5-5-9 9"/>',
 shield:'<path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6z"/>',clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',moon:'<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
 sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 layers:'<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',arrow:'<path d="M5 12h14M13 6l6 6-6 6"/>',
 copy:'<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
 save:'<path d="M5 3h11l3 3v15H5z"/><path d="M8 3v5h7"/><rect x="8" y="13" width="8" height="6"/>',
 terminal:'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3M13 15h4"/>',
 map:'<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
 tasks:'<path d="M10 6h10M10 12h10M10 18h10"/><path d="m3.5 6 1.5 1.5L7.5 5M3.5 12l1.5 1.5 2.5-2.5M3.5 18l1.5 1.5 2.5-2.5"/>',
 info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',edit:'<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
 activity:'<path d="M3 12h4l3-8 4 16 3-8h4"/>',scan:'<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path d="M7 12h10"/>'
};
const icon=(n,cls='')=>`<svg class="ico ${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[n]||''}</svg>`;
const btn=(label,act,cls='',data='',ic='')=>`<button type="button" class="btn ${cls}" data-act="${act}" ${data}>${ic?icon(ic):''}${label}</button>`;
const badge=(text,kind='')=>`<span class="badge ${kind}">${esc(text)}</span>`;
const note=(html,kind='info',ic='info')=>`<div class="note ${kind}">${icon(ic)}<div>${html}</div></div>`;
const empty=(title,text,action='')=>`<div class="empty">${icon('info')}<b>${esc(title)}</b><span>${esc(text)}</span>${action?'<div>'+action+'</div>':''}</div>`;
const loading=(t='Wird geladen …')=>`<div class="loading"><span class="spinner"></span>${esc(t)}</div>`;

const AREAS=[
 {id:'home',label:'Startseite',icon:'home'},
 {id:'games',label:'Meine Spiele',icon:'games'},
 {id:'studio',label:'Kreativstudio',icon:'studio'},
 {id:'production',label:'Produktion',icon:'production'},
 {id:'archive',label:'Archiv',icon:'archive'}];
const TABS={
 games:[['list','Bibliothek','games'],['overview','Projektübersicht','info'],['dlcs','DLCs','layers'],['versions','Versionen','clock']],
 studio:[['ideas','Ideen & Entscheidungen','studio'],['bible','Spielbibel','book'],['refs','Referenzbilder','image']],
 production:[['overview','Überblick','production'],['pipeline','Blender → Unreal','cube'],['agents','Agenten-Team','users'],['live','Live-Monitor','activity'],['direct','Direkt-Studio','terminal'],['tasks','Aufgaben A–Z','tasks'],['roadmap','Ausbauplan','map']],
 archive:[['downloads','Downloads','download'],['files','Originaldateien','folder'],['zips','Projekt-ZIPs','archive'],['scan','Prüfung','scan'],['backup','Sicherung','shield']]};
const STATUS_KIND={'Idee':'','Konzept':'info','In Entwicklung':'accent','Testphase':'warn','Fertig':'ok','Veröffentlicht':'ok'};
const DLC_LABELS={story:'Story & Kanon',prologue:'DLC-Prolog',quests:'DLC-Missionen',new_characters:'Neue Charaktere',new_world:'Zusätzliche Welt / Regionen',new_assets:'Neue 3D-Assets / Referenzen',gameplay:'Gameplay / Fähigkeiten',cinematics:'Zwischensequenzen',menu:'UI / Hauptmenü-Anbindung',integration:'Integration, Savegames & Kompatibilität',qa:'DLC-Tests & Abnahmekriterien',release:'DLC-Packaging & Veröffentlichung'};
const BIBLE_GROUPS=[['Idee & Story',['vision','game_rules','canon','story','prologue','chapters','sidequests','dialogue','endings']],['Figuren & Welt',['characters','bosses','npcs','world','environments']],['Gameplay',['combat','movement','physics','ai','items','progression']],['Präsentation & Bedienung',['ui','cinematics','audio','save_load','accessibility','localization']],['Technik & Veröffentlichung',['performance','technical','qa','release','legal']]];
const JOB_LABEL={plan:'Planung (nur lesen)',implement:'Umsetzung durch Claude',build:'Windows-Spielversion erstellen',blender_test:'Blender-Echttest'};
const AGENT_STATE_KIND={'Arbeitet':'accent live','Abgeschlossen':'ok','Fehler':'err','Wartet':'','Unbekannt':'warn','Keine Verbindung':''};

const S={config:null,games:[],home:null,health:null,area:'home',tab:{},gameId:local.get('game',''),dlcId:'',detail:null,
  mode:local.get('mode','simple'),filter:{q:'',status:'all'},timers:[],
  chat:{open:false,provider:local.get('chatProvider','claude'),busy:false,draft:{},ai:null}};

// ------------------------------------------------------------------ API
async function api(url,opt={}){
  const req={...opt};
  if(req.body!==undefined&&!(req.body instanceof Blob)){req.headers={'Content-Type':'application/json',...(req.headers||{})};req.body=JSON.stringify(req.body)}
  let res;
  try{res=await fetch(url,req)}catch(e){throw Error('GAMEFORGE-Server nicht erreichbar. Läuft das Startfenster noch?')}
  const type=res.headers.get('Content-Type')||'';
  if(!res.ok){let m='Serverfehler ('+res.status+')';try{m=(await res.json()).error||m}catch{};throw Error(m)}
  return type.includes('json')?res.json():res.text();
}
const G=()=>'/api/games/'+enc(S.gameId);
function download(url){const a=document.createElement('a');a.href=url;a.rel='noopener';document.body.appendChild(a);a.click();a.remove();toast('Download gestartet. Er erscheint im Download-Ordner deines Browsers.')}
function upload(url,file,onProgress){
  return new Promise((resolve,reject)=>{const x=new XMLHttpRequest();x.open('POST',url);
    x.upload.onprogress=e=>{if(e.lengthComputable&&onProgress)onProgress(e.loaded/e.total)};
    x.onload=()=>{let d={};try{d=JSON.parse(x.responseText)}catch{};x.status<300?resolve(d):reject(Error(d.error||'Upload fehlgeschlagen'))};
    x.onerror=()=>reject(Error('Verbindung zum GAMEFORGE-Server unterbrochen'));x.send(file)});
}
let toastTimer;
function toast(msg,isErr=false){const t=$('toast');t.innerHTML=icon(isErr?'alert':'check')+'<span>'+esc(msg)+'</span>';t.className='toast'+(isErr?' err':'');t.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.hidden=true,isErr?8000:4500)}

// ------------------------------------------------------------------ Dialoge
let lastFocus=null;
function modal({title,body,actions=[],wide=false,onOpen}){
  lastFocus=document.activeElement;
  $('dialog-title').textContent=title;$('dialog-body').innerHTML=body;
  document.querySelector('#dialog .modal').classList.toggle('wide',wide);
  const foot=$('dialog-foot');foot.innerHTML='';
  actions.forEach(a=>{const b=document.createElement('button');b.type='button';b.className='btn '+(a.primary?'primary':a.danger?'danger':'quiet');b.innerHTML=a.label;
    b.onclick=async()=>{if(!a.onClick){closeModal();return}b.disabled=true;try{const keep=await a.onClick();if(keep!==false)closeModal()}catch(e){toast(e.message,true)}finally{b.disabled=false}};foot.appendChild(b)});
  $('dialog').hidden=false;
  if(onOpen)onOpen();
  setTimeout(()=>{(document.querySelector('#dialog-body input,#dialog-body textarea,#dialog-body select')||foot.querySelector('.primary')||$('close-dialog')).focus()},30);
}
function closeModal(){$('dialog').hidden=true;if(lastFocus&&lastFocus.focus)lastFocus.focus()}
function ask(title,text,okLabel='Bestätigen',danger=false){return new Promise(resolve=>{modal({title,body:`<p class="help" style="font-size:15px;color:var(--text-2)">${text}</p>`,
  actions:[{label:'Abbrechen',onClick:()=>{resolve(false)}},{label:okLabel,primary:!danger,danger,onClick:()=>{resolve(true)}}]});
  $('close-dialog').onclick=()=>{closeModal();resolve(false)}})}
const field=(id,label,value='',opt={})=>`<div class="field"><label for="${id}">${esc(label)}</label>${opt.area?`<textarea id="${id}" ${opt.rows?`style="min-height:${opt.rows}px"`:''} placeholder="${esc(opt.ph||'')}">${esc(value)}</textarea>`:`<input id="${id}" type="${opt.type||'text'}" value="${esc(value)}" placeholder="${esc(opt.ph||'')}">`}${opt.help?`<small>${esc(opt.help)}</small>`:''}</div>`;
const selectField=(id,label,options,current,help='')=>`<div class="field"><label for="${id}">${esc(label)}</label><select id="${id}">${options.map(o=>{const [v,l]=Array.isArray(o)?o:[o,o];return `<option value="${esc(v)}" ${String(v)===String(current)?'selected':''}>${esc(l)}</option>`}).join('')}</select>${help?`<small>${esc(help)}</small>`:''}</div>`;
const val=id=>($(id)?.value??'').trim();

// ------------------------------------------------------------------ Navigation
function go(area,tab){location.hash='#/'+area+(tab?'/'+tab:'')}
function parseHash(){const [,area='home',tab='']=(location.hash||'#/home').split('/');S.area=AREAS.some(a=>a.id===area)?area:'home';if(tab)S.tab[S.area]=tab}
window.addEventListener('hashchange',()=>{parseHash();render()});
function clearTimers(){S.timers.forEach(clearInterval);S.timers=[]}
function renderNav(){
  $('nav').innerHTML=AREAS.map(a=>`<button type="button" class="nav" data-area="${a.id}" ${S.area===a.id?'aria-current="page"':''}>${icon(a.icon)}${a.label}</button>`).join('');
  const g=currentGame();
  const area=AREAS.find(a=>a.id===S.area);
  $('crumb').innerHTML=`${icon(area.icon,'sm')}<b>${esc(area.label)}</b>`;
  const showCtx=S.area!=='home'&&!(S.area==='games'&&(S.tab.games||'list')==='list');
  $('context').style.visibility=S.games.length?'visible':'hidden';
  $('ctx-game').innerHTML=(S.games.length?'':'<option value="">Kein Projekt</option>')+S.games.map(x=>`<option value="${esc(x.id)}" ${x.id===S.gameId?'selected':''}>${esc(x.title)}</option>`).join('');
  const dlcs=S.detail?.dlcs||[];
  $('ctx-dlc').innerHTML=`<option value="">Basisspiel</option>`+dlcs.map(d=>`<option value="${esc(d.id)}" ${d.id===S.dlcId?'selected':''}>DLC: ${esc(d.title)}</option>`).join('');
  $('ctx-dlc').hidden=!g;
  $('context').dataset.dim=showCtx?'':'1';
}
const currentGame=()=>S.games.find(g=>g.id===S.gameId)||null;
const currentDlc=()=>(S.detail?.dlcs||[]).find(d=>d.id===S.dlcId)||null;
async function selectGame(id,{keepDlc=false}={}){
  if(!id)return;
  if(id!==S.gameId&&!keepDlc)S.dlcId='';
  S.gameId=id;local.set('game',id);
  await loadDetail();
}
async function loadDetail(){if(!S.gameId){S.detail=null;return}try{S.detail=await api(G())}catch(e){S.detail=null;toast(e.message,true)}
  if(S.dlcId&&!(S.detail?.dlcs||[]).some(d=>d.id===S.dlcId))S.dlcId=''}
async function refreshAll(){S.games=await api('/api/games');if(S.gameId&&!S.games.some(g=>g.id===S.gameId))S.gameId='';if(!S.gameId&&S.games[0])S.gameId=S.games[0].id;await loadDetail()}

function setMode(mode){S.mode=mode;local.set('mode',mode);document.body.classList.toggle('pro',mode==='pro');
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mode===mode)));
  $('mode-hint').textContent=mode==='pro'?'Profi-Modus: MCP-Details, Logs, Agentenrechte und Buildparameter sind sichtbar.':'Einfach-Modus: Technische Details sind ausgeblendet. Es geht nichts verloren.'}
function setTheme(t){document.documentElement.dataset.theme=t;local.set('theme',t);$('theme-toggle').innerHTML=t==='light'?icon('moon','sm')+'Dunkles Design':icon('sun','sm')+'Helles Design'}

// ------------------------------------------------------------------ Rendering
let lastView='';
async function render(){
  clearTimers();renderNav();
  const key=S.area+'/'+(S.tab[S.area]||'');if(key!==lastView){window.scrollTo(0,0);lastView=key}
  const view=$('view');view.classList.remove('view-enter');void view.offsetWidth;view.classList.add('view-enter');
  try{
    if(S.area==='home')await renderHome();
    else if(S.area==='games')await renderGames();
    else if(!S.gameId||!S.detail)view.innerHTML=needProject();
    else if(S.area==='studio')await renderStudio();
    else if(S.area==='production')await renderProduction();
    else if(S.area==='archive')await renderArchive();
  }catch(e){view.innerHTML=note('Diese Ansicht konnte nicht geladen werden: '+esc(e.message),'err','alert')}
  renderNav();
}
const needProject=()=>`<div class="page-head"><div><p class="kicker">Projekt wählen</p><h1>Für welches Spiel?</h1><p class="lead">Wähle oben ein Projekt oder lege ein neues Spiel an.</p></div></div>${empty('Noch kein Projekt ausgewählt','Projekte findest du unter „Meine Spiele“.',btn('Neues Spiel erstellen','new-game','primary','','plus')+' '+btn('Zu meinen Spielen','goto','','data-area="games"','games'))}`;
function tabs(area,extra={}){const cur=S.tab[area]||TABS[area][0][0];return `<div class="tabs" role="tablist">${TABS[area].map(([id,label,ic])=>`<button type="button" role="tab" class="tab" aria-selected="${cur===id}" data-tab="${area}/${id}">${icon(ic,'sm')}${label}${extra[id]!==undefined?`<span class="count">${extra[id]}</span>`:''}</button>`).join('')}</div>`}
function head(kicker,title,lead,actions=''){return `<div class="page-head"><div><p class="kicker">${kicker}</p><h1>${title}</h1>${lead?`<p class="lead">${lead}</p>`:''}</div>${actions?`<div class="page-actions">${actions}</div>`:''}</div>`}
const ctxLabel=()=>{const g=currentGame(),d=currentDlc();return g?esc(g.title)+(d?' · DLC '+esc(d.title):' · Basisspiel'):'kein Projekt'};

// ---------- Startseite
async function renderHome(){
  const view=$('view');
  if(!S.home)view.innerHTML=loading('Projektstände werden gelesen …');
  S.home=await api('/api/home');
  const h=new Date().getHours(),greet=h<11?'Guten Morgen':h<18?'Guten Tag':'Guten Abend';
  const games=S.home.games,aion=games.find(g=>g.id==='aion-2026'),gen=games.find(g=>g.id==='genesis');
  const last=games[0];
  view.innerHTML=`<section class="hero">
    <p class="kicker">${greet}</p><h1>Was möchtest du heute erschaffen?</h1>
    <p class="lead">Beschreibe deine Idee in normaler Sprache. GAMEFORGE plant mit dir, verteilt die Arbeit an dein 20-köpfiges KI-Team und zeigt dir ehrlich, was wirklich fertig ist.</p>
    <div class="hero-actions">${last?btn('Weiter an '+esc(last.title)+' arbeiten','open-game','primary lg',`data-id="${esc(last.id)}"`,'arrow'):''}
      ${gen&&gen.id!==last?.id?btn('GENESIS öffnen','open-game','lg',`data-id="genesis"`,'games'):''}${aion&&aion.id!==last?.id?btn('AION 2026 öffnen','open-game','lg',`data-id="aion-2026"`,'games'):''}
      ${btn('Mit GAMEFORGE sprechen','chat-open','quiet lg','','chat')}</div>
    <div class="start-grid">
      <button type="button" class="start-tile" data-act="new-game"><span class="ico-wrap">${icon('plus')}</span><span><b>Neues Spiel</b><span>In vier kurzen Schritten von der Idee zum Projekt.</span></span></button>
      <button type="button" class="start-tile" data-act="import-game"><span class="ico-wrap">${icon('upload')}</span><span><b>Vorhandenes Spiel importieren</b><span>Ordner, Unreal-/Blender-Dateien oder ZIP sicher einlagern.</span></span></button>
      <button type="button" class="start-tile" data-act="goto" data-area="games" data-tab="list"><span class="ico-wrap">${icon('games')}</span><span><b>AION / GENESIS öffnen</b><span>Deine Spielebibliothek mit allen Versionen und DLCs.</span></span></button>
    </div></section>
  <div class="section"><div class="section-title"><h2>Deine Projekte – echter Stand</h2><span class="tiny">Zahlen direkt aus der Projektdatenbank</span></div>
  <div class="grid g2">${games.map(projectStatusCard).join('')||empty('Noch keine Projekte','Lege dein erstes Spiel an.',btn('Neues Spiel','new-game','primary','','plus'))}</div></div>
  <div class="section grid g2"><div class="card" id="home-health">${healthHtml(S.health)}</div>
  <div class="card"><div class="card-head"><div><h2>Gut zu wissen</h2><p class="help">Damit nichts schiefgeht.</p></div></div><div class="stack">
    ${note('Ideen aus dem Chat landen erst nach deiner Freigabe in der Spielbibel. Vorher sichert GAMEFORGE automatisch einen Versionsstand.','info','shield')}
    ${note('Referenzbilder erstellst du in ChatGPT. GAMEFORGE liefert dir dafür kopierfertige Prompts – ganz ohne OpenAI-API.','info','image')}
    ${note('Daten-Ordner: <span class="mono">'+esc(S.home.data_dir)+'</span>','info','folder')}</div></div></div>`;
  if(!S.health)loadHealth();
}
function projectStatusCard(g){
  const refPct=g.reference_total?Math.round((g.reference_total-g.reference_open)/g.reference_total*100):0;
  const taskPct=g.tasks_total?Math.round(g.tasks_approved/g.tasks_total*100):0;
  return `<div class="card"><div class="card-head"><div><h2>${esc(g.title)}</h2><p class="tiny">${esc(g.version)} · zuletzt geändert ${day(g.updated_at)}${g.dlc_count?' · '+g.dlc_count+' DLC':''}</p></div>${badge(g.status,STATUS_KIND[g.status])}</div>
   <div class="grid g3" style="gap:10px">
    <div class="metric"><small>Spielbibel</small><strong>${14-g.sections_missing}/14</strong><span>Pflichtbereiche gefüllt</span><div class="bar"><i style="width:${(14-g.sections_missing)/14*100}%"></i></div></div>
    <div class="metric"><small>Referenzbilder</small><strong>${g.reference_total-g.reference_open}/${g.reference_total}</strong><span>freigegeben</span><div class="bar"><i style="width:${refPct}%"></i></div></div>
    <div class="metric"><small>Entwicklung</small><strong>${g.tasks_approved}/${g.tasks_total}</strong><span>Aufgaben abgenommen</span><div class="bar"><i style="width:${taskPct}%"></i></div></div></div>
   <p class="label" style="margin-top:18px">Was jetzt sinnvoll ist</p><div class="stack">${g.next_steps.map((s,i)=>`<button type="button" class="next-step" data-act="next-step" data-id="${esc(g.id)}" data-area="${s.area}" data-tab="${s.tab}"><span class="num">${i+1}</span>${esc(s.text)}${icon('arrow','sm')}</button>`).join('')}</div>
   <div class="btn-row" style="margin-top:14px">${btn('Projekt öffnen','open-game','sm','data-id="'+esc(g.id)+'"','arrow')}${btn('Idee besprechen','chat-for','sm quiet','data-id="'+esc(g.id)+'"','chat')}</div></div>`;
}
async function loadHealth(refresh=false){
  const pill=$('sys-pill');pill.innerHTML='<span class="spinner" style="width:12px;height:12px"></span> System wird geprüft …';
  if($('home-health'))$('home-health').innerHTML=healthHtml(null);
  try{S.health=await api('/api/system/health?'+new URLSearchParams({game_id:S.gameId||'',refresh:refresh?'1':''}))}catch(e){S.health={error:e.message}}
  updatePill();
  if($('home-health'))$('home-health').innerHTML=healthHtml(S.health);
  if($('prod-health'))$('prod-health').innerHTML=healthHtml(S.health,true);
}
function updatePill(){const h=S.health,pill=$('sys-pill');if(!h||h.error){pill.innerHTML='<span class="dot err"></span> Systemprüfung fehlgeschlagen';return}
  const anyMcp=h.mcp.servers.some(s=>s.state==='Verbunden');
  const ok=h.claude.found&&h.claude.logged_in&&h.blender.found&&h.unreal.found&&h.blender.mcp_connected&&h.unreal.mcp_connected;
  pill.innerHTML=`<span class="dot ${ok?'ok':h.claude.found?'warn':'err'}"></span> Claude ${h.claude.found&&h.claude.logged_in?'✓':h.claude.found?'nicht angemeldet':'✗'} · Blender ${h.blender.found?'✓':'✗'} · Unreal ${h.unreal.found?'✓':'✗'} · MCP ${anyMcp?'✓':'✗'}`}
function healthHtml(h,compact=false){
  const title=`<div class="card-head"><div><h2>Werkzeuge auf diesem PC</h2><p class="help">Echte Prüfung: Programme gesucht, Claude-Version abgefragt, MCP-Verbindungen live getestet.</p></div>${btn('Erneut prüfen','health-refresh','sm','','refresh')}</div>`;
  if(!h)return title+loading('Prüfe Claude Code, MCP-Verbindungen, Blender und Unreal … (bis zu einer Minute)');
  if(h.error)return title+note(esc(h.error),'err','alert');
  const row=(ok,label,detail,warn=false)=>`<div class="check"><span class="dot ${ok?'ok':warn?'warn':'err'}"></span><div class="grow">${label}<small>${detail}</small></div>${badge(ok?'OK':warn?'Offen':'Fehlt',ok?'ok':warn?'warn':'err')}</div>`;
  const mcpConnected=h.mcp.servers.filter(s=>s.state==='Verbunden');
  return title+`<div class="check-list">
   ${row(h.claude.found&&h.claude.version,'Claude Code',esc(h.claude.version||h.claude.note))}
   ${h.claude.found?row(h.claude.logged_in===true,'Claude-Anmeldung',h.claude.logged_in===true?'angemeldet ('+esc(h.claude.auth_method||'')+')':h.claude.logged_in===false?'<b>nicht angemeldet</b> – Eingabeaufforderung öffnen, <span class="mono">claude auth login</span> eingeben, dann „Erneut prüfen“.':'Status konnte nicht abgefragt werden',h.claude.logged_in===null):''}
   ${row(mcpConnected.length>0,'MCP-Verbindungen <span class="tiny">(Schnittstelle von Claude zu Blender/Unreal)</span>',esc(h.mcp.servers.length?h.mcp.servers.map(s=>s.name+': '+s.state).join(' · '):h.mcp.message||'nicht geprüft'),true)}
   ${row(h.blender.found,'Blender',esc(h.blender.path||'nicht gefunden')+(h.blender.found?' · MCP in Claude Code: '+(h.blender.mcp_connected?'verbunden':h.blender.mcp_configured?'eingerichtet, nicht verbunden':'nicht eingerichtet'):''))}
   ${row(h.unreal.found,'Unreal Engine',esc(h.unreal.installs.map(u=>'UE '+u.version).join(', ')||'nicht gefunden')+(h.unreal.found?' · MCP in Claude Code: '+(h.unreal.mcp_connected?'verbunden':h.unreal.mcp_configured?'eingerichtet, nicht verbunden':'nicht eingerichtet'):''))}
  </div>
  ${!mcpConnected.length?`<div style="margin-top:14px">${note('<b>Ohne MCP kann Claude Blender und Unreal nicht direkt steuern.</b> Alles andere funktioniert: Planung, Chat, Referenz-Prompts, ZIP-Export und der Blender-Echttest. Einrichtung: siehe Anleitung „MCP einrichten“ in der README.','warn','alert')}</div>`:''}
  <details class="more pro-only"><summary>Technische Details</summary><pre class="log">${esc(JSON.stringify(h,null,2))}</pre></details>
  <p class="tiny" style="margin-top:10px">Geprüft ${when(h.checked_at)}${h.workspace?' im Projektordner '+esc(h.workspace):''}.</p>`;
}

// ---------- Meine Spiele
async function renderGames(){
  const tab=S.tab.games||'list';
  if(tab==='list')return renderLibrary();
  if(!S.detail){$('view').innerHTML=needProject();return}
  const d=S.detail,g=d.game;
  const actions=btn('Idee besprechen','chat-open','','','chat')+btn('Projekt sichern','snapshot','','','save')+btn('Claude-Paket herunterladen','export-claude','primary','','download');
  let body='';
  if(tab==='overview')body=projectOverview();
  if(tab==='dlcs')body=dlcView();
  if(tab==='versions')body=versionsView();
  $('view').innerHTML=head('Spielprojekt · '+esc(g.version),esc(g.title),esc(g.summary||'Noch keine Kurzbeschreibung.'),actions)+tabs('games',{dlcs:d.dlcs.length,versions:d.snapshots.length})+body;
}
function renderLibrary(){
  const states=[['all','Alle'],['idea','Idee & Konzept'],['dev','In Entwicklung & Test'],['done','Fertig & veröffentlicht']];
  const match=g=>{const s=S.filter.status;if(s==='idea'&&!['Idee','Konzept'].includes(g.status))return false;if(s==='dev'&&!['In Entwicklung','Testphase'].includes(g.status))return false;if(s==='done'&&!['Fertig','Veröffentlicht'].includes(g.status))return false;
    const q=S.filter.q.toLowerCase();return !q||[g.title,g.summary,g.genre,g.style].join(' ').toLowerCase().includes(q)};
  const list=S.games.filter(match);
  const covers=[['rgba(60,207,196,.30)','#10283A','#0B141F'],['rgba(134,182,255,.30)','#151F3D','#0C111F'],['rgba(160,170,255,.24)','#1A1A36','#0D0F1E'],['rgba(90,200,255,.24)','#0F2433','#0A121B']];
  $('view').innerHTML=head('Spielebibliothek','Meine Spiele','Alle Projekte mit Versionen und DLCs. Fertige Spiele kannst du jederzeit weiter verbessern.',btn('Neues Spiel','new-game','primary','','plus')+btn('Vorhandenes importieren','import-game','','','upload'))
   +tabs('games')
   +`<div class="toolbar"><div class="search field" style="margin:0">${icon('search','sm')}<input id="lib-search" type="search" placeholder="Spiele durchsuchen …" value="${esc(S.filter.q)}" aria-label="Spiele durchsuchen"></div>
     <div class="chips" role="group" aria-label="Nach Status filtern">${states.map(([k,l])=>`<button type="button" class="chip" data-act="lib-filter" data-k="${k}" aria-pressed="${S.filter.status===k}">${l}</button>`).join('')}</div></div>
   <div class="games">${list.map((g,i)=>{const c=covers[i%covers.length];const mark=g.title.split(/\s+/)[0].slice(0,9).toUpperCase();
     return `<button type="button" class="game" data-act="open-game" data-id="${esc(g.id)}" aria-label="${esc(g.title)} öffnen"><div class="game-cover" style="--c1:${c[0]};--c2:${c[1]};--c3:${c[2]}"><span class="ver">${esc(short(g.version,26))}</span><span class="mark">${esc(mark)}</span></div>
     <div class="game-body"><div style="display:flex;justify-content:space-between;gap:10px;align-items:center"><h3>${esc(g.title)}</h3>${badge(g.status,STATUS_KIND[g.status])}</div><p>${esc(g.summary||'Noch keine Beschreibung')}</p>
     <div class="chips">${g.genre?`<span class="badge plain">${esc(short(g.genre,32))}</span>`:''}${g.style?`<span class="badge plain">${esc(short(g.style,28))}</span>`:''}</div>
     <div class="game-foot"><span>${g.dlc_count} DLC · ${g.archive_count} Archive · ${g.import_count||0} Dateien</span><span style="color:var(--accent);font-weight:650">Öffnen →</span></div></div></button>`}).join('')}</div>
   ${list.length?'':empty(S.games.length?'Keine Treffer':'Noch keine Spiele',S.games.length?'Passe Suche oder Filter an.':'Lege dein erstes Spiel an.',S.games.length?btn('Filter zurücksetzen','lib-reset','sm'):btn('Neues Spiel','new-game','primary','','plus'))}
   <div class="card section" id="trash-card">${loading('Papierkorb wird gelesen …')}</div>`;
  loadTrash();
  const s=$('lib-search');s.oninput=()=>{S.filter.q=s.value;const pos=s.selectionStart;renderLibrary();const n=$('lib-search');n.focus();n.setSelectionRange(pos,pos)};
}
async function loadTrash(){
  const el=$('trash-card');if(!el)return;let items=[];
  try{items=await api('/api/trash')}catch(e){el.innerHTML=note(esc(e.message),'err','alert');return}
  el.innerHTML=`<div class="card-head"><div><h2>Papierkorb ${items.length?'('+items.length+')':''}</h2><p class="help">Gelöschte Spiele mit allen Daten und Dateien. Wiederherstellen stellt den Stand vom Löschzeitpunkt zurück.</p></div></div>
   <div class="stack">${items.map(t=>`<div class="row"><div><div class="t">${esc(t.title)} ${t.broken?badge('beschädigt','err'):''}</div><p>gelöscht ${when(t.deleted_at)} · ${t.file_count??0} Dateien · ${size(t.size)}${t.workspace_not_deleted?' · Projektordner blieb erhalten':''}</p></div>
    <div class="row-actions">${t.restorable?btn('Wiederherstellen','trash-restore','sm primary','data-name="'+esc(t.name)+'"','refresh'):''}${btn('Endgültig löschen','trash-purge','sm danger','data-name="'+esc(t.name)+'" data-title="'+esc(t.title)+'"','x')}</div></div>`).join('')||'<p class="help">Der Papierkorb ist leer.</p>'}</div>`;
}
function projectOverview(){
  const d=S.detail,g=d.game,c=d.check;
  const steps=d.next_steps||[];
  const built=[
    [c.tasks_approved>0,`${c.tasks_approved} von ${c.tasks_total} Entwicklungsaufgaben mit Prüfbeleg abgenommen`],
    [c.tasks_tested>0,`${c.tasks_tested} Aufgaben getestet oder abgenommen`],
    [d.archives.some(a=>a.kind==='Windows-Build'),d.archives.some(a=>a.kind==='Windows-Build')?'Windows-Spielversion im Archiv vorhanden':'Noch keine gebaute Windows-Spielversion'],
    [c.full_source_imported,c.full_source_imported?'Original-Vollprojekt (Unreal/Blender) eingelagert':'Kein Original-Vollprojekt eingelagert'],
    [c.imported_file_count>0,`${c.imported_file_count} Originaldateien importiert`]];
  return `<div class="grid g2">
   <div class="card"><div class="card-head"><div><h2>Die Spielidee</h2><p class="help">Aus deiner Spielbibel.</p></div>${btn('Bearbeiten','edit-game','sm','','edit')}</div>
     <p style="white-space:pre-wrap">${esc(short(g.bible.vision||g.summary||'Noch keine Spielidee hinterlegt.',700))}</p>
     <dl class="summary-list" style="margin-top:16px"><dt>Genre</dt><dd>${esc(g.genre||'offen')}</dd><dt>Stil</dt><dd>${esc(g.style||'offen')}</dd><dt>Perspektive</dt><dd>${esc(g.camera||'offen')}</dd><dt>Engine</dt><dd>${esc(g.engine)}</dd></dl>
     <div class="btn-row" style="margin-top:14px">${btn('Spielbibel öffnen','goto','sm','data-area="studio" data-tab="bible"','book')}</div></div>
   <div class="card"><div class="card-head"><div><h2>Was wurde wirklich gebaut?</h2><p class="help">Nur belegte Ergebnisse zählen.</p></div></div>
     <div class="check-list">${built.map(([ok,t])=>`<div class="check"><span class="dot ${ok?'ok':''}"></span><div class="grow">${esc(t)}</div></div>`).join('')}</div></div>
   <div class="card"><div class="card-head"><div><h2>Was fehlt noch?</h2></div></div>
     ${c.missing_sections.length?`<p class="label">${c.missing_sections.length} leere Pflichtbereiche</p><div class="chips">${c.missing_sections.map(x=>`<span class="badge warn">${esc(x)}</span>`).join('')}</div>`:note('Alle Pflichtbereiche der Spielbibel sind ausgefüllt. Die fachliche Prüfung bleibt deine Entscheidung.','ok','check')}
     <p class="help" style="margin-top:14px">${c.reference_open} Pflicht-Referenzbilder offen · ${c.reference_approved} freigegeben.</p></div>
   <div class="card accent"><div class="card-head"><div><h2>Was soll ich jetzt tun?</h2></div></div><div class="stack">${steps.map((s,i)=>`<button type="button" class="next-step" data-act="next-step" data-id="${esc(g.id)}" data-area="${s.area}" data-tab="${s.tab}"><span class="num">${i+1}</span>${esc(s.text)}${icon('arrow','sm')}</button>`).join('')||'<p class="help">Keine offenen Empfehlungen.</p>'}</div></div></div>
  <div class="card section"><div class="card-head" style="margin-bottom:0"><div><h2>Spiel löschen</h2><p class="help">Das Spiel wird mit allen Daten und Dateien in den Papierkorb gelegt und kann von dort wiederhergestellt werden. Dein lokaler Unreal-/Blender-Projektordner wird nie gelöscht.</p></div>${btn('Spiel löschen …','delete-game','danger','','x')}</div></div>`;
}
function dlcView(){
  const d=S.detail;
  return `<div class="card"><div class="card-head"><div><h2>DLCs zu ${esc(d.game.title)}</h2><p class="help">Jedes DLC gehört zu genau diesem Basisspiel – mit eigener Planung, eigenen Aufgaben, Referenzen, Chatverlauf und eigenem Claude-Paket.</p></div>${btn('DLC erstellen','add-dlc','primary','','plus')}</div>
  <div class="stack">${d.dlcs.length?d.dlcs.map(x=>`<div class="row"><div><div class="t">${esc(x.title)} ${badge(x.status,STATUS_KIND[x.status])}</div><p>${esc(x.summary||'Noch keine Beschreibung')}</p><p class="tiny">${esc(x.version)} · benötigt Basisversion ${esc(x.compatible_version||'noch offen')} · ${d.refs.filter(r=>r.dlc_id===x.id).length} Referenzen · ${d.archives.filter(a=>a.dlc_id===x.id).length} Archive</p></div>
   <div class="row-actions">${btn('Im Kreativstudio planen','dlc-plan','sm','data-dlc="'+esc(x.id)+'"','studio')}${btn('Bearbeiten','edit-dlc','sm quiet','data-dlc="'+esc(x.id)+'"','edit')}${btn('DLC-Paket','export-dlc','sm','data-dlc="'+esc(x.id)+'"','download')}</div></div>`).join(''):empty('Noch keine DLCs','Ein DLC erweitert dein Spiel um neue Story, Regionen oder Figuren.',btn('Erstes DLC anlegen','add-dlc','primary sm','','plus'))}</div></div>`;
}
function versionsView(){
  const d=S.detail;
  return `<div class="card"><div class="card-head"><div><h2>Versionsstände</h2><p class="help">Ein Versionsstand hält Planung, Spielbibel, DLCs und Referenzliste fest. Vor jeder Chat-Übernahme legt GAMEFORGE automatisch einen an. Unreal-/Blender-Dateien sicherst du über das Archiv.</p></div>${btn('Jetzt sichern','snapshot','primary','','save')}</div>
  <div class="stack">${d.snapshots.length?d.snapshots.map(s=>`<div class="row"><div><div class="t">${esc(s.version)}</div><p>${esc(s.notes||'Gesicherter Planungsstand')} · ${when(s.created_at)}</p></div><div class="row-actions">${btn('Wiederherstellen','restore-snapshot','sm','data-id="'+esc(s.id)+'"','refresh')}</div></div>`).join(''):empty('Noch kein Versionsstand','Sichere den aktuellen Planungsstand mit einem Klick.')}</div></div>`;
}

// ---------- Kreativstudio
async function renderStudio(){
  const tab=S.tab.studio||'ideas',d=S.detail,dlc=currentDlc();
  const scopeRefs=d.refs.filter(r=>(r.dlc_id||'')===(S.dlcId||''));
  let body='';
  if(tab==='ideas')body=await ideasView();
  if(tab==='bible')body=dlc?dlcDesignView(dlc):bibleView();
  if(tab==='refs')body=refsView(scopeRefs);
  $('view').innerHTML=head('Kreativstudio · '+ctxLabel(),'Ideen, Story & Welt','Hier entsteht dein Spiel auf dem Papier: Chat-Ideen, Spielbibel und Referenzbilder. Nichts wird ohne deine Freigabe übernommen.',btn('Mit GAMEFORGE sprechen','chat-open','primary','','chat'))
   +tabs('studio',{refs:scopeRefs.length})+body;
}
async function ideasView(){
  const feed=await api(G()+'/ideas?'+new URLSearchParams({dlc_id:S.dlcId}));
  const ch=feed.changes,sg=feed.suggestions;
  const open=ch.filter(c=>c.status==='Vorgeschlagen').length+sg.filter(s=>s.status==='Vorgeschlagen').length;
  return `${note('<b>So funktioniert es:</b> Du schreibst im Chat (rechts unten). GAMEFORGE antwortet mit Vorschlägen. Erst wenn du „Übernehmen“ klickst, wird die Spielbibel geändert – vorher wird automatisch ein Versionsstand gesichert. Umgesetzt im eigentlichen Spiel wird es danach über „Produktion“.','info','info')}
  <div class="grid g3" style="margin-top:18px"><div class="metric"><small>Offene Entscheidungen</small><strong>${open}</strong><span>warten auf dich</span></div><div class="metric"><small>Übernommene Änderungen</small><strong>${ch.filter(c=>c.status==='Übernommen').length}</strong><span>in der Spielbibel gespeichert</span></div><div class="metric"><small>Nachrichten</small><strong>${feed.messages.length}</strong><span>im Gespräch zu ${ctxLabel()}</span></div></div>
  <div class="section grid g2"><div class="card"><div class="card-head"><div><h2>Änderungsentwürfe</h2><p class="help">Konkrete Text-Änderungen mit Vorher/Nachher.</p></div>${btn('Selbst formulieren','manual-change','sm','','edit')}</div><div class="stack">${ch.length?ch.slice().reverse().map(changeCard).join(''):empty('Noch keine Änderungsentwürfe','Bitte im Chat z. B.: „Mach AION düsterer, aber ändere die Hauptgeschichte nicht.“')}</div></div>
  <div class="card"><div class="card-head"><div><h2>Ideen</h2><p class="help">Vorschläge annehmen, ablehnen oder in die Spielbibel übernehmen.</p></div></div><div class="stack">${sg.length?sg.slice().reverse().map(suggestionCard).join(''):empty('Noch keine Ideen','Frag im Chat z. B.: „Erstelle einen Poseidon-Boss mit drei Kampfphasen.“')}</div></div></div>`;
}
const SECTION_LABEL=k=>(Object.fromEntries(S.config.fields)[k])||DLC_LABELS[k]||k;
function ladder(stage){const steps=['Idee','Vorgeschlagen','Von dir genehmigt','In Projektdaten gespeichert','Im Spiel umgesetzt','Getestet'];return `<div class="ladder" aria-label="Status">${steps.map((s,i)=>`<span class="${i<=stage?'on':''}">${s}</span>`).join('')}</div>`}
function changeCard(c){
  const stage=c.status==='Übernommen'?3:c.status==='Abgelehnt'?-1:1;
  return `<div class="proposal"><div class="ptitle"><span>${esc(c.summary)}</span>${badge(c.status==='Übernommen'?'Übernommen':c.status,c.status==='Übernommen'?'ok':c.status==='Abgelehnt'?'err':'warn')}</div>
   <p class="tiny">Bereich: ${esc(SECTION_LABEL(c.section))} · ${c.mode==='replace_text'?'ersetzt eine bestehende Stelle':'ergänzt den Bereich'}</p>
   <div class="diff">${c.mode==='replace_text'?`<div class="old"><small>VORHER</small>${esc(c.old_text)}</div>`:''}<div class="new"><small>${c.mode==='replace_text'?'NACHHER':'NEU HINZU'}</small>${esc(c.new_text)}</div></div>
   ${stage>=0?ladder(stage):''}
   ${c.status==='Vorgeschlagen'?`<div class="btn-row">${btn('Übernehmen','change-apply','sm primary','data-id="'+c.id+'"','check')}${btn('Ablehnen','change-reject','sm quiet','data-id="'+c.id+'"','x')}${btn('Anders formulieren','change-modify','sm quiet','data-id="'+c.id+'"','edit')}</div>`:''}</div>`;
}
function suggestionCard(p){
  const stage=p.integrated?3:p.status==='Angenommen'?2:p.status==='Abgelehnt'?-1:1;
  return `<div class="proposal"><div class="ptitle"><span>${esc(p.title)}</span>${badge(p.integrated?'In Spielbibel':p.status,p.integrated||p.status==='Angenommen'?'ok':p.status==='Abgelehnt'?'err':'')}</div><p>${esc(p.detail)}</p><p class="tiny">Bereich: ${esc(SECTION_LABEL(p.section))}</p>${stage>=0?ladder(stage):''}
   <div class="btn-row">${p.status!=='Angenommen'?btn('Annehmen','idea-accept','sm primary','data-id="'+p.id+'"','check'):''}${p.status!=='Abgelehnt'&&!p.integrated?btn('Ablehnen','idea-reject','sm quiet','data-id="'+p.id+'"','x'):''}${p.status==='Angenommen'&&!p.integrated?btn('In Spielbibel übernehmen','idea-integrate','sm','data-id="'+p.id+'"','book'):''}</div></div>`;
}
function bibleView(){
  const g=S.detail.game,labels=Object.fromEntries(S.config.fields);
  return `<div class="card"><div class="card-head"><div><h2>Spielbibel · ${esc(g.title)}</h2><p class="help">Alles, was hier steht, bekommt Claude als verbindliche Vorgabe. Leere Felder bleiben sichtbar leer – GAMEFORGE erfindet nichts dazu.</p></div>${btn('Speichern','save-bible','primary','','save')}</div>
   <div class="chips" style="margin-bottom:10px">${BIBLE_GROUPS.map(([t],i)=>`<button type="button" class="chip" data-act="bible-jump" data-i="${i}">${esc(t)}</button>`).join('')}</div>
   ${BIBLE_GROUPS.map(([title,keys],i)=>`<details class="more" id="bg-${i}" ${i===0?'open':''}><summary>${esc(title)} · ${keys.filter(k=>(g.bible[k]||'').trim()).length}/${keys.length} ausgefüllt</summary><div style="margin-top:14px">${keys.map(k=>field('b_'+k,labels[k],g.bible[k]||'',{area:true,rows:k==='canon'||k==='story'?170:100})).join('')}</div></details>`).join('')}
   <div class="btn-row" style="justify-content:flex-end;margin-top:16px">${btn('Alle Einträge speichern','save-bible','primary','','save')}</div></div>`;
}
function dlcDesignView(x){
  return `<div class="card"><div class="card-head"><div><h2>DLC-Planung · ${esc(x.title)}</h2><p class="help">Gehört zu ${esc(S.detail.game.title)}. Benötigte Basisversion: ${esc(x.compatible_version||'noch offen')}. Zum Basisspiel wechselst du oben im Projektfeld.</p></div>${btn('Speichern','save-dlc-design','primary','','save')}</div>
   ${Object.keys(DLC_LABELS).map(k=>field('d_'+k,DLC_LABELS[k],x.design[k]||'',{area:true,rows:90})).join('')}
   <div class="btn-row" style="justify-content:flex-end">${btn('Speichern','save-dlc-design','primary','','save')}</div></div>`;
}
function refsView(refs){
  const approved=refs.filter(r=>r.approved).length,open=refs.filter(r=>r.required&&!r.approved).length;
  return `<div class="card"><div class="card-head"><div><h2>Referenzbilder für ${ctxLabel()}</h2><p class="help">1. Prompt kopieren → 2. in ChatGPT einfügen und Bild erzeugen → 3. Bild hier hinzufügen → 4. prüfen und freigeben. Referenzbilder sind Vorlagen, keine fertigen 3D-Modelle.</p></div>
    <div class="btn-row">${btn('Einzelbild','add-ref','sm','','plus')}${btn('Komplettes Bildset','add-ref-bundle','sm primary','','layers')}</div></div>
   <div class="grid g3" style="margin-bottom:18px"><div class="metric"><small>Freigegeben</small><strong>${approved}</strong></div><div class="metric"><small>Pflichtbilder offen</small><strong>${open}</strong></div><div class="metric"><small>Bildaufträge gesamt</small><strong>${refs.length}</strong></div></div>
   <div class="stack">${refs.length?refs.map(r=>`<div class="row"><div class="ref">${r.image_path?`<img class="thumb" src="${G()}/refs/${r.id}/image?v=${enc(r.updated_at)}" alt="Referenz ${esc(r.name)}" loading="lazy">`:`<div class="thumb">${icon('image')}</div>`}
     <div><div class="t">${esc(r.name)} ${badge(r.approved?'Freigegeben':r.image_path?'Bild da – prüfen':'Bild fehlt',r.approved?'ok':r.image_path?'warn':'')}</div><p>${esc(S.config.categories[r.category])} · ${esc(S.config.view_labels[r.view]||r.view)}${r.required?' · Pflicht':''}</p><p class="tiny">${esc(short(r.details||'Keine zusätzlichen Vorgaben',140))}</p></div></div>
     <div class="row-actions">${btn('Prompt kopieren','copy-prompt','sm','data-id="'+r.id+'"','copy')}${btn(r.image_path?'Neues Bild':'Bild hinzufügen','upload-ref','sm','data-id="'+r.id+'"','upload')}${r.image_path?btn(r.approved?'Freigabe zurücknehmen':'Freigeben','approve-ref','sm '+(r.approved?'quiet':'primary'),'data-id="'+r.id+'"','check'):''}</div></div>`).join(''):empty('Noch keine Bildaufträge','Lege für eine Figur, einen Boss oder ein Gebäude ein komplettes Bildset an.',btn('Komplettes Bildset','add-ref-bundle','primary sm','','layers'))}</div></div>`;
}

// ---------- Produktion
async function renderProduction(){
  const tab=S.tab.production||'overview';
  const view=$('view');
  const top=head('Produktion · '+ctxLabel(),'Vom Plan zum echten Spiel','Claude Code, 20 spezialisierte Agenten, Blender und Unreal. Jede Statusangabe stammt aus echten Dateien, Prozessen oder Ereignissen.')+tabs('production');
  view.innerHTML=top+loading();
  const body=await ({overview:prodOverview,pipeline:pipelineView,agents:agentsView,live:liveView,direct:directView,tasks:tasksView,roadmap:roadmapView})[tab]();
  if(S.area==='production'&&(S.tab.production||'overview')===tab)view.innerHTML=top+body;
  afterProduction(tab);
}
async function prodOverview(){
  const pipe=await api(G()+'/pipeline');const dir=await api(G()+'/direct');
  const running=dir.jobs.filter(j=>j.status==='Läuft');
  return `<div class="card"><div class="card-head"><div><h2>Die Produktionskette</h2><p class="help">So wird aus einem Referenzbild ein Objekt in deinem Unreal-Spiel.</p></div></div>
   <div class="flow">${[['1 · Referenzen','Bilder in ChatGPT erzeugen und freigeben'],['2 · Blender','Claude modelliert per MCP-Schnittstelle'],['3 · Dateien','echte .blend und .fbx werden geprüft'],['4 · Unreal','Import ins Projekt unter /Game/GAMEFORGE'],['5 · Test','Quality-Agent schreibt Testbericht'],['6 · Freigabe','du gibst das Asset frei']].map((n,i)=>(i?`<div class="arrow">${icon('arrow','sm')}</div>`:'')+`<div class="node"><b>${n[0]}</b><span>${n[1]}</span></div>`).join('')}</div>
   <div class="btn-row" style="margin-top:16px">${btn('Zur Blender → Unreal-Strecke','goto','primary','data-area="production" data-tab="pipeline"','cube')}${btn('Live-Monitor','goto','','data-area="production" data-tab="live"','activity')}</div></div>
  <div class="grid g2 section"><div class="card"><div class="card-head"><div><h2>Zwei Wege zur Entwicklung</h2></div></div><div class="stack">
    <div class="row top"><div><div class="t">A · Claude-Paket als ZIP</div><p>Alles für Claude Code in einer Datei: Spielkonzept, Daten, Referenzen, Aufgaben, 20 Agentenrollen. In Claude Desktop (Code › Local) öffnen.</p></div><div class="row-actions">${btn('ZIP herunterladen','export-claude','sm primary','','download')}</div></div>
    <div class="row top"><div><div class="t">B · Direkt-Studio</div><p>GAMEFORGE startet eine eigene lokale Claude-Code-Sitzung im Projektordner und zeigt dir Ergebnisse, Logs und Fehler hier an.</p></div><div class="row-actions">${btn('Öffnen','goto','sm','data-area="production" data-tab="direct"','terminal')}</div></div>
    ${note('Beide Wege nutzen dieselben freigegebenen Projektdaten. Chatverläufe in Claude Desktop und im Direkt-Studio sind nicht automatisch synchron.','info','info')}</div></div>
   <div class="card" id="prod-health">${healthHtml(S.health,true)}</div></div>
  <div class="grid g3 section"><div class="metric"><small>Laufende Aufträge</small><strong>${running.length}</strong><span>${running.length?esc(JOB_LABEL[running[0].kind]||running[0].kind):'gerade nichts aktiv'}</span></div>
   <div class="metric"><small>3D-Assets in Arbeit</small><strong>${pipe.assets.length}</strong><span>${pipe.workspace?'im verbundenen Projektordner':'kein Projektordner verbunden'}</span></div>
   <div class="metric"><small>Projektordner</small><strong style="font-size:16px;overflow-wrap:anywhere">${esc(pipe.workspace?short(pipe.workspace,60):'nicht verbunden')}</strong></div></div>`;
}
function stepper(stages,index){return `<div class="stepper" role="list">${stages.map((s,i)=>`<div class="step ${i<index?'done':i===index?'now':''}" role="listitem" ${i===index?'aria-current="step"':''}>${esc(s)}</div>`).join('')}</div>`}
async function pipelineView(){
  const [pipe,dir]=await Promise.all([api(G()+'/pipeline'),api(G()+'/direct')]);
  const h=S.health,refs=S.detail.refs.filter(r=>r.approved&&r.image_path);
  const ready=[[!!pipe.workspace,'Projektordner verbunden',pipe.workspace||'Im Direkt-Studio verbinden'],[!!h?.blender?.found,'Blender installiert',h?.blender?.path||'nicht geprüft'],[!!h?.blender?.mcp_connected,'Blender-MCP in Claude Code verbunden',h?(h.blender.mcp_configured?'eingerichtet, aber nicht verbunden':'nicht eingerichtet'):'nicht geprüft'],[!!h?.unreal?.found,'Unreal Engine installiert',h?.unreal?.installs?.map(u=>'UE '+u.version).join(', ')||'nicht geprüft'],[!!h?.unreal?.mcp_connected,'Unreal-MCP in Claude Code verbunden',h?(h.unreal.mcp_configured?'eingerichtet, aber nicht verbunden':'nicht eingerichtet'):'nicht geprüft']];
  const blenderJobs=dir.jobs.filter(j=>j.kind==='blender_test').slice(0,3);
  return `<div class="grid g2"><div class="card"><div class="card-head"><div><h2>Bereitschaft</h2><p class="help">Ohne MCP-Verbindung startet GAMEFORGE keine Modellierung und meldet auch keinen Erfolg.</p></div>${btn('Prüfen','health-refresh','sm','','refresh')}</div>
    <div class="check-list">${ready.map(([ok,l,d])=>`<div class="check"><span class="dot ${ok?'ok':'warn'}"></span><div class="grow">${l}<small>${esc(d)}</small></div></div>`).join('')}</div></div>
   <div class="card"><div class="card-head"><div><h2>Blender-Echttest</h2><p class="help">Startet Blender im Hintergrund, baut ein kleines Testobjekt, speichert .blend + .fbx und prüft die Dateien. Beweist, dass Blender auf diesem PC arbeitet – nicht die MCP-Verbindung.</p></div></div>
    <div class="btn-row">${btn('Blender-Echttest starten','blender-test','primary','','play')}</div>
    <div class="stack" style="margin-top:14px">${blenderJobs.map(jobRow).join('')||'<p class="help">Noch kein Test durchgeführt.</p>'}</div></div></div>
  <div class="card section"><div class="card-head"><div><h2>3D-Assets</h2><p class="help">${esc(pipe.message)}</p></div></div>
   <div class="stack">${pipe.assets.length?pipe.assets.map(a=>`<div class="card flat" style="padding:16px"><div class="card-head" style="margin-bottom:4px"><div><h3>${esc(a.name)} <span class="tiny">· ${esc(a.type)}</span></h3><p class="tiny">Asset-ID ${esc(a.asset_id)} · ${a.references} Referenzen · angelegt ${when(a.created_at)}</p></div>${badge(a.stage,a.stage==='freigegeben'?'ok':a.job_running?'accent live':a.stage_index>=3?'info':'')}</div>
     ${stepper(pipe.stages,a.stage_index)}
     <div class="grid g3" style="gap:10px;margin-top:10px;font-size:13px">
      <div>${fileState(a.blend,'.blend-Datei')}</div><div>${fileState(a.fbx,'.fbx-Export')}</div><div>${a.unreal_assets.length?`<span class="dot ok"></span> ${a.unreal_assets.length} Unreal-Assets`:'<span class="dot"></span> noch nicht in Unreal'}<br><span class="tiny">${a.qa_report?'Testbericht vorhanden':'kein Testbericht'}</span></div></div>
     <details class="more pro-only"><summary>Dateipfade</summary><pre class="log">${esc(JSON.stringify({blend:a.blend,fbx:a.fbx,unreal:a.unreal_assets,qa:a.qa_report},null,2))}</pre></details>
     <div class="btn-row" style="margin-top:12px">${a.job_running?badge('Claude arbeitet gerade','accent live'):btn(a.stage_index>=3?'Erneut an Claude übergeben':'Claude: Blender → Unreal ausführen','pipeline-start','sm primary','data-id="'+a.asset_id+'"','play')}
      ${a.last_error_job?btn('Fehler anzeigen','show-job','sm','data-id="'+a.last_error_job+'"','alert')+btn('Erneut versuchen','retry-job','sm','data-id="'+a.last_error_job+'"','refresh'):''}
      ${btn('Asset freigeben','asset-approve','sm '+(a.stage==='getestet'?'primary':''),'data-id="'+a.asset_id+'" '+(a.stage==='getestet'?'':'disabled title="Erst nach Unreal-Import und Testbericht möglich"'),'check')}</div></div>`).join(''):empty('Noch kein 3D-Asset-Auftrag','Lege unten einen Auftrag für eine Figur, Waffe oder ein Gebäude an.')}</div></div>
  <div class="card section"><div class="card-head"><div><h2>Neuen 3D-Auftrag anlegen</h2><p class="help">Erstellt einen nachvollziehbaren Auftrag mit Referenzkopien für Blender und Unreal. Dabei wird noch nichts modelliert.</p></div></div>
   <div class="grid g2"><div>${field('p-name','Name des Objekts / der Figur','',{ph:'z. B. Poseidon-Rüstung'})}${selectField('p-type','Art',[['character','Charakter / Boss / NPC'],['static','Gegenstand / Gebäude'],['environment','Landschaft / Level-Objekt'],['vehicle','Fahrzeug'],['weapon','Waffe']],'character')}${field('p-req','Technische Vorgaben','',{area:true,ph:'Größe, Materialien, gewünschte Animationen, Verwendung im Spiel …'})}</div>
   <div><p class="label">Freigegebene Referenzbilder</p>${refs.length?refs.map(r=>`<label class="checkline"><input type="checkbox" class="p-ref" value="${esc(r.id)}"><span>${esc(r.name)} · ${esc(S.config.view_labels[r.view]||r.view)}</span></label>`).join(''):note('Noch keine Referenz freigegeben. Du kannst stattdessen eine genaue Beschreibung eingeben – Claude erstellt dann einen Entwurf zur Freigabe.','info','info')}</div></div>
   <div class="btn-row">${btn('3D-Auftrag anlegen','pipeline-prepare','primary','','plus')}</div></div>`;
}
function fileState(f,label){if(!f.exists)return `<span class="dot"></span> ${label}: fehlt`;return `<span class="dot ${f.format_ok?'ok':'err'}"></span> ${label}: ${size(f.size)}${f.format_ok?'':' – ungültiger Dateikopf'}`}
function jobRow(j){const kind=j.status==='Abgeschlossen'?'ok':j.status==='Läuft'?'accent live':j.status==='Fehlgeschlagen'||j.status==='Unterbrochen'?'err':'';
  return `<div class="row"><div><div class="t">${esc(JOB_LABEL[j.kind]||j.kind)} ${badge(j.status,kind)}</div><p>Gestartet ${when(j.created_at)}${j.ended_at?' · beendet '+when(j.ended_at):''}${j.user_instruction&&j.kind!=='blender_test'?' · '+esc(short(j.user_instruction,90)):''}</p></div>
   <div class="row-actions">${btn(j.status==='Fehlgeschlagen'?'Fehler anzeigen':'Ergebnis','show-job','sm','data-id="'+j.id+'"',j.status==='Fehlgeschlagen'?'alert':'terminal')}${['Fehlgeschlagen','Unterbrochen'].includes(j.status)?btn('Erneut versuchen','retry-job','sm','data-id="'+j.id+'"','refresh'):''}</div></div>`}
async function agentsView(){
  const r=await api('/api/agents');const d=S.detail;
  const groups={management:'Leitung',creative:'Konzept & Story',blender:'Blender & 3D',hybrid:'Gewerkeübergreifend',unreal:'Unreal & Gameplay',qa:'Prüfung',release:'DLC & Release'};
  return `<div class="card"><div class="card-head"><div><h2>Dein KI-Entwicklerteam · 20 Agenten</h2><p class="help">Der Studio Director verteilt klar abgegrenzte Aufgaben – nicht alle 20 gleichzeitig. Jeder Agent hat einen eigenen Schreibbereich, damit sich niemand gegenseitig Dateien überschreibt. Berechtigungen stehen auf „einzeln bestätigen“, nicht auf „alles erlaubt“.</p></div>${badge('20 Rollen eingerichtet','ok')}</div>
   <div class="grid g2"><div>${selectField('a-dlc','Für welchen Bereich?',[['','Basisspiel – '+d.game.title],...d.dlcs.map(x=>[x.id,'DLC: '+x.title])],S.dlcId)}
    <div class="btn-row">${btn('Agenten-Paket herunterladen','agents-download','primary','','download')}${btn('In Projektordner installieren','agents-install','','','folder')}</div></div>
    <div>${note('Eine eingerichtete Rolle ist noch keine laufende Arbeit. Was die Agenten wirklich tun, siehst du im Live-Monitor – nur aus echten Claude-Code-Ereignissen.','info','info')}</div></div></div>
  <div class="agents section">${r.agents.map(a=>`<div class="agent ${a.slug==='studio-director'?'master':''}"><div class="agent-top"><div><span class="no">${String(a.id).padStart(2,'0')}</span> <b>${esc(a.name)}</b></div>${badge(groups[a.group]||a.group,'plain')}</div><p>${esc(a.description)}</p>
    <dl><dt>Liefert</dt><dd>${esc(a.deliverable)}</dd><dt>Übergibt an</dt><dd>${esc(a.handoff)}</dd></dl>
    <details class="more"><summary>Aufgabe & Rechte</summary><dl><dt>Aufgabe</dt><dd>${esc(a.task)}</dd><dt>Eingaben</dt><dd>${esc(a.inputs)}</dd><dt>Schreibbereich</dt><dd class="mono">${esc(a.write_scope)}</dd><dt>MCP</dt><dd>${esc(a.mcp.length?a.mcp.join(', '):'keine')}</dd>
     <dt class="pro-only">Tools</dt><dd class="pro-only mono">${esc(a.tools.join(', '))}</dd><dt class="pro-only">Gesperrt</dt><dd class="pro-only mono">${esc(a.disallowed_tools.join(', ')||'–')}</dd><dt class="pro-only">Rechte</dt><dd class="pro-only">${esc(a.permission_mode)}</dd></dl></details></div>`).join('')}</div>`;
}
async function liveView(){
  const info=await api(G()+'/live');
  return `<div class="card"><div class="card-head"><div><h2>Live-Monitor · ${ctxLabel()}</h2><p class="help">Zeigt nur echte Ereignisse aus Claude-Code-Sitzungen in diesem Projektordner (Start, Ende, Fehler der Agenten). Keine Prozentwerte, keine Fantasie-Fortschritte. Aktualisiert sich alle 3 Sekunden.</p></div>
   <div class="btn-row">${badge(info.configured?'Ereignis-Meldung eingerichtet':'Ereignis-Meldung fehlt',info.configured?'ok':'warn')}${btn(info.configured?'Erneut einrichten':'Einrichten','live-install','sm '+(info.configured?'':'primary'),'','activity')}</div></div>
   ${!info.configured?note('Damit GAMEFORGE sieht, welcher Agent gerade arbeitet, wird im Projektordner eine kleine Meldefunktion (Claude-Code-Hook) eingerichtet. Bestehende Einstellungen werden vorher gesichert, Chat-Inhalte werden nie gespeichert.','info','info'):''}
   <div id="live-body">${liveBody(info)}</div></div>`;
}
function liveBody(v){
  const counts={};(v.agents||[]).forEach(a=>counts[a.state]=(counts[a.state]||0)+1);
  const jobs=(v.jobs||[]).slice(0,6);
  return `<div class="chips" style="margin:6px 0 16px">${['Arbeitet','Fehler','Abgeschlossen','Wartet','Unbekannt','Keine Verbindung'].filter(s=>counts[s]).map(s=>badge(s+': '+counts[s],AGENT_STATE_KIND[s])).join('')}</div>
  <div class="grid g2"><div><p class="label">Agenten</p><div class="agents" style="grid-template-columns:1fr">${(v.agents||[]).map(a=>`<div class="row" style="padding:10px 14px"><div><div class="t" style="font-size:14px">${esc(a.name)}</div><p>${a.last_event?esc(eventLabel(a.last_event))+' · '+when(a.last_event_at):'noch kein Ereignis'}${a.started_at&&a.state==='Arbeitet'?' · seit '+when(a.started_at):''}${a.errors.length?' · '+a.errors.length+' Fehler':''}</p></div>
    <div class="row-actions">${badge(a.state,AGENT_STATE_KIND[a.state])}${a.errors.length?btn('Fehler anzeigen','agent-errors','sm quiet','data-slug="'+esc(a.slug)+'"','alert'):''}</div></div>`).join('')}</div></div>
   <div><p class="label">Aufträge aus GAMEFORGE</p><div class="stack">${jobs.map(jobRow).join('')||'<p class="help">Noch kein Auftrag gestartet.</p>'}</div>
    <p class="label" style="margin-top:18px">Letzte echte Ereignisse</p><div class="stack">${(v.events||[]).slice(0,25).map(e=>`<div class="check"><span class="dot ${e.event==='PostToolUseFailure'?'err':e.event==='SubagentStop'?'ok':''}"></span><div class="grow">${esc(e.agent)} · ${esc(eventLabel(e.event))}${e.tool?' · '+esc(e.tool):''}<small>${when(e.at)}</small></div></div>`).join('')||'<p class="help">Noch keine Ereignisse empfangen. Sie erscheinen, sobald Claude Code in diesem Projektordner arbeitet.</p>'}</div>
    <p class="tiny" style="margin-top:12px">${esc(v.message||'')}</p></div></div>`;
}
const eventLabel=e=>({SessionStart:'Sitzung gestartet',SessionEnd:'Sitzung beendet',SubagentStart:'Agent gestartet',SubagentStop:'Agent fertig',PostToolUseFailure:'Werkzeugfehler'})[e]||e;
async function directView(){
  const r=await api(G()+'/direct');const h=r.health,s=h.settings,d=S.detail;
  const uatHint=(r.unreal_installs||[]).find(u=>u.run_uat);
  return `<div class="grid g2"><div class="card"><div class="card-head"><div><h2>Projektordner verbinden</h2><p class="help">Hier arbeitet Claude Code für ${esc(d.game.title)}. Jedes Spiel hat seinen eigenen Ordner.</p></div></div>
    ${field('d-ws','Lokaler Projektordner',s.workspace,{ph:'C:\\Spiele\\AION',help:'Unreal-Projektordner oder ein neuer, leerer Ordner.'})}
    <div class="pro-only">${field('d-uat','RunUAT.bat (für „Windows-Spielversion erstellen“)',s.uat_path||'',{ph:uatHint?.run_uat||'…\\Engine\\Build\\BatchFiles\\RunUAT.bat',help:uatHint?'Gefunden: '+uatHint.run_uat:'Keine Unreal-Installation im Standardpfad gefunden.'})}</div>
    <div class="btn-row">${btn('Ordner verbinden','direct-save','primary','','folder')}${btn('Neuen Arbeitsordner anlegen','direct-create','','','plus')}</div>
    <details class="more"><summary>Original-Vollprojekt als Arbeitsordner entpacken</summary><div style="margin-top:12px">${selectField('d-archive','Vollprojekt-ZIP aus dem Archiv',[['','Bitte wählen'],...d.archives.filter(a=>['Vollprojekt','DLC-Vollprojekt'].includes(a.kind)).map(a=>[a.id,a.label+' ('+a.original_name+')'])],'','Wird in einen neuen Ordner entpackt. Bestehende Dateien bleiben unberührt; unsichere ZIP-Pfade und Symlinks werden abgelehnt.')}${btn('Sicher entpacken','direct-extract','sm','','archive')}</div></details></div>
   <div class="card"><div class="card-head"><div><h2>Verbindungstest</h2><p class="help">Vorhandene Dateien beweisen keine funktionierende Verbindung. Die echte MCP-Prüfung steht unter „Überblick“.</p></div>${btn('Prüfen','direct-refresh','sm','','refresh')}</div>
    <div class="check-list">${[['Claude Code gefunden',h.claude_cli_detected],['Blender im PATH',h.blender_executable_detected||!!r.blender_path],['Projektordner gültig',h.workspace_valid],['Unreal-Projekt (.uproject) im Ordner',h.uprojects.length>0],['RunUAT konfiguriert',h.uat_configured]].map(([l,ok])=>`<div class="check"><span class="dot ${ok?'ok':'warn'}"></span><div class="grow">${l}</div>${badge(ok?'Ja':'Nein',ok?'ok':'')}</div>`).join('')}</div>
    <p class="tiny pro-only" style="margin-top:10px">MCP-Einträge in .mcp.json: ${esc(h.mcp_names.join(', ')||'keine')} · Unreal-Projekte: ${esc(h.uprojects.join(', ')||'keine')}</p></div></div>
  <div class="card section"><div class="card-head"><div><h2>Auftrag an Claude Code</h2><p class="help">Schreibe in normaler Sprache, was passieren soll. „Plan erstellen“ ändert nichts. „Umsetzen“ darf Dateien im Projektordner bearbeiten – lege vorher eine Sicherung an.</p></div></div>
   ${field('d-ins','Was soll Claude tun?','',{area:true,ph:'z. B. Baue für AION eine spielbare Testszene mit Steuerung und Speichern und dokumentiere den Test.'})}
   ${selectField('d-task','Optional: passende Aufgabe aus „Aufgaben A–Z“',[['','Freier Auftrag'],...d.tasks.filter(t=>!t.dlc_id).map(t=>[t.id,t.phase+' · '+t.title])],'')}
   <label class="checkline pro-only flex"><input type="checkbox" id="d-mcp"><span>Blender-/Unreal-MCP-Werkzeuge für diesen Umsetzungsauftrag erlauben</span></label>
   <div class="btn-row">${btn('Plan erstellen (ändert nichts)','direct-plan','','','book')}${btn('Umsetzen','direct-implement','primary','','play')}${btn('Windows-Spielversion erstellen','direct-build','','','games')}${btn('Projektordner als ZIP sichern','direct-archive','quiet','','archive')}</div>
   <details class="more pro-only"><summary>Technische Details zum Build</summary><p class="help" style="margin-top:8px">„Windows-Spielversion erstellen“ ruft RunUAT BuildCookRun -build -cook -stage -pak -package -archive -targetplatform=Win64 -clientconfig=Development auf. Das Ergebnis landet als ZIP im Archiv. Ein erfolgreicher Build ist noch keine Abnahme.</p></details></div>
  <div class="card section"><div class="card-head"><div><h2>Aufträge & Ergebnisse</h2><p class="help">Echte Ausgaben von Claude Code, Blender und Unreal.</p></div>${btn('Aktualisieren','direct-refresh','sm','','refresh')}</div><div class="stack" id="direct-jobs">${r.jobs.map(jobRow).join('')||empty('Noch keine Aufträge','Starte oben deinen ersten Auftrag.')}</div></div>`;
}
function tasksView(){
  const d=S.detail,tasks=S.dlcId?(S._dlcTasks||[]):d.tasks.filter(t=>!t.dlc_id);
  const done=tasks.filter(t=>t.status==='Abgenommen').length,tested=tasks.filter(t=>['Getestet','Abgenommen'].includes(t.status)).length;
  return `<div class="card"><div class="card-head"><div><h2>Aufgaben A–Z · ${ctxLabel()}</h2><p class="help">Alle Schritte bis zum fertigen Spiel. „Getestet“ und „Abgenommen“ gehen nur mit einem echten Prüfbeleg.</p></div></div>
   <div class="grid g3"><div class="metric"><small>Abgenommen</small><strong>${done}/${tasks.length}</strong><div class="bar"><i style="width:${tasks.length?done/tasks.length*100:0}%"></i></div></div><div class="metric"><small>Getestet oder abgenommen</small><strong>${tested}</strong></div><div class="metric"><small>In Arbeit</small><strong>${tasks.filter(t=>t.status==='In Arbeit').length}</strong></div></div></div>
  ${S.config.phases.map(ph=>{const rows=tasks.filter(t=>t.phase===ph);if(!rows.length)return '';const n=rows.filter(x=>x.status==='Abgenommen').length;
   return `<details class="card" style="margin-top:14px" ${ph.startsWith('01')||S.dlcId?'open':''}><summary style="cursor:pointer;display:flex;justify-content:space-between;gap:10px;font-weight:650"><span>${esc(ph)}</span><span class="tiny">${n}/${rows.length} abgenommen</span></summary><div class="stack" style="margin-top:14px">${rows.map(t=>`<div class="row"><div><div class="t">${esc(t.title)} ${badge(t.status,t.status==='Abgenommen'?'ok':t.status==='Getestet'?'info':t.status==='In Arbeit'?'accent':t.status==='Implementiert'?'warn':'')}</div><p>${esc(t.description)}</p><p class="tiny">Abnahme: ${esc(t.acceptance)}${t.evidence?' · Beleg: '+esc(short(t.evidence,120)):''}</p></div><div class="row-actions">${btn('Status ändern','edit-task','sm','data-id="'+t.id+'"','edit')}</div></div>`).join('')}</div></details>`}).join('')}`;
}
async function roadmapView(){
  const [rs]=await Promise.all([api('/api/roadmap/status')]);const r=S.config.approved_roadmap;
  const byId=Object.fromEntries(r.features.map(f=>[f.id,f]));
  const kind={'geplant':'','Grundlage vorhanden':'info','teilweise umgesetzt':'accent','fertig':'ok'};
  return `<div class="card"><div class="card-head"><div><h2>Ausbauplan · 35 genehmigte Erweiterungen</h2><p class="help">Genehmigt heißt nicht fertig. Der Status unten ist ehrlich eingeschätzt und mit Begründung versehen.</p></div>${btn('Entwicklungsplan herunterladen','download-roadmap','sm','','download')}</div>
   <div class="grid g4">${Object.entries(rs.counts).map(([k,v])=>`<div class="metric"><small>${esc(k)}</small><strong>${v}</strong></div>`).join('')}</div></div>
  ${r.phases.map(ph=>{const fs=rs.features.filter(f=>f.phase.startsWith(ph.id+':'));return `<div class="card section"><h2>Phase ${esc(ph.id)} – ${esc(ph.name)}</h2><p class="help" style="margin-bottom:14px">${esc(ph.goal)}</p><div class="stack">${fs.map(f=>`<div class="row top"><div><div class="t">${f.id}. ${esc(f.title)} ${badge(f.status,kind[f.status])}</div><p>${esc(byId[f.id]?.scope||'')}</p><p class="tiny"><b>Stand:</b> ${esc(f.evidence)}</p><p class="tiny pro-only"><b>Abnahmekriterium:</b> ${esc(byId[f.id]?.acceptance_criteria||'')}</p></div></div>`).join('')}</div></div>`}).join('')}
  <div class="card section"><h2>Abgelehnt – wird nicht gebaut</h2><p class="help" style="margin-bottom:12px">Bestehende normale Sicherungs- und Versionsfunktionen bleiben davon unberührt.</p><div class="chips">${rs.rejected.map(f=>badge(f.id+'. '+f.title,'err')).join('')}</div></div>`;
}
function afterProduction(tab){
  if(tab==='live'){S.timers.push(setInterval(async()=>{if(S.area!=='production'||S.tab.production!=='live')return;try{const v=await api(G()+'/live');if($('live-body'))$('live-body').innerHTML=liveBody(v)}catch{}},3000))}
  if(tab==='direct'||tab==='pipeline'){S.timers.push(setInterval(async()=>{try{const r=await api(G()+'/direct');const running=r.jobs.some(j=>j.status==='Läuft');
    if(tab==='direct'&&$('direct-jobs')&&(running||S._wasRunning))$('direct-jobs').innerHTML=r.jobs.map(jobRow).join('');
    if(tab==='pipeline'&&S._wasRunning&&!running){S._wasRunning=false;render();return}
    S._wasRunning=running}catch{}},3000))}
  if(tab==='tasks'&&S.dlcId&&!S._dlcTasksFor?.startsWith(S.dlcId)){api(G()+'/tasks?dlc_id='+enc(S.dlcId)).then(rows=>{S._dlcTasks=rows;S._dlcTasksFor=S.dlcId;render()})}
}

// ---------- Archiv
async function renderArchive(){
  const tab=S.tab.archive||'downloads',d=S.detail;
  const top=head('Archiv · '+ctxLabel(),'Dateien, Sicherungen & Downloads','Originaldateien bleiben unverändert erhalten und bekommen eine Prüfsumme (SHA-256). Hier lädst du alles wieder herunter.')+tabs('archive',{files:d.files.length,zips:d.archives.length});
  $('view').innerHTML=top+(tab==='scan'?loading('Dateien werden geprüft …'):'');
  const body=tab==='downloads'?downloadsView():tab==='files'?filesView():tab==='zips'?zipsView():tab==='scan'?await scanView():backupView();
  $('view').innerHTML=top+body;
}
function downloadsView(){
  const d=S.detail,full=d.archives.filter(a=>a.kind==='Vollprojekt'&&!a.dlc_id),builds=d.archives.filter(a=>a.kind==='Windows-Build');
  const card=(letter,title,text,content)=>`<div class="card"><div class="card-head"><div><p class="kicker">${letter}</p><h2>${title}</h2><p class="help">${text}</p></div></div>${content}</div>`;
  return `<div class="grid g2">
   ${card('A','Vollständiges Originalprojekt','Deine eingelagerten Original-Unreal-/Blender-Dateien, unverändert.',full.length?`<div class="stack">${full.slice(0,3).map(a=>`<div class="row"><div><div class="t">${esc(a.label)}</div><p>${esc(a.original_name)} · ${size(a.size)} · ${day(a.created_at)}</p></div>${btn('Herunterladen','download-archive','sm primary','data-id="'+a.id+'"','download')}</div>`).join('')}</div>`:note('Noch kein Vollprojekt eingelagert. GAMEFORGE kann nichts herunterladen, was nicht eingelagert wurde.','warn','alert')+`<div class="btn-row" style="margin-top:12px">${btn('Vollprojekt-ZIP einlagern','upload-archive','sm','','upload')}</div>`)}
   ${card('B','Claude-Produktionspaket','Spielkonzept, Spielbibel, Referenzen, Prompts, Aufgaben und die 20 Agentenrollen – für Claude Code.',`<div class="btn-row">${btn('Claude-Paket (ZIP)','export-claude','primary','','download')}${btn('Mit allen Originaldateien','export-all','','','download')}</div><p class="tiny" style="margin-top:10px">„Mit allen Originaldateien“ ist nur so vollständig wie das, was du vorher importiert hast.</p>`)}
   ${card('C','Gebautes Spiel (Windows)','Nur echte, erfolgreich erstellte Builds aus „Windows-Spielversion erstellen“ oder von dir eingelagerte Builds.',builds.length?`<div class="stack">${builds.map(a=>`<div class="row"><div><div class="t">${esc(a.label)}</div><p>${esc(a.version)} · ${size(a.size)} · ${day(a.created_at)}</p></div>${btn('Herunterladen','download-archive','sm primary','data-id="'+a.id+'"','download')}</div>`).join('')}</div>`:note('Noch kein Spiel-Build vorhanden. Es wird keiner vorgetäuscht.','info','info'))}
   ${card('D','DLC-Pakete','Je DLC ein eigenes Claude-Paket – eindeutig dem Basisspiel zugeordnet.',d.dlcs.length?`<div class="stack">${d.dlcs.map(x=>`<div class="row"><div><div class="t">${esc(x.title)}</div><p>für ${esc(d.game.title)} ${esc(x.compatible_version||'')}</p></div>${btn('DLC-Paket','export-dlc','sm','data-dlc="'+x.id+'"','download')}</div>`).join('')}</div>`:note('Dieses Spiel hat noch keine DLCs.','info','info'))}</div>`;
}
function filesView(){
  const d=S.detail,files=d.files||[];
  const cats={documents:'Dokumente',code:'Code / Projekte',images:'Bilder',models:'3D / Unreal-Assets',audio:'Audio',video:'Videos',archives:'Archive',other:'Sonstiges'};
  return `<div class="card"><div class="card-head"><div><h2>Originaldateien hinzufügen</h2><p class="help">Dokumente, Bilder, Audio, Videos, .blend, .uproject, Unreal-Dateien, Quellcode – einzeln oder als ganzer Ordner. Nichts wird überschrieben, alles bekommt eine Prüfsumme.</p></div></div>
   <div class="grid g2"><div class="field file-drop"><label for="src-files">Einzelne oder mehrere Dateien</label><input type="file" id="src-files" multiple></div><div class="field file-drop"><label for="src-folder">Ganzer Projektordner</label><input type="file" id="src-folder" webkitdirectory multiple><small>Ordnerstruktur bleibt erhalten (Chrome / Edge).</small></div></div>
   ${selectField('src-dlc','Gehört zu',[['','Basisspiel: '+d.game.title],...d.dlcs.map(x=>[x.id,'DLC: '+x.title])],S.dlcId)}
   <div class="btn-row">${btn('Dateien einlagern','import-files','primary','','upload')}${btn('Ordner einlagern','import-folder','','','folder')}</div>
   <div id="up-progress" class="help" role="status" aria-live="polite" style="margin-top:10px"></div></div>
  <div class="card section"><div class="card-head"><div><h2>Eingelagert (${files.length})</h2><p class="help">${Object.entries(cats).map(([k,l])=>`${l}: ${files.filter(f=>f.category===k).length}`).join(' · ')}</p></div></div>
   <div class="stack">${files.slice(0,200).map(f=>`<div class="row"><div><div class="t" style="overflow-wrap:anywhere">${esc(f.relpath)}</div><p>${esc(cats[f.category]||'Datei')} · ${size(f.size)} · ${day(f.created_at)}${f.dlc_id?' · DLC':''}</p><p class="tiny pro-only mono">SHA-256 ${esc(f.sha256)}</p></div>
    <div class="row-actions">${f.original_name.toLowerCase().endsWith('.zip')?btn('Inhalt ansehen','inspect-zip','sm quiet','data-id="'+f.id+'"','search'):''}${btn('Original','download-file','sm','data-id="'+f.id+'"','download')}</div></div>`).join('')||empty('Noch nichts eingelagert','Füge oben Dateien oder einen Ordner hinzu.')}</div>${files.length>200?`<p class="tiny">Weitere ${files.length-200} Dateien sind im Export-Manifest enthalten.</p>`:''}</div>`;
}
function zipsView(){
  const d=S.detail;
  return `<div class="card"><div class="card-head"><div><h2>Projekt-ZIPs</h2><p class="help">Vollprojekte, Builds, Referenzsammlungen und DLC-Projekte als ZIP – versioniert und eindeutig zugeordnet.</p></div>${btn('ZIP einlagern','upload-archive','primary','','upload')}</div>
   <div class="stack">${d.archives.map(a=>`<div class="row"><div><div class="t">${esc(a.label)} ${badge(a.kind,'plain')}</div><p>${esc(a.original_name)} · ${esc(a.version||'ohne Version')} · ${size(a.size)} · ${day(a.created_at)} · ${a.dlc_id?'DLC '+esc(d.dlcs.find(x=>x.id===a.dlc_id)?.title||''):'Basisspiel'}</p><p class="tiny pro-only mono">SHA-256 ${esc(a.sha256)}</p></div><div class="row-actions">${btn('Herunterladen','download-archive','sm primary','data-id="'+a.id+'"','download')}</div></div>`).join('')||empty('Noch keine ZIPs','Lege z. B. dein bestehendes Unreal-Projekt als Vollprojekt-ZIP ab.')}</div></div>`;
}
async function scanView(){
  const s=await api(G()+'/scan');
  const list=(arr,fmt)=>arr.length?`<ul class="help">${arr.map(x=>`<li>${fmt(x)}</li>`).join('')}</ul>`:'<p class="help">Keine Auffälligkeiten.</p>';
  return `<div class="card"><div class="card-head"><div><h2>Projekt-Scanner</h2><p class="help">${esc(s.note)}</p></div>${btn('Erneut prüfen','goto','sm','data-area="archive" data-tab="scan"','refresh')}</div>
   ${s.ok?note(`Alle ${s.files_checked} Originaldateien und ${s.archives_checked} Archive sind vorhanden und unverändert groß.`,'ok','check'):note('Es gibt Auffälligkeiten – Details unten.','warn','alert')}
   <div class="grid g2 section"><div><h3>Fehlende Dateien</h3>${list(s.missing,x=>esc(x.type+': '+x.name))}</div><div><h3>Größe weicht ab</h3>${list(s.size_mismatch,x=>esc(x.name+' – '+x.problem))}</div>
   <div><h3>Identische Dateien (Duplikate)</h3>${list(s.duplicates,x=>esc(x.files.join(' = ')))}</div><div><h3>Fehlende Referenzbilder</h3>${list(s.reference_images_missing,x=>esc(x))}</div></div><p class="tiny">Geprüft ${when(s.checked_at)}</p></div>`;
}
function backupView(){
  return `<div class="card"><div class="card-head"><div><h2>Ganze Bibliothek sichern</h2><p class="help">Eine ZIP-Datei mit Datenbank, allen importierten Bildern, Originaldateien und Projekt-ZIPs – für den Umzug auf einen anderen PC oder als Sicherheitskopie.</p></div></div>
   <div class="btn-row">${btn('Komplettsicherung herunterladen','backup','primary lg','','shield')}</div>
   <details class="more"><summary>Wiederherstellen</summary><p class="help" style="margin-top:8px">GAMEFORGE schließen, den Ordner GAMEFORGE_DATA aus der Sicherung neben app.py legen (vorher den aktuellen Ordner umbenennen, nicht löschen), GAMEFORGE neu starten.</p></details></div>
   <div class="card section"><h2>Automatische Sicherungen</h2><p class="help" style="margin-top:6px">Vor jeder Chat-Übernahme und jeder Wiederherstellung legt GAMEFORGE einen Versionsstand an. Vor Datenbank-Aktualisierungen wird die Datenbank nach <span class="mono">GAMEFORGE_DATA/backups</span> kopiert.</p>${btn('Versionsstände ansehen','goto','sm','data-area="games" data-tab="versions"','clock')}</div>`;
}

// ------------------------------------------------------------------ Chat
function chatSkeleton(){
  const g=currentGame();
  $('chat').innerHTML=`<div class="chat-head"><div class="top"><h2>${icon('chat')}Mit GAMEFORGE sprechen</h2><button type="button" class="icon-btn" data-act="chat-close" aria-label="Chat schließen">${icon('x')}</button></div>
   <div class="chat-ctx"><select id="chat-game" class="ctx-select" aria-label="Projekt für den Chat">${S.games.map(x=>`<option value="${esc(x.id)}" ${x.id===S.gameId?'selected':''}>${esc(x.title)}</option>`).join('')}</select>
    <select id="chat-dlc" class="ctx-select" aria-label="Basisspiel oder DLC"><option value="">Basisspiel</option>${(S.detail?.dlcs||[]).map(d=>`<option value="${esc(d.id)}" ${d.id===S.dlcId?'selected':''}>DLC: ${esc(d.title)}</option>`).join('')}</select></div>
   <div class="chat-mode"><span id="chat-ai">KI-Status wird geprüft …</span><div class="seg" role="group" aria-label="Antwortmodus"><button type="button" data-prov="claude" aria-pressed="${S.chat.provider==='claude'}">Claude (echte KI)</button><button type="button" data-prov="offline" aria-pressed="${S.chat.provider==='offline'}">Offline</button></div></div></div>
   <div class="chat-feed" id="chat-feed" aria-live="polite">${g?loading('Gespräch wird geladen …'):''}</div>
   <div class="chat-input"><label for="chat-text" class="sr-only">Deine Nachricht</label><textarea id="chat-text" placeholder="${g?'Idee, Frage oder Änderungswunsch … (Enter sendet, Umschalt+Enter = neue Zeile)':'Beschreibe dein Spiel – daraus wird ein neues Projekt.'}"></textarea>
    <div class="bar-row"><div class="btn-row">${g?btn('Als neues Spiel','chat-newgame','sm quiet','','plus'):''}</div>${btn(g?'Senden':'Spiel anlegen',g?'chat-send':'chat-newgame','primary','id="chat-send"',g?'send':'plus')}</div>
    <div class="chat-status" id="chat-status" role="status"></div></div>`;
  $('chat-game').onchange=async e=>{await selectGame(e.target.value);renderNav();chatSkeleton();loadChat();render()};
  $('chat-dlc').onchange=async e=>{S.dlcId=e.target.value;renderNav();loadChat();render()};
  const t=$('chat-text');const key=()=>S.gameId+'|'+S.dlcId;t.value=S.chat.draft[key()]||'';
  t.oninput=()=>{S.chat.draft[key()]=t.value};
  t.onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();g?sendChat():newGameWizard({vision:t.value})}};
  updateAiLine();
}
async function updateAiLine(){
  if(!S.chat.ai){try{S.chat.ai=await api('/api/ai/status')}catch{S.chat.ai={available:false,detail:'Status unbekannt'}}}
  const el=$('chat-ai');if(!el)return;
  if(S.chat.provider==='claude')el.innerHTML=!S.chat.ai.available?`<span class="dot err"></span> Claude Code nicht gefunden – nur Offline möglich`
    :S.chat.ai.logged_in===false?`<span class="dot err"></span> Claude Code ist nicht angemeldet <button type="button" class="link-btn" data-act="login-help">So geht's</button>`
    :`<span class="dot ok"></span> Antwortet über deine lokale Claude-Code-Anmeldung`;
  else el.innerHTML=`<span class="dot warn"></span> Offline: Vorlagen und echte Projektdaten, keine KI`;
}
function openChat(){S.chat.open=true;document.body.classList.add('chat-open');$('chat').setAttribute('aria-hidden','false');$('chat-fab').setAttribute('aria-expanded','true');chatSkeleton();loadChat();setTimeout(()=>$('chat-text')?.focus(),80)}
function closeChat(){S.chat.open=false;document.body.classList.remove('chat-open');$('chat').setAttribute('aria-hidden','true');$('chat-fab').setAttribute('aria-expanded','false');$('chat-fab').focus()}
const WHO={user:'Du',claude:'Claude · echte KI-Antwort',data:'GAMEFORGE · Projektdaten (keine KI)',offline:'GAMEFORGE · Offline-Vorlage (keine KI)',system:'GAMEFORGE · Status',manual:'GAMEFORGE'};
async function loadChat(scroll=true){
  const feedEl=$('chat-feed');if(!feedEl)return;
  if(!S.gameId){feedEl.innerHTML=`<div class="msg ai"><div class="who">GAMEFORGE</div><div class="body">Noch kein Projekt vorhanden. Beschreibe unten deine Spielidee – ich lege daraus mit dir ein neues Spiel an.</div></div>`;return}
  let feed;try{feed=await api(G()+'/ideas?'+new URLSearchParams({dlc_id:S.dlcId}))}catch(e){feedEl.innerHTML=note(esc(e.message),'err','alert');return}
  const bySource={};[...feed.changes.map(c=>({t:'c',o:c})),...feed.suggestions.map(s=>({t:'s',o:s}))].forEach(x=>{(bySource[x.o.source_id||'_']=bySource[x.o.source_id||'_']||[]).push(x)});
  const card=x=>x.t==='c'?changeCard(x.o):suggestionCard(x.o);
  let html=feed.messages.map(m=>{const me=m.role==='user';const who=me?WHO.user:(WHO[m.provider]||'GAMEFORGE');
    const kind=m.provider==='claude'?badge('KI','accent'):m.provider==='offline'?badge('keine KI','warn'):m.provider==='data'?badge('echte Daten','info'):'';
    return `<div class="msg ${me?'me':'ai'}"><div class="who">${esc(who)} ${me?'':kind}<span style="font-weight:500">${when(m.created_at)}</span></div><div class="body">${esc(m.body)}</div></div>`+(bySource[m.id]||[]).map(card).join('')}).join('');
  html+=(bySource['_']||[]).map(card).join('');
  if(!feed.messages.length)html=`<div class="msg ai"><div class="who">GAMEFORGE</div><div class="body">Hallo! Wir sprechen über ${ctxLabel()}. Erzähl mir deine Idee, frag nach dem Stand oder wünsch dir eine Änderung. Ich ändere nichts ohne deine Freigabe.</div></div>
   <div class="suggest-chips">${['Was ist wirklich fertig, was fehlt?','Erstelle einen Boss mit drei Kampfphasen.','Welche Referenzbilder fehlen noch?','Erstelle ein DLC mit drei neuen Regionen.'].map(q=>`<button type="button" class="chip" data-act="chat-quick">${esc(q)}</button>`).join('')}</div>`;
  if(S.chat.busy)html+=`<div class="msg ai typing"><div class="who">${S.chat.provider==='claude'?'Claude':'GAMEFORGE'}</div><div class="body">${S.chat.provider==='claude'?'Claude denkt nach – das kann bis zu zwei Minuten dauern':'Wird erstellt'}<span class="typing-dots"><i></i><i></i><i></i></span></div></div>`;
  feedEl.innerHTML=html;if(scroll)feedEl.scrollTop=feedEl.scrollHeight;
}
async function sendChat(text){
  const t=$('chat-text');const msg=(text??t.value).trim();
  if(!msg){setChatStatus('Bitte zuerst eine Nachricht schreiben.',true);return}
  if(S.chat.busy)return;
  if(S.chat.provider==='claude'&&S.chat.ai&&!S.chat.ai.available){setChatStatus('Claude Code wurde nicht gefunden. Wechsle auf „Offline“ oder installiere Claude Code.',true);return}
  if(S.chat.provider==='claude'&&S.chat.ai?.logged_in===false){setChatStatus(S.chat.ai.detail,true);return}
  S.chat.busy=true;const gid=S.gameId,did=S.dlcId;
  if(!text){t.value='';S.chat.draft[gid+'|'+did]=''}
  const feedEl=$('chat-feed');feedEl.insertAdjacentHTML('beforeend',`<div class="msg me"><div class="who">Du · gerade eben</div><div class="body">${esc(msg)}</div></div>`);
  loadChatTyping();$('chat-send').disabled=true;setChatStatus('');
  try{await api('/api/games/'+enc(gid)+'/ideas',{method:'POST',body:{message:msg,dlc_id:did,provider:S.chat.provider}});
    setChatStatus(S.chat.provider==='claude'?'Antwort gespeichert. Vorschläge prüfst du direkt hier im Chat.':'Gespeichert. Offline-Antworten sind Vorlagen, keine KI.')}
  catch(e){setChatStatus('Keine KI-Antwort: '+e.message+' Deine Nachricht ist gespeichert, es wurde nichts verändert.',true)}
  finally{S.chat.busy=false;if($('chat-send'))$('chat-send').disabled=false;if(S.gameId===gid&&S.dlcId===did)await loadChat();if(S.area==='studio')render()}
}
function loadChatTyping(){const f=$('chat-feed');f.insertAdjacentHTML('beforeend',`<div class="msg ai typing"><div class="who">${S.chat.provider==='claude'?'Claude':'GAMEFORGE'}</div><div class="body">${S.chat.provider==='claude'?'Claude denkt nach – das kann bis zu zwei Minuten dauern':'Wird erstellt'}<span class="typing-dots"><i></i><i></i><i></i></span></div></div>`);f.scrollTop=f.scrollHeight}
function setChatStatus(m,err=false){const el=$('chat-status');if(el){el.textContent=m;el.classList.toggle('err',err)}}

// ------------------------------------------------------------------ Assistenten & Formulare
function newGameWizard(prefill={}){
  const W={step:0,title:'',vision:prefill.vision||'',genre:'Open World / Action-Adventure',style:'Realistisch',camera:'Third Person',platform:'Windows-PC',wishes:'',summary:''};
  const GENRES=['Open World / Action-Adventure','Rollenspiel (RPG)','Shooter','Jump & Run','Rennspiel','Strategie','Horror','Puzzle / Rätsel','Simulation'];
  const STYLES=['Retro','Pixel-Art','Stilisiert','Realistisch','AAA+ fotorealistisch'];
  const CAMS=['Third Person','First Person','Third/First Hybrid','Top-Down','Seitenansicht (2D)'];
  const PLATS=['Windows-PC','Windows-PC + Konsole','Mobil','Web-Browser'];
  const steps=['Idee','Stil & Plattform','Details','Zusammenfassung'];
  const chips=(key,opts)=>`<div class="chips" role="group">${opts.map(o=>`<button type="button" class="chip" data-w="${key}" data-v="${esc(o)}" aria-pressed="${W[key]===o}">${esc(o)}</button>`).join('')}</div>`;
  const save=()=>{if($('w-title'))W.title=val('w-title');if($('w-vision'))W.vision=$('w-vision').value.trim();if($('w-wishes'))W.wishes=$('w-wishes').value.trim();if($('w-summary'))W.summary=$('w-summary').value.trim()};
  const draw=()=>{
    const bar=`<div class="wizard-steps" aria-label="Schritt ${W.step+1} von ${steps.length}">${steps.map((_,i)=>`<i class="${i<=W.step?'on':''}"></i>`).join('')}</div><p class="kicker">Schritt ${W.step+1} von ${steps.length} · ${steps[W.step]}</p>`;
    let b='';
    if(W.step===0)b=field('w-title','Wie soll dein Spiel heißen?',W.title,{ph:'z. B. OLYMPUS RISING',help:'Kannst du später jederzeit ändern.'})+field('w-vision','Beschreibe deine Idee in eigenen Worten',W.vision,{area:true,rows:150,ph:'z. B. Ein Open-World-Spiel mit antiken Göttern, in dem ich als Sterblicher …'});
    if(W.step===1)b=`<p class="label">Genre</p>${chips('genre',GENRES)}<p class="label" style="margin-top:16px">Grafikstil</p>${chips('style',STYLES)}<p class="label" style="margin-top:16px">Perspektive</p>${chips('camera',CAMS)}<p class="label" style="margin-top:16px">Plattform</p>${chips('platform',PLATS)}`;
    if(W.step===2)b=field('w-summary','Kurzbeschreibung für die Bibliothek (optional)',W.summary,{ph:'Ein Satz, der dein Spiel beschreibt'})+field('w-wishes','Besondere Wünsche (optional)',W.wishes,{area:true,rows:120,ph:'z. B. Bosskämpfe mit Phasen, Unterwasserwelt, Tag-Nacht-Wechsel …',help:'Wird als Wunschliste gespeichert – nicht als fertige Spielregel.'});
    if(W.step===3)b=`<dl class="summary-list"><dt>Titel</dt><dd>${esc(W.title)}</dd><dt>Idee</dt><dd>${esc(W.vision||'–')}</dd><dt>Genre</dt><dd>${esc(W.genre)}</dd><dt>Stil</dt><dd>${esc(W.style)}</dd><dt>Perspektive</dt><dd>${esc(W.camera)}</dd><dt>Plattform</dt><dd>${esc(W.platform)}</dd><dt>Wünsche</dt><dd>${esc(W.wishes||'–')}</dd></dl>
      <div style="margin-top:16px">${note('GAMEFORGE legt an: eigenes Projekt, Spielbibel mit deinen Angaben, 25 Entwicklungsaufgaben, eigenen Arbeitsordner mit den 20 Agentenrollen. Es werden keine Spielinhalte erfunden.','info','info')}</div>`;
    modal({title:'Neues Spiel erstellen',wide:true,body:bar+b,actions:[
      ...(W.step?[{label:'Zurück',onClick:()=>{save();W.step--;draw();return false}}]:[{label:'Abbrechen'}]),
      W.step<3?{label:'Weiter',primary:true,onClick:()=>{save();if(W.step===0&&!W.title)throw Error('Bitte gib deinem Spiel einen Namen.');W.step++;draw();return false}}
      :{label:'Projekt anlegen',primary:true,onClick:async()=>{const g=await api('/api/games',{method:'POST',body:{title:W.title,summary:W.summary||short(W.vision,200),genre:W.genre,style:W.style,camera:W.camera,platform:W.platform,vision:W.vision,wishes:W.wishes}});
        S.games=await api('/api/games');await selectGame(g.id);S.home=null;toast(W.title+' wurde angelegt.');go('games','overview');if(S.chat.open){chatSkeleton();loadChat()}}}]});
    document.querySelectorAll('[data-w]').forEach(b=>b.onclick=()=>{W[b.dataset.w]=b.dataset.v;draw()});
  };
  draw();
}
function importGameWizard(){
  modal({title:'Vorhandenes Spiel importieren',body:`<p class="help" style="margin-bottom:16px">Lege zuerst das Projekt an. Danach wählst du Dateien, einen ganzen Ordner oder ein ZIP aus – alles wird unverändert und mit Prüfsumme eingelagert.</p>${field('i-title','Name des Spiels','',{ph:'z. B. AION (Originalprojekt)'})}${field('i-sum','Kurzbeschreibung (optional)','')}
    <p class="help">Hast du AION oder GENESIS? Die sind schon da – lege die Dateien dort ab: ${btn('AION öffnen','import-into','sm quiet','data-id="aion-2026"')} ${btn('GENESIS öffnen','import-into','sm quiet','data-id="genesis"')}</p>`,
   actions:[{label:'Abbrechen'},{label:'Anlegen & Dateien wählen',primary:true,onClick:async()=>{const t=val('i-title');if(!t)throw Error('Bitte einen Namen eingeben.');const g=await api('/api/games',{method:'POST',body:{title:t,summary:val('i-sum')}});S.games=await api('/api/games');await selectGame(g.id);S.home=null;go('archive','files');toast('Projekt angelegt. Wähle jetzt Dateien oder einen Ordner.')}}]});
}
function editGame(){const g=S.detail.game;
  modal({title:'Projekt bearbeiten',body:field('e-title','Titel',g.title)+field('e-sum','Kurzbeschreibung',g.summary,{area:true,rows:90})+selectField('e-status','Status',S.config.states,g.status,'„Fertig“ geht nur, wenn alle Aufgaben abgenommen, Referenzen freigegeben und Build sowie Vollprojekt archiviert sind.')+`<div class="grid g2">${field('e-ver','Version',g.version)}${field('e-genre','Genre',g.genre)}${field('e-style','Grafikstil',g.style)}${field('e-cam','Perspektive',g.camera)}</div>`,
   actions:[{label:'Abbrechen'},{label:'Speichern',primary:true,onClick:async()=>{await api(G(),{method:'PUT',body:{title:val('e-title'),summary:val('e-sum'),status:val('e-status'),version:val('e-ver'),genre:val('e-genre'),style:val('e-style'),camera:val('e-cam')}});await refreshAll();S.home=null;render();toast('Projekt gespeichert.')}}]})}
function snapshotDialog(){const g=S.detail.game;modal({title:'Projekt sichern',body:field('s-ver','Bezeichnung',g.version)+field('s-notes','Was hat sich geändert? (optional)','',{area:true,rows:90}),actions:[{label:'Abbrechen'},{label:'Versionsstand sichern',primary:true,onClick:async()=>{await api(G()+'/snapshots',{method:'POST',body:{version:val('s-ver'),notes:val('s-notes')}});await loadDetail();render();toast('Versionsstand gesichert.')}}]})}
function addDlcDialog(){const g=S.detail.game;modal({title:'Neues DLC für '+g.title,body:field('n-title','Name des DLCs','',{ph:'z. B. Die Tiefen des Poseidon'})+field('n-sum','Worum geht es?','',{area:true,rows:100})+field('n-compat','Benötigte Version des Basisspiels',g.version),actions:[{label:'Abbrechen'},{label:'DLC anlegen',primary:true,onClick:async()=>{const r=await api(G()+'/dlcs',{method:'POST',body:{title:val('n-title'),summary:val('n-sum'),compatible_version:val('n-compat')}});await loadDetail();S.dlcId=r.id;render();toast('DLC angelegt und als Arbeitsbereich gewählt.')}}]})}
function editDlcDialog(id){const x=S.detail.dlcs.find(d=>d.id===id);if(!x)return;
  modal({title:'DLC bearbeiten',body:field('x-title','Name',x.title)+field('x-sum','Beschreibung',x.summary,{area:true,rows:90})+`<div class="grid g2">${selectField('x-status','Status',S.config.states,x.status)}${field('x-ver','DLC-Version',x.version)}</div>`+field('x-compat','Benötigte Basisversion',x.compatible_version)+'<p class="help">Story, Missionen und Welt des DLCs bearbeitest du im Kreativstudio › Spielbibel.</p>',
   actions:[{label:'Abbrechen'},{label:'Speichern',primary:true,onClick:async()=>{await api(G()+'/dlcs/'+id,{method:'PUT',body:{title:val('x-title'),summary:val('x-sum'),status:val('x-status'),version:val('x-ver'),compatible_version:val('x-compat'),design:x.design}});await loadDetail();render();toast('DLC gespeichert.')}}]})}
function manualChangeDialog(prefill={}){
  const dlc=currentDlc();const fields=dlc?Object.keys(DLC_LABELS).map(k=>[k,DLC_LABELS[k]]):S.config.fields;
  modal({title:'Änderung selbst formulieren',body:selectField('m-sec','Welcher Bereich?',fields,prefill.section||fields[0][0])+field('m-sum','Was wird geändert? (kurz)',prefill.summary||'')+field('m-text','Neuer Text, der ergänzt wird',prefill.text||'',{area:true,rows:160})+note('Das ist erst ein Entwurf. Übernommen wird er erst, wenn du ihn freigibst.','info','info'),
   actions:[{label:'Abbrechen'},{label:'Als Entwurf vormerken',primary:true,onClick:async()=>{await api(G()+'/changes',{method:'POST',body:{dlc_id:S.dlcId,section:val('m-sec'),summary:val('m-sum'),mode:'append',new_text:$('m-text').value}});
     if(prefill.rejectId)await api(G()+'/changes/'+prefill.rejectId+'/decision',{method:'POST',body:{action:'reject'}});
     if(S.chat.open)loadChat();if(S.area==='studio')render();toast('Änderungsentwurf erstellt. Jetzt prüfen und übernehmen.')}}]})}
function addRefDialog(bundle){
  const cats=Object.entries(S.config.categories);
  modal({title:bundle?'Komplettes Bildset anlegen':'Einzelnes Referenzbild anlegen',body:field('r-name','Was soll abgebildet werden?','',{ph:'z. B. Poseidon'})+selectField('r-cat','Art',cats,'character')+(bundle?'<p class="help" style="margin:-6px 0 14px">GAMEFORGE legt automatisch alle nötigen Ansichten an (z. B. Front, Seite, Rücken, Größenvergleich).</p>':selectField('r-view','Ansicht',[],''))+field('r-details','Verbindliche Designdetails','',{area:true,rows:100,ph:'Farben, Kleidung, Größe, Besonderheiten, Kanon …'})+`<p class="help">Gehört zu: <b>${ctxLabel()}</b></p>`,
   actions:[{label:'Abbrechen'},{label:'Anlegen',primary:true,onClick:async()=>{await api(G()+'/refs'+(bundle?'/bundle':''),{method:'POST',body:{name:val('r-name'),category:val('r-cat'),view:bundle?'front':val('r-view'),details:val('r-details'),dlc_id:S.dlcId}});await loadDetail();render();toast(bundle?'Bildset angelegt.':'Bildauftrag angelegt.')}}],
   onOpen:()=>{if(bundle)return;const c=$('r-cat');const fill=()=>{$('r-view').innerHTML=S.config.views[c.value].map(v=>`<option value="${v}">${esc(S.config.view_labels[v]||v)}</option>`).join('')};c.onchange=fill;fill()}});
}
async function copyPrompt(id){
  const r=await api(G()+'/refs/'+id+'/prompt');
  let copied=false;try{await navigator.clipboard.writeText(r.prompt);copied=true}catch{}
  modal({title:copied?'Prompt kopiert':'Prompt zum Kopieren',wide:true,body:(copied?note('Der Prompt ist in der Zwischenablage. Füge ihn jetzt in ChatGPT ein und lass das Bild erzeugen.','ok','check'):note('Automatisches Kopieren war nicht möglich. Markiere den Text und kopiere ihn mit Strg+C.','warn','alert'))+`<pre class="log" id="prompt-text" tabindex="0">${esc(r.prompt)}</pre>`,actions:[{label:'Schließen',primary:true}]});
}
function uploadRefDialog(id){const r=S.detail.refs.find(x=>x.id===id);
  modal({title:'Referenzbild hinzufügen',body:`<p class="help">${esc(r.name)} · ${esc(S.config.view_labels[r.view]||r.view)}. PNG, JPG oder WEBP, höchstens 30 MB.</p><div class="field file-drop" style="margin-top:12px"><input id="r-file" type="file" accept="image/png,image/jpeg,image/webp" aria-label="Bilddatei"></div><div id="r-prog" class="help"></div>`,
   actions:[{label:'Abbrechen'},{label:'Bild hinzufügen',primary:true,onClick:async()=>{const f=$('r-file').files[0];if(!f)throw Error('Bitte ein Bild auswählen.');
     await upload(G()+'/upload?'+new URLSearchParams({reference_id:id,dlc_id:r.dlc_id||'',filename:f.name}),f,p=>{$('r-prog').textContent='Übertrage … '+Math.round(p*100)+' %'});await loadDetail();render();toast('Bild hinzugefügt. Prüfe es jetzt und gib es frei.')}}]})}
function uploadArchiveDialog(){const g=S.detail.game;
  modal({title:'ZIP einlagern',body:selectField('z-kind','Was ist es?',S.config.kinds,'Vollprojekt')+field('z-label','Bezeichnung','Projektarchiv '+g.title)+field('z-ver','Version',g.version)+selectField('z-dlc','Gehört zu',[['','Basisspiel: '+g.title],...S.detail.dlcs.map(d=>[d.id,'DLC: '+d.title])],S.dlcId)+`<div class="field file-drop"><label for="z-file">ZIP-Datei</label><input type="file" id="z-file" accept=".zip,application/zip"></div><div id="z-prog" class="help" role="status"></div>`,
   actions:[{label:'Abbrechen'},{label:'Einlagern',primary:true,onClick:async()=>{const f=$('z-file').files[0];if(!f)throw Error('Bitte eine ZIP-Datei auswählen.');let kind=val('z-kind');const did=val('z-dlc');if(did&&kind==='Vollprojekt')kind='DLC-Vollprojekt';
     await upload(G()+'/upload?'+new URLSearchParams({kind,label:val('z-label'),version:val('z-ver'),dlc_id:did,filename:f.name}),f,p=>{$('z-prog').textContent='Übertrage … '+Math.round(p*100)+' % von '+size(f.size)});await loadDetail();render();toast('ZIP eingelagert und zugeordnet.')}}]})}
async function uploadSources(folder){
  const input=$(folder?'src-folder':'src-files');const files=[...(input?.files||[])];
  if(!files.length){toast('Bitte zuerst '+(folder?'einen Ordner':'Dateien')+' auswählen.',true);return}
  if(files.length>3500&&!await ask('Sehr viele Dateien',`${files.length} einzelne Dateien – als ZIP geht es meist zuverlässiger. Trotzdem fortfahren?`,'Fortfahren'))return;
  const did=val('src-dlc'),prog=$('up-progress');let ok=0;
  for(const f of files){const rel=f.webkitRelativePath||f.name;
    try{await upload(G()+'/files?'+new URLSearchParams({filename:f.name,relpath:rel,dlc_id:did}),f,p=>{prog.textContent=`Datei ${ok+1} von ${files.length}: ${rel} – ${Math.round(p*100)} %`});ok++}
    catch(e){toast(`Import angehalten bei ${rel}: ${e.message}`,true);break}}
  await loadDetail();render();toast(`${ok} von ${files.length} Dateien eingelagert.`,ok<files.length);
}
async function inspectZip(id){const z=await api(G()+'/files/'+id+'/zip-index');
  modal({title:'Inhalt von '+z.filename,wide:true,body:`<p class="help">${z.total_members} Einträge. Vorschau der ersten ${Math.min(120,z.members.length)}. Das Archiv wird dabei nicht entpackt oder ausgeführt.</p><pre class="log">${esc(z.members.slice(0,120).map(m=>m.path+'   '+size(m.size)).join('\n'))}</pre>${z.potentially_large?note('Sehr großes Archiv – Speicherplatz vor dem Entpacken prüfen.','warn','alert'):''}`,actions:[{label:'Schließen',primary:true}]})}
function editTaskDialog(id){const t=[...S.detail.tasks,...(S._dlcTasks||[])].find(x=>x.id===id);if(!t)return;
  modal({title:t.title,body:`<p class="help">${esc(t.description)}</p><p class="help" style="margin:8px 0 16px"><b>Abnahmekriterium:</b> ${esc(t.acceptance)}</p>`+selectField('t-status','Tatsächlicher Stand',S.config.task_statuses,t.status)+field('t-ev','Prüfbeleg (Pflicht für „Getestet“/„Abgenommen“)',t.evidence,{area:true,rows:120,ph:'z. B. Build-Protokoll, Testergebnis, Dateipfad, Screenshot-Name'}),
   actions:[{label:'Abbrechen'},{label:'Speichern',primary:true,onClick:async()=>{await api(G()+'/tasks/'+id,{method:'PUT',body:{status:val('t-status'),evidence:$('t-ev').value}});await loadDetail();S._dlcTasksFor='';render();toast('Aufgabe aktualisiert.')}}]})}
async function showJob(id){const j=await api(G()+'/direct/jobs/'+id);
  modal({title:(JOB_LABEL[j.kind]||j.kind)+' · '+j.status,wide:true,body:`<p class="help">Gestartet ${when(j.created_at)}${j.ended_at?' · beendet '+when(j.ended_at):''}${j.exit_code!==null&&j.exit_code!==undefined?' · Rückgabewert '+j.exit_code:''}</p>${j.status==='Fehlgeschlagen'?note('Der Auftrag ist nicht erfolgreich abgeschlossen worden. Unten steht die echte Ausgabe. Prüfe sie, bevor du es erneut versuchst.','err','alert'):''}<pre class="log">${esc(j.log||'Noch keine Ausgabe.')}</pre>`,
   actions:[...(['Fehlgeschlagen','Unterbrochen'].includes(j.status)?[{label:'Erneut versuchen',onClick:async()=>{await retryJob(id)}}]:[]),{label:'Schließen',primary:true}]})}
async function retryJob(id){if(!await ask('Erneut versuchen?','Der Auftrag wird mit identischem Auftragstext neu gestartet. Prüfe vorher, ob die Ursache behoben ist (z. B. MCP-Verbindung, Anmeldung).','Neu starten'))return;await api(G()+'/direct/jobs/'+id+'/retry',{method:'POST',body:{}});toast('Auftrag neu gestartet.');render()}

// ------------------------------------------------------------------ Aktionen
const ACT={
  'goto':el=>go(el.dataset.area,el.dataset.tab),
  'open-game':async el=>{await selectGame(el.dataset.id);go('games','overview')},
  'next-step':async el=>{await selectGame(el.dataset.id);go(el.dataset.area,el.dataset.tab)},
  'chat-open':()=>openChat(),'chat-close':()=>closeChat(),
  'chat-for':async el=>{await selectGame(el.dataset.id);renderNav();openChat()},
  'chat-send':()=>sendChat(),'chat-quick':el=>sendChat(el.textContent),
  'chat-newgame':()=>newGameWizard({vision:$('chat-text')?.value||''}),
  'new-game':()=>newGameWizard(),'import-game':()=>importGameWizard(),
  'import-into':async el=>{closeModal();await selectGame(el.dataset.id);go('archive','files')},
  'health-refresh':()=>{S.chat.ai=null;loadHealth(true);if(S.chat.open)updateAiLine()},
  'login-help':()=>modal({title:'Claude Code anmelden',body:`<ol class="help" style="font-size:15px;color:var(--text-2);padding-left:20px"><li>Windows-Taste drücken, <b>cmd</b> tippen, Enter.</li><li>Eingeben: <span class="mono">claude auth login</span> und Enter.</li><li>Im Browser mit deinem Claude-Konto anmelden.</li><li>Zurück in GAMEFORGE: „Erneut prüfen“ klicken.</li></ol>`,actions:[{label:'Erneut prüfen',primary:true,onClick:()=>{S.chat.ai=null;updateAiLine();loadHealth(true)}}]}),
  'lib-filter':el=>{S.filter.status=el.dataset.k;renderLibrary()},'lib-reset':()=>{S.filter={q:'',status:'all'};renderLibrary()},
  'edit-game':()=>editGame(),
  'delete-game':()=>{const g=S.detail.game;modal({title:'„'+g.title+'“ löschen?',body:note(`Folgendes wandert in den Papierkorb: Spielbibel, ${S.detail.dlcs.length} DLCs, ${S.detail.refs.length} Referenzaufträge, ${S.detail.files.length} Originaldateien, ${S.detail.archives.length} Projekt-ZIPs, Chatverlauf, Aufgaben und Versionsstände. Vorher wird alles als geprüftes ZIP gesichert. Du kannst das Spiel jederzeit wiederherstellen.`,'warn','alert')+'<div style="height:14px"></div>'+field('del-confirm','Zur Bestätigung den Spielnamen eintippen: '+g.title,'',{ph:g.title}),
    actions:[{label:'Abbrechen'},{label:'In den Papierkorb legen',danger:true,onClick:async()=>{const r=await api(G()+'?'+new URLSearchParams({confirm:$('del-confirm').value.trim()}),{method:'DELETE'});S.gameId='';S.dlcId='';S.home=null;await refreshAll();toast(r.title+' liegt jetzt im Papierkorb.');go('games','list');render()}}]})},
  'trash-restore':async el=>{const r=await api('/api/trash/'+enc(el.dataset.name)+'/restore',{method:'POST',body:{}});S.home=null;await refreshAll();await selectGame(r.restored);toast(r.title+' wurde wiederhergestellt.');render()},
  'trash-purge':el=>modal({title:'Endgültig löschen?',body:note('„'+esc(el.dataset.title)+'“ wird unwiderruflich gelöscht – inklusive aller Dateien in dieser Sicherung. Das kann nicht rückgängig gemacht werden.','err','alert')+'<div style="height:14px"></div>'+field('purge-confirm','Zur Bestätigung ENDGÜLTIG eintippen','',{ph:'ENDGÜLTIG'}),
    actions:[{label:'Abbrechen'},{label:'Endgültig löschen',danger:true,onClick:async()=>{await api('/api/trash/'+enc(el.dataset.name)+'?'+new URLSearchParams({confirm:$('purge-confirm').value.trim()}),{method:'DELETE'});toast('Endgültig gelöscht.');loadTrash()}}]}),'snapshot':()=>snapshotDialog(),
  'restore-snapshot':async el=>{if(!await ask('Versionsstand wiederherstellen?','Spielbibel und Projektangaben werden auf diesen Stand zurückgesetzt. Der aktuelle Stand wird vorher automatisch gesichert. DLCs und Dateien bleiben unverändert.','Wiederherstellen'))return;await api(G()+'/snapshots/'+el.dataset.id+'/restore',{method:'POST',body:{}});await refreshAll();render();toast('Wiederhergestellt. Der vorherige Stand wurde gesichert.')},
  'add-dlc':()=>addDlcDialog(),'edit-dlc':el=>editDlcDialog(el.dataset.dlc),
  'dlc-plan':el=>{S.dlcId=el.dataset.dlc;go('studio','bible')},
  'export-claude':()=>download(G()+'/export'+(S.dlcId?'?dlc_id='+enc(S.dlcId):'')),
  'export-all':()=>download(G()+'/export?include_source=1'),
  'export-dlc':el=>download(G()+'/export?dlc_id='+enc(el.dataset.dlc)),
  'download-archive':el=>download('/api/archive/'+el.dataset.id),'download-file':el=>download('/api/file/'+el.dataset.id),
  'download-roadmap':()=>download('/api/roadmap'),'backup':()=>download('/api/backup'),
  'upload-archive':()=>uploadArchiveDialog(),'import-files':()=>uploadSources(false),'import-folder':()=>uploadSources(true),'inspect-zip':el=>inspectZip(el.dataset.id),
  'manual-change':()=>manualChangeDialog(),
  'change-apply':async el=>{if(!await ask('Änderung übernehmen?','Der Text wird in die Spielbibel bzw. DLC-Planung geschrieben. Vorher wird automatisch ein Versionsstand gesichert. Im eigentlichen Spiel ist damit noch nichts umgesetzt.','Übernehmen'))return;await api(G()+'/changes/'+el.dataset.id+'/decision',{method:'POST',body:{action:'apply'}});await loadDetail();afterDecision('Übernommen und gesichert.')},
  'change-reject':async el=>{await api(G()+'/changes/'+el.dataset.id+'/decision',{method:'POST',body:{action:'reject'}});afterDecision('Abgelehnt. Nichts wurde geändert.')},
  'change-modify':async el=>{const feed=await api(G()+'/ideas?'+new URLSearchParams({dlc_id:S.dlcId}));const c=feed.changes.find(x=>x.id===el.dataset.id);if(c)manualChangeDialog({section:c.section,summary:c.summary,text:c.new_text,rejectId:c.id})},
  'idea-accept':async el=>{await api(G()+'/ideas/'+el.dataset.id+'/decision',{method:'POST',body:{action:'accept'}});afterDecision('Idee angenommen. Sie wird im Claude-Paket berücksichtigt.')},
  'idea-reject':async el=>{await api(G()+'/ideas/'+el.dataset.id+'/decision',{method:'POST',body:{action:'reject'}});afterDecision('Idee abgelehnt.')},
  'idea-integrate':async el=>{if(!await ask('In die Spielbibel übernehmen?','Die Idee wird an den passenden Bereich angehängt. Vorher wird ein Versionsstand gesichert.','Übernehmen'))return;await api(G()+'/ideas/'+el.dataset.id+'/decision',{method:'POST',body:{action:'integrate'}});await loadDetail();afterDecision('In die Spielbibel übernommen.')},
  'bible-jump':el=>{const d=$('bg-'+el.dataset.i);if(d){d.open=true;d.scrollIntoView({behavior:'smooth',block:'start'})}},
  'save-bible':async()=>{const bible={};S.config.fields.forEach(([k])=>bible[k]=$('b_'+k)?.value??S.detail.game.bible[k]??'');await api(G(),{method:'PUT',body:{bible}});await refreshAll();S.home=null;render();toast('Spielbibel gespeichert.')},
  'save-dlc-design':async()=>{const x=currentDlc(),design={};Object.keys(DLC_LABELS).forEach(k=>design[k]=$('d_'+k)?.value??'');await api(G()+'/dlcs/'+x.id,{method:'PUT',body:{design}});await loadDetail();render();toast('DLC-Planung gespeichert.')},
  'add-ref':()=>addRefDialog(false),'add-ref-bundle':()=>addRefDialog(true),'copy-prompt':el=>copyPrompt(el.dataset.id),'upload-ref':el=>uploadRefDialog(el.dataset.id),
  'approve-ref':async el=>{const r=S.detail.refs.find(x=>x.id===el.dataset.id);await api(G()+'/refs/'+r.id+'/approve',{method:'PUT',body:{approved:!r.approved}});await loadDetail();render();toast(r.approved?'Freigabe zurückgenommen.':'Referenz freigegeben.')},
  'edit-task':el=>editTaskDialog(el.dataset.id),
  'agents-download':()=>{const dl=val('a-dlc');download(G()+'/agents/export'+(dl?'?dlc_id='+enc(dl):''))},
  'agents-install':async()=>{if(!await ask('Agenten installieren?','Die 20 Agenten-Dateien werden im verbundenen Projektordner unter .claude/agents/ angelegt. Vorhandene Dateien werden nicht überschrieben – existieren sie schon, bricht die Installation ab.','Installieren'))return;const r=await api(G()+'/agents/install',{method:'POST',body:{dlc_id:val('a-dlc')}});toast(r.written_files+' Dateien angelegt.')},
  'live-install':async()=>{if(!await ask('Ereignis-Meldung einrichten?','Im Projektordner wird .gameforge/agent_hook.py angelegt und in .claude/settings.local.json eingetragen. Bestehende Einstellungen werden vorher gesichert. Es werden nur Agentenname, Ereignis und Zeit gespeichert – keine Chat-Inhalte.','Einrichten'))return;await api(G()+'/live/install',{method:'POST',body:{}});toast('Ereignis-Meldung eingerichtet.');render()},
  'agent-errors':async el=>{const v=await api(G()+'/live');const a=v.agents.find(x=>x.slug===el.dataset.slug);modal({title:'Fehler · '+a.name,body:`<pre class="log">${esc(a.errors.map(e=>when(e.at)+'  Werkzeug: '+(e.tool||'unbekannt')).join('\n'))}</pre><p class="help" style="margin-top:10px">Die vollständige Ausgabe findest du im zugehörigen Auftrag („Fehler anzeigen“).</p>`,actions:[{label:'Schließen',primary:true}]})},
  'pipeline-prepare':async()=>{const r=await api(G()+'/pipeline/prepare',{method:'POST',body:{name:val('p-name'),type:val('p-type'),requirements:$('p-req').value,reference_ids:[...document.querySelectorAll('.p-ref:checked')].map(x=>x.value)}});toast('3D-Auftrag '+r.asset_id+' angelegt. Noch nichts modelliert.');render()},
  'pipeline-start':async el=>{const h=S.health;const noMcp=!(h?.blender?.mcp_connected);
    if(!await ask('Claude: Blender → Unreal starten?',(noMcp?'<b>Achtung:</b> Laut letzter Prüfung ist in Claude Code keine Blender-MCP-Verbindung aktiv. Claude wird den Auftrag dann mit einer Fehlermeldung beenden.<br><br>':'')+'Claude Code arbeitet im verbundenen Projektordner, darf dort Dateien anlegen und die Blender-/Unreal-MCP-Werkzeuge verwenden. Bestehende Assets werden nicht ersetzt. Lege vorher eine Sicherung an.','Starten'))return;
    await api(G()+'/pipeline/start',{method:'POST',body:{asset_id:el.dataset.id,allow_mcp:true}});toast('Auftrag gestartet. Den Verlauf siehst du hier und im Live-Monitor.');render()},
  'asset-approve':async el=>{await api(G()+'/pipeline/'+el.dataset.id+'/approve',{method:'POST',body:{}});toast('Asset freigegeben.');render()},
  'blender-test':async()=>{await api(G()+'/pipeline/blender-test',{method:'POST',body:{}});toast('Blender-Echttest läuft im Hintergrund …');S._wasRunning=true;render()},
  'show-job':el=>showJob(el.dataset.id),'retry-job':el=>retryJob(el.dataset.id),
  'direct-save':async()=>{await api(G()+'/direct',{method:'POST',body:{workspace:val('d-ws'),uat_path:val('d-uat')}});toast('Projektordner verbunden.');S.health=null;loadHealth(true);render()},
  'direct-create':async()=>{await api(G()+'/direct/workspace',{method:'POST',body:{}});toast('Arbeitsordner angelegt.');render()},
  'direct-refresh':()=>render(),
  'direct-extract':async()=>{const id=val('d-archive');if(!id)throw Error('Bitte zuerst ein Vollprojekt-ZIP wählen.');if(!await ask('Projekt entpacken?','Das ZIP wird in einen NEUEN Ordner entpackt und als Projektordner verbunden. Bestehende Dateien bleiben unberührt.','Entpacken'))return;const r=await api(G()+'/direct/extract',{method:'POST',body:{archive_id:id}});toast(r.files+' Einträge entpackt.');render()},
  'direct-archive':async()=>{if(!await ask('Projektordner sichern?','Der aktuelle Projektordner wird als ZIP ins Archiv gelegt. Caches, Build-Ordner, .env und .mcp.json werden ausgelassen.','Sichern'))return;const r=await api(G()+'/direct/archive',{method:'POST',body:{}});await loadDetail();toast(r.files+' Dateien gesichert.');render()},
  'direct-plan':()=>directStart('plan'),'direct-implement':()=>directStart('implement'),'direct-build':()=>directStart('build'),
};
async function directStart(kind){
  const texts={plan:['Plan erstellen?','Claude Code liest das Projekt und erstellt einen Plan. Es werden keine Dateien verändert.'],implement:['Umsetzen?','Claude Code darf jetzt Dateien im Projektordner bearbeiten. Hast du eine Sicherung (z. B. „Projektordner als ZIP sichern“)?'],build:['Windows-Spielversion erstellen?','Unreal kompiliert und verpackt das Spiel. Das kann sehr lange dauern und den PC stark auslasten.']};
  if(!await ask(texts[kind][0],texts[kind][1],'Starten'))return;
  await api(G()+'/direct/start',{method:'POST',body:{kind,instruction:val('d-ins'),task_id:val('d-task'),allow_mcp:!!$('d-mcp')?.checked}});toast('Auftrag gestartet. Status aktualisiert sich automatisch.');S._wasRunning=true;render();
}
async function afterDecision(msg){toast(msg);if(S.chat.open)await loadChat(false);if(S.area==='studio')render()}

document.addEventListener('click',async e=>{
  const nav=e.target.closest('[data-area]:not([data-act])');if(nav){go(nav.dataset.area,nav.dataset.area==='games'?'list':'');return}
  const tab=e.target.closest('[data-tab]:not([data-act])');if(tab){const [a,t]=tab.dataset.tab.split('/');go(a,t);return}
  const prov=e.target.closest('[data-prov]');if(prov){S.chat.provider=prov.dataset.prov;local.set('chatProvider',S.chat.provider);document.querySelectorAll('[data-prov]').forEach(b=>b.setAttribute('aria-pressed',String(b===prov)));updateAiLine();return}
  const el=e.target.closest('[data-act]');if(!el||el.disabled)return;
  const fn=ACT[el.dataset.act];if(!fn)return;
  try{await fn(el)}catch(err){toast(err.message,true)}
});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){if(!$('dialog').hidden)closeModal();else if(S.chat.open)closeChat()}});
$('close-dialog').onclick=closeModal;
$('dialog').addEventListener('click',e=>{if(e.target===$('dialog'))closeModal()});
$('chat-fab').onclick=openChat;
$('sys-pill').onclick=()=>go('production','overview');
$('ctx-game').onchange=async e=>{await selectGame(e.target.value);S.health=null;loadHealth();render();if(S.chat.open){chatSkeleton();loadChat()}};
$('ctx-dlc').onchange=e=>{S.dlcId=e.target.value;S._dlcTasksFor='';S._dlcTasks=[];render();if(S.chat.open){chatSkeleton();loadChat()}};
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>setMode(b.dataset.mode));
$('theme-toggle').onclick=()=>setTheme(document.documentElement.dataset.theme==='light'?'dark':'light');

(async function init(){
  setMode(S.mode);setTheme(local.get('theme','dark'));parseHash();
  try{S.config=await api('/api/config');await refreshAll();$('side-meta').innerHTML=`Lokal auf diesem PC · <b>v${esc(S.config.version)}</b>`}
  catch(e){$('view').innerHTML=note('GAMEFORGE-Server nicht erreichbar: '+esc(e.message),'err','alert');return}
  render();loadHealth();
})();
