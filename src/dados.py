"""
DADOS DO JOGO: todo o conteúdo (salas, inimigos, missões, conquistas e textos).

Para criar uma sala, um inimigo ou uma missão nova, mexa aqui.
A lógica (movimento, combate, menus...) fica em main.py.
"""
import pygame

R = pygame.Rect
LARGURA, ALTURA = 800, 600


# ================================================================ FERRAMENTAS PARA MONTAR SALAS
def moldura(lados):
    """Paredes das bordas; os lados em 'lados' (N, S, E, O) ganham uma passagem."""
    p = []
    p += [R(0, 0, 350, 20), R(450, 0, 350, 20)] if "N" in lados else [R(0, 0, 800, 20)]
    p += [R(0, 580, 350, 20), R(450, 580, 350, 20)] if "S" in lados else [R(0, 580, 800, 20)]
    p += [R(0, 0, 20, 250), R(0, 350, 20, 250)] if "O" in lados else [R(0, 0, 20, 600)]
    p += [R(780, 0, 20, 250), R(780, 350, 20, 250)] if "E" in lados else [R(780, 0, 20, 600)]
    return p


RECT_SAIDA = {"E": (785, 250, 40, 100), "O": (-25, 250, 40, 100),
              "N": (350, -25, 100, 40), "S": (350, 585, 100, 40)}
CHEGADA = {"E": (40, 300), "O": (730, 300), "N": (385, 525), "S": (385, 40)}  # onde você aparece
VIZINHO = {"E": (1, 0), "O": (-1, 0), "N": (0, -1), "S": (0, 1)}              # direção no mapa


def saida(lado, destino, requer=None, msg=None):
    return {"lado": lado, "rect": R(*RECT_SAIDA[lado]), "destino": destino,
            "spawn": CHEGADA[lado], "requer": requer, "msg": msg}


def item(uid, tipo, nome, x, y):
    return {"uid": uid, "id": tipo, "nome": nome, "rect": R(x, y, 22, 22)}


def npc(id_, nome, x, y, roupa, cabelo):
    return {"id": id_, "nome": nome, "rect": R(x, y, 30, 30), "roupa": roupa, "cabelo": cabelo}


def bau(uid, x, y, conteudo):
    """Baú: conteudo = lista de (tipo_do_item, quantidade)."""
    return {"tipo": "bau", "uid": uid, "rect": R(x, y, 34, 28), "conteudo": conteudo}


def placa(x, y, texto):
    return {"tipo": "placa", "uid": None, "rect": R(x, y, 28, 28), "texto": texto}


def santuario(uid, x, y):
    """Santuário: descansa (cura tudo), salva o jogo e vira seu ponto de retorno."""
    return {"tipo": "santuario", "uid": uid, "rect": R(x, y, 36, 36)}


def sala(nome, pos, cor, cor_parede, musica, lados, obstaculos=(), rachadas=(), npcs=(), itens=(),
         objetos=(), inimigos=(), saidas=(), intro=None, ambiente=None, escuro=False):
    return {"nome": nome, "pos": pos, "cor": cor, "cor_parede": cor_parede, "musica": musica,
            "paredes": moldura(lados) + [o[0] for o in obstaculos], "obstaculos": list(obstaculos),
            "rachadas": [{"uid": u, "rect": r} for u, r in rachadas],
            "npcs": list(npcs), "itens": list(itens), "objetos": list(objetos),
            "inimigos": list(inimigos), "saidas": list(saidas), "intro": intro,
            "ambiente": ambiente, "escuro": escuro}


