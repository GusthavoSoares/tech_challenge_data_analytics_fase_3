# Resultados das consultas

CSV baixados do Athena, um por consulta de `sql/perguntas/`.

Nome do arquivo: o mesmo da consulta que o gerou (`p1_....sql` gera
`p1_....csv`), para dar para conferir de onde veio cada número da apresentação.

## Origem

Rodados no Athena, database `state_of_data`, contra a Gold que os três Glue Jobs
produziram no bucket `lab-<id da conta>`. O passo a passo está em
[`../docs/COMO_RODAR_NA_AWS.md`](../docs/COMO_RODAR_NA_AWS.md).

A coluna `mediana_aprox` da P2 é aproximada e depende do motor:
`APPROX_PERCENTILE` tem implementação diferente no Trino e no Spark. Contagem e
média são exatas. Ao citar número, use a média.

## Números para citar

| Arquivo | Achado |
|---|---|
| `p4_tecnologias_adocao.csv` | Python 92,0% e SQL 84,2%, sobre base de 2.095 em 2025 |
| `p5_adocao_ia.csv` | uso pessoal de 80,3% para 97,9% em três edições, contra prioridade da empresa de 36,2% para 60,6% |
| `p7_oportunidades_desafios.csv` | as duas maiores barreiras à IA somam 70,8% dos 587 gestores, e ambas são de capital humano |

Cada percentual traz a base ao lado na própria saída, de propósito: percentual de
múltipla escolha sem denominador explícito é o erro mais fácil de cometer nesta
pesquisa.
