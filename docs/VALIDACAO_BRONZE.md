# Validação da camada Bronze: TC3 Grupo 21

**Data:** 20/08/2026, revisado em 04/09/2026 · **Responsável:** Caio (dono da Silver/Gold)
**Insumo:** os três CSVs exportados da Bronze pelo Gusthavo
(`bronze_dw_state_data_2023.csv`, `_2024.csv`, `_2025.csv`)

Conferência feita antes de escrever a Silver, para não construir a camada em
cima de premissa errada. Tudo abaixo foi medido nos arquivos, não inferido.

---

## Resumo

| | |
|---|---|
| Estrutura das 3 edições | ✅ bate com o documentado |
| Chave primária | ✅ íntegra (3 duplicatas exatas, seguras de remover) |
| `inferSchema` | ✅ **pendência resolvida**, binários voltaram a `0`/`1` |
| Achados novos que a Silver precisa tratar | ⚠️ **3** (um deles silencioso e grave) |
| Ajuste necessário na Bronze | nome dos arquivos (ago) e a normalização, que era de Silver (set) |

---

## 1. Estrutura: confere

| Edição | Linhas | Colunas | Documentado | Chave | Nulos na chave |
|---|---|---|---|---|---|
| 2023-2024 | 5.293 | 399 | 5.293 × 399 ✅ | `id` | 0 |
| 2024-2025 | 5.217 | 403 | 5.217 × 403 ✅ | `token_user` | 0 |
| 2025-2026 | 3.495 | 388 | 3.495 × 388 ✅ | `token_user` | 0 |

**Contraprova de identidade**, interseção de chaves entre edições:

```
2023-2024 ∩ 2024-2025 = 0
2023-2024 ∩ 2025-2026 = 0
2024-2025 ∩ 2025-2026 = 0
```

Zero em todos os pares. Não há chance de duas edições serem o mesmo arquivo.

**Coluna que confirma o ano de coleta**, identificando a edição pelo conteúdo
e não pelo nome do arquivo:

| Arquivo | Coluna | Data de envio (min → max) |
|---|---|---|
| `..._2023.csv` | `empresa_trabalha_passou_layoff_2023` | não coletada nesta edição |
| `..._2024.csv` | `layoff_2024` | 14/10/2024 → 18/12/2024 |
| `..._2025.csv` | `layoff_2025` | 20/10/2025 → 22/12/2025 |

As datas de envio caem 100% dentro do ano da coleta (5.217/5.217 e 3.495/3.495).
Isso valida a injeção do `ano_pesquisa` na Silver para duas das três edições.

---

## 2. Pendências que já estão resolvidas

**`inferSchema`, resolvido.** Varri o domínio de todas as colunas das três
edições procurando `0.0`/`1.0`:

| Edição | Binárias gravadas como `0.0`/`1.0` | Binárias como `0`/`1` |
|---|---|---|
| 2023-2024 | **0** | 329 |
| 2024-2025 | **0** | 323 |
| 2025-2026 | **0** | 316 |

Nenhuma coluna float disfarçada. A troca para `inferSchema=false` surtiu efeito.

**A edição 2025-2026 rodou.** 3.495 × 388, com o dicionário da 2024-2025
reaproveitado: 384 das 388 colunas casam por nome exato com a 2024-2025.

**Cobertura de nomes entre edições** (match exato, já com os nomes semânticos):

```
2023-2024 ∩ 2024-2025 = 336
2024-2025 ∩ 2025-2026 = 384
comuns às três        = 327
```

327 colunas com o mesmo nome nas três edições, base folgada para as ~20 da Silver.

---

## 3. Achados novos

### ⚠️ 3.1 `uf` muda de significado entre edições: o mais perigoso

Este é silencioso: não gera erro, não gera nulo, só produz número errado.

| Edição | `uf` bate com `estado` (moradia) | `uf` bate com `estado_origem` (nascimento) |
|---|---|---|
| 2023-2024 | **99,9%** | não se aplica (a edição não pergunta origem) |
| 2024-2025 | **99,9%** | 2,9% |
| 2025-2026 | 3,8% | **100,0%** |

Em 2025-2026 a coluna `uf` é o estado **onde a pessoa nasceu**. Quem tomar
`uf` como "onde mora" nas três edições, que é a leitura natural do nome, mistura duas perguntas diferentes e erra a
análise regional, que é justamente a pergunta de negócio 6.

O que aconteceu: a rotina de renomeação do ETL gera `_1` quando o nome colide.
Em 2024-2025 saíram `uf` (moradia) e `uf_1` (origem); em 2025-2026 a ordem das
perguntas mudou e saíram `uf` (origem) e `uf_moradia` (moradia).

**Tratamento na Silver:** não usar `uf` da Bronze. A sigla é derivada de
`estado` e `estado_origem`, que são estáveis e explícitos nas três edições.
Conferido: `regiao` bate com a região calculada a partir de `estado` em 99,9%
nas três, e `regiao_origem` bate com `estado_origem` em 99,9%/100%.