# ================================================================ SALAS (12)
SALAS = {
    # ------------------------------------------------------------ VILA (ponto central)
    "vila": sala("Vila de Aurora", (0, 1), (95, 160, 85), (120, 80, 50), "vila.mp3", "EN",
                 obstaculos=[(R(100, 100, 160, 120), "casa"), (R(550, 420, 120, 100), "casa"),
                             (R(330, 230, 60, 60), "pedra")],
                 npcs=[npc("luna", "Anciã Luna", 450, 280, (150, 90, 200), (230, 230, 230)),
                       npc("ferreiro", "Ferreiro Bram", 330, 470, (170, 90, 60), (60, 40, 30))],
                 itens=[item("p_vila", "pocao", "Poção", 650, 120)],
                 objetos=[santuario("s_vila", 250, 340),
                          placa(150, 320, ["Placa: Setas/WASD andam, J ataca, SHIFT desvia, E conversa.",
                                           "Placa: TAB abre as missões e M mostra o mapa. "
                                           "Descanse nos santuários para salvar.",
                                           "Placa: A floresta fica a leste. A Arena de Aurora, ao norte."])],
                 saidas=[saida("E", "floresta1"), saida("N", "arena")],
                 ambiente="vagalumes"),

    "arena": sala("Arena de Aurora", (0, 0), (120, 100, 80), (90, 70, 50), "chefe.mp3", "S",
                  obstaculos=[(R(200, 200, 50, 50), "pilar"), (R(550, 200, 50, 50), "pilar"),
                              (R(200, 380, 50, 50), "pilar"), (R(550, 380, 50, 50), "pilar")],
                  npcs=[npc("mestre", "Mestre da Arena", 385, 90, (200, 60, 60), (40, 30, 30))],
                  itens=[item("p_arena", "pocao", "Poção", 60, 520)],
                  saidas=[saida("S", "vila")],
                  intro=["Arena de Aurora",
                         "Fale com o Mestre da Arena para começar o desafio das 5 ondas!"]),

    # ------------------------------------------------------------ FASE 1: FLORESTA
    "floresta1": sala("Floresta Sussurrante", (1, 1), (40, 110, 60), (20, 70, 30), "floresta.mp3", "OEN",
                      obstaculos=[(R(150, 100, 60, 60), "arvore"), (R(320, 420, 60, 60), "arvore"),
                                  (R(550, 120, 60, 60), "arvore"), (R(620, 430, 60, 60), "arvore"),
                                  (R(200, 400, 60, 60), "arvore"), (R(480, 260, 60, 60), "arvore")],
                      rachadas=[("rocha_f1", R(350, 20, 100, 40))],
                      npcs=[npc("eremita", "Eremita", 90, 150, (110, 80, 50), (200, 200, 200))],
                      itens=[item("p_floresta", "pocao", "Poção", 90, 500)],
                      objetos=[bau("bau_f1", 700, 520, [("moeda", 15)]),
                               placa(300, 160, ["Placa: Dizem que há uma gruta escondida ao norte...",
                                                "Placa: A entrada está tapada por pedras rachadas. "
                                                "Uma bomba resolveria (B)."])],
                      inimigos=[("slime", 260, 220), ("slime", 520, 340), ("slime", 380, 500),
                                ("slime_gigante", 680, 200), ("javali", 480, 470)],
                      saidas=[saida("O", "vila"), saida("E", "floresta2"), saida("N", "gruta")],
                      intro=["FASE 1 - Floresta Sussurrante",
                             "Slimes rondam as trilhas. Ataque com J e pegue as moedas que eles soltam."],
                      ambiente="vagalumes"),
    "gruta": sala("Gruta Secreta", (1, 0), (45, 50, 45), (70, 80, 70), "caverna.mp3", "S",
                  obstaculos=[(R(250, 200, 60, 60), "pedra"), (R(490, 200, 60, 60), "pedra")],
                  objetos=[bau("bau_arco", 385, 150, [("arco", 1), ("flecha", 12)])],
                  inimigos=[("slime_gigante", 200, 350), ("slime_gigante", 560, 350)],
                  saidas=[saida("S", "floresta1")],
                  intro=["Você encontrou uma gruta secreta!",
                         "Um baú brilha no fundo... mas ele não está sozinho."],
                  escuro=True),
    "floresta2": sala("Clareira do Lobo", (2, 1), (35, 100, 55), (20, 70, 30), "chefe.mp3", "OE",
                      obstaculos=[(R(200, 120, 60, 60), "arvore"), (R(200, 420, 60, 60), "arvore"),
                                  (R(380, 260, 60, 60), "arvore"), (R(560, 120, 60, 60), "arvore"),
                                  (R(560, 420, 60, 60), "arvore")],
                      itens=[item("c_floresta", "coracao", "Coração de Vida", 730, 530)],
                      objetos=[santuario("s_floresta", 70, 420)],
                      inimigos=[("slime", 300, 200), ("javali", 450, 470), ("lobo", 650, 200)],
                      saidas=[saida("O", "floresta1"),
                              saida("E", "caverna1", "chave",
                                    "A porta está trancada. O Lobo Sombrio guarda a chave.")],
                      intro=["Um rosnado ecoa entre as árvores...",
                             "O Lobo Sombrio guarda a chave da caverna!"],
                      ambiente="vagalumes"),

    # ------------------------------------------------------------ FASE 2: CAVERNA
    "caverna1": sala("Caverna Cristalina", (3, 1), (45, 45, 60), (80, 80, 95), "caverna.mp3", "OEN",
                     obstaculos=[(R(250, 100, 80, 80), "pedra"), (R(250, 420, 80, 80), "pedra"),
                                 (R(450, 190, 60, 60), "pedra"), (R(450, 360, 60, 60), "pedra")],
                     npcs=[npc("espirito", "Espírito", 120, 200, (120, 200, 230), (200, 240, 255))],
                     itens=[item("p_caverna", "pocao", "Poção", 110, 100),
                            item("amuleto", "amuleto", "Amuleto da Vida", 700, 510)],
                     objetos=[santuario("s_caverna", 150, 440),
                              placa(330, 200, ["Placa: Ao norte fica o Ninho das Aranhas.",
                                               "Placa: Perigo! Leve poções e muita coragem."])],
                     inimigos=[("morcego", 400, 120), ("morcego", 600, 450), ("morcego", 350, 300),
                               ("esqueleto", 620, 200), ("esqueleto", 600, 340)],
                     saidas=[saida("O", "floresta2"), saida("E", "caverna2"), saida("N", "ninho")],
                     intro=["FASE 2 - Caverna Cristalina",
                            "A caverna é escura. Você só enxerga ao redor de si, e ouve asas e ossos rangendo..."],
                     ambiente="poeira", escuro=True),
    "ninho": sala("Ninho das Aranhas", (3, 0), (50, 35, 55), (90, 60, 100), "chefe.mp3", "S",
                  obstaculos=[(R(200, 220, 50, 50), "pilar"), (R(550, 220, 50, 50), "pilar")],
                  itens=[item("p_ninho", "pocao", "Poção", 60, 520)],
                  objetos=[bau("bau_ninho", 700, 70, [("moeda", 25), ("bomba", 3)])],
                  inimigos=[("aranha", 250, 380), ("aranha", 520, 380), ("aranha", 385, 300),
                            ("rainha", 360, 90)],
                  saidas=[saida("S", "caverna1")],
                  intro=["Ninho das Aranhas", "Teias cobrem tudo... Algo enorme espreita no escuro."],
                  escuro=True),
    "caverna2": sala("Salão do Golem", (4, 1), (50, 45, 55), (90, 85, 100), "chefe.mp3", "OS",
                     obstaculos=[(R(250, 150, 60, 60), "pedra"), (R(250, 390, 60, 60), "pedra"),
                                 (R(540, 150, 60, 60), "pedra"), (R(540, 390, 60, 60), "pedra")],
                     itens=[item("p_caverna2", "pocao", "Poção", 60, 520)],
                     objetos=[santuario("s_caverna2", 60, 430)],
                     inimigos=[("esqueleto", 680, 100), ("esqueleto", 680, 480), ("golem", 470, 250)],
                     saidas=[saida("O", "caverna1"),
                             saida("S", "pantano1", "fragmento1",
                                   "A passagem está selada. Derrote o Golem de Pedra.")],
                     intro=["O chão treme... Um gigante de pedra desperta!"],
                     ambiente="poeira"),

    # ------------------------------------------------------------ FASE 3: PÂNTANO
    "pantano1": sala("Pântano Sombrio", (4, 2), (45, 70, 55), (35, 50, 40), "pantano.mp3", "NE",
                     obstaculos=[(R(150, 150, 120, 70), "agua"), (R(500, 380, 140, 80), "agua"),
                                 (R(580, 130, 60, 60), "tronco"), (R(180, 420, 60, 60), "tronco")],
                     npcs=[npc("viajante", "Viajante", 110, 330, (200, 160, 80), (70, 50, 30))],
                     itens=[item("p_pantano", "pocao", "Poção", 700, 100)],
                     objetos=[santuario("s_pantano", 60, 200),
                              bau("bau_broche", 60, 520, [("broche", 1)])],
                     inimigos=[("sapo", 300, 200), ("sapo", 450, 300), ("sapo", 620, 260),
                               ("fantasma", 250, 330), ("fantasma", 680, 480),
                               ("planta", 380, 430), ("planta", 690, 200)],
                     saidas=[saida("N", "caverna2"), saida("E", "pantano2")],
                     intro=["FASE 3 - Pântano Sombrio",
                            "Uma névoa densa cobre o lugar. Sapos pulam, plantas cospem e fantasmas "
                            "atravessam as paredes."],
                     ambiente="nevoa"),
    "pantano2": sala("Lago da Serpente", (5, 2), (40, 65, 60), (35, 50, 40), "chefe.mp3", "ON",
                     obstaculos=[(R(220, 140, 100, 70), "agua"), (R(220, 400, 100, 70), "agua"),
                                 (R(520, 200, 60, 60), "tronco"), (R(520, 340, 60, 60), "tronco")],
                     itens=[item("p_pantano2", "pocao", "Poção", 700, 520)],
                     objetos=[santuario("s_pantano2", 60, 430)],
                     inimigos=[("sapo", 300, 300), ("mago", 420, 130), ("fantasma", 400, 480),
                               ("serpente", 620, 265)],
                     saidas=[saida("O", "pantano1"),
                             saida("N", "castelo1", "fragmento2",
                                   "Os portões do castelo estão selados. Derrote a Serpente.")],
                     intro=["Algo enorme se move sob a água...",
                            "A Serpente do Pântano guarda o segundo fragmento!"],
                     ambiente="nevoa"),

    # ------------------------------------------------------------ FASE 4: CASTELO
    "castelo1": sala("Corredor do Castelo", (5, 1), (60, 55, 75), (110, 100, 130), "castelo.mp3", "SE",
                     obstaculos=[(R(180, 150, 50, 50), "pilar"), (R(180, 400, 50, 50), "pilar"),
                                 (R(560, 150, 50, 50), "pilar"), (R(560, 400, 50, 50), "pilar")],
                     npcs=[npc("soldado", "Soldado Ferido", 120, 200, (90, 110, 150), (110, 80, 50))],
                     itens=[item("p_castelo", "pocao", "Poção", 680, 100)],
                     objetos=[santuario("s_castelo", 250, 480),
                              bau("bau_castelo", 720, 500, [("coracao", 1), ("pocao", 2)])],
                     inimigos=[("cavaleiro", 300, 250), ("cavaleiro", 450, 300), ("cavaleiro", 620, 280),
                               ("esqueleto", 300, 120), ("esqueleto", 300, 480),
                               ("mago", 450, 120), ("mago", 450, 490)],
                     saidas=[saida("S", "pantano2"), saida("E", "castelo2")],
                     intro=["FASE 4 - Castelo do Rei Sombrio",
                            "Cavaleiros e magos amaldiçoados patrulham os corredores."],
                     ambiente="poeira"),
    "castelo2": sala("Salão do Trono", (6, 1), (50, 22, 32), (110, 45, 60), "rei.mp3", "O",
                     obstaculos=[(R(260, 140, 50, 50), "pilar"), (R(260, 410, 50, 50), "pilar"),
                                 (R(560, 140, 50, 50), "pilar"), (R(560, 410, 50, 50), "pilar")],
                     itens=[item("p_trono1", "pocao", "Poção", 60, 520),
                            item("p_trono2", "pocao", "Poção", 730, 520)],
                     objetos=[santuario("s_trono", 60, 430)],
                     inimigos=[("rei", 520, 260)],
                     saidas=[saida("O", "castelo1")],
                     intro=["Rei Sombrio: Então você chegou até aqui...",
                            "Rei Sombrio: Entregue os fragmentos. O cristal será meu!"],
                     ambiente="brasas"),
}

