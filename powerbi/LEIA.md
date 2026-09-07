# Power BI

`tc3_state_of_data.pbix`: o dashboard executivo, 15 telas. Os prints dele são o
material da apresentação, que é o entregável 1.

## De onde vem o dado

```
S3 · GOLD                 modelo dimensional gravado pelo tc3-gold
   │                      16 tabelas Parquet
   │  exportação para CSV, uma tabela por arquivo
   ▼
gold_csv/                 16 arquivos, ~41 MB
   │  Power Query, importação
   ▼
tc3_state_of_data.pbix    modelo em memória, 16 tabelas e 13 relacionamentos
```

O `.pbix` guarda os dados dentro dele, então abre e mostra o dashboard sem
precisar de fonte externa. Os CSV não estão versionados por causa do tamanho:
para regerá-los, basta ler as 16 pastas de `s3://<bucket>/gold/` e gravar uma
por arquivo.

O modelo é o mesmo descrito em [`../docs/MODELO_GOLD.md`](../docs/MODELO_GOLD.md),
sem transformação nenhuma no meio: o que está no Power BI é a Gold. As medidas
estão em [`../docs/MEDIDAS_DAX.md`](../docs/MEDIDAS_DAX.md).

## As telas

| # | Tela | Responde |
|---|---|---|
| 1 | Início | contexto, as 7 perguntas e o funil do pipeline |
| 2 | Sumário executivo | os achados que sustentam a recomendação |
| 3 | Mercado | P1, estrutura do mercado |
| 4 | Perfis | P2, cargos e salários |
| 5 | Diversidade | P3, gênero e raça |
| 6 | Tecnologias | P4, linguagens, clouds, bancos e BI |
| 7 | IA | P5, adoção individual contra prioridade da empresa |
| 8 | Recortes | P6, região, senioridade e modelo de trabalho |
| 9 | Oportunidades | P7, barreiras, benchmark e recomendações |
| | Drill e tooltip | detalhamento por cargo, UF e denominador |
