# Camada Bronze

| Arquivo | Para quê |
|---|---|
| [`job_bronze.py`](job_bronze.py) | o script que roda como Glue Job na AWS |
| [`../../notebooks/01_bronze.ipynb`](../../notebooks/01_bronze.ipynb) | o mesmo passo a passo em notebook, entregável 3 |

O código é do **Gusthavo**. O `job_bronze.py` é o notebook dele com os caminhos
lidos de variável de ambiente e a conferência de contrato no fim. Roda sem
importar nenhum módulo auxiliar: camada de baixo não depende da de cima.

## A regra desta camada

**Cópia fiel da origem, sem nenhuma modificação.** O CSV do Kaggle entra como
veio: nome de coluna original (inclusive `('P1_a ', 'Idade')` em 2023-2024),
acento, espaço e maiúscula preservados. Nenhuma correção, nenhum de-para,
nenhuma tipagem. Quem harmoniza é a Silver.

A normalização de nomes e de acentuação vive na Silver, em
[`../silver/normalizacao_bronze.py`](../silver/normalizacao_bronze.py). A
equivalência entre as duas camadas está medida em
[`../../docs/VALIDACAO_BRONZE.md`](../../docs/VALIDACAO_BRONZE.md) §6.2.

## O contrato que a Silver espera

A Silver recusa a Bronze se o shape não bater, e o job para com erro claro em
vez de produzir uma Silver silenciosamente errada.

| Tabela | Linhas | Colunas |
|---|---|---|
| `bronze_dw_state_data_2023_2024` | 5.293 | 399 |
| `bronze_dw_state_data_2024_2025` | 5.217 | 403 |
| `bronze_dw_state_data_2025_2026` | 3.495 | 388 |

Caminho: `s3://<bucket>/bronze/state_data/<tabela>/`
Formato: Parquet, **todas as colunas string**.

`inferSchema=false` é obrigatório. Com a inferência ligada, colunas binárias de
texto viram float e quebram o join entre edições (afetava 328 de 399 colunas).

Conferência completa em [`../../docs/VALIDACAO_BRONZE.md`](../../docs/VALIDACAO_BRONZE.md).