SECRETAS = {"gruta"}  # salas que só aparecem no mapa depois de visitadas

# ================================================================ INIMIGOS
# ia: perseguir (padrão) | pulo | fantasma | investida | parado | teleporta
TIPOS = {
    "slime":         {"nome": "Slime", "hp": 2, "vel": 1.0, "dano": 1, "tam": 26, "alcance": 220,
                      "drop": 0.30, "moedas": (1, 2), "cor": (80, 200, 90)},
    "slime_gigante": {"nome": "Slime Gigante", "hp": 6, "vel": 0.8, "dano": 1, "tam": 44, "alcance": 240,
                      "drop": 0.50, "moedas": (3, 5), "cor": (50, 160, 80), "divide": ("slime", 2)},
    "morcego":       {"nome": "Morcego", "hp": 1, "vel": 2.2, "dano": 1, "tam": 22, "alcance": 280,
                      "drop": 0.20, "moedas": (1, 2), "cor": (110, 70, 150)},
    "esqueleto":     {"nome": "Esqueleto", "hp": 3, "vel": 0.9, "dano": 1, "tam": 28, "alcance": 300,
                      "drop": 0.30, "moedas": (2, 3), "cor": (235, 235, 220),
                      "ataque": {"padrao": "mira", "intervalo": 130, "vel": 3.2, "qtd": 1,
                                 "cor": (240, 240, 225)}},
    "sapo":          {"nome": "Sapo", "hp": 2, "vel": 3.2, "dano": 1, "tam": 26, "alcance": 300,
                      "drop": 0.30, "moedas": (1, 3), "cor": (110, 190, 70), "ia": "pulo"},
    "fantasma":      {"nome": "Fantasma", "hp": 3, "vel": 1.0, "dano": 1, "tam": 28, "alcance": 360,
                      "drop": 0.25, "moedas": (2, 3), "cor": (210, 220, 255), "ia": "fantasma"},
    "javali":        {"nome": "Javali", "hp": 4, "vel": 1.2, "dano": 1, "tam": 32, "alcance": 320,
                      "drop": 0.30, "moedas": (2, 4), "cor": (160, 105, 70), "ia": "investida",
                      "investida": {"alcance": 240, "preparo": 30, "vel": 6.0, "duracao": 24, "descanso": 45}},
    "aranha":        {"nome": "Aranha", "hp": 3, "vel": 1.8, "dano": 1, "tam": 26, "alcance": 340,
                      "drop": 0.25, "moedas": (2, 3), "cor": (130, 70, 150), "ia": "investida",
                      "investida": {"alcance": 170, "preparo": 16, "vel": 7.0, "duracao": 14, "descanso": 30}},
    "planta":        {"nome": "Planta Carnívora", "hp": 4, "vel": 0, "dano": 1, "tam": 30, "alcance": 380,
                      "drop": 0.40, "moedas": (2, 3), "cor": (70, 170, 70), "ia": "parado",
                      "ataque": {"padrao": "mira", "intervalo": 110, "vel": 3.4, "qtd": 1,
                                 "cor": (140, 240, 90)}},
    "mago":          {"nome": "Mago Sombrio", "hp": 3, "vel": 0.9, "dano": 1, "tam": 28, "alcance": 520,
                      "drop": 0.40, "moedas": (3, 5), "cor": (140, 100, 210), "ia": "teleporta",
                      "ataque": {"padrao": "leque", "intervalo": 150, "vel": 3.4, "qtd": 3,
                                 "cor": (190, 140, 255)}},
    "cavaleiro":     {"nome": "Cavaleiro", "hp": 5, "vel": 1.5, "dano": 1, "tam": 30, "alcance": 320,
                      "drop": 0.40, "moedas": (3, 5), "cor": (170, 170, 190)},
    # ---- chefes
    "lobo":     {"nome": "Lobo Sombrio", "hp": 8, "vel": 2.0, "dano": 1, "tam": 44, "alcance": 380,
                 "boss": True, "moedas": (8, 8), "cor": (90, 90, 120)},
    "golem":    {"nome": "Golem de Pedra", "hp": 16, "vel": 0.9, "dano": 1, "tam": 72, "alcance": 1000,
                 "boss": True, "moedas": (12, 12), "cor": (150, 140, 130),
                 "ataque": {"padrao": "anel", "intervalo": 120, "vel": 3.0, "qtd": 10, "cor": (190, 165, 130)}},
    "serpente": {"nome": "Serpente do Pântano", "hp": 18, "vel": 1.6, "dano": 1, "tam": 56, "alcance": 1000,
                 "boss": True, "moedas": (15, 15), "cor": (80, 190, 80),
                 "ataque": {"padrao": "leque", "intervalo": 75, "vel": 3.6, "qtd": 3, "cor": (120, 235, 90)}},
    "rainha":   {"nome": "Rainha Aranha", "hp": 20, "vel": 1.4, "dano": 1, "tam": 60, "alcance": 1000,
                 "boss": True, "moedas": (20, 20), "cor": (150, 60, 160), "ia": "investida",
                 "investida": {"alcance": 200, "preparo": 26, "vel": 6.5, "duracao": 18, "descanso": 40},
                 "ataque": {"padrao": "leque", "intervalo": 110, "vel": 3.4, "qtd": 5, "cor": (200, 120, 230)},
                 "invoca": {"tipo": "aranha", "qtd": 2, "intervalo": 380, "max": 3, "fase_min": 2}},
    "rei":      {"nome": "Rei Sombrio", "hp": 24, "vel": 1.3, "dano": 1, "tam": 64, "alcance": 1000,
                 "boss": True, "moedas": (25, 25), "cor": (170, 60, 190),
                 "invoca": {"tipo": "morcego", "qtd": 2, "intervalo": 420, "max": 3, "fase_min": 2}},
}

