"""
Gold da PERGUNTA 3: "Qual é o cenário de diversidade de gênero nas
carreiras de dados?"

Diversidade não é uma métrica só. São quatro perguntas diferentes:

  1. REPRESENTAÇÃO, quantas mulheres existem na área
  2. EQUIDADE SALARIAL, elas ganham o mesmo pelo mesmo trabalho
  3. ACESSO À SENIORIDADE, elas chegam aos cargos de cima
  4. EXPERIÊNCIA VIVIDA, elas relatam prejuízo por serem quem são

Reportar só a primeira é o erro clássico: uma empresa pode ter 30% de mulheres
e ainda assim nenhuma em posição de liderança.

⚠️ Comparação salarial por gênero SEM controlar senioridade e cargo mistura
duas coisas: diferença de remuneração e diferença de composição. As duas
tabelas estão aqui separadas de propósito: `salario_bruto` e
`salario_controlado`.
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
    indicador,
    ler_silver,
    marcou,
    sessao,
)

NUMERO, PREFIXO = "3", "gold_dw_p3_"
PERGUNTA = "Qual é o cenário de diversidade de gênero nas carreiras de dados?"


def construir(silver):
    t = {}

    # =====================================================================
    # 1. REPRESENTAÇÃO
    # =====================================================================
    t["representacao"] = (
        base_da_pergunta(silver, "genero")
        .groupBy("ano_pesquisa", "genero")
        .agg(F.count("*").alias("profissionais"))
        .withColumn("pct", F.round(100.0 * F.col("profissionais")
                                   / F.sum("profissionais").over(W.partitionBy("ano_pesquisa")), 1))
        .orderBy("ano_pesquisa", F.desc("profissionais"))
    )

    # Recorte racial junto: diversidade de gênero lida isolada esconde
    # a interseção, que é onde o número costuma ser pior.
    t["genero_x_raca"] = (
        silver.filter(F.col("genero").isNotNull() & F.col("cor_raca_etnia").isNotNull())
              .groupBy("ano_pesquisa", "genero", "cor_raca_etnia")
              .agg(F.count("*").alias("profissionais"))
              .orderBy("ano_pesquisa", F.desc("profissionais"))
    )

    t["representacao_por_cargo"] = (
        silver.filter(F.col("genero").isNotNull() & F.col("cargo_atual").isNotNull())
              .groupBy("cargo_atual", "genero")
              .agg(F.count("*").alias("profissionais"))
              .withColumn("pct_no_cargo",
                          F.round(100.0 * F.col("profissionais")
                                  / F.sum("profissionais").over(W.partitionBy("cargo_atual")), 1))
              .orderBy("cargo_atual", F.desc("profissionais"))
    )

    t["representacao_por_setor"] = (
        silver.filter(F.col("genero").isNotNull() & F.col("setor_empresa").isNotNull())
              .groupBy("setor_empresa", "genero")
              .agg(F.count("*").alias("profissionais"))
              .withColumn("pct_no_setor",
                          F.round(100.0 * F.col("profissionais")
                                  / F.sum("profissionais").over(W.partitionBy("setor_empresa")), 1))
              .orderBy("setor_empresa", F.desc("profissionais"))
    )

    # =====================================================================
    # 2. EQUIDADE SALARIAL
    # =====================================================================
    base_sal = base_da_pergunta(silver, "salario_medio_mensal").filter(F.col("genero").isNotNull())

    # Bruto: mistura remuneração com composição. Serve para dimensionar o gap
    # total, NÃO para afirmar discriminação.
    t["salario_bruto"] = (
        base_sal.groupBy("ano_pesquisa", "genero")
                .agg(F.count("*").alias("profissionais"),
                     F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"),
                     F.round(F.expr("percentile_approx(salario_medio_mensal, 0.5)"), 0).alias("mediana"))
                .orderBy("ano_pesquisa", "genero")
    )

    # Controlado: mesmo cargo, mesma senioridade. É esta que sustenta a
    # afirmação de diferença de remuneração.
    t["salario_controlado"] = (
        base_sal.filter(F.col("nivel_senioridade").isNotNull() & F.col("cargo_atual").isNotNull()
                        & F.col("genero").isin("Masculino", "Feminino"))
                .groupBy("cargo_atual", "nivel_senioridade", "genero")
                .agg(F.count("*").alias("profissionais"),
                     F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
                .filter(F.col("profissionais") >= 20)
                .orderBy("cargo_atual", "nivel_senioridade", "genero")
    )

    # O gap em pontos, por senioridade: o formato que vai para o gráfico.
    pivo = (base_sal.filter(F.col("genero").isin("Masculino", "Feminino")
                            & F.col("nivel_senioridade").isNotNull())
                    .groupBy("ano_pesquisa", "nivel_senioridade")
                    .pivot("genero", ["Masculino", "Feminino"])
                    .agg(F.round(F.avg("salario_medio_mensal"), 0)))
    t["gap_salarial_por_nivel"] = (
        pivo.withColumn("gap_reais", F.col("Masculino") - F.col("Feminino"))
            .withColumn("gap_pct", F.round(100.0 * (F.col("Masculino") - F.col("Feminino"))
                                           / F.col("Masculino"), 1))
            .orderBy("ano_pesquisa", "nivel_senioridade")
    )

    # =====================================================================
    # 3. ACESSO À SENIORIDADE E À LIDERANÇA
    # =====================================================================
    t["senioridade_por_genero"] = (
        apenas_comparavel(silver)
        .filter(F.col("genero").isNotNull() & F.col("nivel_senioridade").isNotNull())
        .groupBy("ano_pesquisa", "genero", "nivel_senioridade")
        .agg(F.count("*").alias("profissionais"))
        .withColumn("pct_do_genero",
                    F.round(100.0 * F.col("profissionais")
                            / F.sum("profissionais").over(
                                W.partitionBy("ano_pesquisa", "genero")), 1))
        .orderBy("ano_pesquisa", "genero", "nivel_senioridade")
    )

    base_gestor = base_da_pergunta(silver, "eh_gestor").filter(F.col("genero").isNotNull())
    t["lideranca_por_genero"] = (
        base_gestor.groupBy("ano_pesquisa", "genero")
                   .agg(F.count("*").alias("base"),
                        F.count(F.when(F.col("eh_gestor"), 1)).alias("gestores"))
                   .withColumn("pct_gestores", F.round(100.0 * F.col("gestores") / F.col("base"), 1))
                   .orderBy("ano_pesquisa", "genero")
    )

    # =====================================================================
    # 4. EXPERIÊNCIA VIVIDA
    # =====================================================================
    # `exp_prof_prejudicada`: respondido por ~51% da base.
    base_exp = base_da_pergunta(silver, "exp_prof_prejudicada")
    t["prejuizo_relatado"] = None
    for col, rotulo in [("exp_prof_prejud_ident_gen", "Prejudicado por identidade de gênero"),
                        ("exp_prof_prejud_cor_raca_etnia", "Prejudicado por cor/raça/etnia"),
                        ("exp_prof_prejud_pcd", "Prejudicado por ser PCD"),
                        ("exp_prof_nao_prejud", "Não se sentiu prejudicado")]:
        parcial = (indicador(base_exp, marcou("exp_prof_prejudicada", col),
                             por=["ano_pesquisa", "genero"], rotulo=rotulo))
        t["prejuizo_relatado"] = parcial if t["prejuizo_relatado"] is None \
            else t["prejuizo_relatado"].unionByName(parcial)
    t["prejuizo_relatado"] = (t["prejuizo_relatado"]
                              .filter(F.col("genero").isNotNull())
                              .orderBy("ano_pesquisa", "indicador", "genero"))

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
