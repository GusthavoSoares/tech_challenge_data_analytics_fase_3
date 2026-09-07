# Consultas do Athena, uma por pergunta de negócio

Rodar em `state_of_data`, com o resultado configurado para
`s3://lab-<id>/log/`. Baixar o CSV de cada uma para `results/`, mantendo o nome
do arquivo que a gerou.

| Arquivo | Pergunta | O que a consulta devolve |
|---|---|---|
| `p1_estrutura_do_mercado.sql` | Como está estruturado o mercado? | distribuição por família de cargo e senioridade, 2025 |
| `p2_perfis_valorizados.sql` | Quais perfis são mais valorizados? | salário médio e mediana por cargo e senioridade |
| `p3_diversidade_genero.sql` | Qual o cenário de diversidade? | participação e salário por gênero, dentro de cada senioridade |
| `p4_tecnologias_adocao.sql` | Quais tecnologias têm maior adoção? | ranking de linguagens sobre a base correta |
| `p5_adocao_ia.sql` | Qual o índice de adoção de IA? | uso pessoal contra prioridade da empresa, por edição |
| `p6_regiao_senioridade_modelo.sql` | Há diferença entre região, senioridade e modelo? | salário por modelo de trabalho, controlado por senioridade |
| `p7_oportunidades_desafios.sql` | Quais oportunidades e desafios? | barreiras à IA apontadas por gestores |

## O denominador é o ponto de atenção

A `gold_dw_bridge_respondente_opcao` só tem linha para quem **marcou** a opção.
Quem não viu a pergunta e quem viu e não marcou nada somem os dois da bridge.

Quem guarda a diferença é o fato: as colunas `qtd_<grupo>` são `NULL` para quem
não viu a pergunta e `0` para quem viu e não marcou. Por isso toda consulta de
múltipla escolha aqui calcula o denominador com `qtd_<grupo> IS NOT NULL`, numa
CTE separada, e devolve a base na saída para você conferir.

Dividir pelo total de 14.002 em vez disso derruba os percentuais pela metade e
inverte conclusão.

## O ano tem dois tipos, e isso morde

`ano_pesquisa` é **coluna de partição** no fato e na Silver. O crawler tipa chave
de partição como `varchar`, porque o valor vem do nome da pasta
(`ano_pesquisa=2025`), não do arquivo. Na bridge ela é coluna comum, e o tipo vem
do Parquet, `integer`.

Por isso as consultas comparam o ano de dois jeitos:

| Tabela | Como comparar |
|---|---|
| `gold_dw_fat_profissionais`, `state_data` | `ano_pesquisa = '2025'`, com aspas |
| `gold_dw_bridge_respondente_opcao` | `ano_pesquisa = 2025`, sem aspas |

Sem as aspas na primeira, o Athena devolve
`TYPE_MISMATCH: Cannot apply operator: varchar = integer`.

## Resultado esperado

Números conferidos contra a Gold. Servem para validar que a execução na AWS
devolveu o esperado.

| Consulta | Confira |
|---|---|
| P4 | base de 2.095, Python 92,0% e SQL 84,2% |
| P5 | 2025 com base 2.105 no uso pessoal, e 60,6% de prioridade sobre base 652 |
| P7 | base de 587 gestores, e as duas maiores barreiras somando 70,8% |

> ⚠️ A mediana da P2 é **aproximada** e o valor muda conforme o motor:
> `APPROX_PERCENTILE` é implementado diferente no Trino e no Spark. Contagem e
> média batem nos dois. Ao citar número, use a média.
