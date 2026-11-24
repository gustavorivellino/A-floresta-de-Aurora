"""
SPRITES: toda a arte do jogo, desenhada por código (sem arquivos externos).

Para usar imagens suas, rode gerar_imagens.py: ele salva cada sprite como PNG em assets/.
Depois é só trocar o PNG (mesmo nome); o jogo carrega e redimensiona sozinho.
"""
import math
import os
import sys

import pygame

from src.dados import SALAS, TIPOS

# sys._MEIPASS existe quando o jogo roda como .exe (PyInstaller); senão, usa a pasta deste arquivo
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
PASTA_ASSETS = os.path.join(BASE, "assets")

R = pygame.Rect


def imagem(nome, padrao):
    """Usa assets/<nome>.png se existir; senão, o desenho padrão."""
    caminho = os.path.join(PASTA_ASSETS, nome + ".png")
    if os.path.exists(caminho):
        try:
            img = pygame.image.load(caminho).convert_alpha()
            if img.get_size() != padrao.get_size():
                img = pygame.transform.smoothscale(img, padrao.get_size())
            return img
        except pygame.error:
            pass
    return padrao


# ================================================================ PERSONAGENS
def sprite_espada():
    """Espada apontando para a direita (46x18): lâmina, guarda dourada, cabo e pomo."""
    s = pygame.Surface((46, 18), pygame.SRCALPHA)
    pygame.draw.polygon(s, (215, 225, 240), [(14, 5), (40, 5), (46, 9), (40, 13), (14, 13)])
    pygame.draw.polygon(s, (140, 155, 180), [(14, 10), (40, 10), (46, 9), (40, 13), (14, 13)])
    pygame.draw.line(s, (255, 255, 255), (16, 7), (39, 7), 1)
    pygame.draw.polygon(s, (60, 70, 100), [(14, 5), (40, 5), (46, 9), (40, 13), (14, 13)], 1)
    pygame.draw.rect(s, (235, 195, 60), (10, 1, 5, 16), border_radius=2)
    pygame.draw.rect(s, (150, 110, 30), (10, 1, 5, 16), 1, border_radius=2)
    pygame.draw.rect(s, (120, 70, 40), (3, 7, 8, 4), border_radius=2)
    pygame.draw.circle(s, (235, 195, 60), (3, 9), 3)
    return s