RECOMPENSAS = {"lobo": [("chave", "Chave Antiga")],
               "golem": [("fragmento1", "Fragmento do Cristal I")],
               "serpente": [("fragmento2", "Fragmento do Cristal II")],
               "rainha": [("anel", "Anel de Força")],
               "rei": [("cristal", "Cristal da Aurora")]}

DIFICULDADES = {"facil": {"nome": "Fácil", "vida": 7, "mult": 0.75,
                          "desc": "7 corações e monstros mais fracos. Ideal para curtir a história."},
                "normal": {"nome": "Normal", "vida": 5, "mult": 1.0,
                           "desc": "5 corações. A experiência padrão."},
                "dificil": {"nome": "Difícil", "vida": 4, "mult": 1.35,
                            "desc": "4 corações e monstros mais resistentes. Para quem quer desafio."}}

# ================================================================ ARENA
ARENA_ONDAS = [
    [("slime", 3)],
    [("slime", 2), ("morcego", 3)],
    [("esqueleto", 2), ("sapo", 3)],
    [("cavaleiro", 2), ("mago", 1), ("fantasma", 2)],
    [("slime_gigante", 2), ("javali", 2), ("mago", 2)],
]
ARENA_SPAWNS = [(60, 60), (700, 60), (60, 500), (700, 500), (120, 300), (640, 300)]

