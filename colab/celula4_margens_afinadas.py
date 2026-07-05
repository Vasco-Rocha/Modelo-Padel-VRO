# === Célula 4 (afinada) — Rallies v9 + cortar tempo útil ===
# Mudança vs versão anterior: margens mais curtas (pre 1.5->0.8, pos 2.5->1.1)
# Motivo: o corte manual real deu 132s; as margens antigas davam 172s (a mais).
# Estas margens devem aterrar perto dos ~132s de ground-truth.

def segmentar(bola, fps, gap_fora_s=2.0, pre=0.8, pos=1.1, minr=1.0):
    n=len(bola); g=int(gap_fora_s*fps); pr=int(pre*fps); po=int(pos*fps); ml=int(minr*fps)
    runs=[]; i=0
    while i<n:
        if not bola[i]: i+=1; continue
        a=i
        while i+1<n and bola[i+1]: i+=1
        runs.append([a,i]); i+=1
    bl=[]
    for r in runs:
        if bl and (r[0]-bl[-1][1]-1)<=g: bl[-1][1]=r[1]
        else: bl.append(r)
    segs=[[max(0,a-pr),min(n-1,b+po)] for a,b in bl if b-a+1>=ml]
    for k in range(len(segs)-1):
        if segs[k][1]>=segs[k+1][0]:
            m=(segs[k][1]+segs[k+1][0])//2; segs[k][1]=m; segs[k+1][0]=m+1
    return segs

segs=segmentar(bola, fps); dur=[(b-a)/fps for a,b in segs]
print(f'{len(segs)} rallies | tempo util {sum(dur):.0f}s/{n/fps:.0f}s ({100*sum(dur)/(n/fps):.0f}%) | media {np.mean(dur):.1f}s' if segs else 'sem rallies')
print(f'ground-truth (corte manual): 132s (45%)  <- comparar com o de cima')

# --- corte do vídeo (igual ao anterior) ---
import subprocess, os
os.makedirs('/content/clips', exist_ok=True); parts=[]
for j,(a,b) in enumerate(segs):
    o=f'/content/clips/r{j:02d}.mp4'
    subprocess.run(['ffmpeg','-y','-ss',f'{a/fps:.2f}','-to',f'{b/fps:.2f}','-i',VIDEO,
                    '-c:v','libx264','-crf','23','-preset','veryfast','-an',o], capture_output=True)
    parts.append(os.path.abspath(o))
open('/content/list.txt','w').write('\n'.join(f"file '{p}'" for p in parts))
OUT='/content/drive/MyDrive/PadelPro_Vision/jogos/parada4_teste/TempoUtil_bola_v2.mp4'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','/content/list.txt','-c','copy',OUT], capture_output=True)
print('condensado na Drive:', os.path.exists(OUT))
