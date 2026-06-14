# Casos de Teste — Simulador de Memória (FIFO vs. LRU)

Conjunto de arquivos de entrada para validar o `simulador_memoria.py` além do
`entrada.txt` padrão. Cada arquivo segue o mesmo formato do enunciado:
a **primeira linha é o número de frames** e as linhas seguintes são as
**páginas acessadas** (um número por linha; comentários iniciados por `#` e
linhas em branco são ignorados).

## Como executar

```bash
# Roda FIFO e LRU (padrão "AMBOS")
python simulador_memoria.py casos_teste/01_gabarito_oficial.txt

# Roda apenas um algoritmo
python simulador_memoria.py casos_teste/02_belady_3frames.txt FIFO
python simulador_memoria.py casos_teste/02_belady_3frames.txt LRU
```

## Resultados de referência

Valores obtidos com a implementação atual (validada contra o gabarito oficial
do enunciado). Use-os para conferir se a lógica continua correta após mudanças.

| Arquivo | Frames | Acessos | FIFO (faults / taxa) | LRU (faults / taxa) |
|---|---|---|---|---|
| `01_gabarito_oficial.txt` | 3 | 12 | 10 / 83.33% | 9 / 75.00% |
| `02_belady_3frames.txt` | 3 | 12 | 9 / 75.00% | 10 / 83.33% |
| `03_belady_4frames.txt` | 4 | 12 | 10 / 83.33% | 8 / 66.67% |
| `04_localidade_lru_vence.txt` | 3 | 12 | 8 / 66.67% | 5 / 41.67% |
| `05_loop_thrashing.txt` | 3 | 12 | 12 / 100.00% | 12 / 100.00% |
| `06_working_set_cabe.txt` | 3 | 10 | 3 / 30.00% | 3 / 30.00% |
| `07_um_frame.txt` | 1 | 8 | 5 / 62.50% | 5 / 62.50% |
| `08_formato_livre.txt` | 3 | 12 | 10 / 83.33% | 9 / 75.00% |

## O que cada caso demonstra

- **01 — Gabarito oficial:** cadeia de referência do enunciado. FIFO 10 / LRU 9.
  Serve de "teste de regressão" principal.
- **02 + 03 — Anomalia de Belády:** a *mesma* cadeia rodada com 3 e depois 4
  frames. No **FIFO**, passar de 3 → 4 frames **aumenta** os page faults
  (9 → 10): é a anomalia de Belády. O **LRU** (algoritmo de pilha) não sofre o
  efeito e melhora com mais frames (10 → 8).
- **04 — Localidade temporal:** a página `4` é reusada com frequência. O LRU a
  mantém na memória, o FIFO a expulsa só por ser "antiga" na fila → LRU gera
  bem menos faults (5 vs 8). Mostra a vantagem prática do LRU.
- **05 — Thrashing:** working set (4 páginas) maior que a memória (3 frames) em
  laço sequencial → 100% de faults nos dois algoritmos. Limite teórico.
- **06 — Working set cabe:** 3 páginas distintas em 3 frames; após a carga
  inicial tudo vira Hit (apenas 3 faults). FIFO == LRU.
- **07 — Um frame (borda):** menor memória possível; valida acessos repetidos
  consecutivos (Hit) e substituição imediata.
- **08 — Formato livre (parser):** mesma cadeia do gabarito, porém com vários
  números por linha, espaçamento irregular e comentário inline. Prova que o
  parser robusto produz o mesmo resultado do formato "um número por linha".