# ================================================================ MISSÕES
# tipo: matar (alvo = tipos de inimigo) | item (item no inventário) | arena (ondas vencidas)
MISSOES = {
    "slimes": {"nome": "Gosma para o Ferreiro", "desc": "Derrote 5 slimes (comuns ou gigantes).",
               "tipo": "matar", "alvo": ("slime", "slime_gigante"), "qtd": 5, "requer": "espada",
               "recompensa": {"moeda": 20, "bomba": 3}},
    "broche": {"nome": "O Broche da Luna", "desc": "Encontre o broche perdido no Pântano Sombrio.",
               "tipo": "item", "item": "broche", "qtd": 1, "requer": "chave",
               "recompensa": {"moeda": 30, "coracao": 1}},
    "pantano": {"nome": "Limpeza do Pântano", "desc": "Derrote 6 sapos ou fantasmas.",
                "tipo": "matar", "alvo": ("sapo", "fantasma"), "qtd": 6, "requer": "fragmento1",
                "recompensa": {"moeda": 25, "flecha": 12}},
    "arena": {"nome": "Campeão de Aurora", "desc": "Vença as 5 ondas da Arena.",
              "tipo": "arena", "qtd": 5, "requer": "espada",
              "recompensa": {"moeda": 50, "coracao": 1}},
    "aranhas": {"nome": "Terror das Teias", "desc": "Derrote a Rainha Aranha no Ninho.",
                "tipo": "matar", "alvo": ("rainha",), "qtd": 1, "requer": "espada",
                "recompensa": {"moeda": 40, "bomba": 2}},
}
QUEST_NPC = {"ferreiro": "slimes", "luna": "broche", "viajante": "pantano",
             "mestre": "arena", "espirito": "aranhas"}

