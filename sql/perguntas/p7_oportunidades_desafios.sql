-- P7. Quais oportunidades e desafios para quem quer investir em Dados e IA?
--
-- As barreiras à IA apontadas por quem respondeu o bloco de gestor, separadas
-- entre capital humano e tecnologia. É o achado que sustenta a recomendação:
-- a maior parte das barreiras não se resolve comprando ferramenta.
--
-- Denominador: `qtd_barreiras_ia_generativa IS NOT NULL`, ou seja, só quem viu
-- a pergunta. Bloco de gestor é condicional, a maioria da base nunca o viu.

-- ⚠️ Repare que aqui o ano vai SEM aspas, e na CTE `base` vai COM.
-- `ano_pesquisa` tem tipo diferente conforme a tabela: no fato ela é coluna de
-- PARTIÇÃO, e o crawler tipa chave de partição como `varchar` porque o valor vem
-- do nome da pasta (`ano_pesquisa=2025`). Na bridge ela é coluna normal e o tipo
-- vem do Parquet, integer. Não é inconsistência de escrita, é o catálogo.

WITH base AS (
    SELECT COUNT(*) AS gestores
    FROM gold_dw_fat_profissionais
    WHERE ano_pesquisa = '2025'
      AND qtd_barreiras_ia_generativa IS NOT NULL
)
SELECT
    o.opcao_rotulo                                           AS barreira,
    COUNT(*)                                                 AS citacoes,
    (SELECT gestores FROM base)                              AS base_gestores,
    ROUND(100.0 * COUNT(*) / CAST((SELECT gestores FROM base) AS DOUBLE), 1) AS pct_dos_gestores
FROM gold_dw_bridge_respondente_opcao b
JOIN gold_dw_dim_opcao o ON o.sk_opcao = b.sk_opcao
WHERE b.ano_pesquisa = 2025
  AND o.grupo = 'barreiras_ia_generativa'
GROUP BY o.opcao_rotulo
ORDER BY citacoes DESC;
