# Contrato da camada Silver: `silver_dw_fat_respondente`

**TC3 Grupo 21** · dono: Caio · atualizado em 30/08/2026

Este é o documento que o resto do grupo precisa para construir a Gold e as
consultas do Athena **sem depender de mim**. Se algo aqui mudar, eu aviso.

---

## O essencial

| | |
|---|---|
| **Tabela** | `state_of_data.silver_dw_fat_respondente` |
| **Caminho** | `s3://tc3-grupo21-datalake/silver/state_data/` |
| **Formato** | Parquet, tipado |
| **Partição** | `ano_pesquisa` (2023 · 2024 · 2025) |
| **Grão** | 1 linha por respondente por edição |
| **Linhas** | **14.002** (5.293 + 5.215 + 3.494) |
| **Colunas** | **79** |
| **Chave** | `sk_respondente`: `sha2(ano_pesquisa \|\| id_origem)`, única e determinística |

`ano_pesquisa` é o **ano da coleta**, não o rótulo da edição:

| ano_pesquisa | edicao | Coletada em | Respondentes |
|---|---|---|---|
| 2023 | 2023-2024 | fim de 2023 | 5.293 |
| 2024 | 2024-2025 | out–dez/2024 | 5.215 |
| 2025 | 2025-2026 | out–dez/2025 | 3.494 |

Filtre sempre por `ano_pesquisa`: é a coluna de partição, e o Athena só faz
partition pruning nela.

---

## Colunas

### Identificação

| Coluna | Tipo | Nota |
|---|---|---|
| `sk_respondente` | string | chave da Gold |
| `ano_pesquisa` | int | **partição** |
| `edicao` | string | `2023-2024`, `2024-2025`, `2025-2026` |
| `id_origem` | string | chave da pesquisa (`id` ou `token_user`) |
| `data_envio` | timestamp | **NULL em 2023**, a edição não coleta |

### Demografia

`idade` (int) · `faixa_etaria` · `genero` · `cor_raca_etnia` · `pcd` ·
`pcd_flag` (boolean) · `vive_brasil` (boolean)

### Localização

| Coluna | Nota |
|---|---|
| `estado_moradia` · `regiao_moradia` · `uf_moradia` | **onde a pessoa mora** |
| `estado_origem` · `regiao_origem` · `uf_origem` | onde nasceu, **NULL em 2023** |

⚠️ **Não use a coluna `uf` da Bronze.** Em 2025-2026 ela é o estado de
nascimento, não o de moradia. `uf_moradia` aqui é derivada de `estado`, que é
estável nas três edições. Detalhe em [`VALIDACAO_BRONZE.md`](VALIDACAO_BRONZE.md) §3.1.

### Formação e carreira

`nivel_ensino` · `area_formacao` · `cargo_atual` · `nivel_senioridade` ·
`tempo_exp_dados` · `tempo_exp_ti` · `setor_empresa` · `forma_trabalho` ·
`eh_gestor` (boolean) · `satisfeito_empresa` (boolean) · `mudou_estado`
(boolean, só 2023)

### Remuneração

| Coluna | Tipo | Nota |
|---|---|---|
| `faixa_salarial` | string | rótulo original, 13 faixas |
| `salario_medio_mensal` | double | ponto médio da faixa |

`salario_medio_mensal` existe para permitir média e mediana. Duas ressalvas:
a faixa aberta do topo usa 40.001 (subestima, viés conservador) e o número
**só faz sentido reportado junto da faixa**, nunca sozinho, porque é
estimativa, não salário declarado.

### Maturidade de dados e IA

`empresa_possui_datalake` (boolean) · `empresa_possui_dw` (boolean) ·
`ia_gen_prioridade` · `llms_bom_resultado` (**só 2025**) ·
`empresa_passou_layoff` (3 categorias) · `houve_layoff` (boolean) ·
`fui_afetado_layoff` (boolean)

### Preferência declarada (resposta única)

`linguagem_preferida` · `cloud_preferida` · `ferramenta_bi_diaria`

---

## Múltipla escolha: os 17 grupos

As ~320 colunas binárias da Bronze (uma por opção) viraram **17 pares**:

```
<grupo>       string, opções marcadas separadas por ", "
qtd_<grupo>   int, quantas foram marcadas
```

| Grupo | Opções (23/24/25) | Respondentes | Nas 3 edições | Rótulo harmonizado |
|---|---|---|---|---|
| `fatores_avaliacao_emprego` | 10/10/10 | 12.815 | sim | sim |
| `uso_ia_generativa` | 23/23/23 | 12.041 | sim | **NÃO** |
| `ferramentas_bi` | 23/18/18 | 9.494 | sim | sim |
| `fontes_dados` | 16/16/8 | 9.494 | sim | **NÃO** |
| `bancos_dados` | 35/35/35 | 9.454 | sim | **NÃO** |
| `linguagens` | 14/14/9 | 9.454 | sim | sim |
| `clouds` | 6/6/6 | 9.295 | sim | sim |
| `exp_prof_prejudicada` | 4/4/4 | 7.140 | sim | sim |
| `atividades_analista_dados` | 47/47/47 | 4.392 | sim | **NÃO** |
| `percepcao_carreira` | 9/9/9 | 3.372 | sim | sim |
| `desafios_gestor` | 25/25/25 | 2.571 | sim | sim |
| `fatores_troca_emprego` | 0/11/11 | 2.528 | ⚠️ **só 2024/25** | sim |
| `cargos_no_time` | 9/10/10 | 2.473 | sim | sim |
| `atividades_engenheiro_dados` | 39/39/39 | 2.406 | sim | **NÃO** |
| `barreiras_ia_generativa` | 7/7/7 | 2.384 | sim | sim |
| `atividades_cientista_dados` | 49/49/49 | 2.010 | sim | **NÃO** |
| `motivos_insatisfacao_2023` | 7/0/0 | 1.318 | ⚠️ **só 2023** | sim |

