"""
Gold da PERGUNTA 6: "Há diferenças relevantes entre regiões, senioridades
ou modelos de trabalho?"

Esta é a pergunta dos RECORTES. As três dimensões cruzam entre si e com
salário, e é isso que o cliente usa para decidir onde e como contratar.

⚠️ REGIÃO vem de `regiao_moradia` / `uf_moradia`, derivadas de `estado`.
NUNCA da coluna `uf` da Bronze: em 2025-2026 ela é o estado de NASCIMENTO.
Ver VALIDACAO_BRONZE §3.1. É o erro que atinge exatamente esta pergunta.

Nota para o Power BI: o mapa não geocodifica macrorregião brasileira. Use
`uf_moradia` (sigla) como localização. Ver MANUAL_POWERBI §3.
"""

import os
import sys

def _raiz_do_projeto():
    """
    Sobe a partir deste arquivo até achar a raiz (a pasta que contém `glue/`).

    Assim o import funciona de qualquer lugar: rodando o script direto, pelo
    notebook, ou com o Glue copiando os módulos para o mesmo diretório.
    """
    p = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if os.path.isdir(os.path.join(p, "glue")):
            return p
        pai = os.path.dirname(p)
        if pai == p:
            break
        p = pai
    return None


_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = _raiz_do_projeto()
for _p in [_AQUI, os.path.join(_AQUI, "..", "silver"),
           os.path.join(_RAIZ, "glue", "silver") if _RAIZ else None,
           os.path.join(_RAIZ, "glue", "gold") if _RAIZ else None]:
    if _p and os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)


from pyspark.sql import Window as W  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402

from gold_comum import (  # noqa: E402
    apenas_comparavel,
    base_da_pergunta,
    gravar,
    ler_silver,
    pct,
    sessao,
)

NUMERO, PREFIXO = "6", "gold_dw_p6_"
PERGUNTA = "Há diferenças relevantes entre regiões, senioridades ou modelos de trabalho?"


