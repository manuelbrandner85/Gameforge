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

    def upload_image(self, path, name=None):
        """Legt ein Bild in ComfyUIs input/-Ordner (über die lokale Schnittstelle) und gibt den Namen zurück."""
        path = Path(path)
        name = name or path.name
        boundary = uuid.uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
                f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}"\r\n'
                f'Content-Type: image/png\r\n\r\n').encode('utf-8') + path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode('utf-8')
        req = urllib.request.Request(f'http://{HOST}:{PORT}/upload/image', data=body,
                                     headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())['name']


# Bild → 3D-Modell: TRELLIS.2 (Microsoft, MIT) nativ in ComfyUI. Modelle von Comfy-Org (MIT); der Bild-Encoder
# DINOv3 steht unter Metas DINOv3-Lizenz (kommerziell erlaubt, Einschränkungen u. a. für Militär/ITAR).
TRELLIS2_MODELS = [
    ('diffusion_models/trellis_2_int8_convrot.safetensors', 'Comfy-Org/TRELLIS.2', 'd01952ad137213f6a868f86b6b877026276f84af5eec23069217475a0bad3a31'),
    ('clip_vision/dino_v3_vit_l.safetensors', 'Comfy-Org/TRELLIS.2', '5cb785e458de7c460579082418af81f5c62380c181599344bdc60898c63468ee'),
    ('vae/trellis_2_shape_vae_bf16.safetensors', 'Comfy-Org/TRELLIS.2', 'de0cb4949a76c59ee5c091a995a69bcc8c51d5aeda939f0c641a50d2a72341f4'),
    ('vae/trellis_2_texture_vae_bf16.safetensors', 'Comfy-Org/TRELLIS.2', '714e5ebf094a610e12a8e3b5175c18a62f37f6ea4218acb6073644456b73ab0e'),
    ('background_removal/birefnet.safetensors', 'Comfy-Org/BiRefNet', '9ab37426bf4de0567af6b5d21b16151357149139362e6e8992021b8ce356a154'),
]


def trellis2_missing(root):
    return [rel for rel, _, _ in TRELLIS2_MODELS if not (Path(root) / 'ComfyUI' / 'models' / rel).is_file()]


