# Trabalho 5 — Pinball com colisão por polígonos (SAT)

Fork de `Trab4/polygonCollision`. É um pinball onde a bola sofre gravidade
e colide com o cenário usando o SAT que já tínhamos no Trab4, só que
estendido pra funcionar entre **círculo (a bola)** e **polígono**
(a maioria dos obstáculos de um pinball não é retângulo nem círculo).

## Como rodar

```bash
pip install pygame
python3 main.py
```

## Controles

| Tecla | Ação |
|---|---|
| `←` / `A` | Flipper esquerdo |
| `→` / `D` / `L` | Flipper direito |
| `ESPAÇO` (segurar/soltar) | Carrega e lança a bola |
| `R` | Reinicia |
| `ESC` | Sai |

## O que veio do Trab4 e o que é novo

- **`shape.py`** — `Polygon` é o mesmo do Trab4 (bounding box, teste de
  convexidade, decomposição convexa, ponto-dentro-do-polígono). Tirei
  o código de arrastar vértice com o mouse (não precisava aqui) e
  adicionei `set_points`, usado pelos flippers pra atualizar a forma
  a cada frame que giram.
- **`collision.py`** — `polygon`/`convex`/`axes`/`project` são os
  mesmos do Trab4. O que é novo é `circle_polygon`: mesmo SAT, mas
  testando também o eixo do centro do círculo até o vértice mais
  próximo (senão erra quando quem toca primeiro é um canto), e
  projetando o círculo como `centro ± raio`. Funciona com qualquer
  polígono, inclusive côncavo (via decomposição).
- **`ball.py`** — física da bola: gravidade, integração, velocidade
  máxima, rastro visual.
- **`flipper.py`** — o flipper é um trapézio afunilado (não é
  retângulo nem círculo), gira em torno de um pivô. Ao colidir, além
  de refletir, soma a velocidade tangencial do ponto de impacto
  (ω × r) na bola — é o que dá o "chute".
- **`entities.py`** — `Wall` (só reflete), `Bumper` (hexágono: reflete
  e soma pontos) e `BonusTrigger` (pentágono: não reflete, só detecta
  que a bola passou por dentro via `point_inside` e aplica o efeito).
- **`main.py`** — monta a mesa, o loop do jogo, o lançador e o placar.

## Onde cada regra do enunciado aparece

- **Regiões que não são só retângulo/círculo:** cantos triangulares,
  defletor do lançador, slingshots (triângulos), bumpers (hexágonos),
  zona-bônus (pentágono) e os flippers (trapézios).
- **Efeito que NÃO muda a trajetória:** a `BonusTrigger` (zona verde).
  A bola passa reto por dentro; ao entrar, ganha pontos e um pequeno
  boost de velocidade *na mesma direção* em que já estava indo — a
  colisão aqui só detecta a passagem, nunca reposiciona/reflete a bola.
- **Efeito que impede/reflete o movimento:** paredes, slingshots e
  flippers refletem a bola. Os bumpers fazem as duas coisas ao mesmo
  tempo: refletem (com restituição > 1, "chutando" a bola pra longe)
  e somam pontos, como um bumper de pinball de verdade.

## Limitações conhecidas

- A calha do lançador se reconecta ao campo por cima sem válvula
  unidirecional; em teoria dá pra bola voltar pra calha depois de já
  estar em jogo (raro na prática).
- Sem som.

## Repaginação visual ("Neon Arcade")

A estética foi refeita do zero, mas **física, colisão (SAT), pontuação,
controles e regras de jogo continuam exatamente como antes** — só o
desenho na tela mudou.

- **`fx.py`** (novo) — utilitários de renderização: preenchimento em
  degradê recortado na forma do polígono (`gradient_polygon_surface`),
  brilho neon ao redor de contornos (`draw_polygon_glow`), brilho radial
  em cache pra bola/bumpers/zona-bônus (`get_radial_glow`), texto com
  halo (`draw_text_glow`) e painéis com cantos arredondados.
- **Mesa**: paredes, defletor e slingshots ganharam degradê + contorno
  neon (ciano, roxo e magenta); bumpers e a zona-bônus pulsam
  suavemente e piscam mais forte ao serem acionados; flippers têm
  gradiente cyan e brilham mais quando ativos.
- **Bola**: acabamento "cromado" (destaque especular + sombra) com
  rastro e brilho externo em vez do círculo liso original.
- **Fundo**: degradê roxo/azul escuro com campo de estrelas cintilante,
  no lugar do preenchimento sólido cinza-escuro.
- **HUD/telas**: placar e vidas com texto neon sobre uma barra
  translúcida; medidor de carga do lançador virou uma barra em degradê
  ciano→magenta com brilho; telas de "pronto" e "fim de jogo" ganharam
  painel com cantos arredondados e borda neon.
