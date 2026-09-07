-- P4. Quais tecnologias têm maior adoção?
--
-- ⚠️ ESTA É A CONSULTA COM A ARMADILHA DO DENOMINADOR.
--
-- A bridge só tem linha para quem MARCOU a opção. Quem não viu a pergunta e
-- quem viu e não marcou nada somem os dois da bridge, e ficam indistinguíveis
-- se você dividir por 14.002.
--
-- O fato guarda a diferença: `qtd_linguagens` é NULL para quem não viu a
-- pergunta e 0 para quem viu e não marcou. O denominador correto é
-- `qtd_linguagens IS NOT NULL`, e é o que a CTE `base` calcula.
--
-- Dividir pelo total do ano em vez disso derruba SQL de 89,5% para algo perto
-- de 61%, e a conclusão inteira muda.
--
-- Troque 'linguagens' por qualquer grupo: bancos_dados, clouds, ferramentas_bi,
-- fontes_dados, linguagem_preferida, cloud_preferida, ferramenta_bi_diaria.

-- ⚠️ Repare que aqui o ano vai SEM aspas, e na CTE `base` vai COM.
-- `ano_pesquisa` tem tipo diferente conforme a tabela: no fato ela é coluna de
-- PARTIÇÃO, e o crawler tipa chave de partição como `varchar` porque o valor vem
-- do nome da pasta (`ano_pesquisa=2025`). Na bridge ela é coluna normal e o tipo
-- vem do Parquet, integer. Não é inconsistência de escrita, é o catálogo.

WITH base AS (
    SELECT COUNT(*) AS respondentes
    FROM gold_dw_fat_profissionais
    WHERE ano_pesquisa = '2025'
      AND qtd_linguagens IS NOT NULL
)
SELECT
    o.opcao_rotulo                                              AS tecnologia,
    COUNT(*)                                                    AS usam,
    (SELECT respondentes FROM base)                             AS base_da_pergunta,
    ROUND(100.0 * COUNT(*) / CAST((SELECT respondentes FROM base) AS DOUBLE), 1) AS pct
FROM gold_dw_bridge_respondente_opcao b
JOIN gold_dw_dim_opcao o ON o.sk_opcao = b.sk_opcao
WHERE b.ano_pesquisa = 2025
  AND o.grupo = 'linguagens'
GROUP BY o.opcao_rotulo
ORDER BY usam DESC
LIMIT 15;
