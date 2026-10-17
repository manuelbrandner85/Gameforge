#!/usr/bin/env python3
"""GAMEFORGE GODMODE 2.0 – lokales KI-Spielestudio: Bibliothek, Chat, Agenten, Produktion.
Nur Python-Standardbibliothek. Bindet ausschließlich an 127.0.0.1.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import io
import json
import os
import re
import subprocess
import shutil
import socket
import sqlite3
import tempfile
import threading
import uuid
import webbrowser
import zipfile
from direct_studio import DirectStudio
import agent_studio
import agent_live
import asset_pipeline
import studio_v2
import game_trash
from reference_engine import engine as ref_engine, art_direction, hardware as ref_hw, quality as ref_quality
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

VERSION = '2.1.0'
SCHEMA_VERSION = 3
ROOT = Path(__file__).resolve().parent
WEB = ROOT / 'web'
RESOURCE = ROOT / 'resources'
FIELDS = [
    ('vision','Spielvision & Ziele'), ('game_rules','Spielregeln & Gameplay-Loop'),
    ('canon','Story-Kanon (verbindlich)'), ('story','Handlung / Akte'), ('prologue','Prolog'),
    ('chapters','Kapitel & Hauptmissionen'), ('sidequests','Nebenmissionen & Geheimnisse'),
    ('dialogue','Dialoge & Entscheidungen'), ('endings','Enden & Konsequenzen'),
    ('characters','Helden & Charaktere'), ('bosses','Bosse & Gegner'), ('npcs','NPCs & lebendige Welt'),
    ('world','Welt, Orte & Karten'), ('environments','Gebäude, Landschaften & Props'),
    ('combat','Kampfsystem & Fähigkeiten'), ('movement','Bewegung & Steuerung'),
    ('physics','Physik, Fahrzeuge & Wasser'), ('ai','NPC-, Gegner- & Boss-KI'),
    ('items','Waffen, Inventar & Ausrüstung'), ('progression','Fortschritt & Balancing'),
    ('ui','Menü, HUD & UX'), ('cinematics','Zwischensequenzen & Kamera'),
    ('audio','Musik, Sprache & Geräusche'), ('save_load','Speichern / Laden'),
    ('accessibility','Barrierefreiheit, Untertitel & Optionen'),
    ('localization','Lokalisierung'), ('performance','Performance & Streaming'),
    ('technical','Unreal-/Blender-Bauplan & MCP'), ('qa','Testfälle & Abnahmekriterien'),
    ('release','Build, Distribution & Updates'), ('legal','Lizenzen & Bild-/Musikrechte')
]
REQUIRED_CORE = ['vision','game_rules','canon','story','prologue','chapters','characters','world','movement','ui','save_load','technical','qa','release']
CATEGORIES = {'character':'Charakter','boss':'Boss','npc':'NPC','weapon':'Waffe','building':'Gebäude','vehicle':'Fahrzeug','environment':'Spielwelt','prop':'Objekt','ui':'UI / Menü','creature':'Kreatur'}
VIEWS = {
 'character':['front','side','back','face','outfit','scale','pose'],
 'boss':['front','side','back','face','detail','scale','combat_pose'],
 'npc':['front','side','back','face','outfit'],
 'weapon':['front','side','grip','detail','scale'],
 'building':['front','side','back','entrance','material','scale'],
 'vehicle':['front','side','back','cockpit','detail','scale'],
 'environment':['overview','map','landmarks','materials','lighting'],
 'prop':['front','side','detail','scale'],
 'ui':['layout','states','icons','typography'],
 'creature':['front','side','back','face','scale','pose']
}
VIEW_LABELS = {'front':'Frontansicht','side':'Seitenansicht','back':'Rückenansicht','face':'Gesicht / Nahaufnahme','outfit':'Outfit / Rüstung','scale':'Größenvergleich','pose':'Pose','combat_pose':'Kampfpose','detail':'Detailansicht','grip':'Griff','entrance':'Eingang','material':'Material','cockpit':'Innenraum / Cockpit','overview':'Übersicht','map':'Draufsicht / Karte','landmarks':'Landmarken','materials':'Materialien','lighting':'Lichtstimmung','layout':'UI-Layout','states':'UI-Zustände','icons':'Icons','typography':'Typografie'}
STATES = ['Idee','Konzept','In Entwicklung','Testphase','Fertig','Veröffentlicht']
KINDS = ['Vollprojekt','Claude-Paket','Windows-Build','Referenzen','DLC-Vollprojekt','Andere']
PHASES = ['01 Bestandsaufnahme','02 Kanon & Gamedesign','03 Spielwelten & Assets','04 Referenzen','05 Blender-Produktion','06 Unreal-Gameplay','07 UI, Audio & Cinematics','08 Integration','09 Test & Optimierung','10 Release & Abnahme','11 Pflege & DLC']
TASK_STATUSES = ['Offen','In Arbeit','Implementiert','Getestet','Abgenommen']
TASK_BLUEPRINTS = [
 ('01 Bestandsaufnahme','Originalunterlagen und Projektdateien erfassen','Alle alten Pakete, Git-Repositories, UE-Projekte, Blender-Dateien, Artworks und fehlenden Dokumente aufnehmen; Widersprüche protokollieren.','Import-Inventar mit Quellen und Versionsstand geprüft'),
 ('01 Bestandsaufnahme','Bestehenden Spielstand technisch untersuchen','Projektstruktur, reale Maps, Builds, fehlende Plugins, Build-Fehler, Rechte und Abhängigkeiten erfassen.','Bestandsbericht mit tatsächlich ausführbaren Nachweisen'),
 ('02 Kanon & Gamedesign','Spielbibel und verbindlichen Kanon abgleichen','Vorhandene Originaldokumente haben Vorrang; offene Fragen als Entscheidungsvorlagen markieren.','Konsistente, genehmigte Spielbibel'),
 ('02 Kanon & Gamedesign','Komplette Story, Prolog, Missionen und Enden','Jeder Ablauf mit Szenen, Bedingungen, Quest-States, Branches, Triggern, Dialogen und Scheitern definieren.','Durchgängiger Ablaufplan ohne lose Story-Enden'),
 ('02 Kanon & Gamedesign','Core Loop, Regeln und Fortschritt','Steuerung, Balancing, Fähigkeiten, Inventar, Pacing, Ökonomie, Scheitern und Speichern detaillieren.','Für sämtliche Kernmechaniken Test- und Zustandsregeln'),
 ('03 Spielwelten & Assets','Weltkarte und alle Orte definieren','Level, Streaming, Zugänge, Missionen, Interaktionsobjekte, LOD und Navigation in Weltkarten aufnehmen.','Vollständiges Level- und World-Partition-Konzept soweit zutreffend'),
 ('03 Spielwelten & Assets','Asset-Inventar und Abhängigkeiten vervollständigen','Alle Charaktere, Bosse, NPCs, Kreaturen, Waffen, Gebäude, Fahrzeuge, Props mit IDs und Größen festlegen.','Asset-Matrix ohne nicht zugeordnete Pflichtobjekte'),
 ('04 Referenzen','Pflichtreferenzen erzeugen und freigeben','GAMEFORGE-Prompts in ChatGPT verwenden, Bilder zurückimportieren und Hauptansichten auf Konsistenz prüfen.','Alle notwendigen Ansichten freigegeben oder begründet als N/A markiert'),
 ('05 Blender-Produktion','3D-Modelle und Materialien umsetzen','Blender via Claude MCP; Maßstab, Topologie, UV, PBR, LOD, Kollision und Export validieren.','Echte .blend-/Exportdateien und Sichtprüfung vorhanden'),
 ('05 Blender-Produktion','Rigs, Animationen und Motion-Systeme','Skeletons, Animationszustände, IK, Root Motion, Übergänge, Kampf- und Cutsceneanimationen.','Animationscheck in Unreal ohne Fehler'),
 ('06 Unreal-Gameplay','Unreal-Projektgrundlage und Buildpipeline','Versionspinning, Plugins, C++/Blueprint-Struktur, Input, automatischer Build und Source Control.','Kompilierter Projektstand und reproduzierbare Builds'),
 ('06 Unreal-Gameplay','Heldensteuerung, Kampf und Fähigkeiten','Movement, Kamera, Treffer, Ausweichen, Fähigkeiten, Zustände, Zielhilfe, Tod und Respawn.','Spielbare Kontrolle samt Gameplaytests'),
 ('06 Unreal-Gameplay','Gegner-KI, Bosse und NPC-Verhalten','AI Controller, Navigation, Behavior, Dialoge, Bossschwierigkeit, World Reactivity.','Funktionierende Gegner/NPC-Szenarien mit Testnachweis'),
 ('06 Unreal-Gameplay','Missionen, Inventar, Fortschritt und Savegames','Questsystem, Trigger, Items, Belohnungen, persistente Zustände, Lade-/Speichertests.','Quest-/Inventar-/Save-Load-Regressionen bestanden'),
 ('06 Unreal-Gameplay','Physik, Fahrzeuge und Interaktionen','Kollision, Gravitation, Bewegung, Fahrzeuge, Wasser, Zerstörung, Interaktionsobjekte soweit relevant.','Nachgewiesene Physik- und Gameplaytests'),
 ('07 UI, Audio & Cinematics','Menüs, HUD, Optionen und Barrierefreiheit','Startmenü, Pause, Settings, Grafik, Audio, Controller, Untertitel, HUD, Navigation und Feedback.','Alle Bildschirmübergänge getestet'),
 ('07 UI, Audio & Cinematics','Prolog, Story-Cinematics, Abspann','Sequencer, Kamerapfade, Timing, Ereignisübergaben, Ton und Untertitel pro Szene.','Sequenzen starten/beenden in korrekten Quest-States'),
 ('07 UI, Audio & Cinematics','Musik, Sprache, Geräusche und Lokalisierung','Audio-Cues, Mix, Voice-Line-IDs, Raumklang, Untertitelsprachen, Rechte.','Audio-/Lokalisierungs-Check bestanden'),
 ('08 Integration','Vollständige Integration und Weltlogik','Alle Level, UI, Quests, Bossbegegnungen und Savegame-Abhängigkeiten zusammenführen.','End-to-End-Spieldurchlauf ohne Blocker'),
 ('08 Integration','DLC-Schnittstellen und Kompatibilität planen','Versionsverträge, Asset-IDs, DLC-Pakete, DLC-Saves, Abhängigkeiten und Migrationsplan.','DLC-Schnittstellen verifiziert'),
 ('09 Test & Optimierung','Automatisierte und manuelle QA','Gameplay, Regression, Smoke, Input, Savegames, Crashes und visuelle Checks.','Testprotokoll mit Belegen und dokumentierten Restfehlern'),
 ('09 Test & Optimierung','Performance, Hardware und Stabilität','FPS-Ziele, Auflösungen, Streaming, Speichernutzung, Ladezeiten, Fehleranalyse.','Performanceprofile auf definierten Zielgeräten'),
 ('10 Release & Abnahme','Finalen Build und Installer erstellen','Zielplattform, Buildprofil, Runtime-Abhängigkeiten, Install/Uninstall, Versionslabel und Signierung falls nötig.','Installierbarer Build von sauberer Maschine geprüft'),
 ('10 Release & Abnahme','Vollständige Abnahme und Rechteprüfung','Lizenznachweise, Content-Freigaben, Spielvollständigkeit, QA-Gate, Manifest und Quellarchiv.','Freigegebene Release-Checkliste mit finalem Projektarchiv'),
 ('11 Pflege & DLC','Updates, Bugfixing, Erweiterungen','Wartungszweige, Migrationen, DLC-Kompatibilität und neue Versionen planen.','Patch- und DLC-Prozess versioniert dokumentiert')
]
FILE_KINDS = {'documents':'.md .txt .pdf .doc .docx .odt .rtf .html .htm .csv .xls .xlsx .ppt .pptx .json .yaml .yml .xml .toml .ini .log', 'code':'.py .cpp .cc .c .h .hpp .cs .js .ts .tsx .jsx .bat .sh .ps1 .uproject .uplugin .sln .vcxproj .gitignore .cfg .ini', 'images':'.png .jpg .jpeg .webp .tiff .tif .bmp .gif .svg .exr .hdr .psd .tga', 'models':'.blend .fbx .obj .glb .gltf .usd .usdz .stl .abc .dae .uasset .umap .blend1', 'audio':'.wav .mp3 .ogg .flac .aiff .wem .bank', 'video':'.mp4 .mov .avi .mkv .webm', 'archives':'.zip .7z .rar .tar .gz'}

def categorize_file(name):
    ext=Path(name).suffix.lower()
    return next((group for group,extensions in FILE_KINDS.items() if ext in extensions.split()),'other')

def safe_relpath(value):
    value=str(value).replace('\\','/')
    if not value or value.startswith('/') or re.match(r'^[A-Za-z]:',value):
        raise ValueError('Ungültiger relativer Pfad')
    parts=value.split('/')
    if len(value)>700 or any(p in ('','.','..') or any(ord(c)<32 for c in p) for p in parts):
        raise ValueError('Unzulässiger Dateipfad')
    return '/'.join(parts)



def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def identifier():
    return uuid.uuid4().hex[:16]


def slug(value):
    return re.sub(r'[^a-z0-9_-]+', '-', value.lower()).strip('-')[:65] or 'projekt'


def clean_filename(name):
    base = Path(str(name).replace('\\','/')).name
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', base)[:150] or 'datei.zip'


def jd(s, default=None):
    try:
        return json.loads(s) if s else (default if default is not None else {})
    except (ValueError, TypeError):
        return default if default is not None else {}


def default_bible():
    return {key:'' for key,_ in FIELDS}


def default_dlc():
    return {k:'' for k in ('story','prologue','quests','new_characters','new_world','new_assets','gameplay','cinematics','menu','integration','qa','release')}


class Store:
    def __init__(self, directory: Path):
        self.base = Path(directory).resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        (self.base/'uploads').mkdir(exist_ok=True)
        (self.base/'refs').mkdir(exist_ok=True)
        (self.base/'imports').mkdir(exist_ok=True)
        self.db_path = self.base/'gameforge.sqlite3'
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys=ON')
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.executescript('''
        CREATE TABLE IF NOT EXISTS games(
          id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '',
          status TEXT NOT NULL DEFAULT 'Konzept', genre TEXT NOT NULL DEFAULT '',
          style TEXT NOT NULL DEFAULT '', engine TEXT NOT NULL DEFAULT 'Unreal Engine 5',
          camera TEXT NOT NULL DEFAULT '', version TEXT NOT NULL DEFAULT 'v0.1',
          bible TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS dlcs(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          title TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Idee',
          version TEXT NOT NULL DEFAULT 'v0.1', compatible_version TEXT NOT NULL DEFAULT '',
          design TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS ref_tasks(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          dlc_id TEXT REFERENCES dlcs(id), name TEXT NOT NULL, category TEXT NOT NULL,
          view TEXT NOT NULL, details TEXT NOT NULL DEFAULT '', required INTEGER NOT NULL DEFAULT 1,
          approved INTEGER NOT NULL DEFAULT 0, image_path TEXT, image_name TEXT,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS archives(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          dlc_id TEXT REFERENCES dlcs(id), kind TEXT NOT NULL, label TEXT NOT NULL,
          version TEXT NOT NULL DEFAULT '', original_name TEXT NOT NULL,
          file_path TEXT NOT NULL, size INTEGER NOT NULL, sha256 TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS snapshots(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          version TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '', snapshot TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS imported_files(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          dlc_id TEXT REFERENCES dlcs(id), relpath TEXT NOT NULL,
          original_name TEXT NOT NULL, stored_name TEXT NOT NULL,
          category TEXT NOT NULL, size INTEGER NOT NULL, sha256 TEXT NOT NULL,
          created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS idea_messages(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          dlc_id TEXT REFERENCES dlcs(id), role TEXT NOT NULL,
          provider TEXT NOT NULL DEFAULT 'manual', body TEXT NOT NULL,
          created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS idea_suggestions(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          dlc_id TEXT REFERENCES dlcs(id), source_id TEXT,
          title TEXT NOT NULL, detail TEXT NOT NULL,
          section TEXT NOT NULL DEFAULT 'story',
          status TEXT NOT NULL DEFAULT 'Vorgeschlagen',
          integrated INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS idea_changes(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          dlc_id TEXT REFERENCES dlcs(id), source_id TEXT,
          section TEXT NOT NULL, summary TEXT NOT NULL,
          mode TEXT NOT NULL, old_text TEXT NOT NULL DEFAULT '',
          new_text TEXT NOT NULL, base_hash TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'Vorgeschlagen', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS production_tasks(
          id TEXT PRIMARY KEY, game_id TEXT NOT NULL REFERENCES games(id),
          dlc_id TEXT REFERENCES dlcs(id), phase TEXT NOT NULL,
          title TEXT NOT NULL, description TEXT NOT NULL,
          acceptance TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Offen',
          evidence TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL);
        ''')
        self.conn.commit()
        self.direct=DirectStudio(self)
        self.schema_version=self.migrate()
        seeded=self.conn.execute("SELECT value FROM schema_meta WHERE key='seeded'").fetchone()
        if not seeded and not self.conn.execute('SELECT COUNT(*) FROM games').fetchone()[0]:
            self.seed()
        self.conn.execute("INSERT OR IGNORE INTO schema_meta(key,value) VALUES('seeded','1')");self.conn.commit()
        self.refengine=ref_engine.ReferenceEngine(self,ROOT)
        # Migration älterer Bibliotheken, keine vorherigen Daten überschreiben.
        for game in self.all('SELECT id FROM games'):
            self.ensure_tasks(game['id'])
        for dlc in self.all('SELECT game_id,id FROM dlcs'):
            self.ensure_dlc_tasks(dlc['game_id'],dlc['id'])

    def migrate(self):
        """Versionierte, rein ergänzende Migration. Vor jeder Änderung an einer vorhandenen
        Bibliothek wird die Datenbank nach GAMEFORGE_DATA/backups gesichert. Rückweg:
        GAMEFORGE schließen und die Sicherungsdatei als gameforge.sqlite3 zurückkopieren;
        v1.0 kann die migrierte Datenbank ebenfalls weiter öffnen (nur neue Spalten/Tabellen)."""
        with self.lock:
            self.conn.execute('CREATE TABLE IF NOT EXISTS schema_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            row=self.conn.execute("SELECT value FROM schema_meta WHERE key='version'").fetchone()
            current=int(row[0]) if row else 1
            if current>=SCHEMA_VERSION:
                return current
            if self.conn.execute('SELECT COUNT(*) FROM games').fetchone()[0]:
                folder=self.base/'backups';folder.mkdir(exist_ok=True)
                target=folder/f'vor_migration_v{SCHEMA_VERSION}_{dt.datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3'
                dst=sqlite3.connect(target)
                try: self.conn.backup(dst)
                finally: dst.close()
            cols=[r[1] for r in self.conn.execute('PRAGMA table_info(direct_jobs)')]
            if 'user_instruction' not in cols: self.conn.execute('ALTER TABLE direct_jobs ADD COLUMN user_instruction TEXT')
            if 'options' not in cols: self.conn.execute('ALTER TABLE direct_jobs ADD COLUMN options TEXT')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS asset_approvals(
                game_id TEXT NOT NULL REFERENCES games(id), asset_id TEXT NOT NULL,
                approved_at TEXT NOT NULL, PRIMARY KEY(game_id,asset_id))''')
            # v3: Reference Engine (nur neue Tabellen)
            self.conn.executescript(ref_engine.SCHEMA)
            self.conn.execute("INSERT OR REPLACE INTO schema_meta(key,value) VALUES('version',?)",(str(SCHEMA_VERSION),))
            self.conn.execute("INSERT OR REPLACE INTO schema_meta(key,value) VALUES('migrated_at',?)",(stamp(),))
            self.conn.commit()
            return SCHEMA_VERSION

    def execute(self, statement, values=()):
        with self.lock:
            cur = self.conn.execute(statement, values)
            self.conn.commit()
            return cur

    def all(self, statement, values=()):
        with self.lock:
            return [dict(row) for row in self.conn.execute(statement, values)]

    def one(self, statement, values=()):
        with self.lock:
            item = self.conn.execute(statement, values).fetchone()
            return dict(item) if item else None

    def seed(self):
        aion = default_bible()
        aion.update({
          'vision':'AION 2026: filmisches Open-World-Action-Adventure im modernen Griechenland (2026). Hyperrealistische Optik; Unreal Engine 5 / Blender. Bestehende Kanonfassung hat Vorrang.',
          'canon':'1102 v. Chr. werden sechs angreifende Götter durch Aion versteinert. 2026 beschädigt ein Energieexperiment das Schutzsystem. Die Götter bleiben BIS ZUM ENDE versteinert. Sechs Lebensknoten sind entscheidend. Gegner benötigen jeweils eine eindeutige Herkunft. Diese Fakten nicht eigenmächtig verändern.',
          'story':'Ein Auserwählter begegnet den Folgen der versteinerten Götter, besteht Prüfungen, erlangt Kräfte und trifft am Ende eine grundlegende Entscheidung über die Rückkehr der Götter. Details müssen gegen vorhandene Originalunterlagen geprüft werden.',
          'characters':'Bestätigte Götter: Zeus, Hermes, Ares, Athene, Hades und Poseidon. Referenz: monumentale, teilweise über 30 m große Götterstatuen. Detaillierte Charakterdaten aus Originalpaketen übernehmen.',
          'bosses':'Bossbegegnungen und Prüfungen vorgesehen. Keine freie Neuerfindung bestehender AION-Kanonentscheidungen.',
          'world':'Modernes Griechenland 2026; antike göttliche Monumente und Orte. Orte, Level und Layout aus bestehenden Originalplänen übernehmen.',
          'technical':'Unreal Engine 5 + Blender. Claude Code soll Blender und Unreal via geprüften MCP-Verbindungen bearbeiten. AION-Planungsstände bis Masterproduktion v18.0 wurden besprochen; hier sind keine Original-UE-/Blender-Projektdateien hinterlegt.',
          'qa':'Vor Umsetzung: Kanon prüfen, Prolog und alle Referenzansichten erfassen, offene und nicht implementierte Arbeit sichtbar markieren. Builds und Performance nicht als fertig melden ohne reale Tests.',
        })
        genesis = default_bible()
        genesis.update({
          'vision':'GENESIS: filmisches ambitioniertes Spielprojekt mit Unreal Engine 5 und Blender; AAA-/Cinematic-Zielbild. Projektunterlagen und Kanon vor Entwicklung importieren.',
          'story':'Bisher beschriebene Struktur: neun Phasen von Entstehung bis Schöpfung. Konkrete Missionen, Dialoge und Enden aus GENESIS-Originalunterlagen übernehmen.',
          'game_rules':'Bekannte Konzeptsysteme: Karma-Profil, Konsequenz-Netzwerk, Traumsequenzen, Emotions-Wetter, Ahnenreihe, Geister-Modus, parallele Zeitlinien, Vertrauen und Politik. Eine Liste mit 63 Kernfeatures wurde zuvor diskutiert und muss mit den Quelldateien abgeglichen werden.',
          'technical':'Unreal Engine 5, Blender, MetaHuman und Motion Matching wurden als Ziel-Technik genannt. Realen Versions- und Implementierungsstand anhand des bestehenden Repositories verifizieren.',
          'qa':'Konzept ist kein fertiger Build. Bestehendes GENESIS-Repository importieren und Inhalte mit diesem Entwurf abgleichen.'
        })
        now = stamp()
        seeds = [
          ('aion-2026','AION 2026','Open-World-Action-Adventure im modernen Griechenland; Götter, Prüfungen und sechs Lebensknoten.','Konzept','Open World / Action Adventure','AAA+ / fotorealistisch','Third/First Hybrid','v18.0 (Planungsstand)',aion),
          ('genesis','GENESIS','Cinematic-Spielprojekt mit neun Schöpfungsphasen und umfangreichen vernetzten Mechaniken.','Konzept','Cinematic / Action Adventure','AAA+ / cinematic','Third/First Hybrid','v0.1 (GAMEFORGE-Eintrag)',genesis)
        ]
        for gid,title,summary,status,genre,style,camera,version,bible in seeds:
            self.conn.execute('INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (gid,title,summary,status,genre,style,'Unreal Engine 5',camera,version,json.dumps(bible,ensure_ascii=False),now,now))
        # Erstes Bildset als offene Arbeit, keine künstlich fertigen Referenzbilder
        for name,cat,views,game in [
            ('Zeus','boss',['front','side','back','scale'],'aion-2026'),
            ('Poseidon','boss',['front','side','back'],'aion-2026'),
            ('GENESIS – Spielfigur','character',['front','side','back'],'genesis')]:
            for view in views:
                self.conn.execute('INSERT INTO ref_tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (identifier(),game,None,name,cat,view,'Original-Design aus bestehendem Projekt prüfen; keine eigenmächtige Kanonänderung.',1,0,None,None,now,now))
        self.conn.commit()

    def ensure_tasks(self,gid):
        if self.one('SELECT id FROM production_tasks WHERE game_id=? AND dlc_id IS NULL LIMIT 1',(gid,)):
            return
        now=stamp()
        with self.lock:
            for phase,title,description,acceptance in TASK_BLUEPRINTS:
                self.conn.execute('INSERT INTO production_tasks VALUES(?,?,?,?,?,?,?,?,?,?)',
                    (identifier(),gid,None,phase,title,description,acceptance,'Offen','',now))
            self.conn.commit()

    def ensure_dlc_tasks(self,gid,did):
        if self.one('SELECT id FROM production_tasks WHERE game_id=? AND dlc_id=? LIMIT 1',(gid,did)):
            return
        now=stamp()
        entries=[
           ('02 Kanon & Gamedesign','DLC-Story und Integration','DLC-Kanon, Erweiterungsumfang und Basisspiel-Abhängigkeiten abgleichen.','Freigegebener DLC-Plan'),
           ('04 Referenzen','DLC-Referenzen komplett','Alle neuen visuellen Assets planen und Referenzen freigeben.','DLC-Pflichtreferenzen vorhanden'),
           ('05 Blender-Produktion','DLC-Assets erstellen','Blender-Projekte, Animationen, Materialien und Exporte für DLC.','Blender-Dateien und Unreal-Import getestet'),
           ('06 Unreal-Gameplay','DLC implementieren','Missions-, Gameplay- und Weltintegration über Unreal.','Spielbare DLC-Funktionen getestet'),
           ('09 Test & Optimierung','DLC-Regressionstests','Basisspiel, Speicherdaten und DLC-Gameplay zusammen prüfen.','DLC-Regression mit echten Belegen'),
           ('10 Release & Abnahme','DLC-Build abnehmen','Kompatible Basisversion, eigenständige Downloads und Rechte prüfen.','DLC-Release-Build geprüft')]
        with self.lock:
            for phase,title,description,acceptance in entries:
                self.conn.execute('INSERT INTO production_tasks VALUES(?,?,?,?,?,?,?,?,?,?)',
                 (identifier(),gid,did,phase,title,description,acceptance,'Offen','',now))
            self.conn.commit()

    def files(self,gid):
        return self.all('SELECT id,game_id,dlc_id,relpath,original_name,category,size,sha256,created_at FROM imported_files WHERE game_id=? ORDER BY created_at DESC',(gid,))

    def tasks(self,gid,dlc_id=None):
        if dlc_id:
            return self.all('SELECT * FROM production_tasks WHERE game_id=? AND dlc_id=? ORDER BY phase,title',(gid,dlc_id))
        return self.all('SELECT * FROM production_tasks WHERE game_id=? AND dlc_id IS NULL ORDER BY phase,title',(gid,))

    def update_task(self,gid,tid,data):
        row=self.one('SELECT * FROM production_tasks WHERE id=? AND game_id=?',(tid,gid))
        if not row: raise ValueError('Aufgabe nicht gefunden')
        status=str(data.get('status',row['status']))
        evidence=str(data.get('evidence',row['evidence'])).strip()[:20000]
        if status not in TASK_STATUSES: raise ValueError('Ungültiger Aufgabenstatus')
        if status in ('Getestet','Abgenommen') and len(evidence)<12:
            raise ValueError('Für getestete/abgenommene Aufgaben bitte einen echten Prüfbeleg mit mindestens 12 Zeichen angeben')
        self.execute('UPDATE production_tasks SET status=?,evidence=?,updated_at=? WHERE id=?',
                     (status,evidence,stamp(),tid))
        return self.one('SELECT * FROM production_tasks WHERE id=?',(tid,))

    def save_game_file(self,stream,length,*,game_id,filename,relpath=None,dlc_id=None):
        if not self.game(game_id): raise ValueError('Unbekanntes Spiel')
        if dlc_id and not self.one('SELECT id FROM dlcs WHERE id=? AND game_id=?',(dlc_id,game_id)):
            raise ValueError('DLC gehört nicht zu diesem Spiel')
        if length<0 or length>8*1024**3:
            raise ValueError('Eine einzelne Datei darf maximal 8 GB groß sein')
        relative=safe_relpath(relpath or filename)
        original=relative.split('/')[-1]
        file_id=identifier(); target=self.base/'imports'/file_id
        digest=hashlib.sha256(); written=0
        try:
            with open(target,'xb') as out:
                while written<length:
                    chunk=stream.read(min(1024*1024,length-written))
                    if not chunk: raise ValueError('Datei unvollständig übertragen')
                    out.write(chunk); digest.update(chunk); written+=len(chunk)
            kind=categorize_file(original)
            self.execute('INSERT INTO imported_files VALUES(?,?,?,?,?,?,?,?,?,?)',
              (file_id,game_id,dlc_id,relative,original,file_id,kind,written,digest.hexdigest(),stamp()))
            return {'id':file_id,'name':original,'path':relative,'size':written,'category':kind,'sha256':digest.hexdigest()}
        except Exception:
            target.unlink(missing_ok=True)
            raise

    def zip_index(self,gid,fid):
        file=self.one('SELECT * FROM imported_files WHERE id=? AND game_id=?',(fid,gid))
        if not file: raise ValueError('Datei nicht gefunden')
        if not file['original_name'].lower().endswith('.zip'):
            raise ValueError('Nur ZIP-Dateien lassen sich hier indexieren')
        path=self.base/'imports'/file['stored_name']
        with zipfile.ZipFile(path) as z:
            members=z.infolist()
            items=[]; uncompressed=0
            for item in members[:2500]:
                items.append({'path':item.filename,'size':item.file_size,'directory':item.is_dir()})
                uncompressed+=item.file_size
            return {'filename':file['original_name'],'total_members':len(members),'shown':len(items),'uncompressed_shown':uncompressed,
              'potentially_large':len(members)>2500 or uncompressed>30*1024**3,'members':items}

    def game(self, gid):
        obj = self.one('SELECT * FROM games WHERE id=?',(gid,))
        if obj: obj['bible'] = jd(obj['bible'],default_bible())
        return obj

    def games(self):
        games = self.all('SELECT * FROM games ORDER BY updated_at DESC')
        for g in games:
            g['bible'] = jd(g['bible'],default_bible())
            g['import_count'] = self.one('SELECT COUNT(*) n FROM imported_files WHERE game_id=?',(g['id'],))['n']
            g['dlc_count'] = self.one('SELECT COUNT(*) n FROM dlcs WHERE game_id=?',(g['id'],))['n']
            g['archive_count'] = self.one('SELECT COUNT(*) n FROM archives WHERE game_id=?',(g['id'],))['n']
            g['has_full_archive'] = bool(self.one("SELECT id FROM archives WHERE game_id=? AND dlc_id IS NULL AND kind='Vollprojekt' ORDER BY created_at DESC LIMIT 1",(g['id'],)))
        return games

    def dlcs(self, gid):
        dlcs = self.all('SELECT * FROM dlcs WHERE game_id=? ORDER BY updated_at DESC',(gid,))
        for d in dlcs: d['design'] = jd(d['design'],default_dlc())
        return dlcs

    def refs(self, gid):
        return self.all('SELECT * FROM ref_tasks WHERE game_id=? ORDER BY category,name,view',(gid,))

    def archives(self, gid):
        return self.all('SELECT id,game_id,dlc_id,kind,label,version,original_name,size,sha256,created_at FROM archives WHERE game_id=? ORDER BY created_at DESC',(gid,))

    def snapshots(self, gid):
        return self.all('SELECT id,game_id,version,notes,created_at FROM snapshots WHERE game_id=? ORDER BY created_at DESC',(gid,))

    def idea_feed(self, gid, dlc_id=None):
        if not self.game(gid): raise ValueError('Spiel unbekannt')
        if dlc_id and not any(d['id']==dlc_id for d in self.dlcs(gid)):
            raise ValueError('DLC unbekannt')
        filt='dlc_id=?' if dlc_id else 'dlc_id IS NULL'
        params=(gid,dlc_id) if dlc_id else (gid,)
        return {'messages':self.all(f'SELECT * FROM idea_messages WHERE game_id=? AND {filt} ORDER BY created_at,rowid',params),
                'suggestions':self.all(f'SELECT * FROM idea_suggestions WHERE game_id=? AND {filt} ORDER BY created_at,rowid',params),
                'changes':self.all(f'SELECT * FROM idea_changes WHERE game_id=? AND {filt} ORDER BY created_at,rowid',params)}

    def add_idea_message(self, gid, body, *, dlc_id=None, provider='manual', role='user'):
        if not self.game(gid): raise ValueError('Spiel unbekannt')
        if dlc_id and not any(x['id']==dlc_id for x in self.dlcs(gid)):
            raise ValueError('DLC unbekannt')
        if role not in ('user','assistant'): raise ValueError('Unbekannte Rolle')
        body=str(body).strip()
        if not body or len(body)>12000: raise ValueError('Bitte eine Idee mit maximal 12.000 Zeichen eingeben')
        mid=identifier()
        self.execute('INSERT INTO idea_messages VALUES(?,?,?,?,?,?,?)',(mid,gid,dlc_id,role,provider,body,stamp()))
        return mid

    def offline_ideas(self, text):
        text=text.lower()
        if any(w in text for w in ('boss','kampf','gegner','gott','fähigkeit')):
            return [
                {'title':'Kampf mit klaren Phasen','detail':'Lege Angriffsmuster, Telegraphing, Ausweichfenster, Schwachstellen, Schwierigkeitsvarianten und Sieg-/Niederlagebedingungen fest.','section':'combat'},
                {'title':'Bossbegegnung in die Story integrieren','detail':'Definiere, warum die Begegnung stattfindet, welche Voraussetzung gilt und was sich nach dem Kampf in Welt und Missionen verändert.','section':'bosses'},
                {'title':'Animationen und Referenzen planen','detail':'Erfasse Charakteransichten, Animationstypen, Maßstab, Kollisionszonen und Blender-/Unreal-Importanforderungen.','section':'technical'}]
        if any(w in text for w in ('welt','tempel','insel','stadt','gebiet','landschaft','level','unterwasser')):
            return [
                {'title':'Weltgebiet spielbar machen','detail':'Definiere Eingänge, Entdeckungsziele, Laufwege, Landmarken, Interaktionen, Grenzen und Übergänge zu anderen Gebieten.','section':'world'},
                {'title':'Umwelt und Gameplay verbinden','detail':'Ergänze Rätsel, Umweltgefahren, Wettereinflüsse, NPCs und nachvollziehbare Quest-Anlässe.','section':'environments'},
                {'title':'Technische Levelplanung','detail':'Lege Größe, Streaming, Navigation, Kollisionen, Performanceziel und Referenzbilder für die Unreal-Produktion fest.','section':'technical'}]
        if any(w in text for w in ('prolog','geschichte','story','handlung','charakter','entscheidung','ende','mission','quest')):
            return [
                {'title':'Motivation und Konsequenzen ausarbeiten','detail':'Definiere Ziele, innere Konflikte, Entscheidungen und sichtbare Folgen für den Spieler.','section':'story'},
                {'title':'Missionen eindeutig strukturieren','detail':'Erstelle Startbedingungen, Spielerschritte, Dialoge, Trigger, Verzweigungen, Fehlerfälle, Belohnungen und Abnahmekriterien.','section':'chapters'},
                {'title':'Prolog und Szenenübergänge','detail':'Plane Einstieg, Kameraperspektiven, Sprechertext, Sound, Gameplay-Übergaben und relevante Referenzen.','section':'cinematics'}]
        return [
            {'title':'Spielidee spielbar definieren','detail':'Beschreibe den Core-Loop: Was macht der Spieler in den ersten fünf Minuten, welche Entscheidungen trifft er und wie erhält er Feedback?','section':'game_rules'},
            {'title':'Story und Spielziel konkretisieren','detail':'Lege Protagonist, Ziel, Hindernisse, Wendepunkte und mögliche Enden fest.','section':'story'},
            {'title':'Produktionsumfang einschätzen','detail':'Erfasse Plattform, Genre, Grafikstil, Weltgröße, notwendige Referenzen und einen ersten spielbaren Vertical Slice.','section':'technical'}]

    def ai_status(self):
        found=bool(shutil.which('claude'))
        auth=studio_v2.claude_auth() if found else {'checked':False,'logged_in':None}
        detail=('Claude Code nicht im PATH. Echte KI-Antworten benötigen eine lokale Claude-Code-Installation mit Anmeldung.' if not found else
                studio_v2.LOGIN_HINT if auth['logged_in'] is False else
                'Claude Code gefunden und angemeldet.' if auth['logged_in'] else 'Claude Code gefunden, Anmeldestatus unbekannt.')
        return {'available':found,'logged_in':auth['logged_in'],'detail':detail}

    def current_document(self,gid,dlc_id,section):
        if dlc_id:
            d=next((x for x in self.dlcs(gid) if x['id']==dlc_id),None)
            if not d: raise ValueError('DLC unbekannt')
            if section not in d['design']: raise ValueError('Ungültiger DLC-Bereich')
            return str(d['design'][section] or '')
        g=self.game(gid)
        if not g: raise ValueError('Spiel unbekannt')
        if section not in dict(FIELDS): raise ValueError('Ungültiger Spielbibel-Bereich')
        return str(g['bible'].get(section,'') or '')

    def creative_claude(self,gid,idea,dlc_id=None):
        g=self.game(gid)
        feed=self.idea_feed(gid,dlc_id)
        dlc=next((d for d in self.dlcs(gid) if d['id']==dlc_id),None)
        src=dlc['design'] if dlc else g['bible']
        # Inhaltsüberblick bewusst begrenzt: keine externen Originaldateien automatisch senden.
        doc={k:str(v)[:6500] for k,v in src.items() if str(v).strip()}
        recent=[{'role':x['role'],'body':x['body'][:1600]} for x in feed['messages'][-14:]]
        instructions=('Du bist GAMEFORGE Creative Director und unterhältst einen echten fortlaufenden deutschsprachigen Chat mit dem Spielentwickler. '
          'Reagiere DIREKT und KONKRET auf die letzte Nutzernachricht, beantworte Fragen, erkläre Auswirkungen und schlage sinnvolle neue Ideen vor. '
          'Nimm Wünsche wie „ändere Zeus von 30 auf 40 Meter“ als Änderungsauftrag zum PRÜFEN, nicht als bloßes Brainstorming. '
          'Nenne, was du verstanden hast, welche Systeme betroffen wären, und welche Angaben eventuell fehlen. '
          'Keine falschen Behauptungen, dass Gameplay oder 3D-Dateien verändert wurden. Du darfst NICHT auf Dateien/MCP/Tools zugreifen. '
          'Gib genau EIN gültiges JSON-Objekt aus, ohne Markdown. Schema: '
          '{"reply":"natürliche Antwort direkt an Nutzer",'
          '"suggestions":[{"title":"optionale neue Idee","detail":"konkrete Beschreibung","section":"story"}],'
          '"changes":[{"summary":"konkrete Änderung","section":"story",'
          '"mode":"append","new_text":"formulierte neue Passage"}]}. '
          'Nur bei ausdrücklich gewünschten Änderungen changes anlegen. Sonst leeres Array. '
          'Weitere erlaubte Änderungsart: mode="replace_text", old_text="EXAKTER Teilstring aus dem aktuellen Bereich", new_text="neuer Text". '
          'Falls bestehender Text nicht vorliegt oder exakt nicht erkennbar ist, NIEMALS einen Ersatz erfinden; frage nach oder append, wenn ausdrücklich Ergänzung gemeint. '
          'Jede Änderung muss einer gültigen section aus der Liste entsprechen. Maximal 4 Vorschläge und maximal 5 Änderungen. '
          'Bestehenden Inhalt möglichst bewahren, nicht eigenmächtig ersetzen. Verfasse vollständige und hilfreiche Antwort. '
          'Fragen zum Projekt- oder Agentenstand beantwortest du ausschließlich anhand von real_status; nichts als fertig bezeichnen, was dort nicht belegt ist. '
          'Gliedere die Antwort verständlich für Nicht-Programmierer: Verstanden, Vorschlag, Auswirkungen, benötigte Dateien, nächster Schritt.')
        payload=json.dumps({'instructions':instructions,
            'valid_sections':list(src.keys()),
            'project':{'name':g['title'],'genre':g['genre'],'style':g['style'],'version':g['version'],
                       'current_documents':doc},
            'dlc':dlc['title'] if dlc else None,'history':recent,
            'real_status':studio_v2.status_answer(self,gid,dlc_id),
            'latest_user_message':idea},ensure_ascii=False)
        if not shutil.which('claude'):
            raise ValueError('Claude Code ist nicht installiert oder nicht im PATH. Deine Nachricht bleibt gespeichert; verwende Vorlagenmodus oder installiere Claude Code.')
        try:
            run=subprocess.run(['claude','-p','--permission-mode','plan','--max-turns','1','--output-format','text'],
                input=payload,text=True,capture_output=True,timeout=150,check=False,cwd=str(self.base),encoding='utf-8',errors='replace')
        except subprocess.TimeoutExpired:
            raise ValueError('Claude hat nicht rechtzeitig geantwortet. Deine Nachricht wurde gespeichert, es wurde nichts verändert.')
        except OSError as err:
            raise ValueError('Claude kann nicht gestartet werden: '+str(err)[:300])
        if run.returncode!=0:
            out=(run.stderr or run.stdout or '')
            if studio_v2.is_auth_error(out):
                studio_v2._auth_cache.clear()
                raise ValueError(studio_v2.LOGIN_HINT)
            raise ValueError('Claude konnte keine Antwort liefern: '+(out or 'Anmeldung und CLI prüfen')[-500:])
        raw=run.stdout.strip()
        raw=re.sub(r'^```(?:json)?\s*|\s*```$', '', raw).strip()
        try: data=json.loads(raw)
        except ValueError: raise ValueError('Claude lieferte keine gültige strukturierte Antwort. Nachricht gespeichert, keine Änderung.')
        if not isinstance(data,dict): raise ValueError('Unerwartete Antwort von Claude')
        return {'reply':str(data.get('reply','')).strip()[:7000] or 'Ich habe deine Nachricht gelesen.',
                'suggestions':data.get('suggestions',[])[:4] if isinstance(data.get('suggestions'),list) else [],
                'changes':data.get('changes',[])[:5] if isinstance(data.get('changes'),list) else []}

    def propose_change(self,gid,*,dlc_id=None,source_id=None,section,summary,mode,new_text,old_text=''):
        if mode not in ('append','replace_text'): raise ValueError('Unbekannte Änderungsart')
        section=str(section);summary=str(summary).strip()[:300]
        old_text=str(old_text);new_text=str(new_text).strip()
        if not summary or not new_text or len(new_text)>20000: raise ValueError('Änderung benötigt Titel und gültigen Inhalt')
        current=self.current_document(gid,dlc_id,section)
        if mode=='replace_text' and (not old_text or current.count(old_text)!=1):
            raise ValueError('Der zu ersetzende Originaltext muss exakt einmal im Projekt vorkommen')
        h=hashlib.sha256(current.encode('utf-8')).hexdigest()
        cid=identifier()
        self.execute('INSERT INTO idea_changes VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
            (cid,gid,dlc_id,source_id,section,summary,mode,old_text,new_text,h,'Vorgeschlagen',stamp()))
        return cid

    def change_decision(self,gid,cid,action):
        if action not in ('apply','reject'): raise ValueError('Aktion ungültig')
        c=self.one('SELECT * FROM idea_changes WHERE id=? AND game_id=?',(cid,gid))
        if not c: raise ValueError('Änderung unbekannt')
        if c['status']!='Vorgeschlagen':raise ValueError('Diese Änderung wurde bereits entschieden')
        if action=='reject':
            self.execute('UPDATE idea_changes SET status=? WHERE id=?',('Abgelehnt',cid))
            return {'status':'Abgelehnt'}
        current=self.current_document(gid,c['dlc_id'],c['section'])
        if hashlib.sha256(current.encode('utf-8')).hexdigest()!=c['base_hash']:
            raise ValueError('Der Zielbereich hat sich inzwischen verändert. Bitte Änderung neu formulieren, damit nichts überschrieben wird.')
        if c['mode']=='replace_text':
            if current.count(c['old_text'])!=1:raise ValueError('Originalpassage nicht mehr eindeutig auffindbar')
            updated=current.replace(c['old_text'],c['new_text'],1)
        else:
            updated=current+('\n\n' if current else '')+c['new_text']
        # Der Snapshot enthält auch die DLC-Planung. Alte Version bleibt erhalten.
        g=self.game(gid)
        self.snapshot(gid,g['version'],f'Vor Chat-Änderung: {c["summary"]}')
        if c['dlc_id']:
            d=next(x for x in self.dlcs(gid) if x['id']==c['dlc_id'])
            design=d['design'];design[c['section']]=updated
            self.update_dlc(gid,c['dlc_id'],{'design':design})
        else:
            bible=g['bible'];bible[c['section']]=updated
            self.update_game(gid,{'bible':bible})
        self.execute('UPDATE idea_changes SET status=? WHERE id=?',('Übernommen',cid))
        self.add_idea_message(gid,f'Änderung übernommen: {c["summary"]}. Bereich {c["section"]} aktualisiert. Sicherheitsversion gespeichert. Spiel- oder 3D-Dateien wurden dadurch noch nicht implementiert.',
            dlc_id=c['dlc_id'],provider='system',role='assistant')
        return {'status':'Übernommen','section':c['section']}

    def brainstorm(self,gid,data):
        dlc=data.get('dlc_id') or None
        message=str(data.get('message','')).strip()
        if not message or len(message)>12000: raise ValueError('Bitte Text mit höchstens 12.000 Zeichen eingeben')
        provider=data.get('provider','offline')
        if provider not in ('offline','claude'): raise ValueError('Unbekannter Modus')
        mid=self.add_idea_message(gid,message,dlc_id=dlc,provider='user')
        if provider=='claude':
            # Nutzertext schon gespeichert, echtes Modellfeedback nur bei erfolgreichem CLI-Aufruf.
            response=self.creative_claude(gid,message,dlc)
        elif studio_v2.is_status_question(message):
            # Statusfragen offline mit echten Daten beantworten – klar als „keine KI“ gekennzeichnet.
            response={'reply':studio_v2.status_answer(self,gid,dlc),'suggestions':[],'changes':[]}
            provider='data'
        else:
            response={'reply':'Deine Nachricht wurde im Projekt gespeichert. Dies ist nur der lokale Vorlagenmodus: Er kann keine echte KI-Antwort oder fachliche Änderungsanalyse liefern. Wähle „Mit Claude antworten“ für einen Dialog und konkrete Änderungsentwürfe.',
                      'suggestions':self.offline_ideas(message),'changes':[]}
        aid=self.add_idea_message(gid,response['reply'],dlc_id=dlc,provider=provider,role='assistant')
        for obj in response['suggestions']:
            if not isinstance(obj,dict):continue
            title=str(obj.get('title','')).strip()[:220];detail=str(obj.get('detail','')).strip()[:3000]
            field=str(obj.get('section','story'))
            if not title or not detail:continue
            valid=self.current_sections(gid,dlc)
            if dlc and field not in valid:
                field={'world':'new_world','environments':'new_assets','chapters':'quests',
                       'characters':'new_characters','bosses':'new_characters','npcs':'new_characters',
                       'combat':'gameplay','game_rules':'gameplay','technical':'integration',
                       'physics':'gameplay','ui':'menu','ai':'gameplay','audio':'new_assets'}.get(field, 'story')
            if field not in valid:continue
            self.execute('INSERT INTO idea_suggestions VALUES(?,?,?,?,?,?,?,?,?,?)',
                (identifier(),gid,dlc,aid,title,detail,field,'Vorgeschlagen',0,stamp()))
        for obj in response['changes']:
            if not isinstance(obj,dict):continue
            try:
                self.propose_change(gid,dlc_id=dlc,source_id=aid,section=obj.get('section',''),
                    summary=obj.get('summary',''),mode=obj.get('mode','append'),
                    new_text=obj.get('new_text',''),old_text=obj.get('old_text',''))
            except ValueError as err:
                self.add_idea_message(gid,'Ein Änderungsentwurf wurde nicht übernommen: '+str(err),
                    dlc_id=dlc,provider='system',role='assistant')
        return self.idea_feed(gid,dlc)

    def current_sections(self,gid,dlc_id):
        return tuple(default_dlc()) if dlc_id else tuple(dict(FIELDS))

    def decide_idea(self,gid,sid,action):
        if action not in ('accept','reject','integrate'): raise ValueError('Unbekannte Aktion')
        row=self.one('SELECT * FROM idea_suggestions WHERE game_id=? AND id=?',(gid,sid))
        if not row: raise ValueError('Vorschlag nicht gefunden')
        if action in ('accept','reject'):
            status='Angenommen' if action=='accept' else 'Abgelehnt'
            self.execute('UPDATE idea_suggestions SET status=?,integrated=0 WHERE id=?',(status,sid))
        elif action=='integrate':
            if row['status']!='Angenommen': raise ValueError('Nur angenommene Vorschläge können integriert werden')
            if row['integrated']: return {'status':'bereits integriert'}
            block=f'\n\n[GAMEFORGE-Idee {sid}] {row["title"]}\n{row["detail"]}'
            if row['dlc_id']:
                d=next((x for x in self.dlcs(gid) if x['id']==row['dlc_id']),None)
                if not d: raise ValueError('DLC fehlt')
                doc=d['design']; k={'chapters':'quests','characters':'new_characters','world':'new_world','combat':'gameplay','technical':'integration','bosses':'new_characters','environments':'new_assets','npcs':'new_characters','game_rules':'gameplay'}.get(row['section'],row['section'])
                if k not in doc:k='story'
                doc[k]=doc.get(k,'')+block
                self.update_dlc(gid,d['id'],{'design':doc})
            else:
                self.snapshot(gid,self.game(gid)['version'],'Automatischer Stand vor Ideenübernahme')
                bible=self.game(gid)['bible'];field=row['section']
                bible[field]=bible.get(field,'')+block
                self.update_game(gid,{'bible':bible})
            self.execute('UPDATE idea_suggestions SET integrated=1 WHERE id=?',(sid,))
        return {'status':'ok'}

    def add_game(self, data):
        title = str(data.get('title','')).strip()
        if not title: raise ValueError('Bitte einen Spielnamen eintragen.')
        if len(title)>120: raise ValueError('Der Spielname darf höchstens 120 Zeichen lang sein.')
        game_id = identifier(); now=stamp()
        bible=default_bible()
        # Angaben aus dem Assistenten sind Nutzerangaben, keine erfundenen Spielinhalte.
        vision=str(data.get('vision','')).strip()[:20000]
        if vision: bible['vision']=vision
        platform=str(data.get('platform','')).strip()[:300]
        if platform: bible['release']='Zielplattform (Angabe aus dem Neues-Spiel-Assistenten): '+platform
        wishes=str(data.get('wishes','')).strip()[:20000]
        if wishes: bible['game_rules']='Wünsche aus dem Neues-Spiel-Assistenten (noch nicht ausgearbeitet):\n'+wishes
        self.execute('INSERT INTO games VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', (game_id,title,str(data.get('summary',''))[:2000],'Idee',str(data.get('genre',''))[:200],
            str(data.get('style',''))[:200],'Unreal Engine 5',str(data.get('camera',''))[:200],'v0.1',json.dumps(bible,ensure_ascii=False),now,now))
        self.ensure_tasks(game_id)
        art_direction.ensure_profile(self,game_id)
        # Jede neue Spielidee erhält eine isolierte lokale Umgebung samt Agenten-Dateien.
        # Kein Anschluss an bestehende Claude-Desktop-Sitzungen; keine Blender/Unreal-Ausführung.
        try:
            workspace=self.direct.create_workspace(game_id)
            agent_studio.install(self.game(game_id), workspace['workspace'])
        except Exception:
            # Die Spieleidee bleibt auch auf Systemen mit eingeschränktem Dateizugriff erhalten.
            pass
        return self.game(game_id)

    def update_game(self, gid, data):
        g = self.game(gid)
        if not g: raise ValueError('Spiel nicht gefunden.')
        cols = ('title','summary','status','genre','style','engine','camera','version')
        changes = {k:str(data[k])[:100000] for k in cols if k in data}
        if 'status' in changes and changes['status'] not in STATES: raise ValueError('Unbekannter Status')
        if changes.get('status') in ('Fertig','Veröffentlicht') and g['status'] not in ('Fertig','Veröffentlicht'):
            tasks=self.tasks(gid)
            if not tasks or any(t['status']!='Abgenommen' for t in tasks):
                raise ValueError('Noch nicht fertig: erst alle Entwicklungsaufgaben mit Prüfbeleg abnehmen.')
            if any(r['required'] and not r['approved'] for r in self.refs(gid)):
                raise ValueError('Noch nicht fertig: Pflichtreferenzen sind nicht alle freigegeben.')
            if not self.one("SELECT id FROM archives WHERE game_id=? AND dlc_id IS NULL AND kind='Windows-Build' LIMIT 1",(gid,)):
                raise ValueError('Noch nicht fertig: finalen Windows-Build zuerst als Archiv sichern.')
            if not self.one("SELECT id FROM archives WHERE game_id=? AND dlc_id IS NULL AND kind='Vollprojekt' LIMIT 1",(gid,)):
                raise ValueError('Noch nicht fertig: vollständiges Originalprojekt zuerst als Vollprojekt-ZIP sichern.')
        if 'bible' in data:
            if not isinstance(data['bible'],dict): raise ValueError('Ungültige Spielbibel')
            changes['bible'] = json.dumps({k:str(data['bible'].get(k,''))[:120000] for k,_ in FIELDS},ensure_ascii=False)
        if changes:
            changes['updated_at']=stamp()
            self.execute('UPDATE games SET '+', '.join(f'{k}=?' for k in changes)+' WHERE id=?',tuple(changes.values())+(gid,))
        return self.game(gid)

    def add_dlc(self, gid, data):
        if not self.game(gid): raise ValueError('Spiel nicht gefunden')
        name = str(data.get('title','')).strip()
        if not name: raise ValueError('DLC-Name fehlt')
        did=identifier(); now=stamp()
        self.execute('INSERT INTO dlcs VALUES(?,?,?,?,?,?,?,?,?,?)',(did,gid,name,str(data.get('summary','')),'Idee','v0.1',str(data.get('compatible_version','')),json.dumps(default_dlc()),now,now))
        self.ensure_dlc_tasks(gid,did)
        return did

    def update_dlc(self, gid,did,data):
        target = self.one('SELECT * FROM dlcs WHERE id=? AND game_id=?',(did,gid))
        if not target: raise ValueError('DLC nicht gefunden')
        cols = ('title','summary','status','version','compatible_version')
        changes={k:str(data[k]) for k in cols if k in data}
        if 'status' in changes and changes['status'] not in STATES: raise ValueError('Unbekannter Status')
        if 'design' in data:
            if not isinstance(data['design'],dict): raise ValueError('Ungültiges DLC-Design')
            changes['design']=json.dumps({k:str(data['design'].get(k,''))[:120000] for k in default_dlc()},ensure_ascii=False)
        if changes:
            changes['updated_at']=stamp()
            self.execute('UPDATE dlcs SET '+', '.join(f'{k}=?' for k in changes)+' WHERE game_id=? AND id=?',tuple(changes.values())+(gid,did))
        return self.one('SELECT id,title FROM dlcs WHERE id=?',(did,))

    def add_ref(self,gid,data):
        if not self.game(gid): raise ValueError('Spiel nicht gefunden')
        name=str(data.get('name','')).strip()
        category=str(data.get('category','character'))
        view=str(data.get('view','front'))
        if not name: raise ValueError('Assetname fehlt')
        if category not in CATEGORIES or view not in VIEWS[category]: raise ValueError('Kategorie oder Ansicht ungültig')
        dlc_id = data.get('dlc_id') or None
        if dlc_id and not self.one('SELECT id FROM dlcs WHERE game_id=? AND id=?',(gid,dlc_id)):
            raise ValueError('DLC gehört nicht zu diesem Spiel')
        rid=identifier(); now=stamp()
        self.execute('INSERT INTO ref_tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                     (rid,gid,dlc_id,name,category,view,str(data.get('details','')),
                     int(bool(data.get('required',True))),0,None,None,now,now))
        return rid

    def add_ref_bundle(self,gid,data):
        """Für einen Assettyp alle Standardansichten als überprüfbare Einzelaufträge anlegen."""
        category=str(data.get('category','character'))
        if category not in VIEWS: raise ValueError('Asset-Kategorie ungültig')
        results=[]
        for view in VIEWS[category]:
            task=dict(data,view=view)
            results.append(self.add_ref(gid,task))
        return results

    def restore_snapshot(self,gid,sid):
        row=self.one('SELECT * FROM snapshots WHERE game_id=? AND id=?',(gid,sid))
        if not row: raise ValueError('Gesicherter Versionsstand nicht gefunden')
        archived=jd(row['snapshot'])
        original=archived.get('game')
        if not original: raise ValueError('Snapshot enthält keinen Projektstand')
        # Immer erst einen neuen Rettungsstand des aktuellen Projekts erstellen
        self.snapshot(gid,self.game(gid)['version']+' (vor Wiederherstellung)','Automatische Sicherung vor Snapshot-Wiederherstellung')
        payload={k:original[k] for k in ('title','summary','status','genre','style','engine','camera','version') if k in original}
        payload['bible']=original['bible']
        self.update_game(gid,payload)
        return self.game(gid)

    def set_ref_approved(self, gid,rid,approved):
        r=self.one('SELECT id,image_path FROM ref_tasks WHERE game_id=? AND id=?',(gid,rid))
        if not r: raise ValueError('Referenz nicht gefunden')
        if approved and not r['image_path']: raise ValueError('Zuerst ein Referenzbild importieren')
        self.execute('UPDATE ref_tasks SET approved=?,updated_at=? WHERE id=?',(int(bool(approved)),stamp(),rid))

    def prompt(self,gid,rid):
        g=self.game(gid)
        r=self.one('SELECT * FROM ref_tasks WHERE game_id=? AND id=?',(gid,rid))
        if not g or not r: raise ValueError('Referenz nicht gefunden')
        canon = g['bible'].get('canon','')[:1500]
        return '\n'.join([
          f'Erstelle EIN konsistentes Produktions-Referenzbild für das Spiel „{g["title"]}“.',
          f'ASSET-ID: {r["id"]} | Asset: {r["name"]} | Kategorie: {CATEGORIES[r["category"]]} | Benötigte Ansicht: {VIEW_LABELS.get(r["view"],r["view"])}.',
          f'Art Direction: {g["style"]}. Genre: {g["genre"]}. Stil und Maßstäbe müssen zum bestehenden Projekt passen.',
          f'Verbindliche Asset-Anforderungen: {r["details"] or "Details anhand freigegebener Hauptreferenz beibehalten."}',
          f'Story-Kanon, soweit relevant: {canon or "Noch nicht festgelegt; keine eigenmächtigen Lore-Details erfinden."}',
          'PRODUKTIONSREGELN: Lesbare Silhouette, unverfälschte Proportionen, keine abgeschnittenen Teile, keine Wasserzeichen, keine störende Typografie.',
          'Bei Front/Seite/Rücken eine ruhige, möglichst orthografische Studioansicht auf neutralem Hintergrund; keine dramatische Perspektivverzerrung.',
          'Andere Ansichten müssen sich auf dieselbe freigegebene Hauptreferenz beziehen. Falls ein Hauptbild mitgeliefert ist, Form, Kleidung, Farben und Ornamentik exakt konsistent halten.',
          'Materialtrennung und technische Details so eindeutig zeigen, dass Blender-Modellierung vorbereitet werden kann.',
          'Dieses Bild ist nur eine visuelle Referenz, kein fertiges 3D-Modell und keine technische Implementierung.'
        ])

    def completeness(self, gid):
        g=self.game(gid)
        if not g: raise ValueError('Spiel nicht gefunden')
        missing=[label for key,label in FIELDS if key in REQUIRED_CORE and not g['bible'].get(key,'').strip()]
        refs=self.refs(gid)
        missing_refs=[r for r in refs if r['required'] and not r['approved']]
        full=bool(self.one("SELECT id FROM archives WHERE game_id=? AND dlc_id IS NULL AND kind='Vollprojekt' LIMIT 1",(gid,)))
        return {'missing_sections':missing,'reference_total':len(refs),'reference_open':len(missing_refs),
                'reference_approved':sum(1 for r in refs if r['approved']),'full_source_imported':full,
                'specification_ready':len(missing)==0 and len(missing_refs)==0,
            'imported_file_count':len(self.files(gid)),
            'tasks_total':len(self.tasks(gid)),
            'tasks_approved':sum(t['status']=='Abgenommen' for t in self.tasks(gid)),
            'tasks_tested':sum(t['status'] in ('Getestet','Abgenommen') for t in self.tasks(gid)),
                'notice':'Automatische Checkliste ersetzt keine manuelle Qualitätskontrolle. Nicht vorhandene Quellprojekte werden nicht erfunden.'}

    def snapshot(self,gid,version,notes=''):
        g=self.game(gid)
        if not g: raise ValueError('Spiel nicht gefunden')
        sid=identifier(); now=stamp()
        capture={'game':g,'dlcs':self.dlcs(gid),'references':self.refs(gid),'archives':self.archives(gid)}
        self.execute('INSERT INTO snapshots VALUES(?,?,?,?,?,?)',(sid,gid,version or g['version'],notes,json.dumps(capture,ensure_ascii=False),now))
        return sid

    def save_upload(self, stream, length, *, filename, kind, game_id, dlc_id=None, reference_id=None, label='', version=''):
        if not self.game(game_id): raise ValueError('Unbekanntes Spiel')
        if dlc_id and not self.one('SELECT id FROM dlcs WHERE id=? AND game_id=?',(dlc_id,game_id)):
            raise ValueError('DLC-Zuordnung ungültig')
        filename=clean_filename(filename)
        if reference_id:
            ref = self.one('SELECT * FROM ref_tasks WHERE id=? AND game_id=?',(reference_id,game_id))
            if not ref: raise ValueError('Unbekannte Referenz')
            if (ref['dlc_id'] or None)!=(dlc_id or None): raise ValueError('Referenz ist einem anderen DLC zugeordnet')
            if Path(filename).suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):
                raise ValueError('Nur PNG, JPG oder WEBP als Bildreferenz erlaubt')
            if length>30*1024*1024: raise ValueError('Bilddatei größer als 30 MB')
            destdir=self.base/'refs'
        else:
            if Path(filename).suffix.lower()!='.zip': raise ValueError('Projektdateien als ZIP importieren')
            destdir=self.base/'uploads'
        file_id=identifier()
        ext=Path(filename).suffix.lower()
        target=(destdir/(file_id+ext))
        h=hashlib.sha256(); written=0
        try:
            with open(target,'xb') as out:
                while written<length:
                    data=stream.read(min(1024*1024,length-written))
                    if not data: raise ValueError('Upload unvollständig')
                    written+=len(data); h.update(data); out.write(data)
            if reference_id:
                with open(target,'rb') as f:
                    magic=f.read(16)
                if not (magic.startswith(b'\x89PNG\r\n\x1a\n') or magic.startswith(b'\xff\xd8\xff') or magic.startswith(b'RIFF') and b'WEBP' in magic):
                    raise ValueError('Datei ist kein unterstütztes Bild')
                # Keine bisherige Bilddatei löschen: revisionssicherer Wechsel auf neue Version
                self.execute('UPDATE ref_tasks SET image_path=?,image_name=?,approved=0,updated_at=? WHERE id=?',
                             (target.name,filename,stamp(),reference_id))
                return {'id':reference_id,'filename':filename,'size':written,'sha256':h.hexdigest()}
            if not zipfile.is_zipfile(target): raise ValueError('Die Datei ist kein gültiges ZIP')
            aid=identifier()
            self.execute('INSERT INTO archives VALUES(?,?,?,?,?,?,?,?,?,?,?)',
              (aid,game_id,dlc_id,kind,label or filename,version,filename,target.name,written,h.hexdigest(),stamp()))
            return {'id':aid,'filename':filename,'size':written,'sha256':h.hexdigest()}
        except Exception:
            target.unlink(missing_ok=True)
            raise

    def zip_package(self,gid,dlc_id=None,include_source=False):
        g=self.game(gid)
        if not g: raise ValueError('Spiel nicht gefunden')
        dlcs=self.dlcs(gid)
        target_dlc=next((d for d in dlcs if d['id']==dlc_id),None) if dlc_id else None
        if dlc_id and not target_dlc: raise ValueError('DLC nicht gefunden')
        refs=[r for r in self.refs(gid) if (r['dlc_id']==dlc_id if dlc_id else r['dlc_id'] is None)]
        checks=self.completeness(gid)
        output=tempfile.SpooledTemporaryFile(max_size=16*1024*1024,mode='w+b')
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
            def write_json(p,obj): z.writestr(p,json.dumps(obj,ensure_ascii=False,indent=2))
            if target_dlc:
                stem=slug(g['title']+'-'+target_dlc['title'])
                project={'base_game':g['title'],'base_id':gid,'dlc':target_dlc,'status':'ENTWURF / nicht implementiert'}
                write_json('DATA/DLC.json',project)
                readme=f'''# {g['title']} — DLC {target_dlc['title']}\n\nDieses Paket enthält DLC-Spezifikationen, nicht automatisch ein fertiges Unreal-DLC.\nBasis-Spiel-ID: {gid}\nDLC-ID: {dlc_id}\nKompatible Basisversion: {target_dlc['compatible_version'] or 'NICHT FESTGELEGT'}\nBedingung: DLC-Abhängigkeiten und Kompatibilität mit realem Unreal-Projekt überprüfen.\n'''
            else:
                stem=slug(g['title'])
                write_json('DATA/GAME.json',g)
                write_json('DATA/DLCS.json',dlcs)
                write_json('DATA/QUALITY_GATE.json',checks)
                txt='\n\n'.join(f'## {label}\n{g["bible"].get(k,"") or "[FEHLT – MUSS AUSGEARBEITET WERDEN]"}' for k,label in FIELDS)
                z.writestr('GAME_BIBLE/GAME_BIBLE.md',f'# {g["title"]}\n\n{txt}\n')
                readme=f'''# {g['title']} — Claude-Code-Produktionspaket\n\nProjekt: {g['title']} | Version: {g['version']} | Status: {g['status']}\nErstellungsdatum: {stamp()}\n\nDieses Paket ist ein PLANUNGS- und REFERENZPAKET. Es ist kein fertiges Spiel.\nUnvollständige Abschnitte: {', '.join(checks['missing_sections']) or 'keine automatisch erkannten'}\nOffene Referenzen: {checks['reference_open']}\nUnreal/Blender-Vollprojekt hinterlegt: {'ja' if checks['full_source_imported'] else 'NEIN'}\n\nSämtliche tatsächlichen Asset- und Projektdaten müssen vor Arbeiten überprüft werden.\n'''
            accepted_ideas=[x for x in self.all("SELECT * FROM idea_suggestions WHERE game_id=? AND status='Angenommen' ORDER BY created_at,rowid",(gid,))
                            if (x['dlc_id']==dlc_id if dlc_id else x['dlc_id'] is None)]
            write_json('CREATIVE_DIRECTOR/ACCEPTED_IDEAS.json',accepted_ideas)
            accepted_changes=[x for x in self.all('SELECT * FROM idea_changes WHERE game_id=? ORDER BY created_at,rowid',(gid,))
                              if (x['dlc_id']==dlc_id if dlc_id else x['dlc_id'] is None) and x['status']=='Übernommen']
            write_json('CREATIVE_DIRECTOR/APPLIED_CHANGES.json',accepted_changes)
            z.writestr('CREATIVE_DIRECTOR/LESEN.md',
             '# Angenommene Ideen\n\nNur Ideen mit Status Angenommen sind berücksichtigt.\n'
             'Nicht integrierte Ideen sind Konzepte, keine umgesetzten Spielfunktionen.\n'
             'Bei Widersprüchen zur Spielbibel Rückfrage halten, nicht eigenmächtig überschreiben.\n')
            write_json('DATA/REFERENCE_TASKS.json',refs)
            imported=[f for f in self.files(gid) if (f['dlc_id']==dlc_id if dlc_id else f['dlc_id'] is None)]
            write_json('DATA/IMPORTED_FILES.json',imported)
            write_json('DATA/PRODUCTION_TASKS.json',self.tasks(gid,dlc_id))
            z.writestr('CLAUDE_CODE/ORIGINALDATEN_IMPORT.md',
              '# Umgang mit Originaldaten\n\nAlle importierten Unterlagen sind Originalquellen. Vor jeder Änderung zuerst inventarisieren, kanonische Version prüfen und Widersprüche melden.\n'
              'Dateien unter IMPORTED_DATA wurden einzeln importiert. ZIP-Archive unter PROJECT_SOURCE sind unveränderte Originalarchive.\n'
              'Fehlende echte Blender-/Unreal-Dateien NICHT halluzinieren. Eingelagerte ZIP-Dateien nur in separater Arbeitskopie entpacken.\n')
            # Leichtgewichtige Originalunterlagen (bis 150 MB gesamt) zur schnellen Bestandsaufnahme.
            doc_budget=150*1024**2
            for f in imported:
                path=self.base/'imports'/f['id']
                if not path.is_file(): continue
                if f['category'] in ('documents','code','images') and f['size']<=doc_budget:
                    z.write(path,'IMPORTED_DATA/'+f['id']+'/'+f['relpath'])
                    doc_budget-=f['size']
            if include_source:
                # Vollständige unveränderte Originaldateien inkl. großer Projekte.
                for f in imported:
                    path=self.base/'imports'/f['id']
                    if path.is_file(): z.write(path,'ALL_IMPORTED_FILES/'+f['id']+'/'+f['relpath'],compress_type=zipfile.ZIP_STORED)

            archive_rows=self.archives(gid)
            write_json('DATA/ARCHIVE_REGISTER.json',archive_rows)
            z.writestr('START_HIER.md',readme)
            claude='''# CLAUDE CODE – VERBINDLICHER ARBEITSAUFTRAG\n\n1. Lese START_HIER.md, DATA/*.json, alle vorhandenen GAME_BIBLE-Dateien und Referenzen.\n2. Unterscheide PLANNED, REFERENCED, IMPLEMENTED, COMPILED, PLAYTESTED, APPROVED. Niemals einen Status erfinden.\n3. Bewahre bestehenden Story-Kanon. Bei Konflikten Originaldokumente prüfen und Auftrag anhalten bis Entscheidung vorliegt.\n4. Analysiere reale Unreal-/Blender-Projekte, sofern sie bereitgestellt wurden; prüfe MCP-Erreichbarkeit einzeln.\n5. Implementiere nur nach priorisiertem Entwicklungsplan. Für jedes System Akzeptanzkriterien und realen Testnachweis dokumentieren.\n6. Modelle durch Blender, Unreal-Projekt über dessen Tools/MCP; Fehler protokollieren, keine unkontrollierten Überschreibungen.\n7. Vor größeren Änderungen Git-Branch und Backup. Vor Löschung, Veröffentlichung, Kauf oder produktiven Zugriffen Zustimmung einholen.\n8. Für DLC zuerst Basisversion, Save-Kompatibilität, Asset-IDs, Paketierung, Abhängigkeiten und Regressionen prüfen.\n9. Dieses Paket kann fehlende Daten enthalten. Melde Lücken, statt fehlende Inhalte heimlich als fertig anzunehmen.\n10. Erzeuge am Ende eine belegbare Build-/Test-/Fehlerliste, nicht nur eine Fertigmeldung.\n'''
            z.writestr('CLAUDE_CODE/ARBEITSAUFTRAG.md',claude)
            z.writestr('CLAUDE_CODE/PRODUKTIONSPLAN.md','''# Stufenplan\n\n01 Bestandsaufnahme und Kanonprüfung\n02 Vollständigkeit / offene Referenzen\n03 Kleinster spielbarer Vertical Slice\n04 Systemarchitektur und Datenmodelle\n05 Blender-Produktion / Unreal-Import\n06 Gameplay / Story / NPC / Missionen\n07 Prolog, Cinematics, UI, Musik und Speicherstände\n08 Integrationstests, Performance und Zugänglichkeit\n09 Packaging, Regressionstests, Abnahme\n''')
            for r in refs:
                z.writestr(f'PROMPTS/{r["id"]}.txt',self.prompt(gid,r['id']))
                if r['image_path']:
                    f=self.base/'refs'/r['image_path']
                    if f.is_file():
                        z.write(f,f'REFERENCES/{r["id"]}_{clean_filename(r["image_name"] or "reference.png")}')
            if include_source:
                for archive in archive_rows:
                    if (archive['dlc_id']==dlc_id if dlc_id else archive['dlc_id'] is None):
                        src=self.one('SELECT file_path FROM archives WHERE id=?',(archive['id'],))
                        p=self.base/'uploads'/src['file_path']
                        if p.is_file(): z.write(p,f'PROJECT_SOURCE/{archive["id"]}_{clean_filename(archive["original_name"])}',compress_type=zipfile.ZIP_STORED)
            # Teamkonfigurationen für 20 bestätigte Claude-Code-Agenten, ohne externe Programme auszuführen.
            for agent_path, agent_text in agent_studio.package_files(g,target_dlc).items():
                z.writestr('AGENT_STUDIO/'+agent_path,agent_text)
            if (RESOURCE/'TEAM_ARCHITEKTUR_20_AGENTEN.md').exists():
                z.write(RESOURCE/'TEAM_ARCHITEKTUR_20_AGENTEN.md','AGENT_STUDIO/TEAM_ARCHITEKTUR_20_AGENTEN.md')
            if (RESOURCE/'MODULE_CATALOG.json').exists():
                z.write(RESOURCE/'MODULE_CATALOG.json','QUALITY_CONTROL/MODULE_CATALOG.json')
            for filename in ('ROADMAP_APPROVED_1_40.json','ENTWICKLUNGSPLAN_1_40.md','AGENTS_APPROVED_1_20.json'):
                item=RESOURCE/filename
                if item.exists(): z.write(item,'GAMEFORGE_ROADMAP/'+filename)
        output.seek(0)
        return output, f'{stem}_{"vollpaket" if include_source else "claude_paket"}.zip'

    def create_backup(self):
        """Vollständige lokale Datenbibliothek ohne aktuelle temporäre Backupdatei sichern."""
        fd,tmp=tempfile.mkstemp(prefix='gameforge-db-',suffix='.sqlite3')
        os.close(fd)
        try:
            dst=sqlite3.connect(tmp)
            try:
                with self.lock:
                    self.conn.backup(dst)
            finally:
                # Unter Windows sonst gesperrt: Temp-Datei ließ sich nicht löschen.
                dst.close()
            output=tempfile.SpooledTemporaryFile(max_size=16*1024*1024,mode='w+b')
            with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,allowZip64=True) as z:
                z.write(tmp,'GAMEFORGE_DATA/gameforge.sqlite3')
                for folder in ('uploads','refs','imports'):
                    for p in (self.base/folder).rglob('*'):
                        if p.is_file(): z.write(p, f'GAMEFORGE_DATA/{p.relative_to(self.base).as_posix()}',compress_type=zipfile.ZIP_STORED if p.suffix.lower()=='.zip' else zipfile.ZIP_DEFLATED)
                z.writestr('SICHERUNG_LESEN.txt','GAMEFORGE schließen. GAMEFORGE_DATA aus der Sicherung an den Speicherort des Programms zurückkopieren. Vorher die aktuelle GAMEFORGE_DATA sichern!')
            output.seek(0)
            return output
        finally:
            Path(tmp).unlink(missing_ok=True)


def json_bytes(obj):
    return json.dumps(obj,ensure_ascii=False).encode('utf-8')


class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self, addr, store):
        self.store=store
        super().__init__(addr,API)


class API(BaseHTTPRequestHandler):
    server_version='GAMEFORGE/'+VERSION
    def log_message(self, format, *args):
        print('[GAMEFORGE]',format%args)

    def send_bytes(self,b,ctype='application/json',filename=None):
        self.send_response(200)
        self.send_header('Content-Type',ctype)
        self.send_header('Content-Length',str(len(b)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        if filename:
            self.send_header('Content-Disposition',f'attachment; filename="{clean_filename(filename)}"')
        self.end_headers()
        self.wfile.write(b)

    def send_stream(self,f,ctype='application/zip',filename=None):
        try:
            f.seek(0,os.SEEK_END)
            length=f.tell()
            f.seek(0)
            self.send_response(200)
            self.send_header('Content-Type',ctype)
            self.send_header('Content-Length',str(length))
            self.send_header('Cache-Control','no-store')
            if filename:
                self.send_header('Content-Disposition',f'attachment; filename="{clean_filename(filename)}"')
            self.end_headers()
            shutil.copyfileobj(f,self.wfile,1024*1024)
        finally:
            f.close()

    def err(self,msg,code=400):
        b=json_bytes({'error':str(msg)})
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def payload(self):
        length=int(self.headers.get('Content-Length','0'))
        if length>2*1024*1024: raise ValueError('JSON zu groß')
        return json.loads(self.rfile.read(length) or '{}')

    def static(self,path):
        mapping={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/refstudio.js':'refstudio.js','/styles.css':'styles.css'}
        name=mapping.get(path)
        if not name: return self.err('Nicht gefunden',404)
        file=WEB/name
        mime='text/html; charset=utf-8' if name.endswith('.html') else ('text/javascript; charset=utf-8' if name.endswith('.js') else 'text/css; charset=utf-8')
        return self.send_bytes(file.read_bytes(),mime)

    def route(self,method):
        parsed=urlparse(self.path); path=parsed.path
        query={k:v[0] for k,v in parse_qs(parsed.query).items()}
        parts=[unquote(p) for p in path.strip('/').split('/')]
        db=self.server.store
        if method=='GET' and path in ('/','/index.html','/app.js','/refstudio.js','/styles.css'): return self.static(path)
        if parts==['api','agents'] and method=='GET':
            return self.send_bytes(json_bytes({'approved_count':20,'agents':agent_studio.roster(detailed=True),
               'notes':'Konfigurationen genehmigt, Claude/MCP auf diesem PC nicht durch diesen Katalog nachgewiesen.'}))
        if parts==['api','roadmap'] and method=='GET':
            return self.send_bytes((RESOURCE/'ENTWICKLUNGSPLAN_1_40.md').read_bytes(),'text/markdown; charset=utf-8',filename='GAMEFORGE_ENTWICKLUNGSPLAN_1_40.md')
        if parts==['api','ai','status'] and method=='GET': return self.send_bytes(json_bytes(db.ai_status()))
        if parts==['api','home'] and method=='GET': return self.send_bytes(json_bytes(studio_v2.home_overview(db)))
        if parts==['api','system','health'] and method=='GET':
            gid=query.get('game_id') or ''
            ws=db.direct.settings(gid).get('workspace') if gid and db.game(gid) else None
            return self.send_bytes(json_bytes(studio_v2.system_health(ws,refresh=query.get('refresh')=='1')))
        if parts==['api','roadmap','status'] and method=='GET':
            return self.send_bytes(json_bytes(studio_v2.roadmap_status(jd((RESOURCE/'ROADMAP_APPROVED_1_40.json').read_text(encoding='utf-8')))))
        if parts==['api','config'] and method=='GET':
            catalog=jd((RESOURCE/'MODULE_CATALOG.json').read_text(encoding='utf-8'))
            return self.send_bytes(json_bytes({'fields':FIELDS,'states':STATES,'categories':CATEGORIES,'views':VIEWS,'view_labels':VIEW_LABELS,'kinds':KINDS,'catalog_modules':len(catalog.get('modules',[])),'version':VERSION,'schema_version':db.schema_version,'pipeline_stages':studio_v2.PIPELINE_STAGES,'approved_roadmap':jd((RESOURCE/'ROADMAP_APPROVED_1_40.json').read_text(encoding='utf-8')),'phases':PHASES,'task_statuses':TASK_STATUSES}))
        if parts==['api','reference','status'] and method=='GET':
            return self.send_bytes(json_bytes(db.refengine.status(query.get('game_id') or None)))
        if parts==['api','reference','system'] and method=='GET':
            return self.send_bytes(json_bytes(ref_hw.system_info(db.base,refresh=query.get('refresh')=='1')))
        if len(parts)==4 and parts[:3]==['api','reference','comfy'] and method=='POST':
            act=parts[3]
            if act=='start': db.refengine.comfy.start()
            elif act=='stop': db.refengine.comfy.stop()
            elif act=='free': db.refengine.comfy.free(True)
            else: raise ValueError('Unbekannte Aktion')
            return self.send_bytes(json_bytes(db.refengine.comfy.status()))
        if parts==['api','trash'] and method=='GET': return self.send_bytes(json_bytes(game_trash.trash_list(db)))
        if len(parts)==4 and parts[:2]==['api','trash'] and parts[3]=='restore' and method=='POST':
            return self.send_bytes(json_bytes(game_trash.restore_game(db,parts[2])))
        if len(parts)==3 and parts[:2]==['api','trash'] and method=='DELETE':
            return self.send_bytes(json_bytes(game_trash.purge(db,parts[2],query.get('confirm',''))))
        if parts==['api','games']:
            if method=='GET': return self.send_bytes(json_bytes(db.games()))
            if method=='POST': return self.send_bytes(json_bytes(db.add_game(self.payload())))
        if len(parts)>=3 and parts[:2]==['api','games']:
            gid=parts[2]
            if len(parts)==3:
                if method=='GET':
                    g=db.game(gid)
                    if not g: raise ValueError('Unbekanntes Spiel')
                    return self.send_bytes(json_bytes({'game':g,'dlcs':db.dlcs(gid),'refs':db.refs(gid),'archives':db.archives(gid),'snapshots':db.snapshots(gid),'check':db.completeness(gid),'files':db.files(gid),'tasks':db.tasks(gid),'next_steps':studio_v2.next_steps(db,gid)}))
                if method=='PUT': return self.send_bytes(json_bytes(db.update_game(gid,self.payload())))
                if method=='DELETE': return self.send_bytes(json_bytes(game_trash.delete_game(db,gid,query.get('confirm',''))))
            if len(parts)==5 and parts[3]=='agents' and parts[4]=='export' and method=='GET':
                game=db.game(gid)
                if not game: raise ValueError('Unbekanntes Spiel')
                did=query.get('dlc_id') or None
                dlc=next((d for d in db.dlcs(gid) if d['id']==did),None) if did else None
                if did and not dlc: raise ValueError('DLC nicht gefunden')
                b=agent_studio.package_bytes(game,dlc)
                return self.send_stream(b,'application/zip',
                    'GAMEFORGE_AGENTEN_'+slug(game['title']+('-'+dlc['title'] if dlc else ''))+'.zip')
            if len(parts)==5 and parts[3]=='agents' and parts[4]=='install' and method=='POST':
                game=db.game(gid)
                if not game: raise ValueError('Unbekanntes Spiel')
                data=self.payload()
                did=data.get('dlc_id') or None
                dlc=next((d for d in db.dlcs(gid) if d['id']==did),None) if did else None
                if did and not dlc: raise ValueError('DLC nicht gefunden')
                settings=db.direct.settings(gid)
                if not settings.get('workspace'):
                    raise ValueError('Erst einen lokalen Projektordner im Direkt-Studio verbinden.')
                result=agent_studio.install(game,settings['workspace'],dlc)
                return self.send_bytes(json_bytes(result))
            if len(parts)==5 and parts[3]=='live' and parts[4]=='install' and method=='POST':
                cfg=db.direct.settings(gid)
                if not cfg['workspace']: raise ValueError('Zuerst einen Projektordner im Direkt-Studio verbinden.')
                return self.send_bytes(json_bytes(agent_live.install(cfg['workspace'])))
            if len(parts)==4 and parts[3]=='live' and method=='GET':
                cfg=db.direct.settings(gid)
                payload=agent_live.status(cfg.get('workspace'),agent_studio.roster())
                payload['jobs']=db.direct.jobs(gid)
                return self.send_bytes(json_bytes(payload))
            if len(parts)>=4 and parts[3]=='reference':
                eng=db.refengine
                if len(parts)==4 and method=='GET':
                    prof=eng.profile(gid)
                    from reference_engine import models as ref_models
                    return self.send_bytes(json_bytes({'profile':prof,'styles':{k:{'label':v['label'],'quality_auto':v['quality_auto']} for k,v in art_direction.STYLES.items()},
                        'qualities':ref_quality.PROFILES,'route':ref_models.route(eng.comfy.root,prof['profile']['style_id'],verified=ref_models.verified_set(db)),
                        'jobs':eng.jobs(gid),'images':eng.images(gid),'status':eng.status(gid)}))
                if len(parts)==5 and parts[4]=='profile' and method=='PUT':
                    return self.send_bytes(json_bytes(art_direction.update_profile(db,gid,self.payload())))
                if len(parts)==5 and parts[4]=='jobs' and method=='POST':
                    return self.send_bytes(json_bytes(eng.create(gid,self.payload())))
                if len(parts)==7 and parts[4]=='jobs' and method=='POST':
                    j=eng.job(parts[5])
                    if j['game_id']!=gid: raise ValueError('Auftrag gehört nicht zu diesem Spiel')
                    return self.send_bytes(json_bytes(eng.cancel(parts[5]) if parts[6]=='cancel' else eng.retry(parts[5])))
                if len(parts)==6 and parts[4]=='images' and method=='GET':
                    return self.send_bytes(eng.image_path(gid,parts[5]).read_bytes(),'image/png')
                if len(parts)==7 and parts[4]=='images' and parts[6]=='review' and method=='POST':
                    return self.send_bytes(json_bytes(eng.review(gid,parts[5],self.payload().get('action',''))))
            if len(parts)==4 and parts[3]=='scan' and method=='GET':
                return self.send_bytes(json_bytes(studio_v2.project_scan(db,gid)))
            if len(parts)==4 and parts[3]=='pipeline' and method=='GET':
                return self.send_bytes(json_bytes(studio_v2.pipeline_assets(db,gid)))
            if len(parts)==5 and parts[3]=='pipeline' and parts[4]=='blender-test' and method=='POST':
                return self.send_bytes(json_bytes(studio_v2.start_blender_test(db,gid)))
            if len(parts)==6 and parts[3]=='pipeline' and parts[5]=='approve' and method=='POST':
                return self.send_bytes(json_bytes(studio_v2.approve_asset(db,gid,parts[4])))
            if len(parts)==7 and parts[3]=='direct' and parts[4]=='jobs' and parts[6]=='retry' and method=='POST':
                return self.send_bytes(json_bytes(db.direct.retry(gid,parts[5])))
            if len(parts)==5 and parts[3]=='pipeline' and parts[4]=='prepare' and method=='POST':
                return self.send_bytes(json_bytes(asset_pipeline.prepare(db,gid,self.payload())))
            if len(parts)==5 and parts[3]=='pipeline' and parts[4]=='start' and method=='POST':
                data=self.payload(); assetid=str(data.get('asset_id',''))
                if not re.fullmatch(r'[a-f0-9]{12}',assetid):raise ValueError('Ungültige Asset-ID')
                cfg=db.direct.settings(gid)
                if not cfg.get('workspace'):raise ValueError('Projektordner fehlt')
                root=Path(cfg['workspace']).resolve()
                jobdir=root/'.gameforge'/'asset_pipeline'/assetid
                specfile=jobdir/'asset_spec.json'
                if not specfile.is_file():raise ValueError('Asset-Auftrag fehlt')
                spec=jd(specfile.read_text(encoding='utf-8'))
                if spec.get('game_id')!=gid or spec.get('asset_id')!=assetid:raise ValueError('Projektzuordnung ungültig')
                text=('Nutze Studio Director und delegiere nacheinander an Blender 3D, Animation/Rigging, Materialien, Unreal-Programmierung und Quality/Testing. '
                      'Arbeite ausschließlich an diesem Asset-Auftrag: .gameforge/asset_pipeline/'+assetid+'/asset_spec.json. '
                      'Lies die dortigen BLENDER_TASK.md und UNREAL_TASK.md sowie die tatsächlich vorhandenen freigegebenen Bildreferenzen. '
                      'Prüfe Blender- und Unreal-MCP vor der ersten Änderung. '
                      'Erzeuge in Blender ein echtes 3D-Asset, speichere die .blend-Datei, exportiere die FBX und importiere sie erst nach echtem Export in Unreal. '
                      'Prüfe und dokumentiere jeden Schritt; bei fehlender Verbindung oder fehlerhaftem Rig ausdrücklich anhalten. '
                      'Ersetze niemals bestehende Assets; schütze Story und Quelldaten. Stelle Status und Testevidenz bereit. '
                      'Importiere in Unreal nach /Game/GAMEFORGE/'+assetid+' (Dateien unter Content/GAMEFORGE/'+assetid+'). '
                      'Der Quality-Agent schreibt am Ende .gameforge/asset_pipeline/'+assetid+'/QA_REPORT.md mit echten Prüfergebnissen, Screenshots/Logs und offenen Fehlern.')
                return self.send_bytes(json_bytes(db.direct.start(gid,{'kind':'implement','instruction':text,'allow_mcp':bool(data.get('allow_mcp',True)),'max_turns':40})))
            if len(parts)==4 and parts[3]=='direct':
                if method=='GET': return self.send_bytes(json_bytes({'health':db.direct.check(gid),'jobs':db.direct.jobs(gid),'unreal_installs':studio_v2.find_unreal(),'blender_path':studio_v2.find_blender()}))
                if method=='POST': return self.send_bytes(json_bytes(db.direct.configure(gid,self.payload())))
            if len(parts)==5 and parts[3]=='direct' and parts[4]=='workspace' and method=='POST':
                return self.send_bytes(json_bytes(db.direct.create_workspace(gid)))
            if len(parts)==5 and parts[3]=='direct' and parts[4]=='archive' and method=='POST':
                return self.send_bytes(json_bytes(db.direct.archive_workspace(gid)))
            if len(parts)==5 and parts[3]=='direct' and parts[4]=='extract' and method=='POST':
                return self.send_bytes(json_bytes(db.direct.extract_archive(gid,self.payload().get('archive_id',''))))
            if len(parts)==5 and parts[3]=='direct' and parts[4]=='start' and method=='POST':
                return self.send_bytes(json_bytes(db.direct.start(gid,self.payload())))
            if len(parts)==6 and parts[3]=='direct' and parts[4]=='jobs' and method=='GET':
                return self.send_bytes(json_bytes(db.direct.job(gid,parts[5])))
            if len(parts)==4 and parts[3]=='ideas':
                if method=='GET': return self.send_bytes(json_bytes(db.idea_feed(gid,query.get('dlc_id') or None)))
                if method=='POST': return self.send_bytes(json_bytes(db.brainstorm(gid,self.payload())))
            if len(parts)==4 and parts[3]=='changes' and method=='POST':
                data=self.payload();return self.send_bytes(json_bytes({'id':db.propose_change(gid,
                    dlc_id=data.get('dlc_id') or None,section=data.get('section',''),
                    summary=data.get('summary',''),mode=data.get('mode','append'),
                    new_text=data.get('new_text',''),old_text=data.get('old_text',''))}))
            if len(parts)==6 and parts[3]=='changes' and parts[5]=='decision' and method=='POST':
                return self.send_bytes(json_bytes(db.change_decision(gid,parts[4],self.payload().get('action',''))))
            if len(parts)==6 and parts[3]=='ideas' and parts[5]=='decision' and method=='POST':
                return self.send_bytes(json_bytes(db.decide_idea(gid,parts[4],self.payload().get('action',''))))
            if len(parts)==4 and parts[3]=='dlcs':
                if method=='POST': return self.send_bytes(json_bytes({'id':db.add_dlc(gid,self.payload())}))
            if len(parts)==5 and parts[3]=='dlcs' and method=='PUT':
                return self.send_bytes(json_bytes(db.update_dlc(gid,parts[4],self.payload())))
            if len(parts)==5 and parts[3]=='refs' and parts[4]=='bundle' and method=='POST':
                return self.send_bytes(json_bytes({'ids':db.add_ref_bundle(gid,self.payload())}))
            if len(parts)==4 and parts[3]=='refs' and method=='POST':
                return self.send_bytes(json_bytes({'id':db.add_ref(gid,self.payload())}))
            if len(parts)==6 and parts[3]=='refs' and parts[5]=='prompt' and method=='GET':
                return self.send_bytes(json_bytes({'prompt':db.prompt(gid,parts[4])}))
            if len(parts)==6 and parts[3]=='refs' and parts[5]=='approve' and method=='PUT':
                db.set_ref_approved(gid,parts[4],self.payload().get('approved',True))
                return self.send_bytes(json_bytes({'ok':True}))
            if len(parts)==6 and parts[3]=='refs' and parts[5]=='image' and method=='GET':
                r=db.one('SELECT image_path,image_name FROM ref_tasks WHERE game_id=? AND id=?',(gid,parts[4]))
                if not r or not r['image_path']: raise ValueError('Bild fehlt')
                f=db.base/'refs'/r['image_path']
                if not f.is_file(): raise ValueError('Referenzdatei fehlt')
                mime={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}.get(f.suffix.lower(),'application/octet-stream')
                return self.send_bytes(f.read_bytes(),mime)
            if len(parts)==6 and parts[3]=='snapshots' and parts[5]=='restore' and method=='POST':
                return self.send_bytes(json_bytes(db.restore_snapshot(gid,parts[4])))
            if len(parts)==4 and parts[3]=='snapshots' and method=='POST':
                data=self.payload()
                return self.send_bytes(json_bytes({'id':db.snapshot(gid,str(data.get('version','')),str(data.get('notes','')))}))
            if len(parts)==4 and parts[3]=='files' and method=='POST':
                length=int(self.headers.get('Content-Length','-1'))
                if length<0: raise ValueError('Dateilänge fehlt')
                result=db.save_game_file(self.rfile,length,game_id=gid,filename=query.get('filename',''),
                     relpath=query.get('relpath') or query.get('filename',''),dlc_id=query.get('dlc_id') or None)
                return self.send_bytes(json_bytes(result))
            if len(parts)==5 and parts[3]=='files' and parts[4]=='list' and method=='GET':
                return self.send_bytes(json_bytes(db.files(gid)))
            if len(parts)==6 and parts[3]=='files' and parts[5]=='zip-index' and method=='GET':
                return self.send_bytes(json_bytes(db.zip_index(gid,parts[4])))
            if len(parts)==4 and parts[3]=='tasks' and method=='GET':
                return self.send_bytes(json_bytes(db.tasks(gid,query.get('dlc_id') or None)))
            if len(parts)==5 and parts[3]=='tasks' and method=='PUT':
                return self.send_bytes(json_bytes(db.update_task(gid,parts[4],self.payload())))
            if len(parts)==4 and parts[3]=='export' and method=='GET':
                content,fn=db.zip_package(gid,dlc_id=query.get('dlc_id') or None,include_source=query.get('include_source')=='1')
                return self.send_stream(content,'application/zip',fn)
            if len(parts)==4 and parts[3]=='upload' and method=='POST':
                length=int(self.headers.get('Content-Length','0'))
                if length<1: raise ValueError('Leere Datei')
                aid=query.get('dlc_id') or None
                rid=query.get('reference_id') or None
                kind=query.get('kind','Andere')
                if kind not in KINDS: raise ValueError('Archivtyp ungültig')
                obj=db.save_upload(self.rfile,length,filename=query.get('filename',''),kind=kind,game_id=gid,
                    dlc_id=aid,reference_id=rid,label=query.get('label',''),version=query.get('version',''))
                return self.send_bytes(json_bytes(obj))
        if len(parts)==3 and parts[:2]==['api','archive'] and method=='GET':
            row=db.one('SELECT * FROM archives WHERE id=?',(parts[2],))
            if not row: raise ValueError('Archiv nicht gefunden')
            file=db.base/'uploads'/row['file_path']
            if not file.is_file(): raise ValueError('Archivdatei fehlt')
            # Archivstream ohne vollständiges Laden in den Arbeitsspeicher
            self.send_response(200)
            self.send_header('Content-Type','application/zip')
            self.send_header('Content-Length',str(file.stat().st_size))
            self.send_header('Content-Disposition',f'attachment; filename="{clean_filename(row["original_name"])}"')
            self.end_headers()
            with open(file,'rb') as f:
                shutil.copyfileobj(f,self.wfile,1024*1024)
            return
        if len(parts)==3 and parts[:2]==['api','file'] and method=='GET':
            row=db.one('SELECT * FROM imported_files WHERE id=?',(parts[2],))
            if not row: raise ValueError('Datei nicht gefunden')
            file=db.base/'imports'/row['stored_name']
            if not file.is_file(): raise ValueError('Originaldatei fehlt')
            self.send_response(200)
            self.send_header('Content-Type','application/octet-stream')
            self.send_header('Content-Length',str(file.stat().st_size))
            self.send_header('Content-Disposition',f'attachment; filename="{clean_filename(row["original_name"])}"')
            self.end_headers()
            with open(file,'rb') as f: shutil.copyfileobj(f,self.wfile,1024*1024)
            return
        if parts==['api','backup'] and method=='GET':
            b=db.create_backup()
            return self.send_stream(b,'application/zip','GAMEFORGE_BIBLIOTHEK_BACKUP.zip')
        return self.err('Pfad nicht gefunden',404)

    def do_GET(self):
        try: self.route('GET')
        except (ValueError,KeyError,sqlite3.Error,OSError,zipfile.BadZipFile) as exc: self.err(str(exc))
    def do_POST(self):
        try: self.route('POST')
        except (ValueError,KeyError,sqlite3.Error,OSError,zipfile.BadZipFile,UnicodeDecodeError) as exc: self.err(str(exc))
    def do_DELETE(self):
        try: self.route('DELETE')
        except (ValueError,KeyError,sqlite3.Error,OSError,zipfile.BadZipFile) as exc: self.err(str(exc))
    def do_PUT(self):
        try: self.route('PUT')
        except (ValueError,KeyError,sqlite3.Error,OSError,zipfile.BadZipFile,UnicodeDecodeError) as exc: self.err(str(exc))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data-dir',type=Path,default=ROOT/'GAMEFORGE_DATA')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    store=Store(args.data_dir)
    try:
        server=Server(('127.0.0.1',args.port),store)
    except OSError:
        server=Server(('127.0.0.1',0),store)
    port=server.server_address[1]
    url=f'http://127.0.0.1:{port}/'
    print(f'\nGAMEFORGE GODMODE {VERSION} – KI-Spielestudio')
    print(f'Spielbibliothek: {url}')
    print(f'Datenverzeichnis: {store.base}')
    print('Zum Beenden Strg+C. Die Daten bleiben gespeichert.\n')
    if not args.no_browser:
        threading.Timer(0.7,lambda: webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        server.server_close()
        store.conn.close()


if __name__=='__main__':
    main()
