"""
Gold da PERGUNTA 7 (autor: Caio Bosnic).

    "Quais oportunidades e desafios para empresas que querem investir
     em Dados e IA?"

É a pergunta de síntese: as outras seis descrevem o mercado, esta responde
o que uma instituição financeira deve FAZER com essa descrição. Por isso as
tabelas aqui são organizadas por **decisão** (contratar, capacitar, investir,
reter), não por tema.

Cada tabela responde uma pergunta que o cliente faria em voz alta.

--------------------------------------------------------------------------
A ARMADILHA QUE MAIS PESA NESTA PERGUNTA
--------------------------------------------------------------------------
Existem TRÊS populações nesta base e elas NÃO se misturam:

  · uso individual de IA .........  9.494  (quem VIU a pergunta de uso pessoal;
                                            a coluna tem 12.041 preenchidas, mas
                                            2.547 são gestores que responderam
                                            só o bloco deles. Use
                                            `base_uso_ia_pessoal()`)
  · estratégia de IA da empresa ..  2.593  (SÓ GESTORES, 100% eh_gestor=true)
  · maturidade de dados ..........  2.396  (SÓ ENGENHEIROS DE DADOS,
                                            0% gestores, 100% de sobreposição
                                            com atividades_engenheiro_dados)

"61% das empresas têm IA como prioridade" é uma frase sobre a segunda. Calcular
sobre 14.002 daria 3% e seria falso por um fator de 20.

⚠️ E a interseção entre a segunda e a terceira é ZERO: ninguém responde os dois
blocos. Não dá para cruzar "prioriza IA" com "tem data lake" nesta base.

⚠️ A maturidade de dados vem de quem CONSTRÓI a infraestrutura, não de quem a
financia. Isso enviesa para cima: engenheiro de dados trabalha, por definição,
em empresa que já investiu em dados. Os 82% com data lake descrevem "empresas
que empregam engenheiros de dados", não "empresas brasileiras".

Toda tabela aqui carrega a coluna `base` para o denominador ir junto no slide.
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


from pyspark.sql import functions as F  # noqa: E402
from pyspark.sql import Window as W  # noqa: E402

from gold_comum import (  # noqa: E402
    apenas_comparavel,
    base_da_pergunta,
    base_uso_ia_pessoal,
    gravar,
    indicador,
    ler_silver,
    marcou,
    pct,
    sessao,
    usa_ia_pessoal,
)

NUMERO = "7"
PERGUNTA = "Quais oportunidades e desafios para empresas que querem investir em Dados e IA?"
RESPONSAVEL = "Caio Bosnic"
PREFIXO = "gold_dw_p7_"

PRIORIDADE_ALTA = [
    "Sim,_e_nossa_principal_prioridade_como_empresa_(com_foco_executivo_significativo"
    "_e_alocacao_de_orcamento_relevante).",
    "Sim,_esta_entre_nossas_principais_prioridades_para_os_proximos_2-4_anos"
    "_(com_discussoes_de_iniciativas_e_orcamentos_de_curto_a_medio_prazo).",
]


def construir(silver):
    t = {}

    # =====================================================================
    # OPORTUNIDADE 1: a demanda por IA está subindo e a oferta acompanha?
    # =====================================================================
    # Base: gestores. É a pergunta sobre a EMPRESA.
    gestores = base_da_pergunta(silver, "ia_gen_prioridade")

    t["ia_prioridade_empresa"] = indicador(
        gestores, F.col("ia_gen_prioridade").isin(PRIORIDADE_ALTA),
        por=["ano_pesquisa"], rotulo="IA generativa é prioridade alta",
    )

    # Base: quem VIU a pergunta de uso pessoal. Não é "todo mundo": a coluna
    # `uso_ia_generativa` junta três perguntas, e gestor tem ela preenchida sem
    # nunca ter sido perguntado sobre uso próprio.
    usuarios = base_uso_ia_pessoal(silver)
    t["ia_uso_individual"] = indicador(
        usuarios, usa_ia_pessoal(),
        por=["ano_pesquisa"], rotulo="usa IA generativa no trabalho",
    )

    # O gap entre as duas curvas é o argumento central da oportunidade:
    # a adoção individual corre na frente da estratégia corporativa.
    t["ia_gap_pessoa_empresa"] = (
        t["ia_uso_individual"].select(
            "ano_pesquisa",
            F.col("pct").alias("pct_pessoas_usam"),
            F.col("base").alias("base_pessoas"))
        .join(
            t["ia_prioridade_empresa"].select(
                "ano_pesquisa",
                F.col("pct").alias("pct_empresas_priorizam"),
                F.col("base").alias("base_gestores")),
            "ano_pesquisa")
        .withColumn("gap_pp",
                    F.round(F.col("pct_pessoas_usam") - F.col("pct_empresas_priorizam"), 1))
        .orderBy("ano_pesquisa")
    )

    # =====================================================================
    # OPORTUNIDADE 2: onde está o talento que ninguém está disputando
    # =====================================================================
    # Concentração geográfica: se 60% está no Sudeste, o resto do país é
    # oferta subaproveitada para quem contrata remoto.
    base_geo = base_da_pergunta(silver, "regiao_moradia")
    t["talento_por_regiao"] = (
        base_geo.groupBy("ano_pesquisa", "regiao_moradia")
                .agg(F.count("*").alias("profissionais"),
                     F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
                .withColumn("pct_do_total",
                            F.round(100.0 * F.col("profissionais")
                                    / F.sum("profissionais").over(
                                        W.partitionBy("ano_pesquisa")), 1))
                .orderBy("ano_pesquisa", F.desc("profissionais"))
    )

    # Trabalho remoto: é o que torna a oferta de fora do Sudeste acessível.
    base_forma = base_da_pergunta(silver, "forma_trabalho")
    t["modelo_trabalho"] = (
        base_forma.groupBy("ano_pesquisa", "forma_trabalho")
                  .agg(F.count("*").alias("profissionais"))
                  .withColumn("pct",
                              F.round(100.0 * F.col("profissionais")
                                      / F.sum("profissionais").over(
                                          W.partitionBy("ano_pesquisa")), 1))
                  .orderBy("ano_pesquisa", F.desc("profissionais"))
    )

    # =====================================================================
    # OPORTUNIDADE 3: o custo de cada perfil
    # =====================================================================
    # Quanto custa cada senioridade e cada cargo. É o insumo direto do
    # planejamento de headcount.
    base_sal = (base_da_pergunta(silver, "salario_medio_mensal")
                .filter(F.col("nivel_senioridade").isNotNull()))
    t["custo_por_senioridade"] = (
        base_sal.groupBy("ano_pesquisa", "nivel_senioridade")
                .agg(F.count("*").alias("profissionais"),
                     F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"),
                     F.round(F.expr("percentile_approx(salario_medio_mensal, 0.5)"), 0).alias("mediana"))
                .orderBy("ano_pesquisa", "nivel_senioridade")
    )

    base_cargo = (base_da_pergunta(silver, "salario_medio_mensal")
                  .filter(F.col("cargo_atual").isNotNull()))
    t["custo_por_cargo"] = (
        apenas_comparavel(base_cargo)
        .groupBy("cargo_atual")
        .agg(F.count("*").alias("profissionais"),
             F.round(F.avg("salario_medio_mensal"), 0).alias("salario_medio"))
        .filter(F.col("profissionais") >= 50)      # corta cargo raro, que dá média instável
        .orderBy(F.desc("salario_medio"))
    )

    # =====================================================================
    # DESAFIO 1: o que trava a adoção de IA, na voz de quem decide
    # =====================================================================
    base_barr = base_da_pergunta(silver, "barreiras_ia_generativa")
    barreiras = [
        ("falta_expertise_ou_recurso", "Falta de expertise ou recurso"),
        ("falta_compreensao_caso_uso", "Falta de compreensão do caso de uso"),
        ("seguranca_privacidade_dados", "Segurança e privacidade dos dados"),
        ("falta_confiab_saida_alucinacao_modelo", "Confiabilidade da saída (alucinação)"),
        ("alta_direcao_nao_ve_valor_prioridade", "Alta direção não vê valor"),
        ("incerteza_rel_regulamentacao", "Incerteza regulatória"),
        ("preocupacao_prop_intelectual", "Propriedade intelectual"),
    ]
    t["barreiras_ia"] = None
    for col, rotulo in barreiras:
        parcial = indicador(base_barr, marcou("barreiras_ia_generativa", col),
                            por=["ano_pesquisa"], rotulo=rotulo)
        t["barreiras_ia"] = parcial if t["barreiras_ia"] is None \
            else t["barreiras_ia"].unionByName(parcial)
    t["barreiras_ia"] = t["barreiras_ia"].orderBy("ano_pesquisa", F.desc("pct"))

    # =====================================================================
    # DESAFIO 2: maturidade de dados: dá para fazer IA em cima do que tem?
    # =====================================================================
    # Sem data lake nem DW, projeto de IA vira projeto de engenharia de dados
    # antes de virar IA. É o desafio que atrasa cronograma.
    base_mat = base_da_pergunta(silver, "empresa_possui_datalake")
    t["maturidade_dados"] = (
        base_mat.groupBy("ano_pesquisa")
                .agg(F.count("*").alias("base"),
                     F.count(F.when(F.col("empresa_possui_datalake"), 1)).alias("com_datalake"),
                     F.count(F.when(F.col("empresa_possui_dw"), 1)).alias("com_dw"),
                     F.count(F.when(F.col("empresa_possui_datalake")
                                    | F.col("empresa_possui_dw"), 1)).alias("com_algum"),
                     F.count(F.when(~F.col("empresa_possui_datalake")
                                    & ~F.col("empresa_possui_dw"), 1)).alias("sem_nenhum"))
                .withColumn("pct_com_datalake", pct(F.col("com_datalake"), F.col("base")))
                .withColumn("pct_sem_nenhum", pct(F.col("sem_nenhum"), F.col("base")))
                .orderBy("ano_pesquisa")
    )

    # =====================================================================
    # DESAFIO 3: escassez de senioridade
    # =====================================================================
    # Se a pirâmide é jovem, contratar sênior é caro e demorado: e projeto de
    # IA precisa de sênior.
    base_nvl = base_da_pergunta(silver, "nivel_senioridade")
    t["piramide_senioridade"] = (
        apenas_comparavel(base_nvl)
        .groupBy("ano_pesquisa", "nivel_senioridade")
        .agg(F.count("*").alias("profissionais"))
        .withColumn("pct",
                    F.round(100.0 * F.col("profissionais")
                            / F.sum("profissionais").over(
                                W.partitionBy("ano_pesquisa")), 1))
        .orderBy("ano_pesquisa", "nivel_senioridade")
    )

    base_exp = base_da_pergunta(silver, "tempo_exp_dados")
    t["experiencia_mercado"] = indicador(
        base_exp,
        F.col("tempo_exp_dados").isin("Mais_de_10_anos", "de_7_a_10_anos"),
        por=["ano_pesquisa"], rotulo="7+ anos de experiência em dados",
    )

    # =====================================================================
    # DESAFIO 4: retenção
    # =====================================================================
    # Contratar não resolve se não segura. Layoff e insatisfação são o custo
    # escondido do plano de expansão.
    base_lay = base_da_pergunta(silver, "empresa_passou_layoff")
    t["layoff"] = (
        base_lay.groupBy("ano_pesquisa")
                .agg(F.count("*").alias("base"),
                     F.count(F.when(F.col("houve_layoff"), 1)).alias("houve"),
                     F.count(F.when(F.col("fui_afetado_layoff"), 1)).alias("afetado"))
                .withColumn("pct_houve", pct(F.col("houve"), F.col("base")))
                .withColumn("pct_afetado", pct(F.col("afetado"), F.col("base")))
                .orderBy("ano_pesquisa")
    )

    base_sat = base_da_pergunta(silver, "satisfeito_empresa")
    t["satisfacao"] = indicador(
        base_sat, F.col("satisfeito_empresa"),
        por=["ano_pesquisa"], rotulo="satisfeito com a empresa atual",
    )

    # O que faria a pessoa trocar de emprego: o preço da retenção.
    base_fat = base_da_pergunta(silver, "fatores_avaliacao_emprego")
    fatores = [
        ("remuneracao_salario", "Remuneração"),
        ("plano_carreira_oport_cresc_prof", "Plano de carreira"),
        ("flexibilidade_trab_remoto", "Flexibilidade / remoto"),
        ("maturidade_empresa_dados_tec", "Maturidade em dados da empresa"),
        ("qualidade_lideres_gestores", "Qualidade da liderança"),
        ("ambiente_clima_trabalho", "Ambiente e clima"),
        ("beneficios", "Benefícios"),
        ("oport_aprendizado_trab_ref_area", "Oportunidade de aprendizado"),
    ]
    t["fatores_retencao"] = None
    for col, rotulo in fatores:
        parcial = indicador(base_fat, marcou("fatores_avaliacao_emprego", col),
                            por=["ano_pesquisa"], rotulo=rotulo)
        t["fatores_retencao"] = parcial if t["fatores_retencao"] is None \
            else t["fatores_retencao"].unionByName(parcial)
    t["fatores_retencao"] = t["fatores_retencao"].orderBy("ano_pesquisa", F.desc("pct"))

    # =====================================================================
    # SÍNTESE: o painel que vai para o material executivo
    # =====================================================================
    # Uma linha por indicador por ano, com o denominador explícito. É esta
    # tabela que alimenta os gráficos da pergunta 7.
    t["painel_sintese"] = (
        t["ia_prioridade_empresa"]
        .unionByName(t["ia_uso_individual"])
        .unionByName(t["experiencia_mercado"])
        .unionByName(t["satisfacao"])
        .select("ano_pesquisa", "indicador", "base", "qtd", "pct")
        .orderBy("indicador", "ano_pesquisa")
    )

    return t


def main():
    spark = sessao("tc3-gold-p7")
    silver = ler_silver(spark).cache()

    print(f"\n=== Gold da pergunta {NUMERO}: {RESPONSAVEL} ===")
    print(f"{PERGUNTA}\n")

    for nome, df in construir(silver).items():
        gravar(df, PREFIXO + nome)

    spark.stop()


if __name__ == "__main__":
    main()
