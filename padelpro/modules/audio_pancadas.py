"""Detecao de pancadas por AUDIO (R15 dos prompts v7).

IMPORTANTE (nota do Vasco): o audio pode estar ATRASADO e ter INTERFERENCIA de outros
campos. Por isso e' apenas um sinal de REFERENCIA/corroboracao — nunca decide sozinho o
inicio, fim ou pancada de um rally. Usa-se para reforcar a confianca do sinal visual (bola).

Metodo: transientes tipo raquete/ressalto = picos de energia de alta frequencia.
So' precisa de numpy + um wav mono (extrair com ffmpeg: -ac 1 -ar 16000 -vn).
"""
from __future__ import annotations
import wave
import numpy as np


def detetar_pancadas_audio(
    wav_path: str,
    hop_s: float = 0.01,
    win_s: float = 0.03,
    min_sep_s: float = 0.25,
    k: float = 3.0,
) -> tuple[list[float], float]:
    """Devolve (lista de timestamps em segundos, duracao_audio_s).

    k = agressividade do limiar (media + k*desvio). Subir k => menos candidatos.
    min_sep_s = separacao minima entre picos (evita contar o mesmo impacto varias vezes).
    """
    wf = wave.open(wav_path, "rb")
    sr = wf.getframerate()
    x = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32)
    wf.close()
    if x.size == 0:
        return [], 0.0
    x /= (np.abs(x).max() + 1e-9)
    xh = np.diff(x, prepend=x[:1])                 # enfase de alta frequencia (transientes)
    hop, win = int(hop_s * sr), int(win_s * sr)
    n = max(0, (len(xh) - win) // hop)
    energia = np.array([np.sum(xh[i * hop:i * hop + win] ** 2) for i in range(n)])
    nov = np.diff(energia, prepend=energia[:1])
    nov[nov < 0] = 0                               # so' subidas de energia
    thr = nov.mean() + k * nov.std()
    picos, last = [], -1e9
    for i in np.where(nov > thr)[0]:
        t = i * hop / sr
        if t - last >= min_sep_s:
            picos.append(round(t, 3))
            last = t
    return picos, len(x) / sr


def corrobora(frame_evento: int, audio_hits_frames: set[int], fps: float,
              tol_s: float = 0.5) -> bool:
    """True se houver um pico de audio a < tol_s de um evento visual (frame).
    Tolerancia larga por causa do possivel atraso do audio."""
    tol = int(tol_s * fps)
    return any(abs(frame_evento - a) <= tol for a in audio_hits_frames)
