"""
A FLORESTA DE AURORA - jogo de aventura e ação em 2D (pygame).

Controles
  Setas / WASD ... andar            J ... espada          K ... arco
  SHIFT ... desvio (dash)           B ... bomba           Q ... poção
  E / ENTER / ESPAÇO ... falar, abrir baús, usar santuários
  TAB ... missões     M ... mapa    P / ESC ... pausa     F11 ... tela cheia

Arquivos
  main.py     o motor do jogo (este arquivo)
  dados.py    salas, inimigos, missões, conquistas e textos
  sprites.py  toda a arte, desenhada por código (ou PNG em assets/)
"""
import json
import math
import os
import random
import sys
import types

import pygame

from code.dados import (ARENA_ONDAS, ARENA_SPAWNS, CONQUISTAS, DIFICULDADES, FALAS_MORTE, FINAL_LUNA,
                   MISSAO_TEXTOS, MISSOES, NOMES_ITEM, PROLOGO, QUEST_NPC, RECOMPENSAS, SALAS,
                   SECRETAS, TIPOS, VIZINHO)
import code.sprites as ART
from code.sprites import PASTA_ASSETS

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    print("Áudio indisponível: o jogo roda sem som.")

LARGURA, ALTURA = 800, 600
try:  # SCALED: a janela pode ser redimensionada e o F11 liga a tela cheia
    ecra = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED | pygame.RESIZABLE)
except pygame.error:
    ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("A Floresta de Aurora")
tela = pygame.Surface((LARGURA, ALTURA))  # tela virtual (permite tremer a câmera)
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("arial", 24)
fonte_pequena = pygame.font.SysFont("arial", 20)
fonte_mini = pygame.font.SysFont("arial", 17)
fonte_micro = pygame.font.SysFont("arial", 13)
fonte_titulo = pygame.font.SysFont("arial", 44, bold=True)
fonte_grande = pygame.font.SysFont("arial", 56, bold=True)

R = pygame.Rect
G = types.SimpleNamespace()  # todo o estado do jogo mora aqui
G.vol_musica, G.vol_efeitos = 0.5, 0.6
G.conquistas = set()
G.toasts = []
G.tick = 0
G.sel = 0
G.volta = "titulo"
G.estado = "titulo"
G.tem_save = False

CAMINHO_SAVE = os.environ.get("AURORA_SAVE") or os.path.join(os.path.expanduser("~"), ".floresta_de_aurora.json")
VERSAO_SAVE = 5

SPR = ART.carregar_sprites()
ICONES = {t: ART.icone(t) for t in ("chave", "fragmento1", "fragmento2", "cristal", "arco", "anel", "flecha", "bomba")}
ICONE_ESPADA = pygame.transform.rotozoom(SPR["espada"], 0, 0.7)
ESPADA_REPOUSO = {d: pygame.transform.rotozoom(SPR["espada"], g, 0.6)
                  for d, g in {(1, 0): 0, (0, 1): -90, (-1, 0): 180, (0, -1): 90}.items()}
_icone = pygame.Surface((32, 32), pygame.SRCALPHA)
_icone.blit(pygame.transform.rotozoom(SPR["espada"], 45, 0.8), (0, 0))
pygame.display.set_icon(_icone)