MISSAO_TEXTOS = {
    "slimes": {
        "oferta": ["Ferreiro Bram: Preciso de gosma de slime para temperar o metal.",
                   "Ferreiro Bram: Derrote 5 slimes e eu pago 20 moedas e 3 bombas. Combinado?"],
        "lembrete": ["Ferreiro Bram: Ainda faltam slimes! Procure na floresta."],
        "entrega": ["Ferreiro Bram: Excelente! Aqui está o pagamento: 20 moedas e 3 bombas."]},
    "broche": {
        "oferta": ["Anciã Luna: Perdi o broche do meu irmão no pântano, ao sul da caverna.",
                   "Anciã Luna: Se você o encontrar, eu lhe darei uma boa recompensa."],
        "lembrete": ["Anciã Luna: O broche deve estar em algum baú do pântano. Procure bem!"],
        "entrega": ["Anciã Luna: O broche dele! Obrigada... aceite este presente de coração."]},
    "pantano": {
        "oferta": ["Viajante: Esses sapos e fantasmas me impedem de acampar em paz.",
                   "Viajante: Derrote 6 deles e eu lhe dou flechas e moedas."],
        "lembrete": ["Viajante: Ainda há muitos deles por aí. Continue!"],
        "entrega": ["Viajante: Finalmente sossego! Tome: 25 moedas e 12 flechas."]},
    "arena": {
        "oferta": ["Mestre da Arena: Vença as 5 ondas e será um campeão de Aurora!",
                   "Mestre da Arena: Missão aceita. Fale comigo de novo para começar."],
        "lembrete": [],
        "entrega": ["Mestre da Arena: Campeão! Aqui está sua recompensa: 50 moedas e um coração."]},
    "aranhas": {
        "oferta": ["Espírito: Ao norte, no Ninho, vive a Rainha Aranha. Ela aterroriza a caverna.",
                   "Espírito: Derrote-a e eu lhe darei moedas e bombas."],
        "lembrete": ["Espírito: A Rainha ainda vive no Ninho, ao norte."],
        "entrega": ["Espírito: A caverna está em paz. Tome sua recompensa!"]},
}