### ⚠️ 3.2 Seis colunas vêm `TRUE`/`FALSE` só em 2024-2025

| Coluna | 2023-2024 | 2024-2025 | 2025-2026 |
|---|---|---|---|
| `vive_brasil` | `0`/`1` | **`FALSE`/`TRUE`** | `0`/`1` |
| `vive_estado_formacao` | ausente | **`FALSE`/`TRUE`** | `0`/`1` |
| `gestor` | `0`/`1` | **`FALSE`/`TRUE`** | `0`/`1` |
| `satisfacao_empresa_atual` | `0`/`1` | **`FALSE`/`TRUE`** | `0`/`1` |
| `empresa_possui_datalake` | `0`/`1` | **`FALSE`/`TRUE`** | `0`/`1` |
| `empresa_possui_dw` | `0`/`1` | **`FALSE`/`TRUE`** | `0`/`1` |

Como a Bronze é toda string, o `union` aceita as duas grafias sem reclamar.
Um `WHERE gestor = '1'` derrubaria os 1.045 gestores de 2024-2025 e ninguém
veria erro nenhum, só um buraco no meio da série.

**Tratamento na Silver:** mapa booleano único, aplicado às três edições.

### ⚠️ 3.3 Dois rótulos com erro de digitação na origem

| Edição | Valor | Deveria ser | Ocorrências |
|---|---|---|---|
| 2023-2024 | `de_R$_101/mes_a_R$_2.000/mes` | `de_R$_1.001/mes_a_R$_2.000/mes` | 1 |
| 2025-2026 | `de_R$_25.001/mes_a_R$_3000/mes` | `de_R$_25.001/mes_a_R$_30.000/mes` | 1 |

São 2 registros em 14.005, mas viram categoria órfã no `GROUP BY` e aparecem
como faixa salarial inexistente no gráfico. Corrigidos na Silver, com o de-para
registrado em `config_silver.py`.

---

## 4. Chaves duplicadas: seguras de remover

| Edição | Chaves repetidas | Colunas em que as linhas diferem |
|---|---|---|
| 2024-2025 | 2 | **0** |
| 2025-2026 | 1 | **0** |

São linhas 100% idênticas em todas as 403/388 colunas, submissão duplicada,
não respondente distinto. `dropDuplicates()` não perde informação.

Total após dedup: **5.293 + 5.215 + 3.494 = 14.002 respondentes.**

---

## 5. Categorias que mudaram entre edições

Não são erro: a pesquisa mudou. Mas viram série temporal falsa se ninguém marcar.

| Coluna | O que mudou |
|---|---|
| `nvl` (senioridade) | 2025-2026 criou **`Especialista/Staff+`** (349 respostas). Sem marcação, parece migração de sênior para especialista. |
| `cargo_atual` | 2023-2024 tinha `Engenheiro_de_Dados/Arquiteto_de_Dados/...` numa opção só; a partir de 2024-2025 arquiteto virou opção separada. Some `Analista_de_Inteligencia_de_Mercado`, `DBA` e `Economista` depois de 2023-2024. |
| `area_formacao` | 2025-2026 criou `Ciencia_de_Dados_/_Inteligencia_Artificial`. Duas opções foram reescritas e uma fusão juntou `Ciencias_Sociais` com Marketing a partir de 2024-2025: tratado por de-para. |
| `tempo_exp_dados` | 2023-2024 oferecia `de_4_a_6_anos` **e** `de_5_a_6_anos`; as outras só a segunda. |

**Tratamento na Silver:** coluna `serie_comparavel` (booleana) marcando as
1.282 linhas cujo valor não existe nas três edições. Quem for montar gráfico
temporal filtra por ela; quem for montar retrato de um ano, ignora.

Colunas que **não** mudaram e harmonizam direto: `genero`, `nvl_ensino`,
`regiao`, `estado`, `pcd`, `setor`, `forma_trabalho`, `faixa_salarial`
(fora os 2 typos) e os rótulos de layoff.

---

## 6. Os ajustes que cabem na Bronze

### 6.1 Nome do arquivo

O conteúdo está certo. O nome do arquivo é que precisa seguir a edição, não o
ano de abertura: `2023`, `2024` e `2025` viram

```
bronze_dw_state_data_2023.csv  →  bronze_dw_state_data_2023_2024
bronze_dw_state_data_2024.csv  →  bronze_dw_state_data_2024_2025
bronze_dw_state_data_2025.csv  →  bronze_dw_state_data_2025_2026
```

Rótulo de edição ambíguo é fonte conhecida de retrabalho: a 2023-2024 já
chegou rotulada como 2022-2023. As três correções da seção anterior (`uf`,
booleano, typo) são de Silver por definição: a Bronze é SOR e tem que continuar
fiel à origem, inclusive nos defeitos dela.

### 6.2 Onde a normalização precisa acontecer

A Bronze é SOR e tem que ser fiel à origem. Duas transformações que estariam
naturalmente na ingestão pertencem, por definição de camada, à Silver:

- `renomear_colunas`: trocava o nome de origem pelo canônico
  (`('P1_a ', 'Idade')` para `idade`)
