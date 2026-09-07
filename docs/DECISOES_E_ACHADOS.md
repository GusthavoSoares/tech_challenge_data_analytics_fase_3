# TC3: Decisões de arquitetura e achados nas bases

Registro das decisões acordadas com o grupo e das validações feitas nas bases do
**State of Data Brasil**. Atualizado em **20/08/2026**.

> Este arquivo guarda o que é específico deste desafio: as decisões tomadas e o
> motivo de cada uma.
>
> A conferência completa dos três arquivos da Bronze, com os números,
> está em [`VALIDACAO_BRONZE.md`](VALIDACAO_BRONZE.md).

---

## 1. Quais bases entram

O enunciado exige o histórico das **3 últimas pesquisas**. As edições publicadas no Kaggle são:
2021 · 2022-2023 · 2023-2024 · 2024-2025 · 2025-2026.

Portanto entram as três últimas:

| Edição | Registros | Colunas | Perguntas | Coleta | Situação |
|---|---|---|---|---|---|
| **2023-2024** | 5.293 | 399 | 71 | fim de 2023 | ✅ extraída |
| **2024-2025** | 5.217 | 403 | 73 | out–dez/2024 | ✅ extraída |
| **2025-2026** | 3.495 | 388 | 69 | out–dez/2025 | ✅ extraída |

⚠️ **A edição 2022-2023 não entra** (353 colunas, 4.271 registros). Como o arquivo da 2023-2024
chegou rotulado como "2022_2023", há risco real de alguém baixar a 2022-2023 achando que completa
o conjunto.

### Convenção de nome das edições

Toda edição é nomeada `ano_da_coleta` + `ano_seguinte`, e a coleta acontece sempre no último
trimestre. Confirmado nas três:

| Edição | Coleta real | Coluna que confirma |
|---|---|---|
| 2023-2024 | fim de 2023 | `empresa_trabalha_passou_layoff_2023` |
| 2024-2025 | out–dez/2024 | `layoff_2024` |
| 2025-2026 | out–dez/2025 | `2.p_empresa_passou_por_layoff_em_2025` |

Por isso a 2024-2025 **não tem nenhum registro de 2025** e a 2025-2026 **não tem nenhum de 2026**. É o comportamento esperado, não falha de extração.

### Correção de nome pendente

Os arquivos entregues em 20/08/2026 estão nomeados pelo ano da coleta, não pela edição:

```
bronze_dw_state_data_2023  →  bronze_dw_state_data_2023_2024
bronze_dw_state_data_2024  →  bronze_dw_state_data_2024_2025
bronze_dw_state_data_2025  →  bronze_dw_state_data_2025_2026
```

Acompanha no notebook: `caminho_*`, `novos_nomes_colunas_*`, `df_state_data_*` e o nome no
`exportar_df_para_csv`.

Rótulo de edição ambíguo é fonte conhecida de retrabalho: a 2023-2024 já chegou rotulada como
2022-2023. O conteúdo dos três arquivos está correto, só o rótulo muda.

---

## 2. Arquitetura acordada

```
Kaggle (3 edições)
   ↓  ingestão (AWS CLI / Boto3)
BRONZE   3 tabelas separadas, sem join, parquet, particionado por ano
   ↓  Glue job (Spark)
SILVER   união harmonizada das 3 edições, 1 linha por respondente
   ↓  Glue job (Spark)
GOLD     fato + dimensões
   ↓
Athena → gráficos e material executivo

Glue Data Catalog cobre as três camadas (não é etapa final)
```

Diagrama: [`arquitetura_tc3.png`](arquitetura_tc3.png) · [`arquitetura_tc3.svg`](arquitetura_tc3.svg)

**Decisão registrada:** a Bronze não recebe dimensão nem fato. Existe prática de mercado que
enriquece a Bronze para ela não parecer uma view de OLTP, mas as aulas da fase definem Bronze como
SOR (cópia fidedigna), e o hands-on do professor faz exatamente CSV → S3 em Parquet → catalogação →
Athena, com o Glue ETL sem nenhuma transformação. Vale citar essa alternativa na apresentação como
decisão consciente.

