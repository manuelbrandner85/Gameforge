'''Asset-Pipeline: verbindliche Handoffs für Claude -> Blender -> Unreal.
Keine Modellierung behaupten. Erzeugte Dateien sind echte reproduzierbare Arbeitsaufträge.
'''
from __future__ import annotations
import json, re, datetime as dt, uuid
from pathlib import Path

def prepare(store,gid,data):
    game=store.game(gid)
    if not game:raise ValueError('Unbekanntes Spiel')
    setting=store.direct.settings(gid)
    if not setting.get('workspace') or not Path(setting['workspace']).is_dir():
        raise ValueError('Zuerst einen Projektordner im Direkt-Studio verbinden.')
    root=Path(setting['workspace']).resolve()
    name=str(data.get('name','')).strip()
    typ=str(data.get('type','')).strip()
    if not name or len(name)>100:raise ValueError('Asset-Namen eingeben (max. 100 Zeichen).')
    if typ not in ('character','static','environment','vehicle','weapon'):raise ValueError('Asset-Typ unbekannt')
    refs=data.get('reference_ids',[])
    if not isinstance(refs,list) or len(refs)>40:raise ValueError('Zu viele oder ungültige Referenzen.')
    if not refs and not str(data.get('requirements','')).strip():raise ValueError('Ohne Referenzen bitte eine genaue 3D-Beschreibung für Claude angeben.')
    available={r['id']:r for r in store.refs(gid)}
    for rid in refs:
        if rid not in available or not available[rid]['approved'] or not available[rid]['image_path']:
            raise ValueError('Die ausgewählten Referenzen müssen zum Spiel gehören, importiert und freigegeben sein.')
    taskid=uuid.uuid4().hex[:12]
    bundle=root/'.gameforge'/'asset_pipeline'/taskid
    bundle.mkdir(parents=True,exist_ok=False)
    folder=bundle/'references';folder.mkdir()
    manifest=[]
    import shutil
    for ix,rid in enumerate(dict.fromkeys(refs)):
        r=available[rid]
        orig=store.base/'refs'/r['image_path']
        if not orig.is_file():raise ValueError('Originalbild fehlt: '+r['name'])
        dest=folder/(str(ix+1).zfill(2)+'_'+rid+orig.suffix.lower())
        shutil.copy2(orig,dest)
        manifest.append({'id':rid,'subject':r['name'],'view':r['view'],'path':str(dest.relative_to(root))})
    details=str(data.get('requirements','')).strip()[:10000]
    spec={'asset_id':taskid,'name':name,'type':typ,'game_id':gid,'game_name':game['title'],
          'style':game['style'],'requirements':details,'references':manifest,
          'status':'SPEZIFIZIERT – NICHT MODELLIERT',
          'source_type':'freigegebene_referenzen' if refs else 'claude_entwurf_aus_beschreibung',
          'outputs':{'blend':f'Assets/{taskid}/{taskid}.blend','fbx':f'Assets/{taskid}/{taskid}.fbx',
                     'ue_destination':f'/Game/GAMEFORGE/{taskid}'},
          'checks':['Referenztreue','Maßstab','UV und PBR','Geometrie','Unreal-Import und Materialzuordnung','Spieltest'],
          'created_at':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}
    (bundle/'asset_spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
    (bundle/'BLENDER_TASK.md').write_text(f'''# Blender-Auftrag – {name}

Lies `asset_spec.json` und vorhandene Dateien im references-Ordner. Ohne Bildreferenzen: Erstelle erst einen nachvollziehbaren Entwurf anhand der Nutzerbeschreibung und verlange eine fachliche Designfreigabe. Der ausgewählte Stil ist: {game['style']}.

1. Verwende Claude Code und Blender-MCP nur wenn tatsächlich verbunden; prüfe MCP vorher.
2. Baue ein **echtes** 3D-Modell anhand der freigegebenen Referenzen, nicht nur ein Platzhalter-Objekt.
3. Für Charaktere: Anatomie, spielbare Topologie, UVs, PBR, Rig, Skinning, benötigte Animationen.
4. Für andere Assets: saubere Maße, korrekte Pivots, UVs, Texturen und Kollisionsvorgaben.
5. Speichere eine `.blend`-Originaldatei und exportiere eine `.fbx` unter den in `asset_spec.json` definierten Zielpfaden.
6. Dokumentiere Abweichungen, nicht umgesetzte Details, echte Exportdateien und Testergebnisse.
7. Kein Objekt gilt durch Bildreferenzen oder Planungs-JSON als erstellt. Fremde Dateien nicht ersetzen.

Sonderwünsche:
{details or '(keine)'}
''',encoding='utf-8')
    (bundle/'UNREAL_TASK.md').write_text(f'''# Unreal-Importauftrag – {name}

1. Warten, bis der Blender-Agent **echte** FBX-, Blend- und Texturdateien vorweist.
2. Unreal-MCP prüfen, anschließend FBX in ein isoliertes `/Game/GAMEFORGE/{taskid}` importieren.
3. Materialien, Normals, Pivot, Maßstab und Achsen überprüfen; für Figuren Skeleton, Animation Blueprints, Retargeting, Collision und LODs prüfen.
4. Bei Figuren: Character Blueprint, Kapsel-/Mesh-Kollision, Animation Graph, Verhalten und Testszene mit Vorgaben abstimmen.
5. Bei Gebäuden: Mesh, Material, Kollisionsmesh, sinnvolle LOD/Nanite-Vorgaben nach Eignung.
6. Importergebnis über Editor-Abfrage oder echte Asset-Dateien verifizieren; Play-in-Editor-Test. Testfehler melden.
7. Nie das Ursprungsasset überschreiben; Import in eigenen Projekt-Unterordner.

Die mitgelieferte `unreal_import_template.py` ist nur ein STARTPUNKT, nicht automatisch ausgeführt. Für Skeletal Meshes und Animationen kann ein separater Import-/Riggingprozess erforderlich sein.
''',encoding='utf-8')
    (bundle/'unreal_import_template.py').write_text('''# Im Unreal Editor Python-Kontext ausführen, NICHT mit normalem Python.
# Pfad zu vorhandener FBX zuvor ersetzen und Importoptionen je nach Asset-Typ ergänzen.
import unreal
FBX_FILE = r"BITTE_ABSOLUTEN_FBX_PFAD_EINTRAGEN"
DEST = "/Game/GAMEFORGE/'''+taskid+'''"
if FBX_FILE.startswith("BITTE_"):
    raise RuntimeError("FBX-Datei vor dem Import auswählen")
job = unreal.AssetImportTask()
job.filename = FBX_FILE
job.destination_path = DEST
job.automated = True
job.replace_existing = False
job.save = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([job])
print("Import-Ergebnis:", [str(x) for x in job.imported_object_paths])
''',encoding='utf-8')
    return {'asset_id':taskid,'name':name,'type':typ,'reference_count':len(manifest),'workspace':str(root),
            'spec_path':str((bundle/'asset_spec.json').relative_to(root)),'status':spec['status'],
            'note':'Asset-Aufträge und Referenzkopien erstellt. Blender und Unreal wurden noch NICHT ausgeführt.'}
