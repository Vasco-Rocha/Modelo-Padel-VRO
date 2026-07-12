# =============================================================================
#  JOGADORES — CORRIDA FINAL sobre o video TODO   (~15-25 min)
#  Corre DEPOIS da celula 4 (usa VIDEO_PATH e CAMPO).
#
#  Parametros escolhidos pela tabela de afinacao:
#      CONF = 0.10    (apanha os jogadores CORTADOS pela borda)
#      IMGSZ = 1280   (apanha os do FUNDO longe)
#  Deteta GENEROSAMENTE. A limpeza faz-se depois, no repo, com as regras do Vasco.
#
#  No fim: descarrega `players_detections_parada4.json` -> por em dados_parada4/
# =============================================================================
import os, json
import numpy as np, supervision as sv
from tqdm import tqdm
from trackers.players_tracker.players_tracker import PlayerTracker

CONF, IMGSZ = 0.10, 1280

video_info = sv.VideoInfo.from_video_path(VIDEO_PATH)
W, H = video_info.resolution_wh
print(f'video: {W}x{H}, {video_info.fps:.2f} fps, {video_info.total_frames} frames')
print(f'CONF={CONF}  IMGSZ={IMGSZ}  (sem max_det -> deteta toda a gente)\n')

try:
    pz = sv.PolygonZone(CAMPO, frame_resolution_wh=video_info.resolution_wh)
except TypeError:
    pz = sv.PolygonZone(CAMPO)

PlayerTracker.CONF = CONF
PlayerTracker.IMGSZ = IMGSZ
tracker = PlayerTracker('weights/players_detection/yolov8m.pt', pz, batch_size=8)
tracker.video_info_post_init(video_info)

BATCH = 8
todos, lote = [], []
for frame in tqdm(sv.get_video_frames_generator(VIDEO_PATH), total=video_info.total_frames):
    lote.append(frame)
    if len(lote) == BATCH:
        todos.extend(tracker.predict_sample(lote)); lote = []
if lote:
    todos.extend(tracker.predict_sample(lote))

print(f'\nframes processados: {len(todos)}')

# ---- gravar (boxes em PIXEIS + tracker_id) ----
serial = [p.serialize() for p in todos]
OUT = '/content/players_detections_parada4.json'
with open(OUT, 'w') as f:
    json.dump(serial, f)

n = len(serial) or 1
med = sum(len(fr) for fr in serial) / n
print(f'\ndeteccoes por frame (BRUTO, inclui publico): media {med:.1f}')
print('  (nao te assustes com o numero -- e suposto. As regras do Vasco limpam depois:')
print('   fora do campo -> imoveis -> continuidade -> cor -> 2 por lado.)')

from google.colab import files
files.download(OUT)
print('\n>>> Poe o ficheiro em  dados_parada4/  e avisa o Centro de Decisoes.')