- `processar_dataframe`: em **todo valor string**, tirava o acento e trocava
  espaço por underline (`Não` para `Nao`, `Cientista de Dados` para
  `Cientista_de_Dados`)

Sintoma que estava à vista o tempo todo: o `dim_rotulos.py` da Gold existe para
converter `Modelo_100%_remoto` de volta em "100% remoto". A Gold passava o
tempo desfazendo o que a Bronze tinha feito.

**As duas funções foram movidas para o início da Silver**
(`glue/silver/normalizacao_bronze.py`), sem uma linha de alteração no que
fazem. A Bronze passou a ser leitura e escrita.

#### A prova de que a mudança é neutra

Não é argumento, é medição. Os três CSV originais foram baixados do Kaggle e
guardados em `origem/`, com hash registrado. Duas comparações:

**1. As funções, aplicadas ao arquivo cru, reproduzem a Bronze antiga:**

| Edição | Células comparadas | Diferenças |
|---|---|---|
| 2023-2024 | 2.111.907 | **0** |
| 2024-2025 | 2.102.451 | **0** |
| 2025-2026 | 1.356.060 | **0** |

**2. A Silver gerada a partir da Bronze crua é idêntica à anterior:**

| | Linhas | Colunas | Células | Diferenças |
|---|---|---|---|---|
| Silver | 14.002 | 79 | 1.106.158 | **0** |

Mesma `sk_respondente` linha a linha, mesma ordem de colunas. Gold, medidas e
dashboard não mudam nada.

#### Duas coisas aprendidas

**Nome de coluna com parêntese e espaço cabe em Parquet.** A edição 2023-2024
tem colunas como `('P1_a ', 'Idade')`, e a suspeita era que o Parquet recusasse.
Testado no Spark 3.5.1: aceita. ⚠️ Conferir no Glue, que roda Spark 3.3 na
versão 4.0: se recusar lá, o contorno é sanitizar **só o nome**, nunca o valor.

**A ordem certa é ingerir e depois harmonizar.** Normalizar na entrada é uma
escolha defensável de engenharia, evita dor de encoding no resto do pipeline.
O custo é perder a rastreabilidade até a origem, e é isso que a camada Bronze
existe para preservar.

---

## 7. Como as ~320 colunas binárias foram agrupadas

Cada pergunta de múltipla escolha da pesquisa vira uma coluna por opção, é daí
que vêm 329 / 323 / 316 das ~400 colunas. Para consolidar sem depender de lista
manual, usei duas passadas:

**Passada 1, classificação semântica, por lista explícita de nomes.** Resolve
`linguagens`, `bancos_dados`, `clouds`, `ferramentas_bi`, `fontes_dados` e
`uso_ia_generativa`. Precisa ser explícita porque essas seis se misturam quando
agrupadas só por comportamento (são respondidas pelo mesmo público).

**Passada 2, máscara de resposta, para o restante.** Colunas da mesma pergunta
têm exatamente o mesmo conjunto de respondentes preenchido: quem respondeu uma
opção respondeu todas. Agrupar por essa máscara separa sozinho os blocos de
atividade e percepção, e os grupos saem **idênticos nas três edições**
(49 · 47 · 39 · 25 colunas).

Resultado: **17 grupos**, cobrindo 323/329 · 323/323 · 310/316 das binárias. O
que fica de fora são as 6 booleanas canônicas (`gestor`, `vive_brasil`,
`empresa_possui_datalake`, `empresa_possui_dw`, `satisfacao_empresa_atual`,
`vive_estado_formacao`) mais `mudou_estado`, que não são múltipla escolha e
viram coluna própria.

**Dois grupos ficaram com nome provisório**, e é o de-para do Alexandre que
fecha:

- `fatores_emprego_declarado` × `fatores_emprego_atual`, duas perguntas com o
  **mesmo conjunto de opções**, separadas na origem só pelo sufixo `_1`. Uma é
  respondida por ~29% da base e a outra por ~92%. O enunciado não está na base.
- `motivos_insatisfacao_2023`, existe só em 2023-2024, com nomes descritivos
  (`salario_atual_n_corresponde_mercado`, `clima_trabalho_ruim`). Pode ser a
  mesma pergunta que virou `fatores_emprego_atual` depois. Enquanto não
  confirmado, fica como grupo próprio e não entra em série temporal.

A lista completa, coluna a coluna e por edição, está em
`glue/silver/grupos_multipla_escolha.py`.

---

## 8. Como reproduzir

```bash
python dev/tests/test_silver_local.py <pasta_com_os_csv>
```

Monta uma Bronze de mentira em Parquet a partir dos CSVs, roda o **mesmo**
`job_silver.py` que vai para o Glue e confere 86 asserções (contagem por
edição, unicidade da sk, ano validado contra a data de envio, domínio dos
booleanos, `uf` derivada × região, cobertura do mapa salarial, marcação de
comparabilidade e ausência de coluna 100% nula).

Executado em 30/08/2026 contra os três CSVs: **86/86 passaram.**
