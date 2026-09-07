-- P1. Como está estruturado o mercado brasileiro de Dados?
--
-- Distribuição dos profissionais por família de cargo e por senioridade, na
-- edição mais recente. Grão do fato: 1 linha por respondente por edição.
--
-- Denominador: todos os respondentes do ano. Cargo e senioridade são pergunta
-- de resposta única, todo mundo respondeu, então aqui não existe a armadilha
-- do NULL da múltipla escolha.

SELECT
    c.familia,
    c.rotulo                                                   AS cargo,
    s.rotulo                                                   AS senioridade,
    COUNT(*)                                                   AS profissionais,
    ROUND(100.0 * COUNT(*) / CAST(SUM(COUNT(*)) OVER () AS DOUBLE), 1)         AS pct_do_ano
FROM gold_dw_fat_profissionais f
JOIN gold_dw_dim_cargo       c ON c.sk_cargo       = f.sk_cargo
JOIN gold_dw_dim_senioridade s ON s.sk_senioridade = f.sk_senioridade
WHERE f.ano_pesquisa = '2025'
GROUP BY c.familia, c.rotulo, s.rotulo
ORDER BY profissionais DESC
LIMIT 25;
