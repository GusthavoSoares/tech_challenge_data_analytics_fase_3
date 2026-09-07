-- P6. Há diferenças entre regiões, senioridades ou modelos de trabalho?
--
-- Salário por modelo de trabalho DENTRO de cada senioridade. O controle por
-- senioridade é o ponto: sem ele, remoto parece pagar mais só porque concentra
-- gente mais sênior.
--
-- `mudou_regiao` entra junto porque a evasão regional é parte da resposta:
-- em algumas regiões a maioria de quem nasceu lá trabalha fora.

SELECT
    s.rotulo                                  AS senioridade,
    m.rotulo                                  AS modelo_trabalho,
    COUNT(*)                                  AS respondentes,
    ROUND(AVG(f.salario_estimado), 0)         AS salario_medio,
    ROUND(100.0 * COUNT(*) FILTER (WHERE f.mudou_regiao = true)
          / CAST(NULLIF(COUNT(*) FILTER (WHERE f.mudou_regiao IS NOT NULL), 0) AS DOUBLE), 1) AS pct_saiu_da_regiao
FROM gold_dw_fat_profissionais f
JOIN gold_dw_dim_senioridade     s ON s.sk_senioridade     = f.sk_senioridade
JOIN gold_dw_dim_modelo_trabalho m ON m.sk_modelo_trabalho = f.sk_modelo_trabalho
WHERE f.ano_pesquisa = '2025'
  AND f.salario_estimado IS NOT NULL
GROUP BY s.rotulo, m.rotulo
HAVING COUNT(*) >= 30
ORDER BY senioridade, salario_medio DESC;
