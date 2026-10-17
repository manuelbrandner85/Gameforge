'use strict';
/* GAMEFORGE Reference Studio – nutzt ausschließlich echte Daten der lokalen Reference Engine. */
(function(){
const RS={data:null,compare:new Set()};
const REVIEW_KIND={'Zur Freigabe':'warn','Freigegeben':'ok','Abgelehnt':'err','Ersetzt':'','Technisch fehlerhaft':'err'};
const JOB_KIND={'Wartend':'','Aktiv':'accent live','Abgeschlossen':'ok','Fehlgeschlagen':'err','Abgebrochen':''};
const Q_LABEL={AUTO:'AUTO (GAMEFORGE entscheidet)',DRAFT:'Entwurf',STANDARD:'Standard',HIGH:'Hohe Qualität',CINEMATIC_MASTER:'Cinematic Master'};
const R=()=>G()+'/reference';

async function load(){RS.data=await api(R());return RS.data}

window.renderRefStudio=async function(){
  const tab=S.tab.refstudio||'overview';
  const top=head('Reference Studio · '+ctxLabel(),'Referenzbilder automatisch erzeugen','Lokal auf deiner Grafikkarte – ohne Cloud, ohne kostenpflichtige API, unabhängig von Claude. Jedes Bild passt sich dem Stil deines Spiels an und wartet auf deine Freigabe.')+tabs('refstudio');
  $('view').innerHTML=top+loading('Reference Engine wird abgefragt …');
  const d=await load();
  let body='';
  if(tab==='overview')body=overviewView(d);
  if(tab==='create')body=createView(d);
  if(tab==='gallery')body=galleryView(d);
  if(tab==='queue')body=queueView(d);
  if(tab==='system')body=await systemView(d);
  if(tab==='help')body=helpView();
  if(S.area==='refstudio'&&(S.tab.refstudio||'overview')===tab)$('view').innerHTML=top+body;
  if(tab==='create')wireCreate();
  const busy=d.jobs.some(j=>j.status==='Wartend'||j.status==='Aktiv');
  if(busy&&['queue','gallery','overview'].includes(tab))S.timers.push(setInterval(async()=>{if(S.area!=='refstudio')return;const n=await api(R());const still=n.jobs.some(j=>j.status==='Wartend'||j.status==='Aktiv');
    if(tab==='queue'&&$('rs-queue'))$('rs-queue').innerHTML=jobList(n.jobs);if(!still)render()},2000));
};

function statusStrip(st){
  const c=st.comfy,g=(st.gpu.gpus||[])[0];
  return `<div class="grid g4"><div class="metric"><small>Bildmodell</small><strong style="font-size:17px">${esc(RS.data.route.ok?RS.data.route.model_name:'keins passend')}</strong><span>${RS.data.route.ok?(RS.data.route.verified_on_this_pc?'auf diesem PC erfolgreich getestet':'noch nicht auf diesem PC getestet'):esc(RS.data.route.reason)}</span></div>
   <div class="metric"><small>ComfyUI (lokal)</small><strong style="font-size:17px">${c.running?'läuft':c.installed?'bereit, gestoppt':'nicht installiert'}</strong><span>${c.running?'nur 127.0.0.1':'startet automatisch beim ersten Auftrag'}</span></div>
   <div class="metric"><small>Grafikkarte</small><strong style="font-size:17px">${esc(g?g.name:'unbekannt')}</strong><span>${g&&g.vram_total_mb?`${(g.vram_used_mb/1024).toFixed(1)} / ${(g.vram_total_mb/1024).toFixed(1)} GB VRAM belegt`:'VRAM nicht messbar'}</span></div>
   <div class="metric"><small>Aufträge</small><strong>${st.counts['Aktiv']+st.counts['Wartend']}</strong><span>${st.counts['Aktiv']} aktiv · ${st.counts['Wartend']} wartend · ${st.to_review} zur Freigabe</span></div></div>`;
}
function overviewView(d){
  const p=d.profile.profile;
  return statusStrip(d.status)+`<div class="grid g2 section"><div class="card"><div class="card-head"><div><h2>Art-Direction-Profil</h2><p class="help">Verbindliche Grundlage für alle Bilder dieses Spiels. ${d.profile.source==='automatisch'?'Automatisch erstellt – bitte prüfen.':'Von dir bearbeitet.'} ${d.profile.approved?badge('freigegeben','ok'):badge('noch nicht freigegeben','warn')}</p></div>${btn('Bearbeiten','rs-edit-profile','sm','','edit')}</div>
    <dl class="summary-list"><dt>Grafikstil</dt><dd><b>${esc(p.style_label)}</b><br><span class="tiny">${esc(p.style_reason)}</span></dd><dt>Qualität (AUTO)</dt><dd>${esc(Q_LABEL[p.quality_auto]||p.quality_auto)}</dd><dt>Licht</dt><dd>${esc(p.lighting)}</dd>
    <dt>Farbpalette</dt><dd>${esc(p.color_palette||'– frei –')}</dd><dt>Materialstil</dt><dd>${esc(p.material_style||'– aus Stil –')}</dd><dt>Polygonbudget</dt><dd>${esc(p.poly_budget)}</dd><dt>Texturen</dt><dd>${esc(p.texture_budget)}</dd><dt>Plattform</dt><dd>${esc(p.platform)}</dd><dt>Engine</dt><dd>${esc(p.engine)}</dd></dl>
    <details class="more pro-only"><summary>Stil-Prompt</summary><pre class="log">${esc(p.style_prompt)}</pre></details></div>
   <div class="card accent"><div class="card-head"><div><h2>So geht's</h2></div></div><div class="stack">
    ${[['1','Stil prüfen','Passt das Profil links zu deinem Spiel? Sonst „Bearbeiten“.','overview'],['2','Bild erzeugen','Objekt beschreiben oder vorhandene Bildaufträge wählen.','create'],['3','Prüfen & freigeben','Varianten vergleichen, freigeben oder neu erzeugen.','gallery'],['4','3D-Produktion','Freigegebene Bilder gehen direkt an Blender → Unreal.','pipeline']].map(([n,t,x,tab])=>`<button type="button" class="next-step" data-act="goto" data-area="${tab==='pipeline'?'production':'refstudio'}" data-tab="${tab}"><span class="num">${n}</span><span><b>${t}</b><br><span class="tiny">${x}</span></span>${icon('arrow','sm')}</button>`).join('')}</div></div></div>`;
}
function createView(d){
  const refs=S.detail.refs.filter(r=>(r.dlc_id||'')===(S.dlcId||''));
  const open=refs.filter(r=>!r.approved);
  const cats=Object.entries(S.config.categories);
  return statusStrip(d.status)+`<div class="grid g2 section"><div class="card"><div class="card-head"><div><h2>Neues Objekt</h2><p class="help">Beschreibe, was gebraucht wird. GAMEFORGE legt die passenden Ansichten an (bei Figuren z. B. Front, Seite, Rücken, Gesicht, Größenvergleich).</p></div></div>
    ${field('rs-name','Was soll abgebildet werden?','',{ph:'z. B. Zeus in Kampfrüstung'})}${selectField('rs-cat','Art des Objekts',cats,'character')}
    <p class="label">Ansichten</p><div class="chips" id="rs-views"></div>
    ${field('rs-details','Verbindliche Designdetails','',{area:true,rows:110,ph:'Größe, Farben, Kleidung, Rüstungsteile, Besonderheiten – wird in jede Ansicht übernommen'})}</div>
   <div class="card"><div class="card-head"><div><h2>…oder vorhandene Bildaufträge</h2><p class="help">${open.length} offene Aufträge für ${ctxLabel()}. Bereits freigegebene Referenzen werden nicht neu berechnet.</p></div></div>
    <div class="stack" style="max-height:340px;overflow:auto">${open.map(r=>`<label class="checkline"><input type="checkbox" class="rs-ref" value="${esc(r.id)}"><span>${esc(r.name)} · ${esc(S.config.view_labels[r.view]||r.view)}${r.image_path?' · Bild vorhanden (nicht freigegeben)':''}</span></label>`).join('')||'<p class="help">Keine offenen Bildaufträge.</p>'}</div></div></div>
  <div class="card section"><div class="grid g2"><div>${selectField('rs-quality','Qualitätsstufe',Object.entries(Q_LABEL),'AUTO',`AUTO wählt für dieses Spiel: ${Q_LABEL[d.profile.profile.quality_auto]}. „Cinematic Master“ heißt höchste Qualität im Stil des Spiels – nicht automatisch fotorealistisch.`)}
    <label class="checkline"><input type="checkbox" id="rs-force"><span>Auch neu erzeugen, wenn schon ein Bild vorhanden ist (neue Variante, alte Versionen bleiben erhalten)</span></label></div>
   <div>${note(d.route.ok?esc(d.route.reason):esc(d.route.reason),d.route.ok?'info':'err',d.route.ok?'info':'alert')}<div class="btn-row" style="margin-top:14px">${btn('Bildproduktion starten','rs-create','primary lg','','play')}</div></div></div>
   <div id="rs-result" style="margin-top:12px"></div></div>`;
}
function wireCreate(){
  const cat=$('rs-cat'),box=$('rs-views');if(!cat)return;
  const fill=()=>{box.innerHTML=S.config.views[cat.value].map(v=>`<button type="button" class="chip" data-rsview="${v}" aria-pressed="true">${esc(S.config.view_labels[v]||v)}</button>`).join('')};
  cat.onchange=fill;fill();
  box.onclick=e=>{const b=e.target.closest('[data-rsview]');if(b)b.setAttribute('aria-pressed',String(b.getAttribute('aria-pressed')!=='true'))};
}
function galleryView(d){
  const byRef={};d.images.forEach(i=>{(byRef[i.ref_task_id]=byRef[i.ref_task_id]||[]).push(i)});
  const refs=S.detail.refs;
  const groups=Object.entries(byRef).map(([rid,imgs])=>{const r=refs.find(x=>x.id===rid)||{name:imgs[0].meta.asset_name,view:imgs[0].meta.view};
    return `<div class="card section"><div class="card-head"><div><h2>${esc(r.name)} · ${esc(S.config.view_labels[r.view]||r.view)}</h2><p class="help">${imgs.length} Version(en) · ${r.approved?'freigegebene Referenz vorhanden':'noch keine Freigabe'}</p></div>${btn('Neue Variante','rs-regen','sm','data-ref="'+esc(rid)+'"','refresh')}</div>
    <div class="games" style="grid-template-columns:repeat(auto-fill,minmax(230px,1fr))">${imgs.map(i=>`<div class="agent" style="padding:10px"><button type="button" class="link-btn" data-act="rs-zoom" data-id="${esc(i.id)}" aria-label="Bild vergrößern"><img src="${R()}/images/${esc(i.id)}" alt="${esc(r.name)} Version ${i.version}" loading="lazy" style="width:100%;border-radius:8px;border:1px solid var(--line);background:var(--surface-3)"></button>
      <div class="agent-top"><b>Version ${i.version}</b>${badge(i.review,REVIEW_KIND[i.review])}</div>
      <p>${esc(i.meta.width+'×'+i.meta.height)} · ${esc(Q_LABEL[i.meta.quality]||i.meta.quality)} · Seed ${esc(i.meta.seed)} · ${esc(i.meta.generation_seconds)} s</p>
      <p>${i.meta.qc.checks.map(c=>`${c.ok?'✓':'✗'} ${esc(c.name)}`).join(' · ')}</p>
      <label class="checkline" style="padding:2px 0"><input type="checkbox" class="rs-cmp" value="${esc(i.id)}" ${RS.compare.has(i.id)?'checked':''}><span>vergleichen</span></label>
      <div class="btn-row">${i.review==='Zur Freigabe'?btn('Freigeben','rs-approve','sm primary','data-id="'+esc(i.id)+'"','check')+btn('Ablehnen','rs-reject','sm quiet','data-id="'+esc(i.id)+'"','x'):''}</div>
      <details class="more pro-only"><summary>Metadaten</summary><pre class="log">${esc(JSON.stringify(i.meta,null,2))}</pre></details></div>`).join('')}</div></div>`}).join('');
  return `<div class="card"><div class="card-head"><div><h2>Galerie & Freigabe</h2><p class="help">Die technische Prüfung (Datei, Auflösung, nicht leer, Belichtung, bei Pixel-Art Raster und Palette) läuft automatisch. Ob Anatomie, Design und Kanon stimmen, entscheidest du – deshalb wartet jedes Bild auf deine Freigabe. Freigegebene Bilder werden zur offiziellen Referenz und gehen an Blender → Unreal.</p></div>${btn('Ausgewählte vergleichen','rs-compare','sm','','layers')}</div></div>`
   +(groups||empty('Noch keine erzeugten Bilder','Starte unter „Erzeugen“ deinen ersten Bildauftrag.',btn('Zu „Erzeugen“','goto','primary sm','data-area="refstudio" data-tab="create"','play')));
}
function jobList(jobs){
  return jobs.map(j=>`<div class="row"><div><div class="t">${esc(j.asset_name)} · ${esc(S.config.view_labels[j.view]||j.view)} ${badge(j.status,JOB_KIND[j.status])}</div>
    <p>${esc(j.step)}${j.error?' · <span style="color:var(--err)">'+esc(short(j.error,240))+'</span>':''}</p>
    <p class="tiny">${esc(Q_LABEL[j.quality]||j.quality)} · ${j.width}×${j.height} · Modell ${esc(j.model_id)} · Versuch ${j.attempts}/${j.max_attempts} · ${when(j.created_at)}</p></div>
    <div class="row-actions">${['Wartend','Aktiv'].includes(j.status)?btn('Abbrechen','rs-cancel','sm','data-id="'+esc(j.id)+'"','x'):''}${['Fehlgeschlagen','Abgebrochen'].includes(j.status)?btn('Erneut versuchen','rs-retry','sm','data-id="'+esc(j.id)+'"','refresh'):''}${j.error?btn('Fehler anzeigen','rs-error','sm quiet','data-id="'+esc(j.id)+'"','alert'):''}</div></div>`).join('')||'<p class="help">Keine Aufträge.</p>';
}
function queueView(d){
  return statusStrip(d.status)+`<div class="card section"><div class="card-head"><div><h2>Warteschlange</h2><p class="help">Es läuft immer nur ein Bild gleichzeitig auf der Grafikkarte – so bleiben GAMEFORGE, Blender und Unreal stabil. Prozentwerte gibt ComfyUI nicht zuverlässig aus, daher steht hier der tatsächliche Arbeitsschritt.</p></div></div><div class="stack" id="rs-queue">${jobList(d.jobs)}</div></div>`;
}
async function systemView(d){
  const sys=await api('/api/reference/system');const c=d.status.comfy;const g=(sys.gpu.gpus||[])[0];
  return `<div class="grid g2"><div class="card"><div class="card-head"><div><h2>Dieser PC</h2><p class="help">Echte Messwerte.</p></div>${btn('Aktualisieren','goto','sm','data-area="refstudio" data-tab="system"','refresh')}</div>
    <dl class="summary-list"><dt>System</dt><dd>${esc(sys.os)}</dd><dt>Prozessor</dt><dd>${esc(sys.cpu)}</dd><dt>Arbeitsspeicher</dt><dd>${sys.ram?sys.ram.total_gb+' GB ('+sys.ram.free_gb+' GB frei)':'–'}</dd>
    <dt>Grafikkarte</dt><dd>${esc(g?g.name:'–')}${g&&g.driver?' · Treiber '+esc(g.driver):''}</dd><dt>VRAM</dt><dd>${g&&g.vram_total_mb?(g.vram_used_mb/1024).toFixed(1)+' von '+(g.vram_total_mb/1024).toFixed(1)+' GB belegt':'nicht messbar'}</dd><dt>Speicherplatz</dt><dd>${sys.disk.free_gb} GB frei</dd></dl></div>
   <div class="card"><div class="card-head"><div><h2>ComfyUI (lokale Bild-KI)</h2><p class="help">Läuft nur auf 127.0.0.1 – nicht im Netzwerk erreichbar.</p></div>${badge(c.running?'läuft':c.installed?'gestoppt':'nicht installiert',c.running?'ok':c.installed?'':'err')}</div>
    <p class="help mono">${esc(c.root||'engines/ComfyUI_windows_portable fehlt')}</p>
    <div class="btn-row" style="margin-top:12px">${c.running?btn('Modelle entladen (VRAM frei)','rs-comfy','sm','data-op="free"','refresh')+btn('ComfyUI beenden','rs-comfy','sm','data-op="stop"','x'):c.installed?btn('ComfyUI starten','rs-comfy','sm primary','data-op="start"','play'):'<span class="help">Erst installieren (siehe README).</span>'}</div>
    <p class="tiny" style="margin-top:10px">Protokoll: <span class="mono">${esc(c.log)}</span></p></div></div>
  <div class="card section"><div class="card-head"><div><h2>Modelle</h2><p class="help">Nur lizenzgeprüfte Modelle aus nachvollziehbaren Quellen. Neue Modelle lassen sich ergänzen, ohne Projekte neu einzurichten.</p></div></div>
   <div class="stack">${d.status.models.map(m=>`<div class="row top"><div><div class="t">${esc(m.name)} ${badge(m.installed?'installiert':'nicht installiert',m.installed?'ok':'warn')} ${d.status.verified_models.includes(m.id)?badge('auf diesem PC getestet','ok'):badge('noch nicht getestet','')}</div>
     <p>Lizenz: <a href="${esc(m.license_url)}" target="_blank" rel="noopener">${esc(m.license)}</a> · kommerzielle Nutzung ${m.commercial_use?'erlaubt':'nicht erlaubt'} · mind. ${m.vram_min_gb} GB VRAM</p>
     <p>Angebunden: ${esc(m.capabilities.join(', '))}</p><p class="tiny">Noch nicht angebunden: ${esc(m.capabilities_not_wired.join(' · '))}</p>
     <p class="tiny">Stile: ${Object.entries(m.styles).map(([k,v])=>esc((RS.data.styles[k]?.label||k)+': '+v)).join(' · ')}</p>
     <details class="more pro-only"><summary>Dateien & Quelle</summary><pre class="log">${esc(m.source+'\n'+Object.entries(m.file_state).map(([f,s])=>(s.exists?'OK  ':'FEHLT ')+f+(s.exists?'  '+size(s.size):'')).join('\n'))}</pre></details></div></div>`).join('')}</div></div>`;
}
function helpView(){
  const items=[['Spiel auswählen','Oben rechts das Projekt (und ggf. DLC) wählen. Jedes Spiel hat eigene Bilder, Profile und Aufträge – nichts wird vermischt.'],
   ['Referenzen erzeugen','„Erzeugen“ → Objekt beschreiben und Ansichten wählen, oder vorhandene Bildaufträge ankreuzen → „Bildproduktion starten“. ComfyUI startet automatisch.'],
   ['Qualität einstellen','AUTO übernimmt die Stufe aus dem Art-Direction-Profil. Entwurf = schnell, Standard = produktionsnah, Hohe Qualität = 2 Varianten, Cinematic Master = höchste Auflösung im Spielstil.'],
   ['Varianten vergleichen','In der Galerie bei zwei oder mehr Bildern „vergleichen“ ankreuzen → „Ausgewählte vergleichen“.'],
   ['Freigeben','„Freigeben“ macht das Bild zur offiziellen Referenz (alte Versionen bleiben erhalten). „Neue Variante“ erzeugt ein weiteres Bild mit neuem Seed.'],
   ['Blender-Produktion starten','Produktion → Blender → Unreal → „3D-Auftrag anlegen“ und die freigegebenen Bilder ankreuzen. Danach „Claude: Blender → Unreal ausführen“ (benötigt Claude-Anmeldung und MCP).'],
   ['Unreal-Status prüfen','Produktion → Blender → Unreal zeigt pro Asset die echte Stufe – „Unreal importiert“ erst, wenn .uasset-Dateien im Projekt liegen.']];
  return `<div class="card"><h2>Hilfe zum Reference Studio</h2><div class="stack" style="margin-top:14px">${items.map(([t,x],i)=>`<div class="row top"><div><div class="t">${i+1}. ${esc(t)}</div><p>${esc(x)}</p></div></div>`).join('')}</div>
   <div style="margin-top:16px">${note('Ein Referenzbild ist eine Vorlage, kein 3D-Modell. Als 3D-Asset zählt etwas erst, wenn eine echte, geprüfte .blend-/.fbx-Datei existiert.','info','info')}</div></div>`;
}
function profileDialog(){
  const d=RS.data,p=d.profile.profile;
  modal({title:'Art-Direction-Profil bearbeiten',wide:true,body:selectField('ap-style','Grafikstil',Object.entries(d.styles).map(([k,v])=>[k,v.label]),p.style_id,'Der Stil bestimmt Modell und Workflow.')
    +selectField('ap-quality','Qualität im AUTO-Modus',[['DRAFT','Entwurf'],['STANDARD','Standard'],['HIGH','Hohe Qualität'],['CINEMATIC_MASTER','Cinematic Master']],p.quality_auto)
    +field('ap-palette','Farbpalette',p.color_palette,{ph:'z. B. Marmorweiß, Gold, Ägäisblau'})+field('ap-material','Materialstil',p.material_style,{ph:'z. B. abgenutzte Bronze, verwitterter Marmor'})
    +field('ap-light','Beleuchtung',p.lighting)+`<div class="grid g2">${field('ap-poly','Polygonbudget',p.poly_budget)}${field('ap-tex','Texturbudget',p.texture_budget)}</div>`
    +field('ap-prompt','Stil-Prompt (Profi)',p.style_prompt,{area:true,rows:90})+field('ap-notes','Notizen',p.notes,{area:true,rows:70})
    +`<label class="checkline"><input type="checkbox" id="ap-approved" ${d.profile.approved?'checked':''}><span>Profil freigeben (verbindlich für alle neuen Bilder)</span></label>`,
   actions:[{label:'Abbrechen'},{label:'Speichern',primary:true,onClick:async()=>{const changedStyle=val('ap-style')!==p.style_id;
     await api(R()+'/profile',{method:'PUT',body:Object.assign({style_id:val('ap-style'),quality_auto:val('ap-quality'),color_palette:val('ap-palette'),material_style:val('ap-material'),lighting:val('ap-light'),poly_budget:val('ap-poly'),texture_budget:val('ap-tex'),notes:val('ap-notes'),approved:$('ap-approved').checked},changedStyle?{}:{style_prompt:$('ap-prompt').value})});toast('Profil gespeichert.');render()}}]});
}
Object.assign(ACT,{
  'rs-edit-profile':()=>profileDialog(),
  'rs-create':async()=>{const refIds=[...document.querySelectorAll('.rs-ref:checked')].map(x=>x.value);const views=[...document.querySelectorAll('[data-rsview][aria-pressed="true"]')].map(b=>b.dataset.rsview);
    const body={quality:val('rs-quality'),force:$('rs-force').checked,dlc_id:S.dlcId};
    if(refIds.length)body.ref_task_ids=refIds;else{body.name=val('rs-name');body.category=val('rs-cat');body.views=views;body.details=$('rs-details').value;if(!views.length)throw Error('Bitte mindestens eine Ansicht wählen.')}
    const r=await api(R()+'/jobs',{method:'POST',body});await loadDetail();
    $('rs-result').innerHTML=note(`<b>${r.created.length} Bildaufträge</b> eingereiht (${esc(Q_LABEL[r.quality])}).${r.skipped.length?'<br>Übersprungen: '+r.skipped.map(s=>esc(s.reason)).join('<br>'):''}`,r.created.length?'ok':'info',r.created.length?'check':'info');
    toast(r.created.length?r.created.length+' Bildaufträge gestartet.':'Nichts neu zu erzeugen – vorhandene Referenzen werden genutzt.')},
  'rs-approve':async el=>{await api(R()+'/images/'+el.dataset.id+'/review',{method:'POST',body:{action:'approve'}});await loadDetail();toast('Freigegeben – jetzt offizielle Referenz.');render()},
  'rs-reject':async el=>{await api(R()+'/images/'+el.dataset.id+'/review',{method:'POST',body:{action:'reject'}});toast('Abgelehnt.');render()},
  'rs-regen':async el=>{const r=await api(R()+'/jobs',{method:'POST',body:{ref_task_ids:[el.dataset.ref],force:true,quality:'AUTO'}});toast(r.created.length+' neue Variante(n) eingereiht.');render()},
  'rs-cancel':async el=>{await api(R()+'/jobs/'+el.dataset.id+'/cancel',{method:'POST',body:{}});toast('Abbruch angefordert.');render()},
  'rs-retry':async el=>{await api(R()+'/jobs/'+el.dataset.id+'/retry',{method:'POST',body:{}});toast('Erneut eingereiht.');render()},
  'rs-error':el=>{const j=RS.data.jobs.find(x=>x.id===el.dataset.id);modal({title:'Fehler · '+j.asset_name,wide:true,body:`<pre class="log">${esc(j.error)}</pre>`,actions:[{label:'Schließen',primary:true}]})},
  'rs-comfy':async el=>{toast(el.dataset.op==='start'?'ComfyUI wird gestartet – das kann eine Minute dauern …':'Wird ausgeführt …');await api('/api/reference/comfy/'+el.dataset.op,{method:'POST',body:{}});render()},
  'rs-zoom':el=>{modal({title:'Vorschau',wide:true,body:`<img src="${R()}/images/${esc(el.dataset.id)}" alt="Referenzbild groß" style="width:100%;border-radius:10px">`,actions:[{label:'Schließen',primary:true}]})},
  'rs-compare':()=>{const ids=[...document.querySelectorAll('.rs-cmp:checked')].map(x=>x.value);if(ids.length<2)throw Error('Bitte mindestens zwei Bilder zum Vergleichen ankreuzen.');
    const imgs=ids.map(id=>RS.data.images.find(i=>i.id===id));
    modal({title:'Vergleich',wide:true,body:`<div class="grid g2">${imgs.map(i=>`<div><img src="${R()}/images/${esc(i.id)}" alt="Version ${i.version}" style="width:100%;border-radius:10px"><p class="help">${esc(i.meta.asset_name)} · Version ${i.version} · ${badge(i.review,REVIEW_KIND[i.review])}</p></div>`).join('')}</div>`,actions:[{label:'Schließen',primary:true}]})},
});
document.addEventListener('change',e=>{if(e.target.classList?.contains('rs-cmp')){e.target.checked?RS.compare.add(e.target.value):RS.compare.delete(e.target.value)}});
})();
