-- P5. Qual é o índice de adoção de IA e seu impacto?
--
-- O gap central do trabalho: adoção individual contra prioridade da empresa.
--
-- `usa_ia_generativa` é derivado SÓ das opções de uso pessoal. Isso importa:
-- a coluna de origem `uso_ia_generativa` juntava três perguntas diferentes
-- (uso pessoal, como a empresa organiza, e a visão do gestor), e gestor nunca
-- viu a pergunta de uso pessoal. Contar gestor como usuário inflava a adoção
-- em mais de 2 pontos sobre uma base 27% maior que a real.
--
-- Por isso o denominador é `usa_ia_generativa IS NOT NULL`, não o total do ano.

SELECT
    ano_pesquisa,
    COUNT(*) FILTER (WHERE usa_ia_generativa IS NOT NULL)              AS base_uso_pessoal,
    ROUND(100.0 * COUNT(*) FILTER (WHERE usa_ia_generativa = true)
          / CAST(NULLIF(COUNT(*) FILTER (WHERE usa_ia_generativa IS NOT NULL), 0) AS DOUBLE), 1) AS pct_usa_ia,
    COUNT(*) FILTER (WHERE ia_prioridade_alta IS NOT NULL)             AS base_prioridade,
    ROUND(100.0 * COUNT(*) FILTER (WHERE ia_prioridade_alta = true)
          / CAST(NULLIF(COUNT(*) FILTER (WHERE ia_prioridade_alta IS NOT NULL), 0) AS DOUBLE), 1) AS pct_empresa_prioriza
FROM gold_dw_fat_profissionais
GROUP BY ano_pesquisa
ORDER BY ano_pesquisa;