def construir(silver):
    t = {}
    base_sal = base_da_pergunta(silver, "salario_medio_mensal")

    # =====================================================================
    # REGIÃO
    # =====================================================================
    t["regiao_panorama"] = (
        base_da_pergunta(silver, "regiao_moradia")
        .groupBy("ano_pesquisa", "regiao_moradia")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"),
             F.round(F.expr("percentile_approx(salario_medio_mensal, 0.5)"), 0).alias("mediana"),
             F.round(F.avg("idade"), 1).alias("idade_media"))
        .withColumn("pct_do_total",
                    F.round(100.0 * F.col("profissionais")
                            / F.sum("profissionais").over(W.partitionBy("ano_pesquisa")), 1))
        .orderBy("ano_pesquisa", F.desc("profissionais"))
    )

    # Para o mapa: sigla da UF, que o Power BI geocodifica
    t["uf_panorama"] = (
        base_da_pergunta(silver, "uf_moradia")
        .groupBy("ano_pesquisa", "uf_moradia", "estado_moradia", "regiao_moradia")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
        .filter(F.col("profissionais") >= 5)
        .orderBy("ano_pesquisa", F.desc("profissionais"))
    )

    # Migração: quem mudou de estado. É o indicador de mobilidade do talento.
    t["migracao"] = (
        silver.filter(F.col("regiao_origem").isNotNull() & F.col("regiao_moradia").isNotNull())
              .withColumn("migrou", F.col("regiao_origem") != F.col("regiao_moradia"))
              .groupBy("ano_pesquisa", "regiao_origem")
              .agg(F.count("*").alias("nascidos_na_regiao"),
                   F.count(F.when(F.col("migrou"), 1)).alias("sairam"))
              .withColumn("pct_saiu", pct(F.col("sairam"), F.col("nascidos_na_regiao")))
              .orderBy("ano_pesquisa", F.desc("pct_saiu"))
    )

    t["regiao_x_senioridade"] = (
        apenas_comparavel(silver)
        .filter(F.col("regiao_moradia").isNotNull() & F.col("nivel_senioridade").isNotNull())
        .groupBy("regiao_moradia", "nivel_senioridade")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
        .withColumn("pct_da_regiao",
                    F.round(100.0 * F.col("profissionais")
                            / F.sum("profissionais").over(W.partitionBy("regiao_moradia")), 1))
        .orderBy("regiao_moradia", "nivel_senioridade")
    )

    # =====================================================================
    # SENIORIDADE
    # =====================================================================
    t["senioridade_panorama"] = (
        apenas_comparavel(base_da_pergunta(silver, "nivel_senioridade"))
        .groupBy("ano_pesquisa", "nivel_senioridade")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"),
             F.round(F.avg("idade"), 1).alias("idade_media"))
        .withColumn("pct", F.round(100.0 * F.col("profissionais")
                                   / F.sum("profissionais").over(W.partitionBy("ano_pesquisa")), 1))
        .orderBy("ano_pesquisa", "nivel_senioridade")
    )

    t["senioridade_x_tempo_exp"] = (
        silver.filter(F.col("nivel_senioridade").isNotNull() & F.col("tempo_exp_dados").isNotNull())
              .groupBy("nivel_senioridade", "tempo_exp_dados")
              .agg(F.count("*").alias("profissionais"))
              .withColumn("pct_do_nivel",
                          F.round(100.0 * F.col("profissionais")
                                  / F.sum("profissionais").over(W.partitionBy("nivel_senioridade")), 1))
              .orderBy("nivel_senioridade", F.desc("profissionais"))
    )

    # =====================================================================
    # MODELO DE TRABALHO
    # =====================================================================
    t["modelo_panorama"] = (
        base_da_pergunta(silver, "forma_trabalho")
        .groupBy("ano_pesquisa", "forma_trabalho")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
        .withColumn("pct", F.round(100.0 * F.col("profissionais")
                                   / F.sum("profissionais").over(W.partitionBy("ano_pesquisa")), 1))
        .orderBy("ano_pesquisa", F.desc("profissionais"))
    )

    t["modelo_x_regiao"] = (
        silver.filter(F.col("forma_trabalho").isNotNull() & F.col("regiao_moradia").isNotNull())
              .groupBy("ano_pesquisa", "regiao_moradia", "forma_trabalho")
              .agg(F.count("*").alias("profissionais"))
              .withColumn("pct_da_regiao",
                          F.round(100.0 * F.col("profissionais")
                                  / F.sum("profissionais").over(
                                      W.partitionBy("ano_pesquisa", "regiao_moradia")), 1))
              .orderBy("ano_pesquisa", "regiao_moradia", F.desc("profissionais"))
    )

    t["modelo_x_senioridade"] = (
        apenas_comparavel(silver)
        .filter(F.col("forma_trabalho").isNotNull() & F.col("nivel_senioridade").isNotNull())
        .groupBy("forma_trabalho", "nivel_senioridade")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
        .orderBy("forma_trabalho", "nivel_senioridade")
    )

    # Remoto paga mais? Controlando por senioridade, para não confundir
    # "remoto paga mais" com "quem é sênior trabalha mais remoto".
    t["remoto_paga_mais"] = (
        base_sal.filter(F.col("forma_trabalho").isNotNull() & F.col("nivel_senioridade").isNotNull())
                .withColumn("eh_remoto", F.col("forma_trabalho") == "Modelo_100%_remoto")
                .groupBy("nivel_senioridade", "eh_remoto")
                .agg(F.count("*").alias("profissionais"),
                     F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
                .orderBy("nivel_senioridade", "eh_remoto")
    )

    # Satisfação e layoff por modelo: a dimensão humana do recorte
    t["satisfacao_por_modelo"] = (
        base_da_pergunta(silver, "satisfeito_empresa")
        .filter(F.col("forma_trabalho").isNotNull())
        .groupBy("ano_pesquisa", "forma_trabalho")
        .agg(F.count("*").alias("base"),
             F.count(F.when(F.col("satisfeito_empresa"), 1)).alias("satisfeitos"))
        .withColumn("pct_satisfeitos", pct(F.col("satisfeitos"), F.col("base")))
        .orderBy("ano_pesquisa", F.desc("pct_satisfeitos"))
    )

    # =====================================================================
    # O CRUZAMENTO DAS TRÊS: a tabela que responde a pergunta
    # =====================================================================
    t["regiao_senioridade_modelo"] = (
        apenas_comparavel(base_sal)
        .filter(F.col("regiao_moradia").isNotNull() & F.col("nivel_senioridade").isNotNull()
                & F.col("forma_trabalho").isNotNull())
        .groupBy("regiao_moradia", "nivel_senioridade", "forma_trabalho")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
        .filter(F.col("profissionais") >= 20)
        .orderBy(F.desc("salario_medio"))
    )

    return t


def main():
    spark = sessao(f"tc3-gold-p{NUMERO}")
    silver = ler_silver(spark).cache()
    print(f"\n=== Gold da pergunta {NUMERO} ===\n{PERGUNTA}\n")
    for nome, df in construir(silver).items():
        gravar(df, PREFIXO + nome, mostrar=False)
    spark.stop()


if __name__ == "__main__":
    main()