**Descartada:** `dim_calendario` na Bronze. A pesquisa é anual, o grão de tempo é a edição, não há
timestamp, mês nem dia para preencher ou enriquecer depois.

### Nomenclatura das tabelas

```
bronze_dw_state_data_<edicao>      ex: bronze_dw_state_data_2023_2024
silver_dw_fat_<edicao>
silver_dw_dim_<dimensao>
gold_dw_fat_profissionais
gold_dw_dim_<dimensao>
```

Pendente de fechar com o grupo: se fato e dimensão existem na Silver **e** na Gold, definir o que
muda entre elas. Proposta: Silver = fato e dimensões conformados no grão de respondente;
Gold = agregações por pergunta de negócio.

---

## 3. Divisão do grupo

| Pessoa | Entrega | Perguntas de negócio |
|---|---|---|
| Allison | Draw.io + fluxo | 3 e 4 |
| Alexandre | ETL + EDA + de-para | 1 e 2 |
| Gusthavo | Bronze | 5 e 6 |
| Caio | Silver e Gold | 7 |

A pergunta 7 (oportunidades e desafios) é síntese das outras seis, depende das respostas de todos.

**Combinado sobre a Gold:** cada um constrói a tabela Gold que alimenta as **suas** perguntas, para
não haver dois donos na mesma camada.

---

## 4. Validações executadas nas bases

### A Bronze da 2023-2024 está correta

Comparação contra o CSV cru `State_of_data_BR_2023_Kaggle - df_survey_2023.csv`:

| Verificação | Resultado |
|---|---|
| estrutura | 399 col × 5.293 linhas nos dois ✅ |
| ids | 5.293 de 5.293, mesmo conjunto e mesma ordem ✅ |
| conteúdo | 2.111.907 células comparadas → **100% idênticas** ✅ |
| contraprova com a 2022-2023 | **interseção de ids = 0** ✅ |

Conclusão: arquivo certo, ETL sem perda. Só o rótulo estava uma edição atrás.

### A diferença de 630 linhas não existe

A planilha de comparação registrava 5.923 registros para 2023 contra 5.293 no arquivo. É
transposição de dígito na planilha, a fonte tem 5.293. Nenhuma linha se perdeu na leitura com
`multiLine=true`.

### ✅ `inferSchema`: resolvido (conferido em 20/08/2026)

O problema original: colunas binárias que na origem são texto (`"0"` / `"1"`) foram gravadas
como `0.0` / `1.0`: 328 de 399 colunas. Quebrava o join entre edições e violava a regra de
Bronze fiel à origem.

Depois da troca para `inferSchema=false`, varredura do domínio de **todas** as colunas das três
edições: **zero** colunas gravadas como `0.0`/`1.0`. Binárias por edição: 329 (2023-2024),
323 (2024-2025), 316 (2025-2026), todas como `0`/`1`.

*(Nota: uma primeira comparação acusou 33% de divergência de conteúdo, era falso positivo por
comparar `1` com `1.0` como string. Normalizando número com número, bate 100%.)*

### ✅ As três edições estão na Bronze e conferem

| Edição | Linhas | Colunas | Chave | Nulos na chave |
|---|---|---|---|---|
| 2023-2024 | 5.293 | 399 | `id` | 0 |
| 2024-2025 | 5.217 | 403 | `token_user` | 0 |
| 2025-2026 | 3.495 | 388 | `token_user` | 0 |

Interseção de chaves **zero** em todos os pares, nenhuma chance de duas edições serem o mesmo
arquivo. As datas de envio caem 100% dentro do ano da coleta (out–dez/2024 e out–dez/2025),
o que valida a injeção do `ano_pesquisa` em duas das três edições.

