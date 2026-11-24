# A Floresta de Aurora

## 👥 Equipe de desenvolvimento

- Gustavo Rivelino — Team Leader
- Gustavo Mazera — Músicas
- Samuel Santos — QA
- Matheus Lima — Desenvolvimento
- Vitor Perrone — Desenvolvimento
- Miguel Joaquim — QA
- Victor Brito — Documentação

Consulte [DOCUMENTACAO.md](DOCUMENTACAO.md) para conhecer
a divisão detalhada das responsabilidades.

Jogo de **aventura e ação em 2D** (visão de cima) feito do zero em **Python com pygame**.
Você explora 9 áreas divididas em 4 fases, luta contra 10 tipos de inimigos e 4 chefes,
compra melhorias com as moedas que ganha e descobre uma história com reviravolta no final.

> Projeto de faculdade. Toda a arte e toda a música/efeitos sonoros são **originais e gerados por código**,
> então não há problema de direitos autorais.

---

## Índice

1. [Como rodar](#1-como-rodar)
2. [Controles](#2-controles)
3. [A história](#3-a-história)
4. [Como jogar](#4-como-jogar)
5. [O mapa e as fases](#5-o-mapa-e-as-fases)
6. [Inimigos e chefes](#6-inimigos-e-chefes)
7. [Itens, moedas e loja](#7-itens-moedas-e-loja)
8. [Pastas e arquivos do projeto](#8-pastas-e-arquivos-do-projeto)
9. [Como o código funciona](#9-como-o-código-funciona)
10. [Como personalizar (imagens, música, inimigos, salas)](#10-como-personalizar)
11. [Problemas comuns](#11-problemas-comuns)
12. [Roteiro para a apresentação](#12-roteiro-para-a-apresentação)

---

## 1. Como rodar

**O que você precisa**

- Python 3.9 ou mais novo
- A biblioteca `pygame`
- (Opcional) `numpy`, só se quiser **regerar** a música e os efeitos sonoros

**Passo a passo**

```bash
# 1) Instale o pygame
pip install pygame

# 2) Entre na pasta do jogo (a que tem o main.py e a pasta assets/)
cd jogo

# 3) Rode
python main.py
```

Em alguns computadores o comando é `python3 main.py` ou `py main.py`.

> **Importante:** mantenha o `main.py` e a pasta `assets/` **juntos**, na mesma pasta.
> Sem a pasta `assets/`, o jogo ainda abre, mas fica sem música, sem efeitos sonoros
> e usa os desenhos padrão no lugar dos arquivos PNG.

---

## 2. Controles

| Tecla | O que faz |
|---|---|
| **Setas** ou **W A S D** | Andar |
| **J** | Atacar com a espada |
| **E**, **ENTER** ou **ESPAÇO** | Falar com personagens e avançar os textos |
| **Q** | Usar uma poção (cura 2 corações) |
| **P** | Pausar / continuar |
| **1, 2, 3** | Comprar na loja do ferreiro |
| **ESC** | Fechar o jogo |

---

## 3. A história

Aurora era uma vila pacífica, protegida pelo brilho do **Cristal da Aurora**.
O **Rei Sombrio** roubou o cristal e lançou uma maldição que apagou as cores da vila.
No processo, o cristal se partiu e seus fragmentos foram entregues a monstros guardiões.

Você é a última esperança de Aurora. A **Anciã Luna** entrega a **Espada de Aurora** e manda
você atrás dos fragmentos. Cada fase termina com um chefe que guarda algo importante:

1. **Lobo Sombrio** guarda a *Chave Antiga* (abre a caverna).
2. **Golem de Pedra** guarda o *Fragmento I* (abre o caminho para o pântano).
3. **Serpente do Pântano** guarda o *Fragmento II* (abre os portões do castelo).
4. **Rei Sombrio** (chefe final) guarda o *Cristal da Aurora*.

Pelo caminho, os personagens contam pistas sobre a história. No final há uma reviravolta
que muda como você enxerga o vilão (sem spoiler aqui, vale a pena descobrir jogando).

---

## 4. Como jogar

1. Na **vila**, fale com a **Anciã Luna** (aperte `E` perto dela). Ela dá a espada e uma poção.
2. Fale com o **Ferreiro Bram** para abrir a loja (use as moedas depois).
3. Siga para o **leste** e avance pelas fases, derrotando os chefes.
4. Derrotando um monstro, ele pode soltar **moedas** e **poções**. Passe por cima para pegar.
5. Se a vida acabar, você **acorda na vila** com a vida cheia, mas **perde metade das moedas**.
   Seu progresso (itens, chefes derrotados) é mantido.
6. Ao pegar o **Cristal da Aurora**, você é levado de volta à vila para o final.

**Dicas**

- Ao tomar dano você fica **invencível por 1 segundo** (o personagem pisca). Aproveite para se afastar.
- Os chefes atiram bolas de energia. **Não fique parado**: ande em círculo e ataque nas brechas.
- Os pilares e pedras das salas servem de **cobertura** contra os tiros.
- Guarde poções para as lutas de chefe e use `Q` antes que a vida acabe.
- Visite o ferreiro sempre que juntar moedas: a **Espada Afiada** facilita muito os chefes.
- Fantasmas atravessam paredes, então não adianta se esconder atrás delas.

---

## 5. O mapa e as fases

O mundo tem **9 salas** ligadas entre si. Algumas passagens só abrem depois de você derrotar um chefe.

```
 1. Vila de Aurora
 2. Floresta Sussurrante
 3. Clareira do Lobo      [chefe: Lobo Sombrio]     -> solta a Chave Antiga
 4. Caverna Cristalina    (porta trancada: pede a Chave Antiga)
 5. Salão do Golem        [chefe: Golem de Pedra]   -> solta o Fragmento I
 6. Pântano Sombrio       (passagem selada: pede o Fragmento I)
 7. Lago da Serpente      [chefe: Serpente]         -> solta o Fragmento II
 8. Corredor do Castelo   (portões selados: pedem o Fragmento II)
 9. Salão do Trono        [chefe final: Rei Sombrio] -> solta o Cristal da Aurora
```

A ordem é sempre essa: cada sala leva à próxima, e você pode **voltar** para qualquer sala anterior
(por exemplo, para visitar o ferreiro na vila).

| Fase | Salas | Chefe | Música | O que tem de novo |
|---|---|---|---|---|
| Vila (início) | Vila de Aurora | nenhum | Vila | Luna, loja do ferreiro |
| 1. Floresta | Floresta Sussurrante, Clareira do Lobo | Lobo Sombrio | Floresta / Chefe | Slimes, Coração de Vida |
| 2. Caverna | Caverna Cristalina, Salão do Golem | Golem de Pedra | Caverna / Chefe | Morcegos, esqueletos, Amuleto da Vida |
| 3. Pântano | Pântano Sombrio, Lago da Serpente | Serpente do Pântano | Pântano / Chefe | Sapos, fantasmas, lagos que bloqueiam |
| 4. Castelo | Corredor do Castelo, Salão do Trono | Rei Sombrio | Castelo / Rei | Cavaleiros, luta final em 3 fases |

**Passagens trancadas**

| Passagem | Pede | Como conseguir |
|---|---|---|
| Clareira do Lobo para a Caverna | Chave Antiga | Derrotar o Lobo Sombrio |
| Salão do Golem para o Pântano | Fragmento I | Derrotar o Golem de Pedra |
| Lago da Serpente para o Castelo | Fragmento II | Derrotar a Serpente do Pântano |

Quando você entra numa sala pela primeira vez, aparece um **texto de introdução** que conta o que está acontecendo.

---

## 6. Inimigos e chefes

### Inimigos comuns

| Inimigo | Vida | Comportamento |
|---|---|---|
| **Slime** | 2 | Devagar, persegue o jogador |
| **Morcego** | 1 | Muito rápido, persegue o jogador |
| **Esqueleto** | 3 | Devagar e **atira ossos** na sua direção |
| **Sapo** | 2 | **Pula** em rajadas e descansa entre os pulos |
| **Fantasma** | 3 | **Atravessa paredes** e obstáculos |
| **Cavaleiro** | 5 | Resistente, persegue com força |

### Chefes (têm barra de vida na parte de baixo da tela)

| Chefe | Vida | Ataques |
|---|---|---|
| **Lobo Sombrio** | 8 | Muito rápido, ataca no corpo a corpo |
| **Golem de Pedra** | 16 | Lento e grande, dispara um **anel de pedras** em todas as direções |
| **Serpente do Pântano** | 18 | Cospe veneno em **leque** (3 tiros) |
| **Rei Sombrio** | 24 | **3 fases**: veja abaixo |

**As 3 fases do Rei Sombrio**

1. **Mais de 66% da vida:** atira uma bola de energia mirada em você.
2. **Entre 66% e 33%:** atira em leque (3 tiros) e **invoca morcegos**.
3. **Menos de 33%:** fica mais rápido, atira em leque de 5 tiros e, de vez em quando, solta um **anel de 12 tiros**.

Cada monstro derrotado solta moedas. Os comuns também podem soltar poções. Os chefes sempre soltam o item da fase.

---

## 7. Itens, moedas e loja

| Item | Efeito |
|---|---|
| **Moeda** | Dinheiro para a loja |
| **Poção** | Cura 2 corações (use com `Q`) |
| **Coração de Vida** | +1 de vida máxima e cura total |
| **Amuleto da Vida** | +2 de vida máxima e cura total |
| **Espada de Aurora** | Sua arma (ganha da Luna) |
| **Chave Antiga** | Abre a caverna |
| **Fragmento do Cristal I e II** | Abrem o pântano e o castelo |
| **Cristal da Aurora** | Item final; leva você de volta à vila para o desfecho |

**Você começa com 5 corações** e 1 de dano por golpe.

**Loja do Ferreiro Bram** (fale com ele na vila; aperte `1`, `2` ou `3`)

| Opção | Preço | Limite |
|---|---|---|
| 1) Poção de Cura | 6 moedas | Quantas quiser |
| 2) Espada Afiada (+1 de dano) | 25 e depois 45 moedas | 2 compras |
| 3) Coração de Ferro (+1 vida máxima) | 20 e depois 30 moedas | 2 compras |

---

## 8. Pastas e arquivos do projeto

```
jogo/
├── main.py              <- o jogo inteiro (rode este)
├── gerar_musicas.py     <- cria as músicas e os efeitos sonoros (precisa de numpy)
├── gerar_imagens.py     <- salva os sprites como arquivos PNG
├── README.md            <- este arquivo
└── assets/
    ├── menu.wav, vila.wav, floresta.wav, caverna.wav,
    │   pantano.wav, castelo.wav, chefe.wav, rei.wav, fim.wav     (músicas)
    ├── sfx_ataque.wav, sfx_acerto.wav, sfx_dano.wav, sfx_item.wav,
    │   sfx_moeda.wav, sfx_pocao.wav, sfx_morte.wav, sfx_chefe.wav,
    │   sfx_compra.wav, sfx_erro.wav                               (efeitos sonoros)
    └── espada.png, jogador.png, npc_*.png, inimigo_*.png          (imagens)
```

---

## 9. Como o código funciona

O `main.py` é dividido em blocos (procure pelas linhas `# =====` para navegar):

| Bloco | Para que serve |
|---|---|
| **ÁUDIO** | `tocar()` toca a música da área em loop; `som()` toca efeitos curtos |
| **MAPA** | O dicionário `SALAS` descreve cada sala: cores, obstáculos, NPCs, itens, inimigos e saídas |
| **TIPOS** | O dicionário `TIPOS` descreve cada inimigo (vida, velocidade, dano, tamanho, ataque) |
| **HISTÓRIA** | Textos do prólogo, final e falas dos personagens (mudam conforme seu progresso) |
| **IMAGENS** | Desenha os sprites por código ou carrega os PNG da pasta `assets/` |
| **INIMIGOS E CHEFES** | A classe `Inimigo`: movimento, perseguição, tiros e fases do Rei |
| **AÇÕES DO JOGADOR** | Ataque, poção, dano, pegar itens, trocar de sala, loja |
| **ESTADO** | `novo_jogo()` zera tudo; as variáveis do jogo ficam guardadas em `G` |
| **ATUALIZAÇÃO** | A cada quadro: move o jogador, os inimigos e os tiros, e checa colisões |
| **EVENTOS** | Lê o teclado |
| **DESENHO** | Desenha cenário, personagens, efeitos, barra de vida e menus |

**Ideias importantes (ótimas para explicar na apresentação)**

- **Game loop:** o jogo repete 60 vezes por segundo: *ler teclado, atualizar, desenhar*.
- **Estados do jogo:** `menu`, `historia`, `jogo`, `loja`, `gameover` e `fim`. Cada um decide o que atualizar e desenhar.
- **Dados separados da lógica:** salas e inimigos são **dicionários**. Para criar conteúdo novo, quase não precisa mexer na lógica.
- **Colisão por eixo:** o jogador se move primeiro em X, depois em Y, e é empurrado para fora de paredes (`mover_rect`).
- **Orientação a objetos:** a classe `Inimigo` cuida de cada monstro, com comportamento próprio (`ia`: perseguir, pular, atravessar paredes).
- **Padrões de ataque:** `mira`, `leque` e `anel` calculam os ângulos dos tiros com seno e cosseno.
- **Acabamento:** partículas, números flutuantes, tremor de câmera, transição entre salas (fade) e piscar ao levar dano.
- **Áudio por síntese:** `gerar_musicas.py` cria ondas sonoras com `numpy`. Cada nota tem forma de onda, ataque e decaimento.

---

## 10. Como personalizar

### Trocar as imagens por arte sua

1. Rode `python gerar_imagens.py` (cria os PNG em `assets/`, se ainda não existirem).
2. Substitua qualquer arquivo, mantendo o **mesmo nome** (por exemplo `assets/espada.png`).
3. Pronto: o jogo carrega seu PNG e **redimensiona sozinho** se o tamanho for diferente.

> Se você apagar um PNG, o jogo volta a usar o desenho padrão daquele sprite.

### Trocar a música

Coloque um arquivo com o mesmo nome em `.mp3` ou `.ogg` (por exemplo `assets/vila.mp3`).
O jogo usa o `.mp3` primeiro, se existir. Para gerar novamente as músicas padrão:
`pip install numpy` e depois `python gerar_musicas.py`.

### Criar um inimigo novo

1. Em `TIPOS`, adicione uma linha:

```python
"aranha": {"nome": "Aranha", "hp": 3, "vel": 1.8, "dano": 1, "tam": 26,
           "alcance": 300, "drop": 0.3, "moedas": (2, 3), "cor": (60, 40, 40)},
```

2. Em `sprite_inimigo`, desenhe o sprite dela (ou coloque `inimigo_aranha.png` em `assets/`).
3. Em `SALAS`, na lista de inimigos de uma sala, acrescente `("aranha", 300, 200)`.

Para o inimigo atirar, acrescente `"ataque": {"padrao": "mira", "intervalo": 120, "vel": 3, "qtd": 1, "cor": (255, 255, 255)}`.
Para ele pular ou atravessar paredes, use `"ia": "pulo"` ou `"ia": "fantasma"`.

### Criar uma sala nova

Copie uma entrada de `SALAS`, mude nome, cores, obstáculos, inimigos e **saídas**.
As saídas usam `saida("E", "nome_da_outra_sala")` (lados: `N`, `S`, `E`, `O`).
Lembre de criar a saída de volta na outra sala. Para trancar a passagem, use o
parâmetro `requer`: `saida("E", "sala_x", "chave", "Mensagem quando estiver trancada")`.

### Ajustar a dificuldade

- Vida inicial: `G.hp_max = G.hp = 5` em `novo_jogo()`.
- Vida dos monstros e chefes: campo `"hp"` em `TIPOS`.
- Preços da loja: função `itens_loja()`.
- Velocidade do jogador: o número `4` na função `atualizar()` (linhas de `dx` e `dy`).

---

## 11. Problemas comuns

| Problema | Solução |
|---|---|
| `ModuleNotFoundError: No module named 'pygame'` | Rode `pip install pygame` |
| O jogo abre mas não toca música | Confirme que a pasta `assets/` está ao lado do `main.py` e que o som do computador está ligado |
| Aparece "Áudio indisponível" no terminal | O computador não tem saída de áudio; o jogo roda normalmente sem som |
| Acentos aparecem errados | Salve e abra os arquivos como UTF-8 |
| `gerar_musicas.py` dá erro de `numpy` | Rode `pip install numpy` |
| Quero reiniciar do zero | Feche e abra o jogo (não existe save em arquivo) |

---

## 12. Roteiro para a apresentação

**Tempo sugerido: 7 a 10 minutos**

1. **Ideia (1 min):** jogo de aventura em Python com pygame; 4 fases, 4 chefes e história com final surpresa.
2. **Demonstração (3 min):** menu, conversa com a Luna, loja do ferreiro, uma luta contra chefe (de preferência o Golem), a porta trancada, e mostre o final.
3. **Como funciona (3 min):**
   - o game loop (ler, atualizar, desenhar);
   - os estados do jogo;
   - salas e inimigos como dicionários;
   - a classe `Inimigo` e os padrões de ataque;
   - as fases do Rei Sombrio.
4. **Áudio e imagens (1 min):** tudo feito por código, sem arquivos baixados. Mostre `gerar_musicas.py`.
5. **Melhorias futuras (30 s):** salvar o jogo em arquivo, mais armas, animação dos sprites, minimapa, modo cooperativo.

---

**Tecnologias:** Python 3, pygame 2, numpy (apenas para gerar o áudio).
**Resumo do tamanho:** cerca de 1.300 linhas no `main.py`, 9 salas, 10 tipos de inimigos, 4 chefes, 9 músicas e 10 efeitos sonoros.
