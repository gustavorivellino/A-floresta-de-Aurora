# A Floresta de Aurora: Documentação Completa

Integrante	        RA	          Responsabilidade
Gustavo Rivelino	  824122890	    Team Leader
Gustavo Mazera	    824112306	    Músicas
Samuel Santos	      824138001	    QA
Matheus Lima	      824147299	    Desenvolvimento
Vitor Perrone	      824110806	    Desenvolvimento
Miguel Joaquim	    824144840	    QA
Victor Brito	      823148423	    Documentação

Documentação do projeto **A Floresta de Aurora**, um jogo de aventura e ação em 2D feito em Python com pygame.

**Sumário**

1. [Visão geral](#1-visão-geral)
2. [Requisitos e instalação](#2-requisitos-e-instalação)
3. [Guia do jogador](#3-guia-do-jogador)
4. [O mundo](#4-o-mundo)
5. [Bestiário](#5-bestiário)
6. [Missões, Arena e Conquistas](#6-missões-arena-e-conquistas)
7. [A história](#7-a-história)
8. [Arquitetura do código](#8-arquitetura-do-código)
9. [Formatos de dados](#9-formatos-de-dados)
10. [Como estender o jogo](#10-como-estender-o-jogo)
11. [Áudio e imagens](#11-áudio-e-imagens)
12. [Testes](#12-testes)
13. [Gerar o executável (.exe)](#13-gerar-o-executável-exe)
14. [Solução de problemas](#14-solução-de-problemas)
15. [Limitações conhecidas e ideias futuras](#15-limitações-conhecidas-e-ideias-futuras)
16. [Histórico de versões](#16-histórico-de-versões)
17. [Resumo para a apresentação](#17-resumo-para-a-apresentação)

---

## 1. Visão geral

| Item | Valor |
|---|---|
| Nome | A Floresta de Aurora |
| Gênero | Aventura e ação, visão de cima (top-down) |
| Linguagem / biblioteca | Python 3 e pygame 2 |
| Resolução | 800 x 600 (a janela pode ser redimensionada; F11 liga a tela cheia) |
| Áreas | 12 salas: 9 no caminho principal (a vila e 4 fases) e 3 extras (Arena, Gruta Secreta e Ninho das Aranhas) |
| Inimigos | 11 comuns + 5 chefes = 16 tipos |
| Extras | Missões, Arena em ondas, conquistas, loja, baús, santuários, segredos, mapa, save, 3 dificuldades |
| Tamanho do código | cerca de 2.700 linhas (`main.py`, `dados.py`, `sprites.py`) |
| Arte e áudio | 100% gerados por código: 25 sprites PNG, 9 músicas e 16 efeitos sonoros |

**Em uma frase:** você é a última esperança da vila de Aurora; precisa vencer quatro chefes, recuperar os fragmentos
do Cristal da Aurora e derrotar o Rei Sombrio, enquanto explora segredos, cumpre missões e melhora seu personagem.

---

## 2. Requisitos e instalação

**Requisitos**

- Python 3.9 ou mais novo
- `pygame` (obrigatório)
- `numpy` (somente para **regerar** o áudio com `gerar_musicas.py`)
- `pyinstaller` (somente para gerar o `.exe`)

**Instalação e execução**

```bash
pip install pygame
cd jogo
python main.py
```

**Estrutura de pastas**

```
jogo/
├── main.py             motor do jogo: loop, menus, combate, missões, save, telas
├── dados.py            conteúdo: salas, inimigos, missões, conquistas, textos
├── sprites.py          arte: desenha personagens, inimigos, itens e cenário por código
├── gerar_musicas.py    sintetiza músicas e efeitos sonoros (numpy)
├── gerar_imagens.py    exporta os sprites como PNG
├── testes.py           testes automáticos
├── README.md           guia rápido
├── DOCUMENTACAO.md     este documento
└── assets/
    ├── menu, vila, floresta, caverna, pantano, castelo, chefe, rei, fim   (.wav, músicas)
    ├── sfx_*.wav                                                          (16 efeitos)
    └── jogador, espada, npc_*, inimigo_*                                  (.png, sprites)
```

Os três arquivos `.py` do jogo (`main.py`, `dados.py`, `sprites.py`) e a pasta `assets/` devem ficar **juntos**.

---

## 3. Guia do jogador

### 3.1 Controles

| Tecla | Ação |
|---|---|
| Setas ou W A S D | Andar (e navegar nos menus) |
| J | Atacar com a espada |
| K | Atirar com o arco (exige o arco e flechas) |
| SHIFT ou L | Desvio rápido (dash) |
| B | Colocar uma bomba |
| Q | Usar uma poção |
| E, ENTER ou ESPAÇO | Interagir: falar, abrir baú, ler placa, descansar; avançar textos; confirmar nos menus |
| TAB | Diário de missões |
| M | Mapa |
| P ou ESC | Pausa |
| F11 | Tela cheia |

### 3.2 Menus

- **Menu inicial:** Continuar (aparece se há save), Novo Jogo, Conquistas, Controles e Sair.
- **Dificuldade** (ao iniciar um novo jogo):

| Dificuldade | Corações iniciais | Vida dos monstros |
|---|---|---|
| Fácil | 7 | 75% |
| Normal | 5 | 100% |
| Difícil | 4 | 135% |

- **Pausa:** Continuar, Salvar jogo, volume da música, volume dos efeitos (setas esquerda e direita ajustam),
  Controles e Voltar ao menu.

### 3.3 Mecânicas

**Vida.** Você tem corações. Ao ser atingido perde 1, fica **invencível por 1 segundo** (o personagem pisca) e é
empurrado. Com pouca vida, as bordas da tela ficam vermelhas e pulsando. Poções curam 2 corações.

**Espada (J).** Ataque corpo a corpo na direção para a qual você olha. Causa 1 de dano (mais com o Anel de Força
e a Espada Afiada). Há um pequeno tempo de recarga entre os golpes.

**Arco (K).** Disparo em linha reta, causa o mesmo dano da espada e consome 1 flecha. Flechas vêm de baús, de
inimigos derrotados (quando você já tem o arco), de missões e da loja.

**Bombas (B).** A bomba é colocada à sua frente e explode depois de cerca de 1,3 segundo. Causa 3 de dano aos
inimigos em volta e **destrói as pedras rachadas**. Cuidado: ela também machuca você se estiver perto.
Você pode ter até 3 bombas acesas ao mesmo tempo.

**Desvio (SHIFT).** Um impulso rápido na direção em que você anda (ou olha). Você fica invencível durante o
desvio. Tem tempo de recarga de uns 0,8 segundo.

**Poções (Q).** Curam 2 corações. Só funcionam se você estiver ferido.

**Itens.** Passe por cima de itens no chão para pegá-los. Os monstros soltam moedas e, às vezes, poções, flechas
e bombas.

**Baús.** Aproxime-se e aperte E. Cada baú abre uma única vez.

**Placas.** Aperte E para ler. Trazem dicas e dão pistas sobre segredos.

**Santuários.** Aperte E: curam toda a sua vida, **salvam o jogo** e passam a ser seu **ponto de retorno**.
Há 8 santuários espalhados pelo mundo.

**Pedras rachadas.** Bloqueiam passagens secretas. Só uma bomba as destrói.

**Escuridão.** A Caverna Cristalina, o Ninho das Aranhas e a Gruta Secreta são escuros: você só enxerga ao
redor de si.

**Loja (Ferreiro Bram, na vila).** Fale com ele e use as teclas 1 a 5:

| Tecla | Produto | Preço | Observação |
|---|---|---|---|
| 1 | Poção de Cura | 6 moedas | Sem limite |
| 2 | Bomba | 8 moedas | Sem limite |
| 3 | 5 Flechas | 5 moedas | Só vende se você já tem o arco |
| 4 | Espada Afiada (+1 de dano) | 25 e depois 45 moedas | 2 compras |
| 5 | Coração de Ferro (+1 vida máxima) | 20 e depois 30 moedas | 2 compras |

**Cair em combate.** Quando a vida zera, aparece "VOCÊ CAIU...". Ao apertar ENTER você volta ao **último
santuário** (a vila, se ainda não usou nenhum) com a vida cheia, **perde metade das moedas** e os chefes se
recuperam. Itens, missões e inimigos comuns derrotados continuam como estavam.

**Corações extras no mundo**

| Onde | O que dá |
|---|---|
| Clareira do Lobo | Coração de Vida (+1) |
| Caverna Cristalina | Amuleto da Vida (+2) |
| Corredor do Castelo (baú) | Coração de Vida (+1) |
| Missão "O Broche da Luna" | +1 |
| Missão "Campeão de Aurora" | +1 |
| Loja | +1 duas vezes |

No total, no modo Normal você pode chegar a 13 corações.

### 3.4 Salvar e continuar

- **Salvamento automático** ao entrar em uma nova sala, ao descansar em um santuário e ao sair para o menu.
- **Salvamento manual** em Pausa, "Salvar jogo".
- O arquivo é `.floresta_de_aurora.json` na sua pasta de usuário (Windows: `C:\Users\SeuNome\`).
  Ele guarda o jogo atual, as **conquistas** e o **volume**. Para zerar tudo, apague o arquivo.
- Há **um único espaço de save**. Começar um "Novo Jogo" e mudar de sala sobrescreve o save anterior.
- Os chefes derrotados e os inimigos comuns eliminados **não voltam** depois de salvar e carregar.
  Os inimigos invocados (por chefes ou pela Arena) não são salvos.

### 3.5 Mapa e diário

- **Mapa (M):** mostra as salas visitadas em azul, a atual em dourado e as vizinhas ainda desconhecidas como "?".
  A Gruta Secreta só aparece depois de visitada. Há também um minimapa no canto inferior direito.
- **Diário (TAB):** lista as missões em andamento (com o progresso) e as concluídas. O jogo mostra a missão ativa
  no canto superior direito da tela.

---

## 4. O mundo

### 4.1 Mapa

O mundo é uma grade. Cada sala tem uma posição `(coluna, linha)`:

```
Linha 0:   Arena(0,0)   Gruta(1,0)*                 Ninho(3,0)
Linha 1:   Vila(0,1) - Floresta1(1,1) - Clareira(2,1) - Caverna1(3,1) - Caverna2(4,1)    Castelo1(5,1) - Trono(6,1)
Linha 2:                                                               Pântano1(4,2) - Pântano2(5,2)

Ligações verticais: Vila-Arena, Floresta1-Gruta*, Caverna1-Ninho, Caverna2-Pântano1, Pântano2-Castelo1
* a Gruta só abre quando se destrói a pedra rachada da Floresta Sussurrante
```

Leitura em ordem de progresso:

```
Vila -> Floresta Sussurrante -> Clareira do Lobo -> Caverna Cristalina -> Salão do Golem
     -> Pântano Sombrio -> Lago da Serpente -> Corredor do Castelo -> Salão do Trono
Extras: Arena (norte da Vila), Gruta Secreta (norte da Floresta), Ninho das Aranhas (norte da Caverna)
```

### 4.2 As 12 salas

| Sala | Fase | Música | Destaques |
|---|---|---|---|
| Vila de Aurora | Início | Vila | Luna, Ferreiro Bram, santuário, placa de controles, poção |
| Arena de Aurora | Extra | Chefe | Mestre da Arena, 5 ondas de monstros |
| Floresta Sussurrante | 1 | Floresta | Eremita, 5 inimigos, baú (15 moedas), placa, pedra rachada, vagalumes |
| Gruta Secreta | Extra (secreta) | Caverna | Baú com o Arco e 12 flechas, 2 Slimes Gigantes, escura |
| Clareira do Lobo | 1 (chefe) | Chefe | Lobo Sombrio, santuário, Coração de Vida |
| Caverna Cristalina | 2 | Caverna | Espírito, santuário, Amuleto da Vida, placa, escura |
| Ninho das Aranhas | Extra (chefe opcional) | Chefe | Rainha Aranha e 3 aranhas, baú (25 moedas e 3 bombas), escuro |
| Salão do Golem | 2 (chefe) | Chefe | Golem de Pedra, santuário |
| Pântano Sombrio | 3 | Pântano | Viajante, santuário, baú com o Broche da Luna, névoa |
| Lago da Serpente | 3 (chefe) | Chefe | Serpente do Pântano, santuário, névoa |
| Corredor do Castelo | 4 | Castelo | Soldado Ferido, santuário, baú (coração e 2 poções) |
| Salão do Trono | 4 (chefe final) | Rei | Rei Sombrio, santuário, brasas no ar |

### 4.3 Passagens trancadas

| Passagem | Exige | Como conseguir |
|---|---|---|
| Clareira do Lobo para a Caverna | Chave Antiga | Derrotar o Lobo Sombrio |
| Salão do Golem para o Pântano | Fragmento do Cristal I | Derrotar o Golem de Pedra |
| Lago da Serpente para o Castelo | Fragmento do Cristal II | Derrotar a Serpente do Pântano |
| Floresta Sussurrante para a Gruta | Pedra rachada destruída | Usar uma bomba |

Ao tentar passar por uma porta trancada, o jogo avisa e empurra você de volta.

### 4.4 Chefes e recompensas

| Chefe | Sala | Recompensa |
|---|---|---|
| Lobo Sombrio | Clareira do Lobo | Chave Antiga |
| Golem de Pedra | Salão do Golem | Fragmento do Cristal I |
| Serpente do Pântano | Lago da Serpente | Fragmento do Cristal II |
| Rainha Aranha (opcional) | Ninho das Aranhas | Anel de Força (+1 de dano permanente) |
| Rei Sombrio | Salão do Trono | Cristal da Aurora |

Todo monstro derrotado também solta moedas. Ao entrar numa sala com chefe, aparece o **nome do chefe** na tela e,
durante a luta, uma **barra de vida** na parte de baixo.

---

## 5. Bestiário

Valores de vida para a dificuldade **Normal** (Fácil multiplica por 0,75 e Difícil por 1,35, arredondando, com mínimo de 1).
Todos causam 1 de dano ao encostar em você, exceto quando indicado.

### 5.1 Inimigos comuns

| Inimigo | Vida | Comportamento | Onde aparece |
|---|---|---|---|
| Slime | 2 | Lento, persegue | Floresta, Clareira, Arena |
| Slime Gigante | 6 | Lento e grande; ao morrer **se divide em 2 slimes** | Floresta, Gruta, Arena |
| Morcego | 1 | Muito rápido, persegue | Caverna, Arena |
| Esqueleto | 3 | Lento; **atira ossos** mirados em você | Caverna, Golem, Castelo, Arena |
| Sapo | 2 | **Pula** em rajadas e descansa entre os pulos | Pântano, Arena |
| Fantasma | 3 | **Atravessa paredes e obstáculos** | Pântano, Arena |
| Javali | 4 | **Investida**: para (pisca amarelo), trava a direção e dispara em linha reta | Floresta, Clareira, Arena |
| Aranha | 3 | **Investida** curta e rápida; guarda o Ninho | Ninho |
| Planta Carnívora | 4 | Fica parada e **cospe** projéteis mirados | Pântano |
| Mago Sombrio | 3 | **Teletransporta-se**, foge de quem chega perto e atira em leque de 3 | Lago, Castelo, Arena |
| Cavaleiro | 5 | Resistente, persegue | Castelo, Arena |

**Dica de leitura dos monstros que investem:** quando o inimigo "pisca amarelo", ele travou a direção. Desvie
para o lado (ou use SHIFT) e ataque quando ele descansar.

### 5.2 Chefes

| Chefe | Vida | Ataques e comportamento |
|---|---|---|
| Lobo Sombrio | 8 | Muito rápido, ataca no corpo a corpo |
| Golem de Pedra | 16 | Lento e enorme; dispara um **anel de 10 pedras** em todas as direções a cada 2 segundos |
| Serpente do Pântano | 18 | Rápida; cospe veneno em **leque de 3** tiros |
| Rainha Aranha | 20 | Investidas; atira em **leque de 5**; abaixo de 66% da vida **chama aranhas** (até 3 vivas) |
| Rei Sombrio | 24 | Três fases, descritas abaixo |

**As 3 fases do Rei Sombrio**

| Fase | Vida restante | O que ele faz |
|---|---|---|
| 1 | acima de 66% | Atira uma bola de energia mirada em você |
| 2 | de 66% a 33% | Atira em leque de 3 e **invoca 2 morcegos** de tempos em tempos |
| 3 | abaixo de 33% | Fica 40% mais rápido, atira em leque de 5 e a cada 3 rajadas solta um **anel de 12 tiros** |

Quando o Rei cai, os morcegos que ele invocou desaparecem.

---

## 6. Missões, Arena e Conquistas

### 6.1 Missões

Cada missão é oferecida por um personagem depois de você cumprir um requisito. Para aceitar, basta conversar.
Para entregar, volte a falar com o mesmo personagem quando o diário disser "PRONTA".

| Missão | Quem pede | Requisito para aparecer | Objetivo | Recompensa |
|---|---|---|---|---|
| Gosma para o Ferreiro | Ferreiro Bram | Ter a espada | Derrotar 5 slimes (comuns ou gigantes) | 20 moedas e 3 bombas |
| O Broche da Luna | Anciã Luna | Ter a Chave Antiga | Achar o broche no baú do Pântano | 30 moedas e +1 coração |
| Limpeza do Pântano | Viajante | Ter o Fragmento I | Derrotar 6 sapos ou fantasmas | 25 moedas e 12 flechas |
| Campeão de Aurora | Mestre da Arena | Ter a espada | Vencer as 5 ondas da Arena | 50 moedas e +1 coração |
| Terror das Teias | Espírito | Ter a espada | Derrotar a Rainha Aranha | 40 moedas e 2 bombas |

### 6.2 Arena de Aurora

Ao norte da vila. Fale com o **Mestre da Arena** para começar. São **5 ondas**; a próxima só vem quando você derrota
todos os monstros da atual:

| Onda | Inimigos |
|---|---|
| 1 | 3 Slimes |
| 2 | 2 Slimes e 3 Morcegos |
| 3 | 2 Esqueletos e 3 Sapos |
| 4 | 2 Cavaleiros, 1 Mago e 2 Fantasmas |
| 5 | 2 Slimes Gigantes, 2 Javalis e 2 Magos |

- Recompensa: 40 moedas na primeira vez e 25 nas seguintes (e a conquista "Campeão da Arena").
- Se você **sair da sala ou cair** no meio do desafio, a Arena reinicia.
- É possível repetir o desafio quantas vezes quiser, por moedas.

### 6.3 Conquistas (14)

Aparecem como avisos na tela ao serem desbloqueadas, ficam gravadas no arquivo de save e podem ser vistas no
menu inicial, em "Conquistas".

| Conquista | Como conseguir |
|---|---|
| Aventureiro | Receber a Espada de Aurora |
| Caçador | Derrotar 50 inimigos |
| Domador de Lobos | Derrotar o Lobo Sombrio |
| Quebra-Pedras | Derrotar o Golem de Pedra |
| Encantador de Serpentes | Derrotar a Serpente do Pântano |
| Caçadora de Aranhas | Derrotar a Rainha Aranha |
| Salvador de Aurora | Terminar o jogo |
| Ricaço | Ter 100 moedas ao mesmo tempo |
| Explorador | Visitar todas as 12 salas |
| Mira Certeira | Encontrar o Arco |
| Detonador | Destruir uma pedra rachada com uma bomba |
| Bom Vizinho | Concluir 3 missões |
| Campeão da Arena | Vencer as 5 ondas da Arena |
| Cliente Fiel | Comprar as 4 melhorias da loja (2 espadas e 2 corações) |

---

## 7. A história

**Prólogo.** Há muito tempo, a vila de Aurora vivia em paz, protegida pelo brilho do Cristal da Aurora. O Rei
Sombrio roubou o cristal e uma maldição apagou as cores da vila. O cristal se partiu e seus fragmentos foram
guardados por monstros. Você é a última esperança de Aurora.

**Desenvolvimento.**

1. A Anciã Luna entrega a Espada de Aurora e manda você atrás dos fragmentos.
2. O **Lobo Sombrio**, na floresta, guarda a chave da caverna.
3. O **Golem de Pedra** guarda o primeiro fragmento; o **Espírito** da caverna conta que ele solta pedras em todas as direções.
4. A **Serpente do Pântano** guarda o segundo fragmento; o Viajante avisa que os fantasmas atravessam paredes.
5. No castelo, o Soldado Ferido conta que o Rei "já não é ele mesmo" e que chama morcegos quando enfraquece.
6. O **Rei Sombrio** protege o último pedaço. Ao ser derrotado, seus últimos lamentos revelam algo sobre quem ele foi.

**Final.** Ao pegar o Cristal da Aurora, os fragmentos se unem e uma luz leva você de volta à vila, onde a Anciã Luna
revela uma verdade sobre o Rei Sombrio e a maldição se quebra. A tela final mostra suas estatísticas: dificuldade,
tempo de jogo, inimigos derrotados, vezes que você caiu, missões, conquistas e atributos.

Os diálogos **mudam conforme o seu progresso**: o mesmo personagem diz coisas diferentes dependendo do que você já
fez. Os textos têm efeito de "digitando"; aperte E uma vez para completar a frase e outra para avançar.

---

## 8. Arquitetura do código

### 8.1 Visão geral dos módulos

```
dados.py  ───────┐
   (conteúdo)    │
                 ├──> sprites.py ───┐
                 │      (arte)      │
                 └──────────────────┴──> main.py (motor: lógica, menus, desenho, loop)
```

- **`dados.py`** não depende de nada do jogo (só do `pygame.Rect`). Contém **o que existe** no jogo: salas, inimigos,
  missões, conquistas, dificuldades, ondas da Arena e todos os textos de história.
- **`sprites.py`** desenha a arte e carrega PNG opcionais de `assets/`. Usa o `dados.py` para saber quais
  personagens e inimigos existem.
- **`main.py`** é o **motor**: estado do jogo, regras, menus, entrada de teclado, desenho e o loop principal.

Essa separação é o coração do projeto: **conteúdo (dados) separado de lógica (código)**. Para criar um inimigo ou
uma sala nova, quase sempre basta editar o `dados.py`.

### 8.2 O loop principal

A função `main()` repete 60 vezes por segundo:

```
1. ler eventos do teclado          ->  tratar_evento()
2. atualizar o mundo               ->  atualizar()      (só quando o estado é "jogo")
3. desenhar na tela virtual        ->  desenhar()
4. copiar para a janela (com tremor de câmera, se houver) e exibir
```

O jogo desenha em uma **tela virtual** (`tela`) e depois a copia para a janela (`ecra`). Isso permite o
**tremor de câmera** (nas explosões, golpes e mortes de chefe) e a janela redimensionável.

### 8.3 Estados do jogo

A variável `G.estado` define o que acontece a cada quadro:

| Estado | O que é |
|---|---|
| `titulo` | Menu inicial |
| `dificuldade` | Escolha de Fácil/Normal/Difícil |
| `historia` | Prólogo |
| `jogo` | Jogando (único estado em que o mundo é atualizado) |
| `pausa` | Menu de pausa |
| `loja` | Loja do ferreiro |
| `diario` | Diário de missões |
| `mapa` | Mapa completo |
| `gameover` | Tela "Você caiu" |
| `fim` | Tela final com estatísticas |
| `conquistas`, `controles` | Telas de consulta |

Cada estado tem um tratador de teclas (`tecla_titulo`, `tecla_jogo`, ...), reunidos no dicionário `TECLAS`, e uma
rotina de desenho dentro de `desenhar()`. As telas de pausa, loja, diário, mapa e game over são desenhadas **por cima**
da cena do jogo (um véu escuro com o menu).

### 8.4 O objeto de estado `G`

Todo o estado vive em um único objeto, `G` (um `SimpleNamespace`). `novo_jogo()` zera tudo.

| Grupo | Variáveis principais |
|---|---|
| Jogador | `jogador` (retângulo), `facing` (direção), `hp`, `hp_max`, `dano`, `invul`, `dash`, `cd_*` (recargas) |
| Recursos | `moedas`, `pocoes`, `flechas`, `bombas`, `inventario` (conjunto de itens-chave) |
| Mundo | `sala`, `inimigos` (por sala), `drops` (itens soltos), `proj` (tiros inimigos), `flechas_voando`, `bombas_ativas` |
| Progresso | `coletados`, `abertos` (baús), `destruidas` (pedras), `mortos` (inimigos), `visitadas`, `intros` |
| Missões e Arena | `missoes`, `arena`, `arena_melhor`, `kills` |
| Diálogo e interface | `dialogo`, `aviso`, `toasts`, `banner`, `sel`, `volta`, `msg_loja` |
| Efeitos | `particulas`, `textos`, `explosoes`, `shake`, `fade`, `tick` |
| Configuração | `vol_musica`, `vol_efeitos`, `conquistas` (mantidos entre jogos) |
| Outros | `dificuldade`, `respawn`, `mortes`, `frames`, `tem_save` |

### 8.5 Mapa das funções do `main.py`

| Área | Funções principais |
|---|---|
| Save e perfil | `ler_arquivo`, `escrever_arquivo`, `carregar_perfil`, `salvar_jogo`, `carregar_jogo` |
| Áudio | `tocar` (música), `som` (efeitos), `aplicar_volume` |
| Utilidades | `mover_rect`, `solidos`, `quebrar`, `texto*`, `painel`, `mostrar_aviso`, `toast`, `faiscas`, `texto_flutuante`, `conquistar` |
| Inimigos | classe `Inimigo`, `ferir`, `morte_inimigo`, `soltar`, `sombra` |
| Ações do jogador | `atacar`, `atirar_flecha`, `colocar_bomba`, `explodir`, `esquivar`, `usar_pocao`, `machucar`, `receber`, `pegar` |
| Interações | `abrir_dialogo`, `avancar_dialogo`, `executar_acao`, `interagir`, `abrir_bau`, `descansar`, `alvo_interacao` |
| Missões e falas | `falas`, `missao_pronta`, `progresso`, `aceitar_missao`, `entregar_missao` |
| Loja | `itens_loja`, `comprar` |
| Arena | `iniciar_arena`, `atualizar_arena`, `concluir_arena`, `resetar_arena` |
| Estado | `novo_jogo`, `entrar_sala`, `continuar`, `terminar_jogo` |
| Atualização | `atualizar` (movimento, inimigos, tiros, itens, troca de sala) |
| Teclado | `tratar_evento`, `tecla_*`, `TECLAS` |
| Desenho | `desenhar`, `desenhar_jogo`, `desenhar_hud`, `desenhar_mapa`, `desenhar_dialogo`, `tela_*`, `desenhar_ambiente`, `desenhar_escuridao` |

### 8.6 Técnicas importantes (boas para explicar)

- **Colisão por eixo (`mover_rect`):** o retângulo se move primeiro em X, depois em Y, e é empurrado para fora de qualquer
  obstáculo. Isso permite deslizar ao longo das paredes.
- **Inteligência dos inimigos (classe `Inimigo`):** cada tipo escolhe um comportamento pelo campo `ia`
  (`perseguir`, `pulo`, `fantasma`, `investida`, `parado`, `teleporta`). A investida é uma pequena **máquina de estados**:
  `normal` -> `preparo` -> `investida` -> `descanso`.
- **Padrões de tiro:** `mira` (1 tiro), `leque` (vários tiros abertos) e `anel` (tiros em círculo), calculados com
  seno e cosseno.
- **Chefe com fases:** o Rei troca de golpe conforme a porcentagem de vida restante (`fase()`).
- **Invocação genérica:** qualquer inimigo com o campo `invoca` chama ajudantes (usado pelo Rei e pela Rainha).
- **Posição com decimais:** inimigos lentos guardam `fx` e `fy` em decimais e só então arredondam para o retângulo.
- **Itens de forma genérica (`receber`):** chão, baús, loja e recompensas de missão usam a mesma função.
- **Diálogos com ações (`da`):** cada diálogo pode terminar numa ação (`espada`, `loja`, `missao:<id>`,
  `entregar:<id>`, `arena`, `final`), executada por `executar_acao`.
- **Missões orientadas a dados:** o tipo (`matar`, `item`, `arena`) define como o progresso é contado.
- **Escuridão:** um véu escuro com um "buraco" de luz em volta do jogador (modo de mistura `BLEND_RGBA_MIN`).
- **Acabamento:** sombras, balanço ao andar, partículas, números flutuantes, tremor de câmera, transição entre salas
  (fade), vinheta vermelha com pouca vida, vagalumes, poeira, brasas e névoa.
- **Save em JSON:** o estado é convertido em um dicionário simples e gravado como texto (ver 9.4).

---

## 9. Formatos de dados

### 9.1 Sala (`SALAS` em `dados.py`)

As salas são criadas com a função `sala(...)`:

| Campo | Significado |
|---|---|
| `nome` | Nome exibido no HUD e no mapa |
| `pos` | Posição `(coluna, linha)` no mapa |
| `cor`, `cor_parede` | Cor do chão e das paredes |
| `musica` | Arquivo de música, por exemplo `"floresta.mp3"` (o jogo procura `.mp3`, `.ogg` e `.wav`) |
| `lados` | Letras das bordas com passagem: `N`, `S`, `E`, `O` |
| `obstaculos` | Lista de `(Rect, estilo)`. Estilos: `arvore`, `pedra`, `casa`, `agua`, `tronco`, `pilar` |
| `rachadas` | Lista de `(uid, Rect)`: pedras que uma bomba destrói |
| `npcs` | Personagens (`npc(...)`) |
| `itens` | Itens fixos no chão (`item(...)`) |
| `objetos` | Baús, placas e santuários (`bau`, `placa`, `santuario`) |
| `inimigos` | Lista de `(tipo, x, y)` |
| `saidas` | Passagens (`saida(lado, destino, requer, msg)`) |
| `intro` | Texto mostrado na primeira vez que você entra |
| `ambiente` | Efeito de ar: `vagalumes`, `poeira`, `brasas` ou `nevoa` |
| `escuro` | `True` para a sala escura |

### 9.2 Inimigo (`TIPOS` em `dados.py`)

| Campo | Significado |
|---|---|
| `nome`, `hp`, `vel`, `dano`, `tam` | Nome, vida, velocidade (pixels por quadro), dano de contato, tamanho |
| `alcance` | Distância em que começa a perseguir (e a atacar) |
| `drop` | Chance de soltar poção |
| `moedas` | Faixa `(mínimo, máximo)` de moedas soltas |
| `cor` | Cor das partículas ao morrer |
| `ia` | `perseguir` (padrão), `pulo`, `fantasma`, `investida`, `parado`, `teleporta` |
| `ataque` | `{"padrao": mira/leque/anel, "intervalo", "vel", "qtd", "cor"}` |
| `investida` | `{"alcance", "preparo", "vel", "duracao", "descanso"}` (para `ia: investida`) |
| `invoca` | `{"tipo", "qtd", "intervalo", "max", "fase_min"}` |
| `divide` | `("tipo", quantidade)`: o que nasce quando ele morre |
| `boss` | `True` para chefes (barra de vida, empurrão menor, sem drops comuns) |

### 9.3 Missão (`MISSOES`)

| Campo | Significado |
|---|---|
| `nome`, `desc` | Título e descrição no diário |
| `tipo` | `matar`, `item` ou `arena` |
| `alvo` | Tipos de inimigo que contam (para `matar`) |
| `item` | Item procurado (para `item`) |
| `qtd` | Quantidade exigida |
| `requer` | Item que você precisa ter para a missão ser oferecida |
| `recompensa` | Dicionário `{tipo_de_item: quantidade}` |

Os textos (`oferta`, `lembrete`, `entrega`) ficam em `MISSAO_TEXTOS`, e `QUEST_NPC` liga cada personagem à sua missão.

### 9.4 Arquivo de save (JSON)

```json
{
  "conquistas": ["aventureiro", "lobo"],
  "config": {"musica": 0.5, "efeitos": 0.6},
  "jogo": {
    "versao": 5, "sala": "caverna1", "x": 40, "y": 300,
    "hp": 6, "hp_max": 8, "dano": 2, "pocoes": 1, "moedas": 77, "flechas": 5, "bombas": 2,
    "compras": {"dano": 1, "coracao": 0}, "conheceu_ferreiro": true,
    "inventario": ["espada", "chave", "arco"],
    "coletados": [], "abertos": [], "destruidas": [], "intros": [], "visitadas": [],
    "missoes": {"slimes": {"estado": "ativa", "prog": 3}},
    "mortos": ["floresta2:2"], "kills": {"slime": 12},
    "mortes": 1, "frames": 12345, "dificuldade": "normal",
    "respawn": ["floresta2", 74, 464], "arena_melhor": 0
  }
}
```

Os inimigos recebem um identificador `"<sala>:<posição na lista>"`, e é essa lista de `mortos` que impede que eles voltem.
A chave `conquistas` e `config` valem para todos os jogos; só `jogo` representa a partida atual.

---

## 10. Como estender o jogo

### 10.1 Criar um inimigo novo

1. Em `dados.py`, adicione uma entrada em `TIPOS`:

```python
"escorpiao": {"nome": "Escorpião", "hp": 3, "vel": 1.6, "dano": 1, "tam": 26, "alcance": 300,
              "drop": 0.3, "moedas": (2, 3), "cor": (200, 150, 60), "ia": "investida",
              "investida": {"alcance": 180, "preparo": 20, "vel": 6.0, "duracao": 16, "descanso": 35}},
```

2. Em `sprites.py`, na função `sprite_inimigo`, adicione um `elif tipo == "escorpiao":` que desenha o sprite
   (ou coloque um `inimigo_escorpiao.png` em `assets/`).
3. Em `dados.py`, coloque `("escorpiao", 300, 200)` na lista `inimigos` de alguma sala.

Para o inimigo atirar, acrescente `"ataque": {"padrao": "mira", "intervalo": 120, "vel": 3.2, "qtd": 1, "cor": (255, 255, 255)}`.
Para um chefe, use `"boss": True` e, se quiser uma recompensa, adicione-o a `RECOMPENSAS`.

### 10.2 Criar uma sala nova

1. Em `dados.py`, crie a entrada em `SALAS` com a função `sala(...)`. Escolha uma `pos` livre no mapa.
2. Ligue com `saida("E", "nome_da_outra_sala")` e crie a **saída de volta** na outra sala (lado oposto).
3. Para trancar: `saida("E", "sala_x", "chave", "Mensagem quando estiver trancada")`.
4. Rode `python testes.py`: o teste 0 confere se as saídas têm volta, se a posição no mapa bate, e se nada nasce
   dentro de uma parede.

### 10.3 Criar uma missão nova

1. Em `MISSOES`, adicione a missão (tipo, alvo, quantidade, `requer`, `recompensa`).
2. Em `MISSAO_TEXTOS`, escreva `oferta`, `lembrete` e `entrega`.
3. Em `QUEST_NPC`, ligue um personagem à missão, por exemplo `"eremita": "minha_missao"`.

### 10.4 Criar uma conquista nova

1. Em `CONQUISTAS`, acrescente `("id", "Nome", "Descrição")`.
2. No ponto do código em que a condição acontece, chame `conquistar("id")`.

### 10.5 Criar um item novo

1. Dê um nome em `NOMES_ITEM` (`dados.py`) e uma cor em `COR_ITEM` (`sprites.py`).
2. Desenhe o ícone em `desenhar_item` (`sprites.py`).
3. Defina o efeito em `receber` (`main.py`).
4. Use o item em baús (`bau(..., [("meu_item", 1)])`), em recompensas de missão ou em `RECOMPENSAS`.

### 10.6 Novo personagem (NPC) e diálogo

1. Crie o personagem na sala com `npc("id", "Nome", x, y, cor_roupa, cor_cabelo)`.
2. Em `falas()` (`main.py`), adicione `if npc_id == "id": return [linhas], False, None`.
   O formato `"Nome: texto"` mostra o nome do falante numa etiqueta acima da caixa de texto.

### 10.7 Ajustar a dificuldade e o equilíbrio

| O que mudar | Onde |
|---|---|
| Corações iniciais e vida dos monstros por dificuldade | `DIFICULDADES` em `dados.py` |
| Vida e velocidade de cada monstro | `TIPOS` em `dados.py` |
| Preços da loja | `itens_loja()` em `main.py` |
| Velocidade do jogador | o número `4` nas linhas `dx` e `dy` de `atualizar()` |
| Alcance da luz nas salas escuras | `LUZ_RAIO` e `criar_luz()` em `main.py` |
| Ondas da Arena | `ARENA_ONDAS` e `ARENA_SPAWNS` em `dados.py` |

---

## 11. Áudio e imagens

### 11.1 Música e efeitos

`gerar_musicas.py` **sintetiza** o áudio com numpy: cada nota é uma onda (seno, harmônicos ou quadrada) com envelope
de ataque e decaimento. Gera **9 trilhas** e **16 efeitos** em `.wav`:

| Trilha | Onde toca |
|---|---|
| `menu` | Menu inicial |
| `vila` | Vila |
| `floresta` | Floresta Sussurrante |
| `caverna` | Caverna Cristalina e Gruta |
| `pantano` | Pântano Sombrio |
| `castelo` | Corredor do Castelo |
| `chefe` | Arena e salas de chefe (Clareira, Golem, Serpente, Ninho) |
| `rei` | Salão do Trono |
| `fim` | Final do jogo |

Efeitos: `ataque`, `acerto`, `dano`, `item`, `moeda`, `pocao`, `morte`, `chefe`, `compra`, `erro`, `flecha`, `bomba`,
`dash`, `bau`, `conquista` e `menu` (arquivos `sfx_<nome>.wav`).

Para regerar: `pip install numpy` e `python gerar_musicas.py`.

**Trocar por músicas suas:** coloque um arquivo com o mesmo nome em `.mp3` ou `.ogg` em `assets/` (por exemplo
`vila.mp3`). O jogo procura nesta ordem: `.mp3`, `.ogg`, `.wav`. O volume pode ser mudado no menu de pausa.

### 11.2 Imagens

Os sprites são desenhados em código (`sprites.py`). Para ter arquivos editáveis:

```bash
python gerar_imagens.py
```

Isso salva 25 PNG em `assets/` (`jogador`, `espada`, `npc_*`, `inimigo_*`). Depois é só **substituir** qualquer PNG
mantendo o nome: o jogo carrega seu arquivo e o **redimensiona sozinho** se o tamanho for diferente. Se você apagar um
PNG, o jogo volta ao desenho padrão.

Itens, objetos (baús, placas, santuários) e obstáculos continuam sendo desenhados por código.

---

## 12. Testes

O arquivo `testes.py` roda a bateria de testes **sem abrir janela e sem som**, usando um save temporário (o seu save
verdadeiro não é tocado):

```bash
python testes.py
```

| Bloco | O que verifica |
|---|---|
| 0 | Estrutura do mapa: toda saída tem volta, posições coerentes, nada nasce dentro de paredes, pontos de retorno livres |
| 1 | Menus: novo jogo, dificuldade, pausa com volume, controles, diário e mapa |
| 2 | Dificuldade altera a vida dos monstros |
| 3 | Loja (5 itens), bomba abre a gruta secreta, baú entrega o arco, conquistas |
| 4 | Flecha acerta o inimigo; o desvio move e dá invencibilidade |
| 5 | Slime Gigante se divide; Javali investe; Planta atira; Mago se teletransporta; Fantasma e Sapo se movem |
| 6 | Lobo, Golem, Serpente e Rainha derrotados com seus prêmios; Rei (fases e invocação), cristal e final |
| 7 | Missões: matar, item e entrega com recompensa |
| 8 | Arena: 5 ondas, recompensa, missão e reinício ao sair |
| 9 | Santuário, game over e retorno, save e load completos |
| 10 | 600 quadros em cada uma das 12 salas com espada, arco, bombas e desvio |
| 11 | Todas as telas desenham sem erro |

Ao final, aparece `TODOS OS TESTES PASSARAM`. **Rode os testes depois de editar o `dados.py`**: ele aponta erros
comuns (saída sem volta, inimigo dentro da parede etc.) antes de você descobrir jogando.

---

## 13. Gerar o executável (.exe)

No **Windows**:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name FlorestaDeAurora --add-data "assets;assets" main.py
```

- O arquivo sai em `dist/FlorestaDeAurora.exe`; ele já leva a pasta `assets/` embutida.
- O `sprites.py` procura os arquivos em `sys._MEIPASS`, que é onde o PyInstaller descompacta tudo.
- No Mac e no Linux, troque `"assets;assets"` por `"assets:assets"` (e o executável sai sem `.exe`).
- `--windowed` esconde o terminal. Para ver mensagens de erro, gere **sem** essa opção.
- Pode demorar alguns segundos para abrir na primeira vez.
- Antivírus às vezes reclamam de programas feitos com PyInstaller (falso positivo).
- O save e as conquistas ficam na pasta do usuário, então continuam funcionando no `.exe`.

**Windows 11 e o Controle Inteligente de Aplicativos.** Esse recurso bloqueia programas sem assinatura digital, e o
`.exe` gerado não é assinado. Se ele for bloqueado, rode o jogo com `python main.py` (ou desligue o recurso por sua
conta e risco). Assinar o `.exe` exige um certificado pago de assinatura de código.

---

## 14. Solução de problemas

| Problema | Causa provável | Solução |
|---|---|---|
| `No module named 'pygame'` | pygame não instalado | `pip install pygame` |
| `No module named 'dados'` ou `'sprites'` | Arquivos separados | Mantenha `main.py`, `dados.py` e `sprites.py` na mesma pasta |
| Sem música/efeitos | Pasta `assets/` ausente ou áudio desligado | Coloque `assets/` ao lado do `main.py` |
| "Áudio indisponível" | Sem placa de som | O jogo roda sem som |
| Jogo lento | Computador fraco | Feche outros programas e use a janela em tamanho normal |
| Janela não redimensiona | Driver sem suporte | O jogo cai para o modo de janela fixa automaticamente |
| `numpy` não encontrado | Só afeta `gerar_musicas.py` | `pip install numpy` |
| Acentos errados | Arquivo salvo em outra codificação | Salve os `.py` em UTF-8 |
| Save corrompido | Edição manual do JSON | Apague `.floresta_de_aurora.json` |
| Quero as conquistas de volta ao zero | — | Apague `.floresta_de_aurora.json` |

---

## 15. Limitações conhecidas e ideias futuras

**Limitações conhecidas (para ser transparente):**

- Os **testes automáticos** cobrem as regras e o fluxo completo do jogo, mas **nada substitui jogar**: o equilíbrio de
  dificuldade (vida dos chefes, dano, preços) foi ajustado por estimativa e pode pedir ajustes depois de jogar.
- A **música e os efeitos** são sintetizados de forma simples (estilo "chiptune/ambiente"); não são composições
  profissionais. Dá para trocar por arquivos `.mp3`/`.ogg` seus.
- Os sprites não têm animação quadro a quadro (há apenas balanço, sombra e o giro da espada).
- Só há **teclado** (sem controle/gamepad) e **um espaço de save**.
- Os chefes se recuperam por completo quando você cai, e inimigos invocados não são salvos.

**Ideias futuras:** vários espaços de save, controle de videogame, novas armas e magias, árvore de habilidades,
mais fases e chefes opcionais, animação de sprites, minimapa com ícones de itens, modo cooperativo local e tradução
para outros idiomas.

---

## 16. Histórico de versões

| Versão | O que trouxe |
|---|---|
| 1 | Protótipo: uma sala, jogador, música e a primeira tela de história |
| 2 | Aventura top-down com salas, NPC, diálogo e itens |
| 3 | Combate, inimigos, chefes, poções, game over e primeira história com final |
| 4 | 9 salas em 4 fases, loja, moedas, espada com imagem, efeitos sonoros, partículas e `.exe` |
| 5 | Esta versão: código em módulos, 12 salas, save/load, menus, 3 dificuldades, arco, bombas, desvio, baús, santuários, segredos, 5 missões, Arena, 14 conquistas, mapa, escuridão, névoa e 6 novos inimigos |

---

## 17. Resumo para a apresentação

**Roteiro sugerido (8 a 10 minutos)**

1. **Ideia (1 min):** jogo de aventura em Python com pygame, com história, fases, chefes e muita interação.
2. **Demonstração (4 min):** menu e dificuldade; fale com a Luna; loja do ferreiro; use a **bomba** na pedra rachada para
   abrir a gruta e pegar o **arco**; mostre o **desvio**; entre numa **caverna escura**; lute com um chefe (o Golem
   mostra bem o padrão de tiros); mostre o **mapa**, o **diário** e uma **conquista**.
3. **Como foi feito (3 min):**
   - separação em `dados.py` (conteúdo), `sprites.py` (arte) e `main.py` (motor);
   - o loop (ler, atualizar, desenhar) e os estados do jogo;
   - a classe `Inimigo` e as IAs (perseguir, investida, teleporte);
   - padrões de tiro e as fases do Rei;
   - save em JSON e testes automáticos.
4. **Áudio e imagens (1 min):** tudo gerado por código, sem arquivos baixados.
5. **Melhorias futuras (30 s):** gamepad, mais armas e fases, animação de sprites.

**Números para citar:** 12 salas, 16 tipos de inimigos, 5 chefes, 5 missões, 14 conquistas, 3 dificuldades,
8 santuários, cerca de 2.700 linhas de código do jogo e uma bateria de testes automáticos.