def trellis2_i2m(image, seed=42, resolution=1536, texture=4096, faces=700000, prefix='gameforge3d/asset', remove_bg=True):
    """API-Workflow Bild → texturiertes 3D-Modell (GLB mit Basisfarbe, Metallic, Rauheit, Normal, AO).
    Nachbau des TRELLIS.2-Zweigs der offiziellen ComfyUI-Vorlage „Pixal3D & TRELLIS.2: Image to Model“
    (gleiche Stufen, Sampler und Backing-Werte), ohne Pixal3D/MoGe."""
    mask = ['192', 0] if remove_bg else ['122', 1]
    ks = lambda model, cond, latent, s, steps, cfg, sched: {'class_type': 'KSampler', 'inputs': {
        'model': model, 'positive': [cond, 0], 'negative': [cond, 1], 'latent_image': latent, 'seed': s, 'steps': steps,
        'cfg': cfg, 'sampler_name': 'euler', 'scheduler': sched, 'denoise': 1.0}}
    wf = {
        '122': {'class_type': 'LoadImage', 'inputs': {'image': image}},
        '193': {'class_type': 'LoadBackgroundRemovalModel', 'inputs': {'bg_removal_name': 'birefnet.safetensors'}},
        '192': {'class_type': 'RemoveBackground', 'inputs': {'bg_removal_model': ['193', 0], 'image': ['122', 0]}},
        '312': {'class_type': 'ImageCropToMask', 'inputs': {'images': ['122', 0], 'masks': mask, 'width': 1024, 'height': 1024,
                                                             'pad_factor': 1.1, 'grow_mask': 0, 'background': '#000000'}},
        '15': {'class_type': 'CLIPVisionLoader', 'inputs': {'clip_name': 'dino_v3_vit_l.safetensors'}},
        '299': {'class_type': 'Trellis2Conditioning', 'inputs': {'clip_vision_model': ['15', 0], 'image': ['312', 0]}},
        '40': {'class_type': 'UNETLoader', 'inputs': {'unet_name': 'trellis_2_int8_convrot.safetensors', 'weight_dtype': 'default'}},
        '199': {'class_type': 'CFGOverride', 'inputs': {'model': ['40', 0], 'cfg': 1.0, 'start_percent': 0.667, 'end_percent': 1.0}},
        '125': {'class_type': 'RescaleCFG', 'inputs': {'model': ['199', 0], 'multiplier': 0.7}},
        '108': {'class_type': 'ModelSamplingSD3', 'inputs': {'model': ['125', 0], 'shift': 5.0}},
        '279': {'class_type': 'CFGOverride', 'inputs': {'model': ['40', 0], 'cfg': 1.0, 'start_percent': 0.769, 'end_percent': 1.0}},
        '126': {'class_type': 'RescaleCFG', 'inputs': {'model': ['279', 0], 'multiplier': 0.5}},
        '87': {'class_type': 'EmptyTrellis2LatentStructure', 'inputs': {'batch_size': 1}},
        '3': ks(['108', 0], '299', ['87', 0], seed + 14, 12, 7.5, 'normal'),
        '117': {'class_type': 'VAELoader', 'inputs': {'vae_name': 'trellis_2_shape_vae_bf16.safetensors'}},
        '118': {'class_type': 'VAELoader', 'inputs': {'vae_name': 'trellis_2_texture_vae_bf16.safetensors'}},
        '119': {'class_type': 'VaeDecodeStructureTrellis2', 'inputs': {'samples': ['3', 0], 'vae': ['117', 0], 'resolution': '32'}},
        '91': {'class_type': 'Trellis2ShapeStage', 'inputs': {'positive': ['299', 0], 'negative': ['299', 1], 'voxel': ['119', 0]}},
        '18': ks(['126', 0], '91', ['91', 2], seed, 20, 7.5, 'normal'),
        '94': {'class_type': 'Trellis2UpsampleStage', 'inputs': {'positive': ['91', 0], 'negative': ['91', 1], 'shape_latent': ['18', 0],
                                                                 'vae': ['117', 0], 'target_resolution': int(resolution)}},
        '23': ks(['126', 0], '94', ['94', 2], seed, 12, 7.5, 'simple'),
        '92': {'class_type': 'VaeDecodeShapeTrellis', 'inputs': {'samples': ['23', 0], 'vae': ['117', 0]}},
        '98': {'class_type': 'Trellis2TextureStage', 'inputs': {'positive': ['94', 0], 'negative': ['94', 1], 'shape_latent': ['23', 0]}},
        '12': ks(['40', 0], '98', ['98', 2], seed + 1, 12, 1.0, 'normal'),
        '93': {'class_type': 'VaeDecodeTextureTrellis', 'inputs': {'samples': ['12', 0], 'vae': ['118', 0], 'shape_subdivides': ['92', 1]}},
        '202': {'class_type': 'GetMeshInfo', 'inputs': {'mesh': ['92', 0]}},
        '241': {'class_type': 'RemeshMesh', 'inputs': {'mesh': ['202', 0], 'resolution': 768, 'sign_mode': 'udf', 'band': 1.0,
                                                       'project_back': 0.0, 'fix_poles': False, 'smooth_iters': 20,
                                                       'drop_small_components': 0.01, 'precluster_max_verts': 20000000}},
        '186': {'class_type': 'DecimateMesh', 'inputs': {'mesh': ['241', 0], 'target_face_count': int(faces), 'placement_mode': 'midpoint'}},
        '238': {'class_type': 'MeshSmoothNormals', 'inputs': {'mesh': ['186', 0], 'crease_angle': 180.0}},
        '196': {'class_type': 'UnwrapMesh', 'inputs': {'mesh': ['238', 0], 'segmenter': 'pec', 'resolution': int(texture), 'padding': 1,
                                                       'weld_distance': 0.0002}},
        '147': {'class_type': 'BakeTextureFromVoxel', 'inputs': {'mesh': ['196', 0], 'voxel_colors': ['93', 0], 'reference_mesh': ['92', 0],
                                                                 'texture_size': int(texture)}},
        '224': {'class_type': 'BakeNormalMapFromMesh', 'inputs': {'low_poly': ['196', 0], 'high_poly': ['241', 0], 'resolution': 2048,
                                                                  'cage_distance': 0.05, 'ignore_backfaces': True}},
        '233': {'class_type': 'BakeAmbientOcclusion', 'inputs': {'low_poly': ['196', 0], 'high_poly': ['241', 0], 'resolution': 1024,
                                                                 'samples': 64, 'max_distance': 0.71, 'strength': 1.0, 'bias': 0.01}},
        '210': {'class_type': 'ApplyTextureToMesh', 'inputs': {'mesh': ['196', 0], 'base_color': ['147', 0], 'metallic': ['147', 1],
                                                               'roughness': ['147', 2], 'occlusion': ['233', 0], 'normal_map': ['224', 0]}},
        '260': {'class_type': 'MeshSmoothNormals', 'inputs': {'mesh': ['210', 0], 'crease_angle': 180.0}},
        '400': {'class_type': 'SaveGLB', 'inputs': {'mesh': ['260', 0], 'filename_prefix': prefix}},
    }
    return wf


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
