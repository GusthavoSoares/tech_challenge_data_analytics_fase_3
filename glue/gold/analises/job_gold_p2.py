"""
Gold da PERGUNTA 2: "Quais perfis profissionais são mais valorizados?"

"Valorizado" tem duas leituras e as duas importam:

  · quanto o mercado PAGA  ......... salário por cargo, senioridade, formação
  · quanto o mercado DISPUTA ....... volume de vagas recebidas, progressão

A primeira sai do salário. A segunda sai do bloco `percepcao_carreira`, que
mede como a pessoa avalia as oportunidades que recebe, e é respondido por
~24% da base, não por todos.
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

NUMERO, PREFIXO = "2", "gold_dw_p2_"
PERGUNTA = "Quais perfis profissionais são mais valorizados?"

MIN_AMOSTRA = 30   # abaixo disso a média salarial oscila demais para reportar


def construir(silver):
    t = {}
    base_sal = base_da_pergunta(silver, "salario_medio_mensal")

    def salario_por(coluna, minimo=MIN_AMOSTRA, por_ano=True):
        chaves = (["ano_pesquisa", coluna] if por_ano else [coluna])
        return (
            base_sal.filter(F.col(coluna).isNotNull())
                    .groupBy(*chaves)
                    .agg(F.count("*").alias("profissionais"),
                         F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"),
                         F.round(F.expr("percentile_approx(salario_medio_mensal, 0.5)"), 0).alias("mediana"),
                         F.round(F.expr("percentile_approx(salario_medio_mensal, 0.75)"), 0).alias("p75"))
                    .filter(F.col("profissionais") >= minimo)
                    .orderBy(F.desc("salario_medio"))
        )

    # --- quanto paga -----------------------------------------------------
    t["salario_por_cargo"] = salario_por("cargo_atual")
    t["salario_por_cargo_geral"] = salario_por("cargo_atual", minimo=50, por_ano=False)
    t["salario_por_senioridade"] = salario_por("nivel_senioridade")
    t["salario_por_formacao"] = salario_por("nivel_ensino")
    t["salario_por_area_formacao"] = salario_por("area_formacao")
    t["salario_por_setor"] = salario_por("setor_empresa")
    t["salario_por_tempo_exp"] = salario_por("tempo_exp_dados")

    # Gestão paga mais? A comparação que o cliente sempre faz.
    t["salario_gestor_x_ic"] = (
        base_sal.filter(F.col("eh_gestor").isNotNull())
                .groupBy("ano_pesquisa", "eh_gestor")
                .agg(F.count("*").alias("profissionais"),
                     F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
                .orderBy("ano_pesquisa", "eh_gestor")
    )

    # --- o salto entre níveis, que é o que orienta plano de carreira -----
    janela = W.partitionBy("ano_pesquisa").orderBy("ordem")
    ordem_nivel = F.when(F.col("nivel_senioridade") == "Junior", 1) \
                   .when(F.col("nivel_senioridade") == "Pleno", 2) \
                   .when(F.col("nivel_senioridade") == "Senior", 3) \
                   .when(F.col("nivel_senioridade") == "Especialista/Staff+", 4)
    t["salto_entre_niveis"] = (
        t["salario_por_senioridade"]
        .withColumn("ordem", ordem_nivel)
        .withColumn("salario_anterior", F.lag("salario_medio").over(janela))
        .withColumn("salto_pct",
                    F.round(100.0 * (F.col("salario_medio") - F.col("salario_anterior"))
                            / F.col("salario_anterior"), 1))
        .orderBy("ano_pesquisa", "ordem")
    )

    # --- quanto o mercado disputa ---------------------------------------
    # `percepcao_carreira` é respondido por ~24%: não é a base inteira.
    base_perc = base_da_pergunta(silver, "percepcao_carreira")
    percepcoes = [
        ("qtd_oportunidades_vagas_emprego_receb", "Recebe muitas oportunidades"),
        ("senioridade_vagas_recebidas_rel_experiencia", "Vagas compatíveis com a senioridade"),
        ("vel_progressao_carreira", "Progressão de carreira rápida"),
        ("oportunidades_progresso_carreira", "Tem oportunidade de progredir"),
        ("aprov_processos_seletivos_entrevistas", "Aprova nos processos seletivos"),
        ("nvl_cobranca_e_stress_trab", "Nível de cobrança e stress"),
    ]
    t["percepcao_carreira"] = None
    for col, rotulo in percepcoes:
        parcial = indicador(base_perc, marcou("percepcao_carreira", col),
                            por=["ano_pesquisa"], rotulo=rotulo)
        t["percepcao_carreira"] = parcial if t["percepcao_carreira"] is None \
            else t["percepcao_carreira"].unionByName(parcial)
    t["percepcao_carreira"] = t["percepcao_carreira"].orderBy("ano_pesquisa", F.desc("pct"))

    # --- ranking final: o perfil mais valorizado -------------------------
    # Cargo x senioridade, só onde há amostra. É a tabela que responde a
    # pergunta em uma linha.
    t["perfil_mais_valorizado"] = (
        apenas_comparavel(base_sal)
        .filter(F.col("cargo_atual").isNotNull() & F.col("nivel_senioridade").isNotNull())
        .groupBy("cargo_atual", "nivel_senioridade")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
        .filter(F.col("profissionais") >= MIN_AMOSTRA)
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