**Duplicidade de chave:** 2 em 2024-2025 e 1 em 2025-2026, são linhas **100% idênticas** em
todas as colunas, submissão duplicada e não respondente distinto. `dropDuplicates()` não perde
informação. Total após dedup: **14.002 respondentes**.

**Cobertura de nomes de coluna** (match exato, já com os nomes semânticos do ETL):
2023-2024 ∩ 2024-2025 = 336 · 2024-2025 ∩ 2025-2026 = 384 · comuns às três = **327**.

---

## 5. Achados que afetam a Silver

**Nenhuma base tem coluna de edição.** É preciso injetar `ano_pesquisa` a partir da origem do
arquivo. Nas edições 2024-2025 e 2025-2026 dá para validar contra a data de envio; na 2023-2024 não
há contra o que validar.

**A chave primária muda de nome:**

| Edição | Chave (após o ETL) | Duplicados |
|---|---|---|
| 2023-2024 | `id` | 0 |
| 2024-2025 | `token_user` | 2 |
| 2025-2026 | `token_user` | 1 |

Criar uma `sk_respondente` própria na Silver e tratar os duplicados.
*(Correção: os arquivos entregues já saem do ETL com `token_user` em 2025-2026: `0.a_token`
é o nome cru do Kaggle, não o que chega na Bronze.)*

### ⚠️ `uf` muda de SIGNIFICADO entre edições: achado de 20/08/2026

O mais perigoso da base, porque é silencioso: não gera erro nem nulo, só produz número errado.

| Edição | `uf` bate com `estado` (moradia) | `uf` bate com `estado_origem` (nascimento) |
|---|---|---|
| 2023-2024 | **99,9%** |, (a edição não pergunta origem) |
| 2024-2025 | **99,9%** | 2,9% |
| 2025-2026 | 3,8% | **100,0%** |

Em 2025-2026 `uf` é o estado **onde a pessoa nasceu**. Quem tomar `uf` como "onde mora" nas três
edições, a leitura natural do nome, erra a análise regional, que é a pergunta de negócio 6.

Causa: a rotina de renomeação gera `_1` na colisão. Em 2024-2025 saíram `uf` (moradia) e `uf_1`
(origem); em 2025-2026 a ordem das perguntas mudou e saíram `uf` (origem) e `uf_moradia` (moradia).

**Decisão:** a Silver **não usa `uf`**. A sigla é derivada de `estado` e `estado_origem`, que são
explícitos e estáveis nas três. Conferido: `regiao` bate com a região calculada a partir de
`estado` em 99,9% nas três edições.

### ⚠️ Seis colunas vêm `TRUE`/`FALSE` só em 2024-2025

`vive_brasil` · `vive_estado_formacao` · `gestor` · `satisfacao_empresa_atual` ·
`empresa_possui_datalake` · `empresa_possui_dw`

Nas outras duas edições as mesmas colunas vêm `0`/`1`. Como a Bronze é toda string, o `union`
aceita as duas grafias sem reclamar, e um `WHERE gestor = '1'` derrubaria os 1.045 gestores de
2024-2025 sem acusar erro nenhum.

**Decisão:** mapa booleano único na Silver, cobrindo as duas grafias.

### ⚠️ Dois rótulos com erro de digitação na origem

| Edição | Valor | Deveria ser | Ocorrências |
|---|---|---|---|
| 2023-2024 | `de_R$_101/mes_a_R$_2.000/mes` | `de_R$_1.001/mes_a_R$_2.000/mes` | 1 |
| 2025-2026 | `de_R$_25.001/mes_a_R$_3000/mes` | `de_R$_25.001/mes_a_R$_30.000/mes` | 1 |

São 2 registros em 14.005, mas viram categoria órfã no `GROUP BY` e aparecem como faixa salarial
inexistente no gráfico. Corrigidos na Silver.

### ⚠️ Categorias que nasceram ou sumiram entre edições

Não é erro, a pesquisa mudou. Mas vira série temporal falsa se ninguém marcar.

