# Onde está cada base

O caminho do dado, da origem ao dashboard, e o que deste repositório é
versionado. Serve para conferir de onde saiu qualquer número da apresentação.

---

## O caminho

```
Kaggle                     3 CSV, um por edição, como a comunidade publicou
   │                       state_of_data_{2023_2024, 2024_2025, 2025_2026}.csv
   ▼
s3://<bucket>/entrada/     os mesmos 3 arquivos, sem tocar em nada
   │  Glue Job tc3-bronze
   ▼
bronze/state_data/         3 tabelas Parquet, tudo string, cópia fiel
   │  Glue Job tc3-silver
   ▼
silver/state_data/         1 tabela, 14.002 linhas × 76 colunas,
   │                       particionada por ano_pesquisa
   │  Glue Job tc3-gold
   ▼
gold/                      16 tabelas: 1 fato, 13 dimensões, catálogo de
   │                       opções e bridge
   ├──► Athena             as 7 consultas de sql/perguntas/
   └──► CSV ──► Power BI   tc3_state_of_data.pbix
```

Um crawler cataloga as três camadas no database `state_of_data` do Glue Data
Catalog. É por ele que o Athena enxerga as tabelas.

---

## O que está neste repositório

| O quê | Onde |
|---|---|
| Os 3 jobs do Glue | `glue/bronze/`, `glue/silver/`, `glue/gold/` |
| As 85 análises de conferência | `glue/gold/analises/` |
| As 7 consultas do Athena | `sql/perguntas/` |
| O resultado de cada consulta | `results/*.csv` |
| Amostra das dimensões | `data/amostras/` |
| Modelo dimensional em planilha | `data/gold_modelo_dimensional.xlsx` |
| Dashboard | `powerbi/tc3_state_of_data.pbix` |

## O que não está, e por quê

| O quê | Por quê |
|---|---|
| Os 3 CSV da origem | são do Kaggle, ~42 MB, e o link está no fim deste arquivo |
| Bronze, Silver e Gold em Parquet | vivem no S3, os jobs regeram em minutos |
| Os 16 CSV que alimentam o Power BI | ~41 MB, saem da Gold, e o `.pbix` já os carrega dentro |
| Projeto do Power BI em texto | o entregável é o `.pbix`, que abre com os dados |

---

## Para regerar do zero

Na AWS, o passo a passo está em
[`COMO_RODAR_NA_AWS.md`](COMO_RODAR_NA_AWS.md): subir os 3 CSV para
`entrada/`, rodar os três jobs na ordem e passar o crawler.

Na máquina, sem AWS, está em [`COMO_RODAR_LOCAL.md`](COMO_RODAR_LOCAL.md).
É o mesmo código, os caminhos vêm de parâmetro:

```powershell
python dev\scripts\preparar_bronze_local.py "caminho\dos\csv"
python glue\silver\job_silver.py --TC3_PATH_BRONZE ... --TC3_PATH_SILVER ...
python glue\gold\job_gold.py     --TC3_PATH_SILVER ... --TC3_PATH_GOLD ...
python dev\tests\test_silver_local.py "caminho\dos\csv"
```

---

## Documentos de referência

| O quê | Onde |
|---|---|
| Dicionário da Silver, coluna a coluna | [`CONTRATO_SILVER.md`](CONTRATO_SILVER.md) |
| Modelo dimensional da Gold | [`MODELO_GOLD.md`](MODELO_GOLD.md) |
| Conferência da Bronze | [`VALIDACAO_BRONZE.md`](VALIDACAO_BRONZE.md) |
| Decisões e achados | [`DECISOES_E_ACHADOS.md`](DECISOES_E_ACHADOS.md) |
| Respostas das 7 perguntas | [`RESPOSTAS_P1_A_P6.md`](RESPOSTAS_P1_A_P6.md), [`RESPOSTA_P7.md`](RESPOSTA_P7.md) |

---

## Fonte

Pesquisa **State of Data Brasil**, comunidade Data Hackers em parceria com a
Bain & Company. Edições 2023-2024, 2024-2025 e 2025-2026.
<https://www.kaggle.com/datahackers/datasets>
