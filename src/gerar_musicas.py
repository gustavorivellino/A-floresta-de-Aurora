"""
Gera as 5 trilhas do jogo (loops em .wav) na pasta assets/.
Músicas originais, sintetizadas por código: sem direitos autorais.
Uso: python gerar_musicas.py   (precisa de numpy: pip install numpy)
"""
import os
import wave
import numpy as np

SR = 22050
PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(PASTA, exist_ok=True)


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def envelope(n, ataque, decaimento, solta):
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / max(ataque, 1e-4)) * np.exp(-t * decaimento)
    ns = int(solta * SR)
    if 0 < ns < n:
        env[-ns:] *= np.linspace(1, 0, ns)
    return env


def instrumento(tipo, m, dur):
    """Retorna o som de uma nota (dur em segundos)."""
    f = freq(m)
    if tipo == "sino":
        n = int((dur + 1.2) * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) \
            + 0.2 * np.sin(2 * np.pi * 3 * f * t)
        return s * envelope(n, 0.005, 3.0, 0.2) * 0.5
    if tipo == "flauta":
        n = int((dur + 0.1) * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) \
            + 0.1 * np.sin(2 * np.pi * 3 * f * t)
        return s * envelope(n, 0.04, 0.3, 0.12) * 0.5
    if tipo == "metal":  # som mais brilhante, para o final
        n = int((dur + 0.1) * SR)
        t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 6))
        return s * envelope(n, 0.03, 0.4, 0.1) * 0.35
    if tipo == "baixo":
        n = int((dur + 0.1) * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t)
        return s * envelope(n, 0.01, 1.2, 0.1) * 0.7
    # pad: som longo e suave
    n = int((dur + 0.5) * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.004 * t)
    return s * envelope(n, 0.4, 0.0, 0.6) * 0.25


def renderizar(nome, bpm, compassos, eventos, eco=0.0):
    """eventos: lista de (inicio_em_tempos, midi, duracao_em_tempos, instrumento)."""
    seg_por_tempo = 60.0 / bpm
    total = int(compassos * 4 * seg_por_tempo * SR)
    buf = np.zeros(total)
    for ini, midi, dur, inst in eventos:
        som = instrumento(inst, midi, dur * seg_por_tempo)
        pos = int(ini * seg_por_tempo * SR)
        idx = (pos + np.arange(len(som))) % total  # dá a volta: loop sem corte
        buf[idx] += som
    if eco:
        buf += eco * np.roll(buf, int(0.5 * SR))
    buf = buf / np.max(np.abs(buf)) * 0.8
    dados = (buf * 32767).astype(np.int16)
    with wave.open(os.path.join(PASTA, nome + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(dados.tobytes())
    print(f"{nome}.wav  ({len(buf) / SR:.0f}s)")


def melodia(lista, inicio=0.0, inst="flauta"):
    ev, t = [], inicio
    for midi, dur in lista:
        ev.append((t, midi, dur, inst))
        t += dur
    return ev


# ---- MENU: arpejos calmos (C - Am - F - G) -------------------------------
acordes = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]]
ev = []
for c in range(8):
    ac = acordes[c % 4]
    for i, k in enumerate([0, 1, 2, 3, 2, 1, 2, 1]):
        ev.append((c * 4 + i * 0.5, ac[k], 0.5, "sino"))
    ev.append((c * 4, ac[0] - 12, 4, "pad"))
renderizar("menu", 80, 8, ev, eco=0.25)

# ---- VILA: alegre, escala pentatônica -------------------------------------
mel = melodia([
    (64, 1), (67, 1), (69, 1), (67, 1),
    (67, 1), (64, .5), (62, .5), (64, 2),
    (69, 1), (72, 1), (69, 1), (67, 1),
    (69, 1), (67, 1), (64, 2),
    (64, 1), (67, 1), (72, 1), (69, 1),
    (67, 1), (69, .5), (67, .5), (64, 2),
    (69, 1), (67, 1), (64, 1), (62, 1),
    (60, 4),
])
raizes = [48, 43, 45, 41, 48, 43, 41, 48]
for c, r in enumerate(raizes):
    mel.append((c * 4, r, 2, "baixo"))
    mel.append((c * 4 + 2, r + 7, 2, "baixo"))
renderizar("vila", 110, 8, mel)

# ---- FLORESTA: misteriosa, lá menor ---------------------------------------
acordes = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 60, 64, 67], [55, 59, 62, 67]]
ev = []
for c in range(8):
    ac = acordes[c % 4]
    for i, k in enumerate([0, 2, 1, 3]):
        ev.append((c * 4 + i, ac[k], 1, "sino"))
    ev.append((c * 4, ac[0] - 24, 4, "pad"))
ev += melodia([(72, 3)], 0, "flauta") + melodia([(71, 3)], 8, "flauta") \
    + melodia([(69, 4)], 16, "flauta") + melodia([(67, 2), (64, 2)], 24, "flauta")
renderizar("floresta", 70, 8, ev, eco=0.3)

# ---- CAVERNA: sombria, drones graves e sinos esparsos ---------------------
ev = []
for c in range(0, 8, 2):
    ev.append((c * 4, 38, 8, "pad"))
    ev.append((c * 4, 45, 8, "pad"))
for ini, m in [(1, 74), (4.5, 81), (7, 77), (10, 79), (13.5, 74), (17, 84),
               (20, 77), (23.5, 81), (26, 79), (29, 74)]:
    ev.append((ini, m, 1, "sino"))
renderizar("caverna", 60, 8, ev, eco=0.45)

# ---- FIM: vitoriosa, dó maior ---------------------------------------------
mel = melodia([
    (67, 1), (72, 1), (76, 2),
    (77, 1), (76, 1), (72, 2),
    (74, 1), (71, 1), (67, 2),
    (72, 4),
    (72, 1), (76, 1), (79, 2),
    (81, 1), (79, 1), (76, 2),
    (77, 1), (74, 1), (71, 1), (67, 1),
    (72, 4),
], 0, "metal")
acordes = [[48, 52, 55], [53, 57, 60], [55, 59, 62], [48, 52, 55]] * 2
for c, ac in enumerate(acordes):
    for m in ac:
        mel.append((c * 4, m + 12, 4, "pad"))
    for b in range(4):
        mel.append((c * 4 + b, ac[0] - 12, 1, "baixo"))
renderizar("fim", 100, 8, mel)

# ---- CHEFE: tenso e rápido, ré menor (usado na luta final) -----------------
acordes = [[50, 53, 57], [46, 50, 53], [48, 52, 55], [45, 49, 52]]
ev = []
padrao = [0, 1, 2, 1, 0, 2, 1, 2]
for c in range(16):
    ac = acordes[c % 4]
    for i, k in enumerate(padrao):
        ev.append((c * 4 + i * 0.5, ac[0] - 12, 0.5, "baixo"))
        ev.append((c * 4 + i * 0.5, ac[k] + 12, 0.5, "metal"))
renderizar("chefe", 140, 16, ev, eco=0.2)
