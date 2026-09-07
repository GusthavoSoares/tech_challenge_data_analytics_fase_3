"""
Gold da PERGUNTA 4: "Quais tecnologias têm maior adoção entre os
profissionais?"

Linguagens, bancos, clouds e ferramentas de BI. Todos são grupos de múltipla
escolha, então valem as duas regras:

  · o denominador é quem VIU a pergunta (~60-71% da base, não 14.002);
  · a opção é casada inteira com `marcou()`, não com LIKE.

⚠️ `bancos_dados` está entre os grupos com rótulo NÃO harmonizado entre
edições (ver config §2c). A adoção de cada banco em um ano é confiável; a
série temporal do grupo precisa do de-para do Alexandre. Por isso as tabelas
de banco saem por ano e a série fica marcada.
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
    base_da_pergunta,
    gravar,
    ler_silver,
    sessao,
)

NUMERO, PREFIXO = "4", "gold_dw_p4_"
PERGUNTA = "Quais tecnologias têm maior adoção entre os profissionais?"


def ranking(silver, grupo, minimo=20):
    """
    Explode o grupo em uma linha por opção e calcula adoção sobre a base
    que respondeu, não sobre a Silver inteira.
    """
    base = base_da_pergunta(silver, grupo)
    tamanho = (base.groupBy("ano_pesquisa").agg(F.count("*").alias("base")))
    explodido = (
        base.filter(F.col(grupo) != "")
            .select("ano_pesquisa",
                    F.explode(F.split(F.col(grupo), ", ")).alias("tecnologia"))
            .groupBy("ano_pesquisa", "tecnologia")
            .agg(F.count("*").alias("usuarios"))
    )
    return (
        explodido.join(tamanho, "ano_pesquisa")
                 .withColumn("pct_adocao", F.round(100.0 * F.col("usuarios") / F.col("base"), 1))
                 .withColumn("posicao",
                             F.row_number().over(W.partitionBy("ano_pesquisa")
                                                  .orderBy(F.desc("usuarios"))))
                 .filter(F.col("usuarios") >= minimo)
                 .orderBy("ano_pesquisa", "posicao")
    )


def construir(silver):
    t = {}

    # --- os quatro rankings de adoção ------------------------------------
    t["linguagens"] = ranking(silver, "linguagens")
    t["bancos_dados"] = ranking(silver, "bancos_dados")
    t["clouds"] = ranking(silver, "clouds", minimo=5)
    t["ferramentas_bi"] = ranking(silver, "ferramentas_bi")
    t["fontes_dados"] = ranking(silver, "fontes_dados")

    # --- a preferida / a do dia a dia ------------------------------------
    # ⚠️ Estas três colunas PARECEM resposta única e não são: a pessoa marca
    # mais de uma e a origem concatena. `ferramenta_bi_diaria` tinha 1.422
    # strings distintas, 1.031 delas aparecendo uma única vez. A Silver já
    # normaliza (ordena e usa ", "), então aqui explodimos como qualquer
    # outro grupo: agrupar pela string inteira contaria "Python, SQL" como
    # uma categoria própria, separada de "Python".
    for coluna, nome in [("linguagem_preferida", "linguagem_preferida"),
                         ("cloud_preferida", "cloud_preferida"),
                         ("ferramenta_bi_diaria", "bi_do_dia_a_dia")]:
        t[nome] = ranking(silver, coluna, minimo=10)

    # --- quantas tecnologias por pessoa ----------------------------------
    # Um profissional que usa 6 linguagens é diferente de um que usa 2: e o
    # número médio é um indicador de amplitude do stack.
    t["amplitude_stack"] = (
        silver.filter(F.col("qtd_linguagens").isNotNull())
              .groupBy("ano_pesquisa")
              .agg(F.count("*").alias("base"),
                   F.round(F.avg("qtd_linguagens"), 2).alias("media_linguagens"),
                   F.round(F.avg("qtd_bancos_dados"), 2).alias("media_bancos"),
                   F.round(F.avg("qtd_clouds"), 2).alias("media_clouds"),
                   F.round(F.avg("qtd_ferramentas_bi"), 2).alias("media_bi"))
              .orderBy("ano_pesquisa")
    )

    # --- stack por cargo: o que cada perfil realmente usa ----------------
    base_ling = base_da_pergunta(silver, "linguagens").filter(F.col("cargo_atual").isNotNull())
    tam_cargo = base_ling.groupBy("cargo_atual").agg(F.count("*").alias("base"))
    t["linguagem_por_cargo"] = (
        base_ling.filter(F.col("linguagens") != "")
                 .select("cargo_atual", F.explode(F.split(F.col("linguagens"), ", ")).alias("tecnologia"))
                 .groupBy("cargo_atual", "tecnologia")
                 .agg(F.count("*").alias("usuarios"))
                 .join(tam_cargo, "cargo_atual")
                 .withColumn("pct_adocao", F.round(100.0 * F.col("usuarios") / F.col("base"), 1))
                 .filter(F.col("usuarios") >= 20)
                 .orderBy("cargo_atual", F.desc("usuarios"))
    )

    # --- cloud x senioridade: onde o investimento em nuvem se concentra --
    base_cloud = base_da_pergunta(silver, "clouds").filter(F.col("nivel_senioridade").isNotNull())
    tam_nvl = base_cloud.groupBy("nivel_senioridade").agg(F.count("*").alias("base"))
    t["cloud_por_senioridade"] = (
        base_cloud.filter(F.col("clouds") != "")
                  .select("nivel_senioridade", F.explode(F.split(F.col("clouds"), ", ")).alias("cloud"))
                  .groupBy("nivel_senioridade", "cloud")
                  .agg(F.count("*").alias("usuarios"))
                  .join(tam_nvl, "nivel_senioridade")
                  .withColumn("pct_adocao", F.round(100.0 * F.col("usuarios") / F.col("base"), 1))
                  .orderBy("nivel_senioridade", F.desc("usuarios"))
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