# ================================================================ CONQUISTAS
CONQUISTAS = [
    ("aventureiro", "Aventureiro", "Receba a Espada de Aurora."),
    ("cacador", "Caçador", "Derrote 50 inimigos."),
    ("lobo", "Domador de Lobos", "Derrote o Lobo Sombrio."),
    ("golem", "Quebra-Pedras", "Derrote o Golem de Pedra."),
    ("serpente", "Encantador de Serpentes", "Derrote a Serpente do Pântano."),
    ("rainha", "Caçadora de Aranhas", "Derrote a Rainha Aranha."),
    ("salvador", "Salvador de Aurora", "Quebre a maldição e termine o jogo."),
    ("rico", "Ricaço", "Tenha 100 moedas ao mesmo tempo."),
    ("explorador", "Explorador", "Visite todas as salas do mundo."),
    ("arqueiro", "Mira Certeira", "Encontre o Arco."),
    ("bombeiro", "Detonador", "Destrua uma pedra rachada com uma bomba."),
    ("ajudante", "Bom Vizinho", "Complete 3 missões."),
    ("campeao", "Campeão da Arena", "Vença as 5 ondas da Arena."),
    ("compras", "Cliente Fiel", "Compre as 4 melhorias da espada e do coração na loja."),
]

# ================================================================ HISTÓRIA
PROLOGO = [
    "Há muito tempo, a vila de Aurora vivia em paz,",
    "protegida pelo brilho do Cristal da Aurora.",
    "Até que o Rei Sombrio roubou o cristal,",
    "e uma maldição apagou as cores da vila.",
    "O cristal se partiu, e seus fragmentos foram guardados por monstros.",
    "Você é a última esperança de Aurora.",
]