# ================================================================ ARQUIVO DE SAVE E PERFIL
def ler_arquivo():
    try:
        with open(CAMINHO_SAVE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def escrever_arquivo(jogo=None):
    """Grava conquistas e configurações (e, se vier, o jogo salvo) no arquivo de save."""
    d = ler_arquivo()
    d["conquistas"] = sorted(G.conquistas)
    d["config"] = {"musica": G.vol_musica, "efeitos": G.vol_efeitos}
    if jogo is not None:
        d["jogo"] = jogo
    try:
        with open(CAMINHO_SAVE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
    except OSError:
        pass
    G.tem_save = "jogo" in d


def carregar_perfil():
    d = ler_arquivo()
    G.conquistas = set(d.get("conquistas", []))
    cfg = d.get("config", {})
    G.vol_musica = float(cfg.get("musica", 0.5))
    G.vol_efeitos = float(cfg.get("efeitos", 0.6))
    G.tem_save = "jogo" in d
    aplicar_volume()


def salvar_jogo(avisar=True):
    escrever_arquivo({
        "versao": VERSAO_SAVE, "sala": G.sala, "x": G.jogador.x, "y": G.jogador.y, "hp": G.hp,
        "hp_max": G.hp_max, "dano": G.dano, "pocoes": G.pocoes, "moedas": G.moedas,
        "flechas": G.flechas, "bombas": G.bombas, "compras": G.compras,
        "conheceu_ferreiro": G.conheceu_ferreiro, "inventario": sorted(G.inventario),
        "coletados": sorted(G.coletados), "abertos": sorted(G.abertos),
        "destruidas": sorted(G.destruidas), "intros": sorted(G.intros),
        "visitadas": sorted(G.visitadas), "missoes": G.missoes, "mortos": sorted(G.mortos),
        "kills": G.kills, "mortes": G.mortes, "frames": G.frames, "dificuldade": G.dificuldade,
        "respawn": list(G.respawn), "arena_melhor": G.arena_melhor})
    if avisar:
        mostrar_aviso("Jogo salvo.")


def carregar_jogo():
    d = ler_arquivo().get("jogo")
    if not d:
        return False
    novo_jogo(d.get("dificuldade", "normal"))
    G.sala = d.get("sala") if d.get("sala") in SALAS else "vila"
    G.jogador.topleft = (d.get("x", 100), d.get("y", 300))
    for chave in ("hp", "hp_max", "dano", "pocoes", "moedas", "flechas", "bombas", "compras",
                  "conheceu_ferreiro", "mortes", "frames", "kills", "arena_melhor", "missoes"):
        if chave in d:
            setattr(G, chave, d[chave])
    for chave in ("inventario", "coletados", "abertos", "destruidas", "intros", "visitadas", "mortos"):
        setattr(G, chave, set(d.get(chave, [])))
    G.respawn = tuple(d.get("respawn", ("vila", 100, 300)))
    for nome in G.inimigos:
        G.inimigos[nome] = [e for e in G.inimigos[nome] if e.uid not in G.mortos]
    G.visitadas.add(G.sala)
    G.fade = 255
    G.estado = "jogo"
    tocar(SALAS[G.sala]["musica"])
    return True


# ================================================================ ÁUDIO
musica_atual = None
_sons = {}


def aplicar_volume():
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(G.vol_musica)


def tocar(arquivo):
    """Toca a trilha da área em loop (assets/<nome>.mp3, .ogg ou .wav)."""
    global musica_atual
    if arquivo == musica_atual:
        return
    musica_atual = arquivo
    base = os.path.splitext(arquivo)[0]
    for ext in (".mp3", ".ogg", ".wav"):  # um .mp3 seu tem prioridade sobre o .wav gerado
        caminho = os.path.join(PASTA_ASSETS, base + ext)
        if os.path.exists(caminho) and pygame.mixer.get_init():
            try:
                pygame.mixer.music.load(caminho)
                aplicar_volume()
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass
            return


def som(nome):
    """Toca um efeito sonoro (assets/sfx_<nome>.wav)."""
    if not pygame.mixer.get_init():
        return
    if nome not in _sons:
        caminho = os.path.join(PASTA_ASSETS, f"sfx_{nome}.wav")
        try:
            _sons[nome] = pygame.mixer.Sound(caminho) if os.path.exists(caminho) else None
        except pygame.error:
            _sons[nome] = None
    if _sons[nome]:
        _sons[nome].set_volume(G.vol_efeitos)
        _sons[nome].play()


# ================================================================ AUXILIARES
def quebrar(texto, largura, f):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if f.size(teste)[0] <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    linhas.append(atual)
    return linhas


def texto(s, x, y, f=fonte_pequena, cor=(255, 255, 255)):
    tela.blit(f.render(s, True, cor), (x, y))


def texto_centro(s, y, f=fonte, cor=(255, 255, 255)):
    img = f.render(s, True, cor)
    tela.blit(img, (LARGURA // 2 - img.get_width() // 2, y))


def texto_direita(s, x, y, f=fonte_pequena, cor=(255, 255, 255)):
    img = f.render(s, True, cor)
    tela.blit(img, (x - img.get_width(), y))


def painel(rect, alpha=140, borda=None):
    sup = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sup, (10, 10, 22, alpha), sup.get_rect(), border_radius=10)
    if borda:
        pygame.draw.rect(sup, borda, sup.get_rect(), 2, border_radius=10)
    tela.blit(sup, rect.topleft)


def mostrar_aviso(s):
    G.aviso, G.aviso_tempo = s, 150  # ~2,5 segundos


def toast(s):
    G.toasts.append({"texto": s, "t": 200})


def mover_rect(r, dx, dy, obstaculos):
    """Move um retângulo eixo por eixo, tratando colisões com os obstáculos."""
    r.x += dx
    for o in obstaculos:
        if r.colliderect(o):
            if dx > 0:
                r.right = o.left
            elif dx < 0:
                r.left = o.right
    r.y += dy
    for o in obstaculos:
        if r.colliderect(o):
            if dy > 0:
                r.bottom = o.top
            elif dy < 0:
                r.top = o.bottom


def faiscas(centro, cor, n=8, forca=3.0):
    for _ in range(n):
        a, v = random.uniform(0, 2 * math.pi), random.uniform(1, forca)
        G.particulas.append({"x": float(centro[0]), "y": float(centro[1]), "vx": math.cos(a) * v,
                             "vy": math.sin(a) * v, "vida": random.randint(15, 30), "cor": cor})


def texto_flutuante(centro, s, cor=(255, 255, 255)):
    G.textos.append({"x": centro[0], "y": centro[1], "txt": s, "vida": 40, "cor": cor})


def solidos(com_npcs=False):
    """Tudo que bloqueia a passagem na sala atual (paredes, pedras que ainda não explodiram, baús...)."""
    s = SALAS[G.sala]
    lista = list(s["paredes"])
    lista += [r["rect"] for r in s["rachadas"] if r["uid"] not in G.destruidas]
    lista += [o["rect"] for o in s["objetos"]]
    if com_npcs:
        lista += [n["rect"] for n in s["npcs"]]
    return lista


def conquistar(cid):
    if cid in G.conquistas:
        return
    G.conquistas.add(cid)
    nome = next(c[1] for c in CONQUISTAS if c[0] == cid)
    toast("Conquista: " + nome)
    som("conquista")
    escrever_arquivo()


# ================================================================ INIMIGOS E CHEFES
class Inimigo:
    def __init__(self, tipo, x, y, uid=None):
        self.tipo = tipo
        self.d = TIPOS[tipo]
        mult = DIFICULDADES[G.dificuldade]["mult"]
        self.hp = self.hp_max = max(1, round(self.d["hp"] * mult))
        self.rect = R(x, y, self.d["tam"], self.d["tam"])
        self.fx, self.fy = float(x), float(y)  # posição com casas decimais
        self.uid = uid                          # identifica inimigos da sala (para o save)
        self.flash = 0                          # pisca branco ao levar dano
        self.t = 0                              # tempo até mudar a direção de passeio
        self.dir = (0, 0)
        self.tiro = random.randint(60, 120)     # tempo até o próximo ataque à distância
        self.ciclo = random.randint(0, 59)      # ritmo dos pulos (sapo)
        self.volleys = 0
        self.est, self.tmr, self.dir_inv = "normal", 0, (0, 0)  # investida
        self.tp = 90                            # tempo até o mago se teletransportar
        self.tinv = self.d.get("invoca", {}).get("intervalo", 0)
        self.anim = random.random() * 6

    def fase(self):
        r = self.hp / self.hp_max
        return 1 if r > .66 else 2 if r > .33 else 3

    def ataque(self):
        if self.tipo == "rei":  # o Rei muda de golpe a cada fase da luta
            f = self.fase()
            if f == 1:
                return {"padrao": "mira", "intervalo": 80, "vel": 4.0, "qtd": 1, "cor": (255, 90, 160)}
            if f == 2:
                return {"padrao": "leque", "intervalo": 70, "vel": 4.0, "qtd": 3, "cor": (255, 90, 160)}
            return {"padrao": "leque", "intervalo": 52, "vel": 4.4, "qtd": 5, "cor": (255, 60, 120)}
        return self.d.get("ataque")

    def velocidade(self):
        v = self.d["vel"]
        return v * 1.4 if self.tipo == "rei" and self.fase() == 3 else v

    def passeio(self, vel):
        self.t -= 1
        if self.t <= 0:
            self.t = random.randint(30, 90)
            self.dir = random.choice([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)])
        return self.dir[0] * vel * 0.5, self.dir[1] * vel * 0.5

    def ia_investida(self, vx, vy, dist, vel):
        """Persegue, para (pisca amarelo = aviso), dispara em linha reta e descansa."""
        inv = self.d["investida"]
        if self.est == "preparo":
            self.tmr -= 1
            if self.tmr <= 0:
                self.est, self.tmr = "investida", inv["duracao"]
            return 0, 0
        if self.est == "investida":
            self.tmr -= 1
            if self.tmr <= 0:
                self.est, self.tmr = "descanso", inv["descanso"]
            return self.dir_inv[0] * inv["vel"], self.dir_inv[1] * inv["vel"]
        if self.est == "descanso":
            self.tmr -= 1
            if self.tmr <= 0:
                self.est = "normal"
            return 0, 0
        if 0 < dist < self.d["alcance"]:
            if dist < inv["alcance"]:
                self.est, self.tmr = "preparo", inv["preparo"]
                self.dir_inv = (vx / dist, vy / dist)  # a direção é travada: dá para desviar!
                return 0, 0
            return vx / dist * vel, vy / dist * vel
        return self.passeio(vel)

    def ia_mago(self, vx, vy, dist, vel):
        """Teletransporta de tempos em tempos e foge de quem chega perto."""
        self.tp -= 1
        if self.tp <= 0 and dist > 0:
            self.tp = 150
            paredes = SALAS[G.sala]["paredes"]
            for _ in range(25):
                nx, ny = random.randint(40, 730), random.randint(40, 530)
                if (R(nx, ny, self.rect.w, self.rect.h).collidelist(paredes) < 0
                        and 160 < math.hypot(nx - G.jogador.centerx, ny - G.jogador.centery) < 330):
                    faiscas(self.rect.center, (180, 130, 255), 8)
                    self.rect.topleft = (nx, ny)
                    self.fx, self.fy = float(nx), float(ny)
                    faiscas(self.rect.center, (180, 130, 255), 8)
                    break
        if 0 < dist < 150:
            return -vx / dist * vel, -vy / dist * vel
        return 0, 0

    def atualizar(self, paredes):
        d = self.d
        if self.flash:
            self.flash -= 1
        vx = G.jogador.centerx - self.rect.centerx
        vy = G.jogador.centery - self.rect.centery
        dist = math.hypot(vx, vy)
        ia = d.get("ia", "perseguir")
        vel = self.velocidade()
        if ia == "parado":
            mx = my = 0
        elif ia == "investida":
            mx, my = self.ia_investida(vx, vy, dist, vel)
        elif ia == "teleporta":
            mx, my = self.ia_mago(vx, vy, dist, vel)
        elif 0 < dist < d["alcance"]:  # perseguir / pulo / fantasma
            if ia == "pulo":
                self.ciclo = (self.ciclo + 1) % 60
                vel = vel if self.ciclo < 20 else 0
            mx, my = vx / dist * vel, vy / dist * vel
        else:
            mx, my = self.passeio(d["vel"])
        self.mover(mx, my, [] if ia == "fantasma" else paredes)  # fantasma atravessa paredes

        atq = self.ataque()
        if atq and 0 < dist < d["alcance"] + 120:
            self.tiro -= 1
            if self.tiro <= 0:
                self.tiro = atq["intervalo"]
                self.atirar(atq)

        inv = d.get("invoca")
        if inv and self.fase() >= inv["fase_min"]:  # chefes chamam ajudantes quando enfraquecem
            self.tinv -= 1
            if self.tinv <= 0:
                self.tinv = inv["intervalo"]
                if sum(1 for e in G.inimigos[G.sala] if e.tipo == inv["tipo"]) < inv["max"]:
                    for i in range(inv["qtd"]):
                        x = max(40, min(730, self.rect.centerx + (-70 if i == 0 else 70)))
                        y = max(40, min(520, self.rect.centery))
                        G.inimigos[G.sala].append(Inimigo(inv["tipo"], x, y))
                    faiscas(self.rect.center, (200, 80, 220), 14)

    def atirar(self, atq):
        cx, cy = self.rect.center
        base = math.atan2(G.jogador.centery - cy, G.jogador.centerx - cx)
        padrao, qtd = atq["padrao"], atq["qtd"]
        if self.tipo == "rei" and self.fase() == 3:  # na fase final, a cada 3 rajadas vem um anel
            self.volleys += 1
            if self.volleys % 3 == 0:
                padrao, qtd = "anel", 12
        if padrao == "mira":
            angulos = [base]
        elif padrao == "leque":
            angulos = [base + (i - (qtd - 1) / 2) * 0.28 for i in range(qtd)]
        else:
            angulos = [base + 2 * math.pi * i / qtd for i in range(qtd)]
        for a in angulos:
            G.proj.append({"x": float(cx), "y": float(cy), "vx": math.cos(a) * atq["vel"],
                           "vy": math.sin(a) * atq["vel"], "rect": R(0, 0, 12, 12),
                           "dano": 1, "cor": atq["cor"]})

    def mover(self, vx, vy, paredes):
        self.fx += vx
        self.fy += vy
        mover_rect(self.rect, round(self.fx) - self.rect.x, round(self.fy) - self.rect.y, paredes)
        self.rect.clamp_ip(R(20, 20, 760, 560))
        if self.rect.x != round(self.fx):
            self.fx = float(self.rect.x)
        if self.rect.y != round(self.fy):
            self.fy = float(self.rect.y)

    def desenhar(self):
        spr = SPR["inimigo_" + self.tipo]
        tinta = (130, 130, 130) if self.flash else (150, 120, 0) if self.est == "preparo" else None
        if tinta:
            spr = spr.copy()
            spr.fill(tinta + (0,), special_flags=pygame.BLEND_RGB_ADD)
        oy = 0
        if self.d["vel"] > 0:  # balanço suave ao andar
            oy = int(math.sin(G.tick * 0.15 + self.anim) * (3 if self.d.get("ia") == "fantasma" else 2))
        sombra(self.rect)
        tela.blit(spr, (self.rect.x, self.rect.y + oy))


_sombras = {}


def sombra(r):
    w = r.w + 6
    if w not in _sombras:
        s = pygame.Surface((w, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 70), s.get_rect())
        _sombras[w] = s
    tela.blit(_sombras[w], (r.centerx - w // 2, r.bottom - 7))


def soltar(sala_, tipo, centro, valor=0):
    x, y = centro
    nome = NOMES_ITEM.get(tipo, tipo)
    G.drops[sala_].append({"uid": None, "id": tipo, "nome": nome, "valor": valor,
                           "rect": R(x - 11, y - 11, 22, 22)})


def ferir(e, dano, kx=0, ky=0):
    """Tira vida de um inimigo (espada, flecha ou bomba)."""
    if e not in G.inimigos[G.sala]:
        return
    e.hp -= dano
    e.flash = 8
    som("acerto")
    faiscas(e.rect.center, (255, 255, 255), 5, 2.5)
    texto_flutuante(e.rect.midtop, f"-{dano}")
    if kx or ky:
        forca = 8 if e.d.get("boss") else 16  # chefes são empurrados menos
        mover_rect(e.rect, int(kx * forca), int(ky * forca), solidos())
        e.fx, e.fy = float(e.rect.x), float(e.rect.y)
    if e.hp <= 0:
        morte_inimigo(e)


def morte_inimigo(e):
    if e not in G.inimigos[G.sala]:
        return
    G.inimigos[G.sala].remove(e)
    if e.uid:
        G.mortos.add(e.uid)
    chefe = e.d.get("boss", False)
    som("chefe" if chefe else "morte")
    faiscas(e.rect.center, e.d["cor"], 30 if chefe else 12, 5 if chefe else 3.5)
    if chefe:
        G.shake = 25
    cx, cy = e.rect.center
    G.kills[e.tipo] = G.kills.get(e.tipo, 0) + 1
    if sum(G.kills.values()) >= 50:
        conquistar("cacador")
    for tipo, _nome in RECOMPENSAS.get(e.tipo, []):
        soltar(G.sala, tipo, (cx, cy))
    lo, hi = e.d["moedas"]
    soltar(G.sala, "moeda", (cx + 28, cy + 10), random.randint(lo, hi))
    if not chefe:
        sorteio = random.random()
        if sorteio < e.d.get("drop", 0):
            soltar(G.sala, "pocao", (cx - 28, cy + 10))
        elif "arco" in G.inventario and sorteio < e.d.get("drop", 0) + 0.2:
            soltar(G.sala, "flecha", (cx - 28, cy + 10), 3)
        elif sorteio > 0.94:
            soltar(G.sala, "bomba", (cx - 28, cy + 10), 1)
    if "divide" in e.d:  # slime gigante se divide
        tipo, qtd = e.d["divide"]
        for i in range(qtd):
            G.inimigos[G.sala].append(Inimigo(tipo, max(30, min(740, cx - 13 + (i * 2 - 1) * 16)), max(30, min(540, cy - 13))))
    if e.tipo == "lobo":
        mostrar_aviso("O Lobo Sombrio caiu! Ele deixou uma chave.")
    if e.tipo == "rei":
        G.inimigos[G.sala].clear()  # os morcegos invocados somem junto
    for cid in ("lobo", "golem", "serpente", "rainha"):
        if e.tipo == cid:
            conquistar(cid)
    for qid, m in MISSOES.items():  # progresso das missões de "matar"
        st = G.missoes.get(qid)
        if st and st["estado"] == "ativa" and m["tipo"] == "matar" and e.tipo in m["alvo"] and st["prog"] < m["qtd"]:
            st["prog"] += 1
            if st["prog"] >= m["qtd"]:
                toast("Missão pronta para entregar: " + m["nome"])
    if e.tipo in FALAS_MORTE:
        G.proj.clear()
        abrir_dialogo(FALAS_MORTE[e.tipo])


# ================================================================ AÇÕES DO JOGADOR
def atacar():
    if "espada" not in G.inventario or G.cd_ataque > 0:
        return
    G.cd_ataque, G.anim_ataque = 22, 8
    som("ataque")
    fx, fy = G.facing
    j = G.jogador
    if fx:
        area = R(j.right if fx > 0 else j.left - 48, j.centery - 24, 48, 48)
    else:
        area = R(j.centerx - 24, j.bottom if fy > 0 else j.top - 48, 48, 48)
    G.area_ataque = area
    for e in list(G.inimigos[G.sala]):
        if area.colliderect(e.rect):
            ferir(e, G.dano, fx, fy)


def atirar_flecha():
    if "arco" not in G.inventario:
        mostrar_aviso("Você ainda não tem um arco.")
    elif G.flechas <= 0:
        som("erro")
        mostrar_aviso("Sem flechas!")
    elif G.cd_flecha <= 0:
        G.flechas -= 1
        G.cd_flecha = 18
        fx, fy = G.facing
        j = G.jogador
        G.flechas_voando.append({"x": float(j.centerx), "y": float(j.centery), "vx": fx * 10.0,
                                 "vy": fy * 10.0, "rect": R(0, 0, 12, 12)})
        som("flecha")


def colocar_bomba():
    if G.bombas <= 0:
        som("erro")
        mostrar_aviso("Você não tem bombas.")
    elif len(G.bombas_ativas) < 3:
        fx, fy = G.facing
        G.bombas -= 1
        G.bombas_ativas.append({"x": G.jogador.centerx + fx * 34, "y": G.jogador.centery + fy * 34, "t": 80})


def explodir(b):
    G.bombas_ativas.remove(b)
    som("bomba")
    G.shake = 14
    G.explosoes.append({"x": b["x"], "y": b["y"], "t": 12})
    faiscas((b["x"], b["y"]), (255, 170, 60), 24, 6)
    for e in list(G.inimigos[G.sala]):
        if math.hypot(e.rect.centerx - b["x"], e.rect.centery - b["y"]) < 85 + e.rect.w / 2:
            ferir(e, 3)
    if math.hypot(G.jogador.centerx - b["x"], G.jogador.centery - b["y"]) < 70:
        machucar(1, R(int(b["x"]), int(b["y"]), 1, 1))
    for r in SALAS[G.sala]["rachadas"]:
        if r["uid"] not in G.destruidas:
            dx = max(r["rect"].left - b["x"], 0, b["x"] - r["rect"].right)
            dy = max(r["rect"].top - b["y"], 0, b["y"] - r["rect"].bottom)
            if math.hypot(dx, dy) < 85:
                G.destruidas.add(r["uid"])
                faiscas(r["rect"].center, (150, 140, 130), 20, 4)
                mostrar_aviso("A pedra se despedaçou!")
                conquistar("bombeiro")


def esquivar():
    if G.cd_dash > 0 or G.dash > 0:
        return
    t = pygame.key.get_pressed()
    dx = int(t[pygame.K_RIGHT] or t[pygame.K_d]) - int(t[pygame.K_LEFT] or t[pygame.K_a])
    dy = int(t[pygame.K_DOWN] or t[pygame.K_s]) - int(t[pygame.K_UP] or t[pygame.K_w])
    if dx == 0 and dy == 0:
        dx, dy = G.facing
    n = math.hypot(dx, dy)
    G.dash_dir = (dx / n, dy / n)
    G.dash, G.cd_dash = 9, 50
    G.invul = max(G.invul, 16)  # invencível durante o desvio
    som("dash")


def usar_pocao():
    if G.pocoes > 0 and G.hp < G.hp_max:
        G.pocoes -= 1
        G.hp = min(G.hp_max, G.hp + 2)
        som("pocao")
        texto_flutuante(G.jogador.midtop, "+2", (255, 120, 140))
        mostrar_aviso("Você usou uma poção (+2 de vida)")
    elif G.pocoes == 0:
        som("erro")
        mostrar_aviso("Você não tem poções")


def machucar(dano, origem):
    """Tira vida do jogador (com invencibilidade curta e empurrão)."""
    if G.invul > 0 or G.estado != "jogo":
        return
    G.hp -= dano
    G.invul = 60
    G.shake = 10
    som("dano")
    faiscas(G.jogador.center, (230, 50, 70), 8)
    vx = G.jogador.centerx - origem.centerx
    vy = G.jogador.centery - origem.centery
    d = math.hypot(vx, vy) or 1
    mover_rect(G.jogador, int(vx / d * 22), int(vy / d * 22), solidos(True))
    if G.hp <= 0:
        G.hp = 0
        G.mortes += 1
        G.estado = "gameover"
        resetar_arena()


def receber(tipo, valor=1):
    """Dá um item ao jogador (usado por chão, baús, loja e recompensas)."""
    if tipo == "moeda":
        G.moedas += valor
        som("moeda")
        if G.moedas >= 100:
            conquistar("rico")
    elif tipo == "pocao":
        G.pocoes += valor
        som("item")
    elif tipo == "coracao":
        G.hp_max += valor
        G.hp = G.hp_max
        som("item")
    elif tipo == "amuleto":
        G.hp_max += 2
        G.hp = G.hp_max
        som("item")
    elif tipo == "flecha":
        G.flechas += valor
        som("item")
    elif tipo == "bomba":
        G.bombas += valor
        som("item")
    elif tipo == "arco":
        G.inventario.add("arco")
        som("item")
        conquistar("arqueiro")
    elif tipo == "anel":
        G.inventario.add("anel")
        G.dano += 1
        som("item")
    else:  # chave, fragmentos, cristal, broche, espada
        G.inventario.add(tipo)
        som("item")
        if tipo == "espada":
            conquistar("aventureiro")


def pegar(it, lista_drop=None):
    tipo, valor = it["id"], it.get("valor") or 1
    receber(tipo, valor)
    if tipo == "moeda":
        texto_flutuante(G.jogador.midtop, f"+{valor}", (255, 215, 60))
    elif tipo == "pocao":
        mostrar_aviso("Você pegou: Poção (Q para usar)")
    elif tipo == "coracao":
        mostrar_aviso("Coração de Vida! Vida máxima +1")
    elif tipo == "amuleto":
        mostrar_aviso("Amuleto da Vida! Vida máxima +2")
    elif tipo == "anel":
        mostrar_aviso("Anel de Força! Seu dano aumentou em 1")
    else:
        mostrar_aviso("Você pegou: " + it["nome"] + (f" x{valor}" if valor > 1 else ""))
    if tipo == "cristal":
        abrir_dialogo(["Os fragmentos se unem e o Cristal da Aurora volta a brilhar!",
                       "Uma luz envolve você e o leva de volta para casa..."], da="final")
    if lista_drop is not None:
        lista_drop.remove(it)
    else:
        G.coletados.add(it["uid"])


# ---------------------------------------------------------------- INTERAÇÕES
def abrir_dialogo(linhas, final=False, da=None):
    G.dialogo = {"linhas": linhas, "i": 0, "car": 0, "final": final, "da": da}


def separar_falante(linha):
    if ": " in linha:
        nome, resto = linha.split(": ", 1)
        if len(nome) <= 24 and nome[:1].isupper() and "." not in nome:
            return nome, resto
    return None, linha


def avancar_dialogo():
    d = G.dialogo
    _, resto = separar_falante(d["linhas"][d["i"]])
    if d["car"] < len(resto):  # primeiro apertar completa o texto; o segundo avança
        d["car"] = len(resto)
        return
    d["i"] += 1
    d["car"] = 0
    if d["i"] >= len(d["linhas"]):
        G.dialogo = None
        executar_acao(d.get("da"))
        if d["final"]:
            terminar_jogo()


def executar_acao(da):
    if not da:
        return
    nome, _, arg = da.partition(":")
    if nome == "espada":
        receber("espada")
        receber("pocao")
        mostrar_aviso("Você recebeu a Espada de Aurora (J) e uma Poção (Q)")
    elif nome == "loja":
        G.estado, G.msg_loja = "loja", ""
    elif nome == "final":
        entrar_sala("vila", (395, 300))
        abrir_dialogo(FINAL_LUNA, final=True)
    elif nome == "missao":
        aceitar_missao(arg)
    elif nome == "entregar":
        entregar_missao(arg)
    elif nome == "arena":
        iniciar_arena()


def terminar_jogo():
    G.estado = "fim"
    conquistar("salvador")
    tocar("fim.mp3")


def alvo_interacao():
    """O que está ao alcance do jogador (NPC, baú, placa ou santuário)."""
    s = SALAS[G.sala]
    for n in s["npcs"]:
        if G.jogador.inflate(60, 60).colliderect(n["rect"]):
            return n["rect"], "Pressione E para falar"
    for o in s["objetos"]:
        if G.jogador.inflate(50, 50).colliderect(o["rect"]):
            if o["tipo"] == "bau":
                return o["rect"], "Pressione E para abrir" if o["uid"] not in G.abertos else "Vazio"
            return o["rect"], "Pressione E para " + ("ler" if o["tipo"] == "placa" else "descansar")
    return None, None


def interagir():
    s = SALAS[G.sala]
    for n in s["npcs"]:
        if G.jogador.inflate(60, 60).colliderect(n["rect"]):
            linhas, final, da = falas(n["id"])
            abrir_dialogo(linhas, final, da)
            return
    for o in s["objetos"]:
        if G.jogador.inflate(50, 50).colliderect(o["rect"]):
            if o["tipo"] == "placa":
                abrir_dialogo(o["texto"])
            elif o["tipo"] == "bau":
                abrir_bau(o)
            else:
                descansar(o)
            return


def abrir_bau(o):
    if o["uid"] in G.abertos:
        mostrar_aviso("O baú está vazio.")
        return
    G.abertos.add(o["uid"])
    partes = []
    for tipo, valor in o["conteudo"]:
        receber(tipo, valor)
        partes.append(NOMES_ITEM.get(tipo, tipo) + (f" x{valor}" if valor > 1 else ""))
    som("bau")
    faiscas(o["rect"].center, (255, 220, 100), 14, 3)
    mostrar_aviso("Você encontrou: " + ", ".join(partes))


def descansar(o):
    """Santuário: cura tudo, salva o jogo e vira o ponto de retorno."""
    G.hp = G.hp_max
    G.respawn = (G.sala, o["rect"].centerx - 14, o["rect"].bottom + 8)
    som("pocao")
    faiscas(o["rect"].center, (140, 220, 255), 18, 3)
    salvar_jogo(avisar=False)
    mostrar_aviso("Você descansou. Vida restaurada e progresso salvo.")


# ---------------------------------------------------------------- MISSÕES
def missao_pronta(qid):
    m, st = MISSOES[qid], G.missoes.get(qid)
    if not st or st["estado"] != "ativa":
        return False
    if m["tipo"] == "matar":
        return st["prog"] >= m["qtd"]
    if m["tipo"] == "item":
        return m["item"] in G.inventario
    return G.arena_melhor >= m["qtd"]  # arena


def progresso(qid):
    m, st = MISSOES[qid], G.missoes[qid]
    if m["tipo"] == "matar":
        return f"{min(st['prog'], m['qtd'])}/{m['qtd']}"
    if m["tipo"] == "item":
        return "1/1" if m["item"] in G.inventario else "0/1"
    return f"{min(G.arena_melhor, m['qtd'])}/{m['qtd']}"


def aceitar_missao(qid):
    G.missoes[qid] = {"estado": "ativa", "prog": 0}
    toast("Missão aceita: " + MISSOES[qid]["nome"])
    som("item")


def entregar_missao(qid):
    m = MISSOES[qid]
    for tipo, valor in m["recompensa"].items():
        receber(tipo, valor)
    if m["tipo"] == "item":
        G.inventario.discard(m["item"])
    G.missoes[qid]["estado"] = "entregue"
    toast("Missão concluída: " + m["nome"])
    if sum(1 for s in G.missoes.values() if s["estado"] == "entregue") >= 3:
        conquistar("ajudante")


def falas(npc_id):
    """Retorna (linhas, é o final do jogo?, ação extra). O texto muda com o seu progresso."""
    inv = G.inventario
    qid = QUEST_NPC.get(npc_id)
    if qid:  # missões têm prioridade
        m, t, st = MISSOES[qid], MISSAO_TEXTOS[qid], G.missoes.get(qid)
        if st and st["estado"] == "ativa":
            if missao_pronta(qid):
                return t["entrega"], False, "entregar:" + qid
            if t["lembrete"]:
                return t["lembrete"], False, "loja" if npc_id == "ferreiro" else None
        elif st is None and m["requer"] in inv:
            return t["oferta"], False, "missao:" + qid

    if npc_id == "luna":
        if "espada" not in inv:
            return ["Anciã Luna: Jovem viajante, o Rei Sombrio roubou o Cristal da Aurora, "
                    "e ele se partiu em pedaços.",
                    "Anciã Luna: Leve esta Espada de Aurora. Ataque com a tecla J.",
                    "Anciã Luna: O ferreiro da vila melhora sua espada. Os monstros soltam moedas.",
                    "Anciã Luna: Comece pela floresta, a leste. O Lobo Sombrio guarda a chave "
                    "da caverna."], False, "espada"
        if "chave" not in inv:
            return ["Anciã Luna: Siga a floresta para o leste. O Lobo Sombrio guarda a chave da caverna.",
                    "Anciã Luna: Descanse nos santuários para salvar o jogo e use poções com Q."], False, None
        if "fragmento1" not in inv:
            return ["Anciã Luna: A caverna fica depois da floresta. "
                    "O Golem de Pedra guarda o primeiro fragmento do cristal."], False, None
        if "fragmento2" not in inv:
            return ["Anciã Luna: Ao sul da caverna fica o pântano. "
                    "A Serpente guarda o segundo fragmento."], False, None
        return ["Anciã Luna: Só falta o castelo, ao norte do pântano. O Rei Sombrio espera por você.",
                "Anciã Luna: Cuidado... ele é mais forte do que parece. "
                "E, no fundo, ainda é alguém que eu amo."], False, None
    if npc_id == "ferreiro":
        if not G.conheceu_ferreiro:
            G.conheceu_ferreiro = True
            return ["Ferreiro Bram: Bem-vindo! Eu forjo melhorias para quem enfrenta os monstros.",
                    "Ferreiro Bram: Também vendo bombas e flechas. Uma bomba abre muitos segredos!"], False, "loja"
        return ["Ferreiro Bram: De volta? Vamos ver o que eu tenho."], False, "loja"
    if npc_id == "mestre":
        if "espada" not in inv:
            return ["Mestre da Arena: Você nem tem uma espada! Volte quando estiver armado."], False, None
        if G.arena["ativa"]:
            return ["Mestre da Arena: Concentre-se! O desafio está em andamento!"], False, None
        if G.arena_melhor >= len(ARENA_ONDAS):
            return ["Mestre da Arena: Quer enfrentar as 5 ondas outra vez? Vale moedas!",
                    "Mestre da Arena: Prepare-se!"], False, "arena"
        return ["Mestre da Arena: Cinco ondas de monstros... Está pronto?",
                "Mestre da Arena: Que comece o desafio!"], False, "arena"
    if npc_id == "eremita":
        if "chave" in inv:
            return ["Eremita: Você derrotou o Lobo! A caverna fica ao leste da clareira."], False, None
        return ["Eremita: Cuidado, viajante. O Lobo Sombrio era um lobo comum, "
                "até o Rei Sombrio corromper a floresta.",
                "Eremita: Dizem que há uma gruta secreta ao norte, tapada por pedras rachadas. "
                "Uma bomba do ferreiro resolve.",
                "Eremita: Ela guarda um arco antigo. Boa para atacar de longe (tecla K)."], False, None
    if npc_id == "espirito":
        if "fragmento1" in inv:
            return ["Espírito: O Golem descansa agora. Siga ao sul, rumo ao pântano."], False, None
        return ["Espírito: Eu sou o que restou de um antigo guardião.",
                "Espírito: O Golem solta pedras em todas as direções. Desvie pelas diagonais!",
                "Espírito: Esta caverna é escura: você só enxerga ao redor de si."], False, None
    if npc_id == "viajante":
        return ["Viajante: Os fantasmas atravessam paredes, não adianta se esconder atrás de obstáculos.",
                "Viajante: A Serpente cospe veneno em leque. Use o desvio (SHIFT) para passar entre os tiros!"], False, None
    if npc_id == "soldado":
        return ["Soldado Ferido: O Rei... não é mais ele mesmo. Quando enfraquece, chama morcegos.",
                "Soldado Ferido: E no fim ele fica furioso. Use as poções do salão e os pilares!"], False, None
    return ["..."], False, None


# ---------------------------------------------------------------- LOJA
def itens_loja():
    c = G.compras
    return [
        {"nome": "Poção de Cura", "preco": 6, "ok": True},
        {"nome": "Bomba", "preco": 8, "ok": True},
        {"nome": "5 Flechas", "preco": 5, "ok": "arco" in G.inventario, "nota": "precisa do arco"},
        {"nome": "Espada Afiada (+1 de dano)", "preco": [25, 45][c["dano"]] if c["dano"] < 2 else None, "ok": True},
        {"nome": "Coração de Ferro (+1 vida máx.)", "preco": [20, 30][c["coracao"]] if c["coracao"] < 2 else None, "ok": True},
    ]


def comprar(i):
    it = itens_loja()[i]
    if it["preco"] is None:
        som("erro")
        G.msg_loja = "Esgotado!"
    elif not it["ok"]:
        som("erro")
        G.msg_loja = "Você ainda não tem o " + it.get("nota", "item").replace("precisa do ", "")
    elif G.moedas < it["preco"]:
        som("erro")
        G.msg_loja = "Moedas insuficientes."
    else:
        G.moedas -= it["preco"]
        if i == 0:
            G.pocoes += 1
        elif i == 1:
            G.bombas += 1
        elif i == 2:
            G.flechas += 5
        elif i == 3:
            G.compras["dano"] += 1
            G.dano += 1
        else:
            G.compras["coracao"] += 1
            G.hp_max += 1
            G.hp = G.hp_max
        som("compra")
        G.msg_loja = "Comprado: " + it["nome"]
        if G.compras["dano"] == 2 and G.compras["coracao"] == 2:
            conquistar("compras")


# ---------------------------------------------------------------- ARENA
def resetar_arena():
    G.inimigos["arena"].clear()
    G.arena.update(ativa=False, onda=0, espera=0, limpas=0)


def iniciar_arena():
    G.arena.update(ativa=True, onda=0, espera=60, limpas=0)
    mostrar_aviso("Que comece o desafio!")


def concluir_arena():
    G.arena["ativa"] = False
    primeira = "arena_ok" not in G.coletados
    G.coletados.add("arena_ok")
    G.arena_melhor = len(ARENA_ONDAS)
    receber("moeda", 40 if primeira else 25)
    mostrar_aviso("Arena vencida! Você ganhou " + ("40" if primeira else "25") + " moedas.")
    conquistar("campeao")


def atualizar_arena():
    a = G.arena
    if not a["ativa"] or G.inimigos["arena"]:
        return
    if a["onda"] > a["limpas"]:  # acabou de vencer uma onda
        a["limpas"] = a["onda"]
        G.arena_melhor = max(G.arena_melhor, a["limpas"])
        if a["limpas"] < len(ARENA_ONDAS):
            mostrar_aviso(f"Onda {a['limpas']} vencida!")
    a["espera"] -= 1
    if a["espera"] > 0:
        return
    if a["onda"] >= len(ARENA_ONDAS):
        concluir_arena()
        return
    tipos = [t for t, n in ARENA_ONDAS[a["onda"]] for _ in range(n)]
    for tipo, (x, y) in zip(tipos, random.sample(ARENA_SPAWNS, len(tipos))):
        G.inimigos["arena"].append(Inimigo(tipo, x, y))
    a["onda"] += 1
    a["espera"] = 100


# ================================================================ ESTADO
def novo_jogo(dificuldade="normal"):
    """(Re)começa a aventura do zero. Conquistas e configurações são mantidas."""
    G.dificuldade = dificuldade
    G.sala = "vila"
    G.jogador = R(100, 300, 28, 28)
    G.facing = (0, 1)
    G.hp_max = G.hp = DIFICULDADES[dificuldade]["vida"]
    G.dano = 1
    G.pocoes = G.moedas = G.flechas = G.bombas = 0
    G.compras = {"dano": 0, "coracao": 0}
    G.conheceu_ferreiro = False
    G.msg_loja = ""
    G.inventario, G.coletados, G.abertos, G.destruidas = set(), set(), set(), set()
    G.intros, G.visitadas, G.mortos = set(), {"vila"}, set()
    G.missoes, G.kills = {}, {}
    G.mortes = G.frames = 0
    G.respawn = ("vila", 100, 300)
    G.arena = {"ativa": False, "onda": 0, "espera": 0, "limpas": 0}
    G.arena_melhor = 0
    G.dialogo = None
    G.aviso, G.aviso_tempo = "", 0
    G.banner = None
    G.invul = G.cd_ataque = G.anim_ataque = G.cd_flecha = G.cd_dash = G.dash = G.shake = G.fade = 0
    G.dash_dir = (0, 0)
    G.area_ataque = None
    G.proj, G.flechas_voando, G.bombas_ativas, G.explosoes = [], [], [], []
    G.particulas, G.textos = [], []
    G.drops = {nome: [] for nome in SALAS}
    G.inimigos = {nome: [Inimigo(*e, uid=f"{nome}:{i}") for i, e in enumerate(s["inimigos"])]
                  for nome, s in SALAS.items()}


def entrar_sala(destino, spawn, auto=True):
    if G.sala == "arena" and destino != "arena":
        resetar_arena()
    G.sala = destino
    G.jogador.topleft = spawn
    G.proj.clear()
    G.flechas_voando.clear()
    G.fade = 255
    G.visitadas.add(destino)
    if len(G.visitadas) >= len(SALAS):
        conquistar("explorador")
    tocar(SALAS[destino]["musica"])
    chefe = next((e for e in G.inimigos[destino] if e.d.get("boss")), None)
    G.banner = {"texto": chefe.d["nome"], "t": 150} if chefe else None
    intro = SALAS[destino].get("intro")
    if intro and destino not in G.intros:
        G.intros.add(destino)
        abrir_dialogo(intro)
    if auto and G.estado == "jogo":
        salvar_jogo(avisar=False)


def continuar():
    """Depois de cair: volta ao último santuário com a vida cheia, mas perde metade das moedas."""
    G.hp = G.hp_max
    G.moedas //= 2
    G.invul = 90
    G.dash = 0
    G.proj.clear()
    for lista in G.inimigos.values():  # chefes se recuperam
        for e in lista:
            if e.d.get("boss"):
                e.hp = e.hp_max
    G.estado = "jogo"
    sala_r, x, y = G.respawn
    entrar_sala(sala_r, (x, y))
    mostrar_aviso("Você acordou no último santuário e perdeu metade das moedas.")


# ================================================================ ATUALIZAÇÃO
def atualizar():
    if G.aviso_tempo > 0:
        G.aviso_tempo -= 1
    G.fade = max(0, G.fade - 14)
    for t in G.toasts[:]:
        t["t"] -= 1
        if t["t"] <= 0:
            G.toasts.remove(t)
    if G.banner:
        G.banner["t"] -= 1
        if G.banner["t"] <= 0:
            G.banner = None
    for p in G.particulas[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vida"] -= 1
        if p["vida"] <= 0:
            G.particulas.remove(p)
    for t in G.textos[:]:
        t["y"] -= 0.8
        t["vida"] -= 1
        if t["vida"] <= 0:
            G.textos.remove(t)
    for x in G.explosoes[:]:
        x["t"] -= 1
        if x["t"] <= 0:
            G.explosoes.remove(x)

    if G.dialogo:
        G.dialogo["car"] += 2  # efeito de "digitando"
        return
    G.frames += 1
    s = SALAS[G.sala]
    j = G.jogador
    G.invul = max(0, G.invul - 1)
    G.cd_ataque = max(0, G.cd_ataque - 1)
    G.cd_flecha = max(0, G.cd_flecha - 1)
    G.cd_dash = max(0, G.cd_dash - 1)
    G.anim_ataque = max(0, G.anim_ataque - 1)
    barreiras = solidos(True)

    # movimento (ou desvio)
    if G.dash > 0:
        G.dash -= 1
        dx, dy = int(G.dash_dir[0] * 12), int(G.dash_dir[1] * 12)
        faiscas(j.center, (200, 220, 255), 1, 1)
    else:
        t = pygame.key.get_pressed()
        dx = (int(t[pygame.K_RIGHT] or t[pygame.K_d]) - int(t[pygame.K_LEFT] or t[pygame.K_a])) * 4
        dy = (int(t[pygame.K_DOWN] or t[pygame.K_s]) - int(t[pygame.K_UP] or t[pygame.K_w])) * 4
        if dx:
            G.facing = (1 if dx > 0 else -1, 0)
        elif dy:
            G.facing = (0, 1 if dy > 0 else -1)
    mover_rect(j, dx, dy, barreiras)

    atualizar_arena()
    solidos_inimigos = solidos()
    for e in list(G.inimigos[G.sala]):
        e.atualizar(solidos_inimigos)
    for e in G.inimigos[G.sala]:
        if j.colliderect(e.rect):
            machucar(e.d["dano"], e.rect)
            break

    for p in G.proj[:]:  # projéteis dos inimigos
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["rect"].center = (int(p["x"]), int(p["y"]))
        if p["rect"].collidelist(solidos_inimigos) >= 0 or not R(0, 0, LARGURA, ALTURA).contains(p["rect"]):
            G.proj.remove(p)
        elif p["rect"].colliderect(j):
            machucar(p["dano"], p["rect"])
            G.proj.remove(p)

    for f in G.flechas_voando[:]:  # flechas do jogador
        f["x"] += f["vx"]
        f["y"] += f["vy"]
        f["rect"].center = (int(f["x"]), int(f["y"]))
        if f["rect"].collidelist(solidos_inimigos) >= 0 or not R(0, 0, LARGURA, ALTURA).contains(f["rect"]):
            G.flechas_voando.remove(f)
            continue
        for e in G.inimigos[G.sala]:
            if f["rect"].colliderect(e.rect):
                ferir(e, G.dano, f["vx"] / 10, f["vy"] / 10)
                G.flechas_voando.remove(f)
                break

    for b in G.bombas_ativas[:]:
        b["t"] -= 1
        if b["t"] <= 0:
            explodir(b)

    for it in s["itens"]:  # itens do chão e itens soltos pelos inimigos
        if it["uid"] not in G.coletados and j.colliderect(it["rect"]):
            pegar(it)
    for it in list(G.drops[G.sala]):
        if j.colliderect(it["rect"]):
            pegar(it, G.drops[G.sala])

    if G.dialogo is None and G.estado == "jogo":  # trocar de sala
        for sd in s["saidas"]:
            if j.colliderect(sd["rect"]):
                if sd["requer"] and sd["requer"] not in G.inventario:
                    som("erro")
                    mostrar_aviso(sd["msg"] or "A passagem está bloqueada.")
                    j.x += {"E": -20, "O": 20}.get(sd["lado"], 0)
                    j.y += {"N": 20, "S": -20}.get(sd["lado"], 0)
                else:
                    entrar_sala(sd["destino"], sd["spawn"])
                break


# ================================================================ EVENTOS (teclado)
CONFIRMA = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e, pygame.K_SPACE)
CIMA, BAIXO = (pygame.K_UP, pygame.K_w), (pygame.K_DOWN, pygame.K_s)
ESQ, DIR = (pygame.K_LEFT, pygame.K_a), (pygame.K_RIGHT, pygame.K_d)


def ir_para(estado, sel=0):
    G.estado, G.sel = estado, sel


def sair():
    pygame.quit()
    sys.exit()


def mover_selecao(k, n):
    if k in CIMA:
        G.sel = (G.sel - 1) % n
        som("menu")
    elif k in BAIXO:
        G.sel = (G.sel + 1) % n
        som("menu")


def itens_titulo():
    return (["Continuar"] if G.tem_save else []) + ["Novo Jogo", "Conquistas", "Controles", "Sair"]


def tecla_titulo(k):
    itens = itens_titulo()
    mover_selecao(k, len(itens))
    if k == pygame.K_ESCAPE:
        sair()
    elif k in CONFIRMA:
        escolha = itens[G.sel]
        som("item")
        if escolha == "Continuar":
            if not carregar_jogo():
                G.tem_save = False
        elif escolha == "Novo Jogo":
            ir_para("dificuldade", 1)
        elif escolha == "Conquistas":
            ir_para("conquistas")
        elif escolha == "Controles":
            G.volta = "titulo"
            ir_para("controles")
        else:
            sair()


def tecla_dificuldade(k):
    chaves = list(DIFICULDADES)
    mover_selecao(k, len(chaves))
    if k == pygame.K_ESCAPE:
        ir_para("titulo")
    elif k in CONFIRMA:
        novo_jogo(chaves[G.sel])
        ir_para("historia")


def tecla_historia(k):
    if k in CONFIRMA or k == pygame.K_ESCAPE:
        ir_para("jogo")
        tocar(SALAS[G.sala]["musica"])


def tecla_simples(destino):
    def f(k):
        if k in CONFIRMA or k == pygame.K_ESCAPE:
            ir_para(destino() if callable(destino) else destino)
    return f


def itens_pausa():
    return ["Continuar", "Salvar jogo", f"Música: {round(G.vol_musica * 100)}%",
            f"Efeitos: {round(G.vol_efeitos * 100)}%", "Controles", "Voltar ao menu"]


def tecla_pausa(k):
    mover_selecao(k, 6)
    if k in (pygame.K_ESCAPE, pygame.K_p):
        G.estado = "jogo"
    elif G.sel in (2, 3) and (k in ESQ or k in DIR):
        passo = 0.1 if k in DIR else -0.1
        if G.sel == 2:
            G.vol_musica = max(0.0, min(1.0, round(G.vol_musica + passo, 1)))
            aplicar_volume()
        else:
            G.vol_efeitos = max(0.0, min(1.0, round(G.vol_efeitos + passo, 1)))
            som("item")
        escrever_arquivo()
    elif k in CONFIRMA:
        if G.sel == 0:
            G.estado = "jogo"
        elif G.sel == 1:
            salvar_jogo()
            som("compra")
        elif G.sel == 4:
            G.volta = "pausa"
            ir_para("controles")
        elif G.sel == 5:
            salvar_jogo(avisar=False)
            ir_para("titulo")
            tocar("menu.mp3")


def tecla_loja(k):
    if k in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
        comprar(k - pygame.K_1)
    elif k in CONFIRMA or k == pygame.K_ESCAPE:
        G.estado = "jogo"


def tecla_jogo(k):
    if G.dialogo:
        if k in CONFIRMA:
            avancar_dialogo()
        return
    if k in (pygame.K_ESCAPE, pygame.K_p):
        ir_para("pausa")
    elif k in CONFIRMA:
        interagir()
    elif k == pygame.K_j:
        atacar()
    elif k == pygame.K_k:
        atirar_flecha()
    elif k == pygame.K_b:
        colocar_bomba()
    elif k == pygame.K_q:
        usar_pocao()
    elif k in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_l):
        esquivar()
    elif k == pygame.K_TAB:
        ir_para("diario")
    elif k == pygame.K_m:
        ir_para("mapa")


def tecla_voltar_jogo(k):
    if k in CONFIRMA or k in (pygame.K_ESCAPE, pygame.K_TAB, pygame.K_m):
        G.estado = "jogo"


def tecla_gameover(k):
    if k in CONFIRMA:
        continuar()


def tecla_fim(k):
    if k in CONFIRMA:
        carregar_perfil()
        ir_para("titulo")
        tocar("menu.mp3")


TECLAS = {"titulo": tecla_titulo, "dificuldade": tecla_dificuldade, "historia": tecla_historia,
          "conquistas": tecla_simples("titulo"), "controles": tecla_simples(lambda: G.volta),
          "pausa": tecla_pausa, "loja": tecla_loja, "jogo": tecla_jogo, "mapa": tecla_voltar_jogo,
          "diario": tecla_voltar_jogo, "gameover": tecla_gameover, "fim": tecla_fim}


def tratar_evento(ev):
    if ev.type == pygame.QUIT:
        sair()
    if ev.type != pygame.KEYDOWN:
        return
    if ev.key == pygame.K_F11:
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            pass
        return
    TECLAS.get(G.estado, lambda k: None)(ev.key)


# ================================================================ DESENHO: EFEITOS VISUAIS
def criar_vinheta():
    peq = pygame.Surface((16, 12), pygame.SRCALPHA)
    for x in range(16):
        for y in range(12):
            d = math.hypot((x - 7.5) / 7.5, (y - 5.5) / 5.5)
            peq.set_at((x, y), (200, 0, 0, int(255 * max(0.0, min(1.0, (d - 0.55) / 0.6)))))
    return pygame.transform.smoothscale(peq, (LARGURA, ALTURA))


def criar_luz(raio=190):
    luz = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    luz.fill((0, 0, 10, 215))
    for r in range(raio, 0, -2):
        pygame.draw.circle(luz, (0, 0, 10, int(215 * (r / raio) ** 1.8)), (raio, raio), r)
    return luz


def criar_nevoa():
    n = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    rnd = random.Random(7)
    for _ in range(9):
        x, y = rnd.randint(0, LARGURA), rnd.randint(60, ALTURA - 60)
        w, h = rnd.randint(260, 420), rnd.randint(90, 160)
        for dx in (-LARGURA, 0, LARGURA):  # repete nas bordas: rolagem sem emendas
            pygame.draw.ellipse(n, (190, 215, 200, 26), (x + dx, y, w, h))
    return n


def criar_fundo_titulo():
    f = pygame.Surface((LARGURA, ALTURA))
    for y in range(ALTURA):
        k = y / ALTURA
        pygame.draw.line(f, (int(18 + 40 * k), int(24 + 22 * k), int(52 + 36 * k)), (0, y), (LARGURA, y))
    rnd = random.Random(3)
    for _ in range(70):
        pygame.draw.circle(f, (220, 225, 255), (rnd.randint(0, LARGURA), rnd.randint(0, 380)), rnd.choice((1, 1, 2)))
    return f


VINHETA, LUZ, NEVOA, FUNDO_TITULO = criar_vinheta(), criar_luz(), criar_nevoa(), criar_fundo_titulo()
LUZ_RAIO = 190


def textura_fundo(s):
    """Fundo com textura (grama/pedra) feita de pequenos blocos aleatórios."""
    rnd = random.Random(s["nome"])
    fundo = pygame.Surface((LARGURA, ALTURA))
    fundo.fill(s["cor"])
    for _ in range(900):
        v = rnd.randint(-14, 14)
        cor = tuple(max(0, min(255, k + v)) for k in s["cor"])
        pygame.draw.rect(fundo, cor, (rnd.randrange(LARGURA), rnd.randrange(ALTURA), rnd.randint(2, 6), rnd.randint(2, 6)))
    return fundo


FUNDOS = {nome: textura_fundo(s) for nome, s in SALAS.items()}


def desenhar_parede(p, cor):
    pygame.draw.rect(tela, cor, p)
    pygame.draw.rect(tela, tuple(int(k * 0.65) for k in cor), p, 3)


def desenhar_ambiente(s):
    amb, t = s["ambiente"], G.tick
    if amb == "vagalumes":
        for k in range(14):
            x = (k * 97 + 40 * math.sin(t * 0.012 + k)) % LARGURA
            y = (k * 53 + 30 * math.cos(t * 0.010 + k * 1.7)) % ALTURA
            b = 0.55 + 0.45 * math.sin(t * 0.05 + k)
            pygame.draw.circle(tela, (int(255 * b), int(240 * b), int(120 * b)), (int(x), int(y)), 2)
    elif amb == "poeira":
        for k in range(16):
            x = (k * 71 + t * 0.15 * (1 + k % 3)) % LARGURA
            y = (k * 37 + 20 * math.sin(t * 0.01 + k)) % ALTURA
            pygame.draw.circle(tela, (150, 150, 170), (int(x), int(y)), 1)
    elif amb == "brasas":
        for k in range(18):
            y = ALTURA - (t * 0.9 + k * 47) % ALTURA
            x = (k * 71 + 20 * math.sin(t * 0.02 + k)) % LARGURA
            pygame.draw.circle(tela, (255, 150 + (k * 13) % 80, 40), (int(x), int(y)), 2)
    elif amb == "nevoa":
        ox = int(t * 0.25) % LARGURA
        tela.blit(NEVOA, (-ox, 0))
        tela.blit(NEVOA, (LARGURA - ox, 0))


def desenhar_escuridao():
    esc = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    esc.fill((0, 0, 10, 215))
    esc.blit(LUZ, (G.jogador.centerx - LUZ_RAIO, G.jogador.centery - LUZ_RAIO), special_flags=pygame.BLEND_RGBA_MIN)
    tela.blit(esc, (0, 0))


def desenhar_espada():
    """Espada empunhada (parada) ou girando durante o ataque."""
    if "espada" not in G.inventario:
        return
    j = G.jogador
    if G.anim_ataque > 0:
        fx, fy = G.facing
        p = 1 - G.anim_ataque / 8
        ang = math.atan2(fy, fx) + (p - 0.5) * 2.2
        mao = (j.centerx + math.cos(ang) * 8, j.centery + math.sin(ang) * 8)
        centro = (mao[0] + math.cos(ang) * 23, mao[1] + math.sin(ang) * 23)
        img = pygame.transform.rotozoom(SPR["espada"], -math.degrees(ang), 1.0)
        tela.blit(img, img.get_rect(center=centro))
    else:
        img = ESPADA_REPOUSO[G.facing]
        fx, fy = G.facing
        tela.blit(img, img.get_rect(center=(j.centerx + fx * 16, j.centery + fy * 16 + 4)))


# ================================================================ DESENHO: MAPA E HUD
def conexoes(s):
    return [(VIZINHO[sd["lado"]], sd["destino"]) for sd in s["saidas"]]


def desenhar_mapa(x0, y0, cw, ch, gap, nomes=False):
    """Desenha as salas já visitadas (e as vizinhas ainda desconhecidas, como '?')."""
    def centro(pos):
        return x0 + pos[0] * (cw + gap) + cw // 2, y0 + pos[1] * (ch + gap) + ch // 2

    for nome in G.visitadas:
        s = SALAS[nome]
        for (dx, dy), dest in conexoes(s):
            if dest in SECRETAS and dest not in G.visitadas:
                continue
            a, b = centro(s["pos"]), centro(SALAS[dest]["pos"])
            pygame.draw.line(tela, (150, 150, 170), a, b, 2)
    mostrar = set(G.visitadas)
    for nome in G.visitadas:
        for _, dest in conexoes(SALAS[nome]):
            if dest not in SECRETAS or dest in G.visitadas:
                mostrar.add(dest)
    for nome in mostrar:
        s = SALAS[nome]
        px, py = s["pos"]
        r = R(x0 + px * (cw + gap), y0 + py * (ch + gap), cw, ch)
        visitada = nome in G.visitadas
        atual = nome == G.sala
        cor = (240, 200, 60) if atual else (90, 110, 150) if visitada else (50, 55, 70)
        pygame.draw.rect(tela, cor, r, border_radius=4)
        pygame.draw.rect(tela, (230, 230, 240), r, 2 if atual else 1, border_radius=4)
        if nomes:
            rot = s["nome"] if visitada else "?"
            for k, linha in enumerate(quebrar(rot, cw - 8, fonte_micro)[:3]):
                tela.blit(fonte_micro.render(linha, True, (255, 255, 255) if not atual else (20, 20, 20)),
                          (r.x + 5, r.y + 4 + k * 13))
        elif visitada and any(o["tipo"] == "santuario" for o in s["objetos"]):
            pygame.draw.circle(tela, (160, 225, 255), r.center, 2)


def desenhar_hud(s):
    painel(R(10, 8, 350, 94))
    texto(s["nome"], 26, 14)
    for i in range(G.hp_max):
        desenhar_coracao(26 + i * 22, 42, i < G.hp)
    x, y = 26, 70
    if "espada" in G.inventario:
        tela.blit(ICONE_ESPADA, (x, y + 2))
        texto(f"x{G.dano}", x + 36, y, fonte_mini)
        x += 74
    for tipo in ("chave", "fragmento1", "fragmento2", "arco", "anel"):
        if tipo in G.inventario:
            tela.blit(ICONES[tipo], (x, y))
            x += 28

    painel(R(530, 8, 262, 78))
    texto_direita(f"Moedas: {G.moedas}   Poções: {G.pocoes}", 782, 14)
    if "arco" in G.inventario or G.bombas > 0:
        texto_direita(f"Flechas: {G.flechas}   Bombas: {G.bombas}", 782, 36, fonte_mini, (225, 225, 240))
    if G.sala == "arena" and G.arena["ativa"]:
        texto_direita(f"Onda {min(G.arena['onda'], len(ARENA_ONDAS))}/{len(ARENA_ONDAS)}", 782, 58, fonte_mini, (255, 200, 120))
    else:
        ativa = next((q for q, st in G.missoes.items() if st["estado"] == "ativa"), None)
        if ativa:
            cor = (150, 255, 160) if missao_pronta(ativa) else (255, 235, 140)
            texto_direita(f"{MISSOES[ativa]['nome']} {progresso(ativa)}", 782, 58, fonte_mini, cor)

    painel(R(LARGURA - 135, ALTURA - 62, 125, 50), 110)  # minimapa
    desenhar_mapa(LARGURA - 129, ALTURA - 57, 14, 10, 3)


def desenhar_coracao(x, y, cheio):
    cor = (230, 50, 70) if cheio else (80, 45, 55)
    pygame.draw.circle(tela, cor, (x + 5, y + 5), 5)
    pygame.draw.circle(tela, cor, (x + 13, y + 5), 5)
    pygame.draw.polygon(tela, cor, [(x, y + 7), (x + 18, y + 7), (x + 9, y + 17)])


def desenhar_dialogo():
    d = G.dialogo
    nome, resto = separar_falante(d["linhas"][d["i"]])
    caixa = R(40, 440, 720, 140)
    painel(caixa, 225, (255, 255, 255))
    if nome:
        etiqueta = R(60, 424, fonte_pequena.size(nome)[0] + 24, 28)
        pygame.draw.rect(tela, (240, 200, 80), etiqueta, border_radius=6)
        tela.blit(fonte_pequena.render(nome, True, (30, 20, 10)), (etiqueta.x + 12, etiqueta.y + 3))
    restante = d["car"]
    for k, linha in enumerate(quebrar(resto, 680, fonte)):
        tela.blit(fonte.render(linha[:max(0, restante)], True, (255, 255, 255)), (60, 462 + k * 30))
        restante -= len(linha) + 1
    if d["car"] >= len(resto) and (G.tick // 20) % 2 == 0:
        texto_direita("E >>", 745, 553, fonte_pequena, (170, 170, 190))


def desenhar_jogo():
    s = SALAS[G.sala]
    tela.blit(FUNDOS[G.sala], (0, 0))
    for p in s["paredes"][:len(s["paredes"]) - len(s["obstaculos"])]:
        desenhar_parede(p, s["cor_parede"])
    for r, estilo in s["obstaculos"]:
        ART.desenhar_obstaculo(tela, r, estilo)
    for r in s["rachadas"]:
        if r["uid"] not in G.destruidas:
            ART.desenhar_obstaculo(tela, r["rect"], "rachada")
    for o in s["objetos"]:
        sombra(o["rect"])
        ART.desenhar_objeto(tela, o, G.tick, o["uid"] in G.abertos)
    for it in s["itens"]:
        if it["uid"] not in G.coletados:
            ART.desenhar_item(tela, it)
    for it in G.drops[G.sala]:
        ART.desenhar_item(tela, it)

    for n in s["npcs"]:
        sombra(n["rect"])
        tela.blit(SPR["npc_" + n["id"]], n["rect"])
        rot = fonte_pequena.render(n["nome"], True, (255, 255, 255))
        tela.blit(rot, (n["rect"].centerx - rot.get_width() // 2, n["rect"].y - 24))
    for e in G.inimigos[G.sala]:
        e.desenhar()

    for b in G.bombas_ativas:  # bombas com pavio piscando
        pygame.draw.circle(tela, (40, 40, 50), (int(b["x"]), int(b["y"])), 9)
        if (b["t"] // 6) % 2 == 0:
            pygame.draw.circle(tela, (255, 190, 60), (int(b["x"]) + 6, int(b["y"]) - 9), 3)
    for x in G.explosoes:
        raio = 85 * (1 - x["t"] / 12) + 12
        pygame.draw.circle(tela, (255, 200, 80), (int(x["x"]), int(x["y"])), int(raio), 4)
        pygame.draw.circle(tela, (255, 120, 40), (int(x["x"]), int(x["y"])), int(raio * 0.6), 3)
    for p in G.proj:
        pygame.draw.circle(tela, p["cor"], p["rect"].center, 7)
        pygame.draw.circle(tela, (255, 255, 255), p["rect"].center, 3)
    for f in G.flechas_voando:
        fx, fy = f["vx"] / 10, f["vy"] / 10
        c = f["rect"].center
        pygame.draw.line(tela, (190, 150, 90), (c[0] - fx * 12, c[1] - fy * 12), (c[0] + fx * 8, c[1] + fy * 8), 3)
        pygame.draw.circle(tela, (220, 220, 230), (c[0] + int(fx * 9), c[1] + int(fy * 9)), 3)

    j = G.jogador
    cima = G.facing == (0, -1)
    sombra(j)
    andando = G.tick % 60 < 60 and (G.dash > 0 or any(pygame.key.get_pressed()[k] for k in CIMA + BAIXO + ESQ + DIR))
    oy = int(math.sin(G.tick * 0.5) * 1.5) if andando else 0
    if cima and G.anim_ataque == 0:
        desenhar_espada()
    if not (G.invul > 0 and (G.invul // 4) % 2):  # pisca quando machucado
        tela.blit(SPR["jogador"], (j.x, j.y + oy))
    if not cima or G.anim_ataque > 0:
        desenhar_espada()

    for p in G.particulas:
        pygame.draw.circle(tela, p["cor"], (int(p["x"]), int(p["y"])), 3)
    for t in G.textos:
        tela.blit(fonte_pequena.render(t["txt"], True, t["cor"]), (t["x"] - 8, int(t["y"])))

    desenhar_ambiente(s)
    if s["escuro"]:
        desenhar_escuridao()

    rect, dica = alvo_interacao()
    if rect and not G.dialogo:
        img = fonte_pequena.render(dica, True, (255, 255, 120))
        tela.blit(img, (rect.centerx - img.get_width() // 2, rect.bottom + 6 if rect.y < 60 else rect.y - 46))

    desenhar_hud(s)

    chefe = next((e for e in G.inimigos[G.sala] if e.d.get("boss")), None)
    if chefe and not G.dialogo:
        barra = R(LARGURA // 2 - 200, 546, 400, 14)
        pygame.draw.rect(tela, (30, 10, 10), barra)
        pygame.draw.rect(tela, (200, 40, 50), (barra.x, barra.y, int(barra.w * chefe.hp / chefe.hp_max), barra.h))
        pygame.draw.rect(tela, (255, 255, 255), barra, 2)
        rot = fonte_pequena.render(chefe.d["nome"], True, (255, 255, 255))
        tela.blit(rot, (LARGURA // 2 - rot.get_width() // 2, 522))

    if G.banner:  # nome do chefe ao entrar na sala
        t = G.banner["t"]
        img = fonte_titulo.render(G.banner["texto"].upper(), True, (255, 220, 120))
        img.set_alpha(max(0, min(255, t * 6, (150 - t) * 6)))
        tela.blit(img, (LARGURA // 2 - img.get_width() // 2, 150))
    if G.aviso_tempo > 0:
        texto_centro(G.aviso, 112, fonte, (255, 255, 120))
    for i, t in enumerate(G.toasts[-3:]):  # conquistas e missões
        caixa = R(LARGURA // 2 - 200, 160 + i * 40, 400, 34)
        painel(caixa, 200, (240, 200, 80))
        img = fonte_pequena.render(t["texto"], True, (255, 235, 150))
        tela.blit(img, (caixa.centerx - img.get_width() // 2, caixa.y + 6))
    if G.dialogo:
        desenhar_dialogo()

    if G.hp <= max(1, G.hp_max // 4) and G.estado == "jogo":  # pouca vida: bordas vermelhas pulsando
        VINHETA.set_alpha(int(100 + 90 * math.sin(G.tick * 0.12)))
        tela.blit(VINHETA, (0, 0))
    if G.fade > 0:
        veu = pygame.Surface((LARGURA, ALTURA))
        veu.set_alpha(G.fade)
        tela.blit(veu, (0, 0))


# ================================================================ DESENHO: TELAS
def lista_menu(itens, y0, passo=46, largura=380):
    for i, rot in enumerate(itens):
        sel = i == G.sel
        r = R(LARGURA // 2 - largura // 2, y0 + i * passo, largura, 38)
        if sel:
            pygame.draw.rect(tela, (240, 200, 80), r, border_radius=8)
        else:
            painel(r, 120)
        img = fonte.render(rot, True, (30, 20, 10) if sel else (230, 230, 245))
        tela.blit(img, (r.centerx - img.get_width() // 2, r.y + 5))


def tela_titulo():
    tela.blit(FUNDO_TITULO, (0, 0))
    texto_centro("A Floresta de Aurora", 60, fonte_titulo, (240, 220, 120))
    flut = int(math.sin(G.tick * 0.04) * 6)
    grande = pygame.transform.rotozoom(SPR["espada"], 45, 3.6)
    tela.blit(grande, grande.get_rect(center=(LARGURA // 2, 190 + flut)))
    lista_menu(itens_titulo(), 290, 50)
    texto_centro("Setas/W S escolhem   ENTER confirma   F11 tela cheia", 560, fonte_mini, (160, 165, 190))


def tela_dificuldade():
    tela.blit(FUNDO_TITULO, (0, 0))
    texto_centro("Escolha a dificuldade", 70, fonte_titulo, (240, 220, 120))
    chaves = list(DIFICULDADES)
    lista_menu([DIFICULDADES[c]["nome"] for c in chaves], 180, 54)
    texto_centro(DIFICULDADES[chaves[G.sel]]["desc"], 380, fonte_pequena, (200, 205, 230))
    texto_centro("ESC volta", 560, fonte_mini, (160, 165, 190))


def tela_historia():
    tela.fill((10, 10, 15))
    for i, linha in enumerate(PROLOGO):
        texto_centro(linha, 130 + i * 50)
    texto_centro("ENTER para continuar", 530, fonte_pequena, (160, 160, 160))


def tela_conquistas():
    tela.blit(FUNDO_TITULO, (0, 0))
    texto_centro(f"Conquistas  {len(G.conquistas)}/{len(CONQUISTAS)}", 24, fonte_titulo, (240, 220, 120))
    for i, (cid, nome, desc) in enumerate(CONQUISTAS):
        ok = cid in G.conquistas
        y = 96 + i * 33
        pygame.draw.rect(tela, (240, 200, 80) if ok else (70, 75, 95), (60, y + 4, 18, 18), 0 if ok else 2, border_radius=3)
        if ok:
            pygame.draw.lines(tela, (30, 20, 10), False, [(64, y + 13), (68, y + 18), (75, y + 8)], 3)
        texto(nome, 92, y, fonte_pequena, (255, 240, 180) if ok else (150, 155, 175))
        texto(desc, 330, y, fonte_mini, (210, 215, 235) if ok else (115, 120, 140))
    texto_centro("ENTER ou ESC para voltar", 566, fonte_mini, (160, 165, 190))


def tela_controles():
    tela.blit(FUNDO_TITULO, (0, 0))
    texto_centro("Controles", 40, fonte_titulo, (240, 220, 120))
    linhas = [("Setas / WASD", "andar"), ("J", "atacar com a espada"), ("K", "atirar com o arco"),
              ("SHIFT (ou L)", "desvio rápido: invencível por um instante"), ("B", "colocar uma bomba"),
              ("Q", "usar poção (+2 de vida)"), ("E / ENTER / ESPAÇO", "falar, abrir baús, ler placas, descansar"),
              ("TAB", "diário de missões"), ("M", "mapa"), ("P / ESC", "pausa e menu"), ("F11", "tela cheia")]
    for i, (tecla, desc) in enumerate(linhas):
        texto(tecla, 110, 130 + i * 34, fonte, (255, 235, 140))
        texto(desc, 380, 130 + i * 34, fonte_pequena, (225, 228, 245))
    texto_centro("ENTER ou ESC para voltar", 560, fonte_mini, (160, 165, 190))


def tela_pausa():
    veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    veu.fill((0, 0, 0, 170))
    tela.blit(veu, (0, 0))
    texto_centro("PAUSA", 80, fonte_titulo, (240, 220, 120))
    lista_menu(itens_pausa(), 160, 50)
    texto_centro("Use as setas esquerda e direita para mudar o volume", 480, fonte_mini, (170, 175, 200))


def tela_loja():
    veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    veu.fill((0, 0, 0, 170))
    tela.blit(veu, (0, 0))
    caixa = R(90, 110, 620, 360)
    painel(caixa, 235, (230, 190, 90))
    texto_centro("Forja do Ferreiro Bram", 126, fonte, (255, 220, 120))
    texto_centro(f"Suas moedas: {G.moedas}", 162, fonte_pequena, (255, 235, 140))
    for i, it in enumerate(itens_loja()):
        disp = it["preco"] is not None and it["ok"]
        cor = (255, 255, 255) if disp else (130, 130, 130)
        texto(f"{i + 1})  {it['nome']}", 120, 210 + i * 44, fonte, cor)
        preco = f"{it['preco']} moedas" if it["preco"] is not None else "ESGOTADO"
        if it["preco"] is not None and not it["ok"]:
            preco = "precisa do arco"
        texto_direita(preco, 680, 214 + i * 44, fonte_pequena, (255, 215, 60) if disp else cor)
    if G.msg_loja:
        texto_centro(G.msg_loja, 432, fonte_pequena, (160, 255, 160))
    texto_centro("Teclas 1 a 5 compram   |   E para sair", 452, fonte_mini, (170, 170, 190))


def tela_diario():
    veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    veu.fill((0, 0, 0, 185))
    tela.blit(veu, (0, 0))
    texto_centro("Diário de Missões", 36, fonte_titulo, (240, 220, 120))
    if not G.missoes:
        texto_centro("Nenhuma missão ainda. Converse com os moradores!", 250, fonte_pequena, (200, 205, 230))
    y = 110
    for estado, titulo_ in (("ativa", "EM ANDAMENTO"), ("entregue", "CONCLUÍDAS")):
        lista = [q for q, st in G.missoes.items() if st["estado"] == estado]
        if not lista:
            continue
        texto(titulo_, 70, y, fonte_pequena, (160, 165, 190))
        y += 30
        for qid in lista:
            m = MISSOES[qid]
            pronta = estado == "ativa" and missao_pronta(qid)
            cor = (150, 255, 160) if pronta or estado == "entregue" else (255, 235, 140)
            texto(m["nome"], 90, y, fonte, cor)
            texto_direita("concluída" if estado == "entregue" else ("PRONTA! Entregue ao morador" if pronta else progresso(qid)), 730, y + 4, fonte_pequena, cor)
            if estado == "ativa":
                texto(m["desc"], 90, y + 28, fonte_mini, (200, 205, 225))
            y += 66 if estado == "ativa" else 36
        y += 14
    texto_centro("TAB ou ESC para voltar", 566, fonte_mini, (160, 165, 190))


def tela_mapa():
    veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    veu.fill((0, 0, 0, 205))
    tela.blit(veu, (0, 0))
    texto_centro("Mapa de Aurora", 50, fonte_titulo, (240, 220, 120))
    desenhar_mapa(50, 190, 86, 44, 14, nomes=True)
    texto_centro("Dourado: onde você está    Azul: já visitada    Cinza: ainda desconhecida", 440, fonte_mini, (190, 195, 215))
    texto_centro("M ou ESC para voltar", 566, fonte_mini, (160, 165, 190))


def tela_fim():
    tela.fill((250, 235, 170))
    texto_centro("FIM", 70, fonte_grande, (60, 40, 10))
    texto_centro("A maldição foi quebrada e Aurora voltou a brilhar!", 150, fonte, (60, 40, 10))
    seg = G.frames // 60
    concluidas = sum(1 for s in G.missoes.values() if s["estado"] == "entregue")
    linhas = [f"Dificuldade: {DIFICULDADES[G.dificuldade]['nome']}",
              f"Tempo de jogo: {seg // 60:02d}:{seg % 60:02d}",
              f"Inimigos derrotados: {sum(G.kills.values())}",
              f"Vezes que você caiu: {G.mortes}",
              f"Missões concluídas: {concluidas}/{len(MISSOES)}",
              f"Conquistas: {len(G.conquistas)}/{len(CONQUISTAS)}",
              f"Vida máxima: {G.hp_max}   Dano: {G.dano}   Moedas: {G.moedas}"]
    for i, l in enumerate(linhas):
        texto_centro(l, 220 + i * 36, fonte_pequena, (80, 60, 30))
    texto_centro("Obrigado por jogar!  Pressione ENTER para voltar ao menu.", 530, fonte_pequena, (60, 40, 10))


def desenhar():
    e = G.estado
    if e == "titulo":
        tela_titulo()
    elif e == "dificuldade":
        tela_dificuldade()
    elif e == "historia":
        tela_historia()
    elif e == "conquistas":
        tela_conquistas()
    elif e == "controles":
        tela_controles()
    elif e == "fim":
        tela_fim()
    else:  # jogo e telas sobrepostas ao jogo
        desenhar_jogo()
        if e == "pausa":
            tela_pausa()
        elif e == "loja":
            tela_loja()
        elif e == "diario":
            tela_diario()
        elif e == "mapa":
            tela_mapa()
        elif e == "gameover":
            veu = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            veu.fill((90, 0, 0, 170))
            tela.blit(veu, (0, 0))
            texto_centro("VOCÊ CAIU...", 210, fonte_grande, (255, 220, 220))
            texto_centro("ENTER para voltar ao último santuário (perde metade das moedas)", 320, fonte_pequena)


# ================================================================ LOOP PRINCIPAL
def main():
    carregar_perfil()
    novo_jogo()
    ir_para("titulo")
    tocar("menu.mp3")
    while True:
        for ev in pygame.event.get():
            tratar_evento(ev)
        if G.estado == "jogo":
            atualizar()
        G.tick += 1
        desenhar()
        ecra.fill((0, 0, 0))
        ox = oy = 0
        if G.shake > 0:  # câmera tremendo
            ox, oy = random.randint(-4, 4), random.randint(-4, 4)
            G.shake -= 1
        ecra.blit(tela, (ox, oy))
        pygame.display.flip()
        relogio.tick(60)


if __name__ == "__main__":
    main()