| Coluna | O que mudou |
|---|---|
| `nvl` (senioridade) | 2025-2026 criou `Especialista/Staff+` (349 respostas) |
| `cargo_atual` | 2023-2024 tinha engenheiro e arquiteto numa opção só; a partir de 2024-2025 arquiteto virou opção separada. Somem `Analista_de_Inteligencia_de_Mercado`, `DBA` e `Economista` |
| `area_formacao` | 2025-2026 criou `Ciencia_de_Dados_/_Inteligencia_Artificial`; `Ciencias_Sociais` só em 2023-2024 |
| `tempo_exp_dados` | 2023-2024 oferecia `de_4_a_6_anos` **e** `de_5_a_6_anos`; as outras só a segunda |

**Decisão:** coluna `serie_comparavel` (booleana) na Silver, marcando as 1.282 linhas cujo valor
não existe nas três edições. Comparação entre anos filtra por ela; retrato de um ano ignora.

**`empresa_passou_layoff` não é booleana**, apesar do nome. São três respostas (não houve /
houve e não me afetou / houve e fui afetado), com rótulos idênticos nas três edições. A Silver
guarda a categoria e deriva dois flags: `houve_layoff` e `fui_afetado_layoff`.

Colunas que **não** mudaram e harmonizam direto: `genero`, `nvl_ensino`, `regiao`, `estado`,
`pcd`, `setor`, `forma_trabalho` e `faixa_salarial` (fora os 2 typos).

**Duas gerações de schema:**

```
2022-2023 e 2023-2024 ....  ('P0', 'id')   ('P1_a ', 'Idade')     ← formato tupla
2024-2025 e 2025-2026 ....  0.a_token      1.a_idade              ← prefixo numérico
```

Por isso são necessários dicionários de renomeação diferentes, e por isso o dicionário da 2024-2025
não serve para a 2023-2024.

**O dicionário da 2024-2025 cobre 99% da 2025-2026**, desde que o match seja pelo texto e não pelo
prefixo. Pelo nome completo dá 73%; ignorando o prefixo `N.x_`, sobe para 385 de 388.

Só três colunas são realmente novas na 2025-2026:

- `2.p_empresa_passou_por_layoff_em_2025`
- `3.g_empresa_está_conseguindo_ter_bons_resultados_com_llms`
- `4.c.8_DAX`

**Parte da divergência de nomes foi criada pelo ETL, não pela pesquisa.** A rotina de renomeação
acrescenta `_1`, `_2` quando o nome já existe. Resultado: `databricks_1` e `databricks_2` (2023-2024)
são o mesmo conceito que `databricks_analista` e `engenheiro_dados_databricks` (2024-2025). O mesmo
vale para `google_dataflow_1` × `google_dataflow_analista`, `video_1` × `video_fonte` e
`ibm_data_stage_1` × `ibm_data_stage_analista`. O de-para precisa resolver isso, senão a mesma
tecnologia vira duas colunas distintas na Silver.

**Volume de colunas.** 399 / 403 / 388 colunas, mas apenas 71 / 73 / 69 perguntas, a diferença são
os binários criados por pergunta de múltipla escolha (uma coluna por tecnologia). O grupo decidiu
consolidar para ~20 colunas na Silver, agrupando as múltiplas escolhas em string separada por
vírgula ou em código para dicionário.

---

## 6. Pendências

Fechadas em 20/08/2026, conferidas nos arquivos:

- [x] ~~Rodar a 2025-2026 no ETL~~, rodou: 3.495 × 388, 384/388 colunas casando com a 2024-2025
- [x] ~~Trocar `inferSchema` para `false`~~, zero colunas `0.0`/`1.0` nas três edições

Abertas:

- [ ] **Gusthavo:** renomear os arquivos da Bronze para a convenção de edição,      `..._2023` → `..._2023_2024`, `..._2024` → `..._2024_2025`, `..._2025` → `..._2025_2026`.
      É o único ajuste que cabe na Bronze; o conteúdo está certo.