def sprite_pessoa(cor_roupa, cor_cabelo, tamanho):
    w, h = tamanho
    s = pygame.Surface(tamanho, pygame.SRCALPHA)
    pygame.draw.rect(s, cor_roupa, (3, 12, w - 6, h - 12), border_radius=5)   # corpo
    pygame.draw.circle(s, (240, 200, 160), (w // 2, 9), 8)                     # cabeça
    pygame.draw.rect(s, cor_cabelo, (w // 2 - 8, 1, 16, 7), border_radius=4)   # cabelo
    pygame.draw.circle(s, (30, 30, 30), (w // 2 - 3, 10), 1)                   # olhos
    pygame.draw.circle(s, (30, 30, 30), (w // 2 + 3, 10), 1)
    return s


def sprite_inimigo(tipo):
    w = TIPOS[tipo]["tam"]
    c = w // 2
    s = pygame.Surface((w, w), pygame.SRCALPHA)
    if tipo in ("slime", "slime_gigante"):
        base, claro = ((80, 200, 90), (130, 235, 140)) if tipo == "slime" else ((50, 160, 80), (100, 210, 120))
        pygame.draw.ellipse(s, base, (0, w // 3, w, w * 2 // 3))
        pygame.draw.ellipse(s, claro, (w // 5, w // 3 + 2, w // 4, w // 6))
        pygame.draw.circle(s, (20, 40, 20), (int(w * .35), int(w * .62)), 2 if tipo == "slime" else 3)
        pygame.draw.circle(s, (20, 40, 20), (int(w * .68), int(w * .62)), 2 if tipo == "slime" else 3)
        if tipo == "slime_gigante":
            pygame.draw.polygon(s, (240, 200, 60), [(c - 9, w // 3 + 2), (c - 9, w // 3 - 8), (c - 4, w // 3 - 2),
                                                    (c, w // 3 - 9), (c + 4, w // 3 - 2), (c + 9, w // 3 - 8),
                                                    (c + 9, w // 3 + 2)])
    elif tipo == "morcego":
        pygame.draw.polygon(s, (90, 50, 130), [(0, 2), (c, c), (2, w - 5)])
        pygame.draw.polygon(s, (90, 50, 130), [(w, 2), (c, c), (w - 2, w - 5)])
        pygame.draw.ellipse(s, (60, 30, 90), (c - 5, 4, 10, w - 8))
        pygame.draw.circle(s, (255, 80, 80), (c - 2, 9), 1)
        pygame.draw.circle(s, (255, 80, 80), (c + 2, 9), 1)
    elif tipo == "esqueleto":
        pygame.draw.rect(s, (225, 225, 210), (c - 6, 14, 12, 10), border_radius=2)
        for k in range(3):
            pygame.draw.line(s, (90, 90, 80), (c - 5, 16 + k * 3), (c + 5, 16 + k * 3), 1)
        pygame.draw.rect(s, (225, 225, 210), (c - 5, 23, 3, 5))
        pygame.draw.rect(s, (225, 225, 210), (c + 2, 23, 3, 5))
        pygame.draw.circle(s, (240, 240, 228), (c, 8), 8)
        pygame.draw.circle(s, (20, 20, 20), (c - 3, 8), 2)
        pygame.draw.circle(s, (20, 20, 20), (c + 3, 8), 2)
        pygame.draw.rect(s, (20, 20, 20), (c - 2, 12, 4, 2))
    elif tipo == "sapo":
        pygame.draw.ellipse(s, (110, 190, 70), (0, 8, w, w - 10))
        pygame.draw.circle(s, (130, 215, 90), (6, 8), 5)
        pygame.draw.circle(s, (130, 215, 90), (w - 6, 8), 5)
        pygame.draw.circle(s, (20, 30, 10), (6, 8), 2)
        pygame.draw.circle(s, (20, 30, 10), (w - 6, 8), 2)
        pygame.draw.arc(s, (50, 90, 30), (5, 12, w - 10, 10), 3.4, 6.0, 2)
    elif tipo == "fantasma":
        cor = (225, 232, 255, 190)
        pygame.draw.circle(s, cor, (c, c - 2), c - 2)
        pygame.draw.rect(s, cor, (2, c - 2, w - 4, c - 2))
        for k in range(3):
            pygame.draw.circle(s, (0, 0, 0, 0), (6 + k * 8, w - 2), 4)
        pygame.draw.circle(s, (30, 30, 60), (c - 5, c - 4), 3)
        pygame.draw.circle(s, (30, 30, 60), (c + 5, c - 4), 3)
    elif tipo == "javali":
        pygame.draw.ellipse(s, (160, 105, 70), (0, 8, w, w - 10))
        pygame.draw.polygon(s, (120, 75, 50), [(4, 12), (7, 2), (12, 11)])
        pygame.draw.polygon(s, (120, 75, 50), [(w - 4, 12), (w - 7, 2), (w - 12, 11)])
        pygame.draw.ellipse(s, (205, 155, 145), (c - 7, w - 15, 14, 10))
        pygame.draw.polygon(s, (245, 245, 235), [(c - 11, w - 10), (c - 8, w - 3), (c - 6, w - 10)])
        pygame.draw.polygon(s, (245, 245, 235), [(c + 11, w - 10), (c + 8, w - 3), (c + 6, w - 10)])
        pygame.draw.circle(s, (255, 60, 60), (c - 6, 15), 2)
        pygame.draw.circle(s, (255, 60, 60), (c + 6, 15), 2)
    elif tipo == "aranha":
        for k in range(4):
            y = 5 + k * 5
            pygame.draw.line(s, (60, 30, 80), (c, c), (0, y), 2)
            pygame.draw.line(s, (60, 30, 80), (c, c), (w - 1, y), 2)
        pygame.draw.circle(s, (130, 70, 150), (c, c + 1), 7)
        pygame.draw.circle(s, (160, 100, 180), (c, c - 6), 4)
        pygame.draw.circle(s, (255, 70, 70), (c - 2, c - 7), 1)
        pygame.draw.circle(s, (255, 70, 70), (c + 2, c - 7), 1)
    elif tipo == "planta":
        pygame.draw.rect(s, (50, 130, 50), (c - 3, c, 6, c))
        pygame.draw.polygon(s, (60, 160, 60), [(c, w - 6), (2, w - 12), (6, w - 2)])
        pygame.draw.polygon(s, (60, 160, 60), [(c, w - 6), (w - 2, w - 12), (w - 6, w - 2)])
        pygame.draw.circle(s, (200, 60, 90), (c, c - 3), 11)
        pygame.draw.circle(s, (60, 10, 20), (c, c - 1), 7)
        for k in range(4):
            x = c - 6 + k * 4
            pygame.draw.polygon(s, (250, 250, 240), [(x, c - 7), (x + 3, c - 7), (x + 1, c - 2)])
    elif tipo == "mago":
        pygame.draw.polygon(s, (90, 50, 140), [(c, 10), (2, w), (w - 2, w)])
        pygame.draw.circle(s, (240, 200, 160), (c, 10), 6)
        pygame.draw.polygon(s, (60, 30, 100), [(c - 9, 9), (c + 9, 9), (c, 0)])
        pygame.draw.circle(s, (30, 30, 30), (c - 2, 11), 1)
        pygame.draw.circle(s, (30, 30, 30), (c + 2, 11), 1)
        pygame.draw.line(s, (130, 90, 50), (w - 4, 6), (w - 4, w - 1), 2)
        pygame.draw.circle(s, (190, 140, 255), (w - 4, 5), 3)
    elif tipo == "cavaleiro":
        pygame.draw.rect(s, (150, 150, 170), (4, 12, w - 8, w - 12), border_radius=4)
        pygame.draw.rect(s, (110, 110, 130), (4, 12, w - 8, w - 12), 2, border_radius=4)
        pygame.draw.circle(s, (175, 175, 195), (c, 9), 9)
        pygame.draw.rect(s, (30, 30, 40), (c - 6, 7, 12, 3))
        pygame.draw.polygon(s, (200, 50, 50), [(c, 0), (c + 8, 4), (c, 5)])
        pygame.draw.rect(s, (90, 60, 140), (w - 9, 14, 7, 12), border_radius=2)
    elif tipo == "lobo":
        pygame.draw.ellipse(s, (70, 70, 90), (0, w // 4, w, w * 3 // 4))
        pygame.draw.polygon(s, (70, 70, 90), [(4, w // 4 + 4), (10, 0), (18, w // 4 + 4)])
        pygame.draw.polygon(s, (70, 70, 90), [(w - 18, w // 4 + 4), (w - 10, 0), (w - 4, w // 4 + 4)])
        pygame.draw.circle(s, (255, 60, 60), (int(w * .32), int(w * .5)), 3)
        pygame.draw.circle(s, (255, 60, 60), (int(w * .68), int(w * .5)), 3)
        pygame.draw.polygon(s, (240, 240, 240), [(c - 6, w * 3 // 4), (c - 3, w - 6), (c, w * 3 // 4)])
        pygame.draw.polygon(s, (240, 240, 240), [(c, w * 3 // 4), (c + 3, w - 6), (c + 6, w * 3 // 4)])
    elif tipo == "golem":
        pygame.draw.rect(s, (125, 118, 112), (10, 22, w - 20, w - 24), border_radius=8)
        pygame.draw.rect(s, (125, 118, 112), (0, 26, 16, 30), border_radius=6)
        pygame.draw.rect(s, (125, 118, 112), (w - 16, 26, 16, 30), border_radius=6)
        pygame.draw.rect(s, (140, 132, 126), (24, 2, w - 48, 26), border_radius=6)
        pygame.draw.rect(s, (255, 210, 70), (30, 11, 6, 5))
        pygame.draw.rect(s, (255, 210, 70), (w - 36, 11, 6, 5))
        pygame.draw.line(s, (80, 75, 70), (24, 38), (34, 50), 2)
        pygame.draw.line(s, (80, 75, 70), (w - 24, 44), (w - 34, 58), 2)
        pygame.draw.rect(s, (70, 65, 62), (10, 22, w - 20, w - 24), 3, border_radius=8)
    elif tipo == "serpente":
        pygame.draw.ellipse(s, (40, 140, 60), (2, 24, w - 4, w - 26))
        pygame.draw.ellipse(s, (70, 180, 90), (12, 32, w - 24, w - 42))
        pygame.draw.ellipse(s, (50, 160, 70), (w - 30, 2, 28, 24))
        pygame.draw.circle(s, (255, 230, 60), (w - 20, 10), 3)
        pygame.draw.circle(s, (255, 230, 60), (w - 10, 10), 3)
        pygame.draw.line(s, (230, 50, 60), (w - 3, 17), (w, 22), 2)
    elif tipo == "rainha":
        for k in range(4):
            y = 14 + k * 9
            pygame.draw.line(s, (70, 30, 90), (c, c + 4), (1, y), 3)
            pygame.draw.line(s, (70, 30, 90), (c, c + 4), (w - 2, y), 3)
        pygame.draw.ellipse(s, (100, 45, 120), (c - 18, c - 4, 36, 32))
        pygame.draw.ellipse(s, (140, 80, 160), (c - 10, c + 4, 20, 16))
        pygame.draw.circle(s, (130, 70, 150), (c, c - 12), 11)
        pygame.draw.polygon(s, (240, 200, 60), [(c - 10, c - 20), (c - 10, c - 30), (c - 5, c - 24), (c, c - 31),
                                                (c + 5, c - 24), (c + 10, c - 30), (c + 10, c - 20)])
        for dx in (-5, 5):
            pygame.draw.circle(s, (255, 60, 60), (c + dx, c - 13), 2)
        for dx in (-9, 9):
            pygame.draw.circle(s, (255, 60, 60), (c + dx, c - 10), 1)
    elif tipo == "rei":
        cx, cy = c, w // 3
        pygame.draw.rect(s, (60, 20, 70), (6, cy, w - 12, w - cy), border_radius=8)
        pygame.draw.rect(s, (120, 50, 130), (6, cy, w - 12, w - cy), 3, border_radius=8)
        pygame.draw.circle(s, (205, 195, 215), (cx, cy), 14)
        pygame.draw.polygon(s, (240, 200, 60), [
            (cx - 14, cy - 10), (cx - 14, cy - 24), (cx - 7, cy - 16), (cx, cy - 26),
            (cx + 7, cy - 16), (cx + 14, cy - 24), (cx + 14, cy - 10)])
        pygame.draw.circle(s, (230, 40, 40), (cx - 6, cy), 2)
        pygame.draw.circle(s, (230, 40, 40), (cx + 6, cy), 2)
    return s


# todos os sprites do jogo, por nome (gerar_imagens.py salva cada um como PNG)
PADROES = {"jogador": sprite_pessoa((60, 110, 220), (90, 50, 20), (28, 28)),
           "espada": sprite_espada()}
for _s in SALAS.values():
    for _n in _s["npcs"]:
        PADROES["npc_" + _n["id"]] = sprite_pessoa(_n["roupa"], _n["cabelo"], (30, 30))
for _t in TIPOS:
    PADROES["inimigo_" + _t] = sprite_inimigo(_t)


def carregar_sprites():
    """Carrega os PNG de assets/ (se existirem) ou usa os desenhos padrão. Precisa da janela aberta."""
    return {nome: imagem(nome, surf) for nome, surf in PADROES.items()}


# ================================================================ ITENS
COR_ITEM = {"chave": (240, 200, 40), "cristal": (120, 230, 255), "pocao": (220, 50, 70),
            "amuleto": (240, 190, 50), "moeda": (255, 215, 60), "coracao": (255, 100, 140),
            "fragmento1": (255, 150, 60), "fragmento2": (100, 230, 120), "arco": (160, 110, 60),
            "flecha": (170, 130, 80), "bomba": (50, 50, 60), "anel": (240, 200, 60),
            "broche": (255, 140, 190), "espada": (215, 225, 240)}


def desenhar_item(s, it):
    """Desenha um item (it['id'] e it['rect']) na superfície s."""
    r, tipo = it["rect"], it["id"]
    cor = COR_ITEM.get(tipo, (255, 255, 255))
    if tipo == "cristal":
        pts = [r.midtop, r.midright, r.midbottom, r.midleft]
        pygame.draw.polygon(s, cor, pts)
        pygame.draw.polygon(s, (255, 255, 255), pts, 2)
    elif tipo in ("fragmento1", "fragmento2"):
        pts = [(r.centerx, r.y), (r.right - 3, r.centery - 2), (r.centerx + 4, r.bottom), (r.x + 3, r.centery + 3)]
        pygame.draw.polygon(s, cor, pts)
        pygame.draw.polygon(s, (255, 255, 255), pts, 2)
    elif tipo == "chave":
        pygame.draw.circle(s, cor, (r.x + 7, r.centery), 7)
        pygame.draw.circle(s, (60, 50, 10), (r.x + 7, r.centery), 3)
        pygame.draw.rect(s, cor, (r.x + 12, r.centery - 2, 10, 4))
        pygame.draw.rect(s, cor, (r.x + 18, r.centery, 3, 6))
    elif tipo == "pocao":
        pygame.draw.circle(s, cor, (r.centerx, r.centery + 3), 8)
        pygame.draw.rect(s, (200, 200, 210), (r.centerx - 3, r.y, 6, 8))
        pygame.draw.circle(s, (255, 190, 200), (r.centerx - 3, r.centery), 2)
    elif tipo == "moeda":
        pygame.draw.circle(s, cor, r.center, 8)
        pygame.draw.circle(s, (200, 150, 20), r.center, 8, 2)
        pygame.draw.line(s, (200, 150, 20), (r.centerx, r.centery - 4), (r.centerx, r.centery + 4), 2)
    elif tipo == "coracao":
        x, y = r.x + 2, r.y + 3
        pygame.draw.circle(s, cor, (x + 5, y + 5), 5)
        pygame.draw.circle(s, cor, (x + 13, y + 5), 5)
        pygame.draw.polygon(s, cor, [(x, y + 7), (x + 18, y + 7), (x + 9, y + 17)])
    elif tipo == "arco":
        pygame.draw.arc(s, cor, (r.x + 4, r.y + 1, 14, 20), math.pi / 2, 3 * math.pi / 2, 3)
        pygame.draw.line(s, (230, 230, 220), (r.x + 11, r.y + 2), (r.x + 11, r.y + 20), 1)
        pygame.draw.line(s, (200, 200, 190), (r.x + 4, r.centery), (r.right - 2, r.centery), 2)
    elif tipo == "flecha":
        pygame.draw.line(s, cor, (r.x + 3, r.bottom - 3), (r.right - 4, r.y + 4), 3)
        pygame.draw.polygon(s, (190, 190, 200), [(r.right - 1, r.y + 1), (r.right - 8, r.y + 3), (r.right - 3, r.y + 8)])
        pygame.draw.line(s, (220, 60, 60), (r.x + 3, r.bottom - 3), (r.x + 7, r.bottom - 9), 2)
    elif tipo == "bomba":
        pygame.draw.circle(s, cor, (r.centerx, r.centery + 2), 8)
        pygame.draw.circle(s, (110, 110, 125), (r.centerx - 3, r.centery - 1), 2)
        pygame.draw.line(s, (200, 170, 100), (r.centerx + 3, r.centery - 6), (r.centerx + 7, r.y + 2), 2)
        pygame.draw.circle(s, (255, 180, 50), (r.centerx + 7, r.y + 2), 2)
    elif tipo == "anel":
        pygame.draw.circle(s, cor, (r.centerx, r.centery + 2), 8, 3)
        pygame.draw.circle(s, (80, 160, 255), (r.centerx, r.centery - 6), 3)
    elif tipo == "broche":
        pygame.draw.circle(s, cor, r.center, 9)
        pygame.draw.circle(s, (240, 200, 60), r.center, 9, 2)
        pygame.draw.circle(s, (255, 240, 250), r.center, 3)
    elif tipo == "espada":
        img = pygame.transform.rotozoom(PADROES["espada"], 45, 0.6)
        s.blit(img, img.get_rect(center=r.center))
    else:  # amuleto
        pygame.draw.circle(s, cor, r.center, 10, 3)
        pygame.draw.circle(s, (80, 160, 255), r.center, 4)


def icone(tipo):
    sup = pygame.Surface((24, 24), pygame.SRCALPHA)
    desenhar_item(sup, {"id": tipo, "rect": R(1, 1, 22, 22)})
    return sup


# ================================================================ CENÁRIO
def desenhar_obstaculo(s, r, estilo):
    if estilo == "arvore":
        pygame.draw.rect(s, (80, 50, 30), (r.centerx - 6, r.centery, 12, r.h // 2))
        pygame.draw.circle(s, (25, 90, 40), (r.centerx, r.centery - 4), r.w // 2)
        pygame.draw.circle(s, (40, 130, 60), (r.centerx - 6, r.centery - 10), r.w // 4)
    elif estilo == "pedra":
        pygame.draw.rect(s, (95, 95, 110), r, border_radius=10)
        pygame.draw.rect(s, (130, 130, 145), (r.x + 6, r.y + 6, r.w // 2, r.h // 4), border_radius=6)
        pygame.draw.rect(s, (60, 60, 72), r, 3, border_radius=10)
    elif estilo == "rachada":
        pygame.draw.rect(s, (115, 105, 100), r, border_radius=6)
        pygame.draw.rect(s, (70, 62, 58), r, 3, border_radius=6)
        pts = [(r.x + 12, r.y + 4), (r.x + 22, r.centery - 2), (r.x + 16, r.centery + 6), (r.x + 30, r.bottom - 4)]
        pygame.draw.lines(s, (35, 30, 28), False, pts, 2)
        pts2 = [(r.right - 14, r.y + 4), (r.right - 26, r.centery), (r.right - 18, r.bottom - 5)]
        pygame.draw.lines(s, (35, 30, 28), False, pts2, 2)
    elif estilo == "casa":
        pygame.draw.rect(s, (170, 140, 100), r)
        pygame.draw.polygon(s, (170, 60, 50), [(r.x - 8, r.y + r.h // 3), (r.centerx, r.y - 16),
                                               (r.right + 8, r.y + r.h // 3)])
        pygame.draw.rect(s, (90, 60, 35), (r.centerx - 10, r.bottom - 30, 20, 30))
        pygame.draw.rect(s, (110, 80, 50), r, 3)
    elif estilo == "agua":
        pygame.draw.rect(s, (40, 90, 110), r, border_radius=18)
        pygame.draw.rect(s, (70, 130, 150), (r.x + 10, r.y + 10, r.w // 3, 4), border_radius=2)
        pygame.draw.rect(s, (25, 60, 80), r, 3, border_radius=18)
    elif estilo == "tronco":
        pygame.draw.rect(s, (70, 50, 35), r, border_radius=8)
        pygame.draw.circle(s, (110, 80, 50), r.center, r.w // 3)
        pygame.draw.circle(s, (70, 50, 35), r.center, r.w // 3, 2)
    elif estilo == "pilar":
        pygame.draw.rect(s, (120, 110, 130), r)
        pygame.draw.rect(s, (165, 155, 175), (r.x, r.y, r.w, 8))
        pygame.draw.rect(s, (80, 72, 90), r, 3)


def desenhar_objeto(s, obj, tick, aberto=False):
    """Baús, placas e santuários."""
    r, tipo = obj["rect"], obj["tipo"]
    if tipo == "bau":
        pygame.draw.rect(s, (130, 85, 45), (r.x, r.y + 10, r.w, r.h - 10), border_radius=3)
        pygame.draw.rect(s, (80, 50, 25), (r.x, r.y + 10, r.w, r.h - 10), 2, border_radius=3)
        if aberto:
            pygame.draw.rect(s, (255, 215, 80), (r.x + 4, r.y + 10, r.w - 8, 5))
            pygame.draw.polygon(s, (150, 100, 55), [(r.x, r.y + 10), (r.x + 4, r.y - 4), (r.right - 4, r.y - 4), (r.right, r.y + 10)])
        else:
            pygame.draw.rect(s, (150, 100, 55), (r.x, r.y + 2, r.w, 12), border_radius=6)
            pygame.draw.rect(s, (80, 50, 25), (r.x, r.y + 2, r.w, 12), 2, border_radius=6)
            pygame.draw.rect(s, (240, 200, 60), (r.centerx - 3, r.y + 9, 6, 8), border_radius=1)
    elif tipo == "placa":
        pygame.draw.rect(s, (100, 70, 40), (r.centerx - 3, r.y + 10, 6, 18))
        pygame.draw.rect(s, (190, 150, 95), (r.x, r.y, r.w, 17), border_radius=3)
        pygame.draw.rect(s, (110, 80, 45), (r.x, r.y, r.w, 17), 2, border_radius=3)
        for k in range(2):
            pygame.draw.line(s, (90, 60, 35), (r.x + 5, r.y + 5 + k * 5), (r.right - 5, r.y + 5 + k * 5), 1)
    elif tipo == "santuario":
        pulso = int(3 * math.sin(tick * 0.08))
        halo = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(halo, (120, 200, 255, 55), (35, 35), 24 + pulso)
        pygame.draw.circle(halo, (160, 225, 255, 70), (35, 35), 15 + pulso // 2)
        s.blit(halo, (r.centerx - 35, r.centery - 41))
        pygame.draw.rect(s, (105, 105, 120), (r.x + 4, r.y + 22, r.w - 8, 14), border_radius=3)
        pygame.draw.rect(s, (70, 70, 85), (r.x + 4, r.y + 22, r.w - 8, 14), 2, border_radius=3)
        pts = [(r.centerx, r.y - 2), (r.centerx + 9, r.y + 12), (r.centerx, r.y + 24), (r.centerx - 9, r.y + 12)]
        pygame.draw.polygon(s, (130, 215, 255), pts)
        pygame.draw.polygon(s, (230, 250, 255), pts, 2)