**Rótulo harmonizado = NÃO** significa que a mesma opção tem nome diferente
entre edições e a normalização automática colidiria dentro do ano. Adoção num
ano é confiável; série temporal daquele grupo precisa do de-para do Alexandre.

⚠️ Três colunas parecem resposta única e **não são**: `linguagem_preferida`,
`cloud_preferida` e `ferramenta_bi_diaria`. A pessoa marca mais de uma e a
origem concatena (`ferramenta_bi_diaria` tinha 1.422 strings distintas). A
Silver normaliza para o mesmo formato dos grupos, com `qtd_` própria.

### Como consultar

```sql
-- quem usa Python
SELECT COUNT(*) FROM silver_dw_fat_respondente
WHERE ano_pesquisa = 2025 AND linguagens LIKE '%python%';

-- adoção por ano
SELECT ano_pesquisa,
       COUNT(*)                                                   AS respondentes,
       COUNT(*) FILTER (WHERE linguagens LIKE '%python%')          AS usa_python,
       ROUND(100.0 * COUNT(*) FILTER (WHERE linguagens LIKE '%python%')
             / COUNT(*), 1)                                        AS pct
FROM silver_dw_fat_respondente
WHERE linguagens IS NOT NULL          -- ⚠️ ver "NULL não é zero"
GROUP BY ano_pesquisa ORDER BY 1;

-- explodir em bridge, quando precisar do grão de opção
SELECT sk_respondente, ano_pesquisa, TRIM(linguagem) AS linguagem
FROM silver_dw_fat_respondente
CROSS JOIN UNNEST(SPLIT(linguagens, ', ')) AS t(linguagem)
WHERE linguagens IS NOT NULL AND linguagens <> '';
```

### ⚠️ NULL não é zero

| Estado | `linguagens` | `qtd_linguagens` | Significa |
|---|---|---|---|
| não respondeu o bloco | `NULL` | `NULL` | a pergunta não se aplicava |
| respondeu, não marcou nada | `''` | `0` | viu a pergunta e não marcou |

Muitos blocos só são exibidos a parte da base (`atividades_cientista_dados`
tem 2.010 de 14.002). **Sempre filtre `IS NOT NULL` antes de calcular
percentual**, usar 14.002 como denominador de um bloco que 2.010 pessoas
viram derruba qualquer número pela metade.

---

## As três ressalvas

**1. `serie_comparavel` (boolean).** 1.282 linhas têm valor que não existe nas
três edições: `Especialista/Staff+` na senioridade (só 2025), arquiteto como
cargo separado (só 2024/2025), `Ciencia_de_Dados/IA` na formação (só 2025),
`de_4_a_6_anos` no tempo de experiência (só 2023).

```sql
WHERE serie_comparavel = true    -- comparação ENTRE anos
-- retrato de um ano só: pode ignorar
```

Sem isso, categoria nova de questionário vira "crescimento" no gráfico.

**2. Dois grupos não cobrem as três edições**: `fatores_troca_emprego` e
`motivos_insatisfacao_2023`. Não use em série temporal. Podem ser a mesma
pergunta renomeada; está no de-para do Alexandre confirmar.

**3. Nomes provisórios.** `fatores_avaliacao_emprego` e `fatores_troca_emprego`
são duas perguntas com o mesmo conjunto de opções, separadas na origem só pelo
sufixo `_1`. E o sufixo **inverte entre edições**: em 2023 a pergunta ampla vem
sem sufixo, em 2024/25 vem com `_1`. Por isso o agrupamento aqui é pela base
observada, não pelo nome. Os rótulos são a minha leitura; se o de-para trouxer
o enunciado, renomeio.

---

## O que a Silver deliberadamente NÃO faz

Nenhuma agregação de negócio, isso é Gold, por definição de camada. A Silver
entrega o grão de respondente conformado; contagem, percentual, ranking e corte
por pergunta de negócio ficam na camada de cima.

A Gold é **um star schema só**, que responde as sete perguntas. Ver
[`MODELO_GOLD.md`](MODELO_GOLD.md).

---

## Reprodutibilidade

```bash
python dev/tests/test_silver_local.py <pasta_com_os_csv>
```

Roda o mesmo `job_silver.py` que vai para o Glue, contra uma Bronze de mentira
montada dos CSVs, sem gastar sessão do AWS Academy. **86 asserções**, incluindo
contra-prova da lista consolidada contra os binários de origem, estabilidade da
base de cada grupo e harmonização dos rótulos entre edições.

Última execução, 30/08/2026: **86/86.**
