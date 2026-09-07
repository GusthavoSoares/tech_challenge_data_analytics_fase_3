-- P2. Quais perfis profissionais são mais valorizados?
--
-- Salário médio estimado por cargo e senioridade. O `salario_estimado` é o
-- ponto médio da faixa que o respondente marcou, calculado na Silver: a origem
-- dá faixa, não valor.
--
-- `HAVING COUNT(*) >= 30` corta combinação com amostra pequena demais para
-- média fazer sentido. Sem esse corte, um cargo com 3 respondentes aparece no
-- topo da lista e engana.
--
-- ⚠️ A mediana é APROXIMADA e depende do motor. `APPROX_PERCENTILE` usa
-- algoritmos diferentes no Trino (Athena) e no Spark, e o Trino interpola: a
-- mesma consulta devolveu 18.123 no Athena e 18.001 no Spark para a mesma linha.
-- Nenhum dos dois está errado. Ao citar número na apresentação, use a MÉDIA, que
-- é exata e bate nos dois. A mediana serve para enxergar a assimetria, não para
-- ser reproduzida ao centavo.

SELECT
    c.rotulo                             AS cargo,
    s.rotulo                             AS senioridade,
    COUNT(*)                             AS respondentes,
    ROUND(AVG(f.salario_estimado), 0)    AS salario_medio_mes,
    ROUND(APPROX_PERCENTILE(f.salario_estimado, 0.5), 0) AS mediana_aprox
FROM gold_dw_fat_profissionais f
JOIN gold_dw_dim_cargo       c ON c.sk_cargo       = f.sk_cargo
JOIN gold_dw_dim_senioridade s ON s.sk_senioridade = f.sk_senioridade
WHERE f.ano_pesquisa = '2025'
  AND f.salario_estimado IS NOT NULL
GROUP BY c.rotulo, s.rotulo
HAVING COUNT(*) >= 30
ORDER BY salario_medio_mes DESC
LIMIT 20;
