"""
Gold da PERGUNTA 1: "Como está estruturado o mercado brasileiro de Dados?"

O retrato do mercado: quem são essas pessoas, onde estão, o que estudaram,
em que setor trabalham e como se distribuem entre cargos e senioridade.

É a pergunta descritiva, a base sobre a qual as outras seis conversam.
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
    sessao,
)

NUMERO, PREFIXO = "1", "gold_dw_p1_"
PERGUNTA = "Como está estruturado o mercado brasileiro de Dados?"


def _distribuicao(df, coluna, minimo=0):
    """Contagem + % dentro do ano. O padrão de quase toda tabela desta pergunta."""
    return (
        base_da_pergunta(df, coluna)
        .groupBy("ano_pesquisa", coluna)
        .agg(F.count("*").alias("profissionais"))
        .withColumn("pct", F.round(100.0 * F.col("profissionais")
                                   / F.sum("profissionais").over(W.partitionBy("ano_pesquisa")), 1))
        .filter(F.col("profissionais") >= minimo)
        .orderBy("ano_pesquisa", F.desc("profissionais"))
    )


def construir(silver):
    t = {}

    # --- tamanho e composição da amostra --------------------------------
    t["visao_geral"] = (
        silver.groupBy("ano_pesquisa", "edicao")
              .agg(F.count("*").alias("respondentes"),
                   F.round(F.avg("idade"), 1).alias("idade_media"),
                   F.round(F.expr("percentile_approx(idade, 0.5)"), 0).alias("idade_mediana"),
                   F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"),
                   F.count(F.when(F.col("eh_gestor"), 1)).alias("gestores"))
              .orderBy("ano_pesquisa")
    )

    # --- quem são --------------------------------------------------------
    t["faixa_etaria"] = _distribuicao(silver, "faixa_etaria")
    t["formacao"] = _distribuicao(silver, "nivel_ensino")
    t["area_formacao"] = _distribuicao(silver, "area_formacao")

    # --- onde estão ------------------------------------------------------
    t["regiao"] = _distribuicao(silver, "regiao_moradia")
    # UF é a granularidade do mapa: o Power BI NÃO geocodifica macrorregião
    # brasileira (Sudeste, Sul...). Ver MANUAL_POWERBI §3.
    t["uf"] = _distribuicao(silver, "uf_moradia", minimo=5)
    t["setor"] = _distribuicao(silver, "setor_empresa")

    # --- o que fazem -----------------------------------------------------
    t["cargo"] = _distribuicao(silver, "cargo_atual")
    t["senioridade"] = (
        apenas_comparavel(base_da_pergunta(silver, "nivel_senioridade"))
        .groupBy("ano_pesquisa", "nivel_senioridade")
        .agg(F.count("*").alias("profissionais"))
        .withColumn("pct", F.round(100.0 * F.col("profissionais")
                                   / F.sum("profissionais").over(W.partitionBy("ano_pesquisa")), 1))
        .orderBy("ano_pesquisa", "nivel_senioridade")
    )
    t["tempo_experiencia"] = _distribuicao(silver, "tempo_exp_dados")

    # --- maturidade das empresas (só gestores respondem) -----------------
    base_mat = base_da_pergunta(silver, "empresa_possui_datalake")
    t["maturidade_empresas"] = (
        base_mat.groupBy("ano_pesquisa")
                .agg(F.count("*").alias("base_gestores"),
                     F.count(F.when(F.col("empresa_possui_datalake"), 1)).alias("com_datalake"),
                     F.count(F.when(F.col("empresa_possui_dw"), 1)).alias("com_dw"))
                .withColumn("pct_datalake", F.round(100.0 * F.col("com_datalake") / F.col("base_gestores"), 1))
                .withColumn("pct_dw", F.round(100.0 * F.col("com_dw") / F.col("base_gestores"), 1))
                .orderBy("ano_pesquisa")
    )

    # --- composição dos times (quais cargos a empresa tem) ---------------
    base_time = base_da_pergunta(silver, "cargos_no_time")
    cargos = ["analista_dados", "cientista_dados", "engenheiro_dados", "analista_bi",
              "engenheiro_analytics", "engenheiro_ml_ia", "arquiteto_dados",
              "analista_business", "data_product_manager", "dba"]
    t["composicao_times"] = None
    for c in cargos:
        parcial = (base_time.groupBy("ano_pesquisa")
                   .agg(F.count("*").alias("base"),
                        F.count(F.when(F.col("cargos_no_time").contains(c), 1)).alias("qtd"))
                   .withColumn("pct", F.round(100.0 * F.col("qtd") / F.col("base"), 1))
                   .withColumn("cargo_no_time", F.lit(c)))
        t["composicao_times"] = parcial if t["composicao_times"] is None \
            else t["composicao_times"].unionByName(parcial)
    t["composicao_times"] = t["composicao_times"].orderBy("ano_pesquisa", F.desc("pct"))

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