FINAL_LUNA = [
    "Anciã Luna: O Cristal da Aurora! Você conseguiu!",
    "Anciã Luna: Sabe... o Rei Sombrio era meu irmão, o antigo guardião da vila.",
    "Anciã Luna: O poder do cristal o corrompeu. Agora, de volta ao seu lugar, ele traz paz outra vez.",
    "A luz do cristal quebra a maldição e as cores voltam à vila.",
]

FALAS_MORTE = {
    "golem": ["Golem de Pedra: Eu guardava este fragmento... para que ele não fosse usado para o mal.",
              "O Golem se desfaz em pedras e deixa um fragmento brilhante."],
    "serpente": ["Serpente do Pântano: O Rei corrompeu até a água... leve o fragmento. Salve Aurora.",
                 "A Serpente mergulha no lago e deixa o segundo fragmento para trás."],
    "rainha": ["Rainha Aranha: Meus filhotes... você venceu. Leve este anel, guerreiro.",
               "A Rainha tomba e deixa um anel dourado para trás."],
    "rei": ["Rei Sombrio: Não... o cristal... eu só queria proteger Aurora...",
            "Rei Sombrio: Leve-o de volta... e cuide da vila... irmã..."],
}

NOMES_ITEM = {"moeda": "Moeda", "pocao": "Poção", "coracao": "Coração de Vida", "amuleto": "Amuleto da Vida",
              "flecha": "Flechas", "bomba": "Bombas", "arco": "Arco", "anel": "Anel de Força",
              "broche": "Broche da Luna", "chave": "Chave Antiga", "espada": "Espada de Aurora",
              "fragmento1": "Fragmento do Cristal I", "fragmento2": "Fragmento do Cristal II",
              "cristal": "Cristal da Aurora"}
