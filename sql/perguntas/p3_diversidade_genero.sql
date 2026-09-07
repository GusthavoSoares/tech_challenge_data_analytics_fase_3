-- P3. Qual é o cenário de diversidade de gênero?
--
-- Duas coisas na mesma consulta: participação por edição e gap salarial dentro
-- de cada senioridade.
--
-- O gap é calculado DENTRO da senioridade de propósito. Comparar o salário
-- médio de homens e mulheres sem controlar por senioridade mistura dois efeitos
-- (quanto se ganha no nível, e quem chega ao nível) e infla o número.

SELECT
    f.ano_pesquisa,
    s.rotulo                                                AS senioridade,
    g.rotulo                                                AS genero,
    COUNT(*)                                                AS respondentes,
    ROUND(100.0 * COUNT(*)
          / CAST(SUM(COUNT(*)) OVER (PARTITION BY f.ano_pesquisa, s.rotulo) AS DOUBLE), 1) AS pct_no_nivel,
    ROUND(AVG(f.salario_estimado), 0)                       AS salario_medio
FROM gold_dw_fat_profissionais f
JOIN gold_dw_dim_genero      g ON g.sk_genero_valor = f.sk_genero_valor
JOIN gold_dw_dim_senioridade s ON s.sk_senioridade  = f.sk_senioridade
WHERE f.serie_comparavel = true
GROUP BY f.ano_pesquisa, s.rotulo, g.rotulo
ORDER BY f.ano_pesquisa, senioridade, respondentes DESC;
