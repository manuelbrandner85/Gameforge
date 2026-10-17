"""Lokale ComfyUI-Anbindung. Startet ComfyUI nur auf 127.0.0.1 (keine Netzwerkfreigabe)."""
from __future__ import annotations
import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

PORT = 8188
HOST = '127.0.0.1'


def find_root(app_root):
    """Sucht die portable ComfyUI-Installation im GAMEFORGE-Ordner engines/."""
    base = Path(app_root) / 'engines'
    for cand in sorted(base.glob('ComfyUI_windows_portable*'), reverse=True):
        if (cand / 'ComfyUI' / 'main.py').is_file():
            return cand
    return None


def python_exe(root):
    for p in (root / 'python_embeded' / 'python.exe', root / 'python_embedded' / 'python.exe'):
        if p.is_file():
            return p
    return None


class Comfy:
    def __init__(self, app_root, log_dir):
        self.app_root = Path(app_root)
        self.log_dir = Path(log_dir); self.log_dir.mkdir(parents=True, exist_ok=True)
        self.proc = None
        self.lock = threading.Lock()
        self.client_id = uuid.uuid4().hex
        self._object_info = None

    @property
    def root(self):
        return find_root(self.app_root)

    def _req(self, path, data=None, timeout=10):
        url = f'http://{HOST}:{PORT}{path}'
        body = json.dumps(data).encode('utf-8') if data is not None else None
        req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'} if body else {})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return json.loads(raw) if raw and r.headers.get('Content-Type', '').startswith('application/json') else raw

    def online(self):
        try:
            return self._req('/system_stats', timeout=2)
        except (urllib.error.URLError, OSError, ValueError):
            return None

    def status(self):
        stats = self.online()
        root = self.root
        return {'installed': bool(root), 'root': str(root) if root else None, 'running': bool(stats),
                'started_by_gameforge': bool(self.proc and self.proc.poll() is None),
                'url': f'http://{HOST}:{PORT}', 'system_stats': stats,
                'log': str(self.log_dir / 'comfyui.log')}

    def start(self, wait=180):
        with self.lock:
            if self.online():
                return True
            root = self.root
            if not root:
                raise RuntimeError('ComfyUI ist nicht installiert (erwartet unter engines/ComfyUI_windows_portable).')
            py = python_exe(root)
            if not py:
                raise RuntimeError('Das eingebettete Python von ComfyUI fehlt.')
            log = open(self.log_dir / 'comfyui.log', 'ab')
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            self.proc = subprocess.Popen([str(py), '-s', str(root / 'ComfyUI' / 'main.py'), '--listen', HOST, '--port', str(PORT),
                                          '--disable-auto-launch', '--windows-standalone-build'],
                                         cwd=str(root), stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, creationflags=flags)
            t0 = time.time()
            while time.time() - t0 < wait:
                if self.proc.poll() is not None:
                    raise RuntimeError('ComfyUI wurde beim Start beendet. Details im Protokoll: ' + str(self.log_dir / 'comfyui.log'))
                if self.online():
                    self._object_info = None
                    return True
                time.sleep(1.5)
            raise RuntimeError('ComfyUI antwortet nach dem Start nicht (Zeitlimit).')

    def stop(self):
        with self.lock:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
                try:
                    self.proc.wait(20)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                return True
            return False

    def object_info(self):
        if self._object_info is None:
            self._object_info = self._req('/object_info', timeout=30)
        return self._object_info

    def missing_nodes(self, workflow):
        info = self.object_info()
        return sorted({n['class_type'] for n in workflow.values() if n['class_type'] not in info})

    def queue(self, workflow):
        res = self._req('/prompt', {'prompt': workflow, 'client_id': self.client_id}, timeout=30)
        if res.get('node_errors'):
            raise RuntimeError('ComfyUI lehnt den Workflow ab: ' + json.dumps(res['node_errors'])[:800])
        return res['prompt_id']

    def history(self, prompt_id):
        h = self._req('/history/' + urllib.parse.quote(prompt_id), timeout=10)
        return h.get(prompt_id) if isinstance(h, dict) else None

    def queue_state(self):
        return self._req('/queue', timeout=5)

    def interrupt(self):
        try:
            self._req('/interrupt', {}, timeout=5)
            return True
        except (urllib.error.URLError, OSError):
            return False

    def free(self, unload=True):
        try:
            self._req('/free', {'unload_models': unload, 'free_memory': True}, timeout=10)
            return True
        except (urllib.error.URLError, OSError):
            return False

    def fetch_image(self, filename, subfolder, typ):
        q = urllib.parse.urlencode({'filename': filename, 'subfolder': subfolder, 'type': typ})
        return self._req('/view?' + q, timeout=60)


def klein_t2i(prompt, seed, width, height, steps=4, cfg=1.0, prefix='gameforge', pixel=None):
    """API-Workflow: FLUX.2 klein Text→Bild. Optional deterministische Pixel-Art-Nachbearbeitung."""
    wf = {
        '1': {'class_type': 'UNETLoader', 'inputs': {'unet_name': 'flux-2-klein-4b.safetensors', 'weight_dtype': 'default'}},
        '2': {'class_type': 'CLIPLoader', 'inputs': {'clip_name': 'qwen_3_4b.safetensors', 'type': 'flux2', 'device': 'default'}},
        '3': {'class_type': 'VAELoader', 'inputs': {'vae_name': 'flux2-vae.safetensors'}},
        '4': {'class_type': 'CLIPTextEncode', 'inputs': {'text': prompt, 'clip': ['2', 0]}},
        '5': {'class_type': 'EmptyFlux2LatentImage', 'inputs': {'width': width, 'height': height, 'batch_size': 1}},
        '6': {'class_type': 'Flux2Scheduler', 'inputs': {'steps': steps, 'width': width, 'height': height}},
        '7': {'class_type': 'RandomNoise', 'inputs': {'noise_seed': seed}},
        '8': {'class_type': 'KSamplerSelect', 'inputs': {'sampler_name': 'euler'}},
        '9': {'class_type': 'CFGGuider', 'inputs': {'model': ['1', 0], 'positive': ['4', 0], 'negative': ['10', 0], 'cfg': cfg}},
        '10': {'class_type': 'ConditioningZeroOut', 'inputs': {'conditioning': ['4', 0]}},
        '11': {'class_type': 'SamplerCustomAdvanced', 'inputs': {'noise': ['7', 0], 'guider': ['9', 0], 'sampler': ['8', 0],
                                                                 'sigmas': ['6', 0], 'latent_image': ['5', 0]}},
        '12': {'class_type': 'VAEDecode', 'inputs': {'samples': ['11', 0], 'vae': ['3', 0]}},
    }
    last = ['12', 0]
    if pixel:
        g = int(pixel.get('pixel_grid', 8)); colors = int(pixel.get('colors', 24))
        wf['20'] = {'class_type': 'ImageScale', 'inputs': {'image': last, 'upscale_method': 'area', 'width': width // g, 'height': height // g, 'crop': 'disabled'}}
        wf['21'] = {'class_type': 'ImageQuantize', 'inputs': {'image': ['20', 0], 'colors': colors, 'dither': 'none'}}
        wf['22'] = {'class_type': 'ImageScale', 'inputs': {'image': ['21', 0], 'upscale_method': 'nearest-exact', 'width': (width // g) * g, 'height': (height // g) * g, 'crop': 'disabled'}}
        last = ['22', 0]
    wf['30'] = {'class_type': 'SaveImage', 'inputs': {'images': last, 'filename_prefix': prefix}}
    return wf