- [ ] **Alexandre:** consolidar as múltiplas escolhas e preencher o de-para.
      A Silver já tem as 30 colunas de resposta única harmonizadas, falta agrupar os ~320
      binários de tecnologia (uma coluna por ferramenta) em lista ou código.
      ⚠️ Cuidado com os sufixos `_1`/`_2`: em 2023-2024 `databricks_1` e `databricks_2` batem
      com `databricks` em 45% e 60%, ou seja, **não são cópias**, são perguntas diferentes que
      colidiram no nome. O mesmo vale para `remuneracao_salario_1` (23%) e `oracle_1` (89%).
- [ ] **Grupo:** fechar a diferença entre fato/dimensão na Silver e na Gold.
      Proposta do Caio: **Silver** = um fato conformado no grão de respondente
      (`silver_dw_fat_respondente`, 14.002 linhas, sem dimensão separada, não vale a pena
      normalizar 30 colunas de survey); **Gold** = `gold_dw_fat_profissionais` com as dimensões
      que as perguntas de negócio precisam (`dim_tempo`, `dim_cargo`, `dim_geografia`,
      `dim_faixa_salarial`) e as agregações por pergunta.
- [ ] **Allison:** aplicar os ajustes do diagrama.
- [ ] **Caio:** Gold + pergunta 7, depois que as outras seis tiverem resposta.

---

## 7. Decisões de arquitetura

As regras que o pipeline segue hoje. Quem for mexer, mexe sabendo o motivo.

### 7.1 A Bronze é cópia fiel, e a normalização é da Silver

Renomear coluna e tirar acento de valor são trabalho da Silver, não da ingestão.
A Bronze grava o CSV como veio do Kaggle: nome de coluna original, inclusive
`('P1_a ', 'Idade')` em 2023-2024, e tudo string.

As funções estão em `glue/silver/normalizacao_bronze.py`, e a equivalência entre
as duas camadas está medida em `VALIDACAO_BRONZE.md` §6.2: 6,7 milhões de
células conferidas.

### 7.2 `uso_ia_generativa` não é uma pergunta, são três

A coluna junta uso pessoal, organização na empresa e visão do gestor, porque a
origem reaproveita o mesmo bloco de opções. Gestor nunca vê a pergunta de uso
pessoal e mesmo assim tem a coluna preenchida.

O que isso obriga:

- a Gold separa as 30 opções em três grupos, via `SUBGRUPO`;
- `usa_ia_generativa` deriva só das opções de uso pessoal, e o job falha se um
  gestor aparecer nos grupos pessoal ou empresa;
- as listas `IA_PESSOAL`, `IA_EMPRESA` e `IA_GESTOR` vivem em `gold_comum.py`,
  fonte única para a Gold e para os jobs de análise;
- a base de adoção individual é **9.494**, não os 12.041 de coluna preenchida,
  e a adoção é **89,2%**.

Quem escrever análise nova: `base_uso_ia_pessoal()`, nunca
`base_da_pergunta(silver, "uso_ia_generativa")`.

### 7.3 Especialista/Staff+ fica fora de comparação entre anos

A categoria nasceu em 2025-2026. Em série temporal ela vira "crescimento" que é
opção nova de questionário. O filtro é `serie_comparavel`, que cobre as quatro
colunas que mudaram de categoria entre edições: `nivel_senioridade`,
`cargo_atual`, `area_formacao` e `tempo_exp_dados`.

Em retrato de um ano só, ela entra normalmente.

### 7.4 O pipeline roda na AWS

Bronze, Silver e Gold como Glue Jobs, catálogo em `state_of_data` com 20 tabelas
e as 7 consultas no Athena. Passo a passo em `COMO_RODAR_NA_AWS.md`.

O mesmo arquivo `.py` roda na máquina e no Glue: os caminhos vêm de
`parametro()`, que lê `sys.argv` primeiro e variável de ambiente depois. Não
existe `if local else nuvem` em lugar nenhum do código.
